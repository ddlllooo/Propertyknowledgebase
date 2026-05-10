from datetime import date

from flask import Blueprint, request
from sqlalchemy import or_

from extensions.db import db
from models.chat_log import ChatLog
from models.qa import QaKnowledge
from services.category_service import ensure_category, refresh_category_question_count
from utils.auth import admin_required, get_current_user
from utils.response import fail, success


admin_qa_bp = Blueprint("admin_qa", __name__)


def get_positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def normalize_keywords(value):
    if isinstance(value, list):
        return ",".join(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, str):
        return value.strip()
    return ""


def get_optional_positive_int(value):
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


@admin_qa_bp.get("/list")
@admin_required
def list_qa():
    keyword = (request.args.get("keyword") or "").strip()
    category = (request.args.get("category") or "").strip()
    status = (request.args.get("status") or "").strip()
    page = get_positive_int(request.args.get("page"), 1)
    page_size = get_positive_int(request.args.get("pageSize"), 10)

    query = QaKnowledge.query

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                QaKnowledge.question.like(pattern),
                QaKnowledge.answer.like(pattern),
                QaKnowledge.keywords.like(pattern),
            )
        )

    if category:
        query = query.filter(QaKnowledge.category == category)

    if status:
        query = query.filter(QaKnowledge.status == status)

    total = query.count()
    records = (
        query.order_by(QaKnowledge.updated_at.desc(), QaKnowledge.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return success(
        {
            "list": [item.to_dict() for item in records],
            "total": total,
        },
        "查询成功",
    )


@admin_qa_bp.get("/stats")
@admin_required
def qa_stats():
    today = date.today().isoformat()
    total = QaKnowledge.query.count()
    published = QaKnowledge.query.filter(QaKnowledge.status == "已发布").count()
    disabled = QaKnowledge.query.filter(QaKnowledge.status == "已停用").count()
    draft = QaKnowledge.query.filter(QaKnowledge.status == "草稿").count()
    pending = QaKnowledge.query.filter(QaKnowledge.status == "待审核").count()
    today_updated = QaKnowledge.query.filter(QaKnowledge.updated_at >= today).count()

    return success(
        {
            "total": total,
            "published": published,
            "disabled": disabled,
            "draft": draft,
            "pending": pending,
            "todayUpdated": today_updated,
        },
        "查询成功",
    )


@admin_qa_bp.post("/batch-create")
@admin_required
def batch_create_qa():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return fail("请提供待导入的问答列表")

    current_user = get_current_user()
    created = []
    errors = []
    existing_questions = set(
        row[0]
        for row in db.session.query(QaKnowledge.question).all()
    )

    for idx, item_data in enumerate(items):
        question = (item_data.get("question") or "").strip()
        answer = (item_data.get("answer") or "").strip()
        category = (item_data.get("category") or "").strip()
        category_description = (item_data.get("categoryDescription") or "").strip()
        source = (item_data.get("source") or "").strip()
        status = (item_data.get("status") or "已发布").strip()

        if not question:
            errors.append({"row": idx + 1, "message": "问题不能为空"})
            continue
        if not answer:
            errors.append({"row": idx + 1, "message": "答案不能为空"})
            continue
        if not category:
            errors.append({"row": idx + 1, "message": "分类不能为空"})
            continue

        if question in existing_questions:
            errors.append({"row": idx + 1, "message": f"问题已存在：{question[:30]}"})
            continue

        ensure_category(category, category_description)
        item = QaKnowledge(
            question=question,
            answer=answer,
            category=category,
            keywords=normalize_keywords(item_data.get("keywords")),
            source=source,
            status=status,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        db.session.add(item)
        created.append(item)
        existing_questions.add(question)
        refresh_category_question_count(category)

    if created:
        db.session.commit()

    return success(
        {
            "createdCount": len(created),
            "errorCount": len(errors),
            "errors": errors,
        },
        f"成功导入 {len(created)} 条",
    )


@admin_qa_bp.post("/create")
@admin_required
def create_qa():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    answer = (payload.get("answer") or "").strip()
    category = (payload.get("category") or "").strip()
    category_description = (payload.get("categoryDescription") or "").strip()
    source = (payload.get("source") or "").strip()
    status = (payload.get("status") or "已发布").strip()
    chat_log_id = get_optional_positive_int(payload.get("chatLogId"))

    if not question:
        return fail("问题不能为空")
    if not answer:
        return fail("答案不能为空")

    existing = QaKnowledge.query.filter(QaKnowledge.question == question).first()
    if existing:
        return fail("该问题已存在，请勿重复创建")

    current_user = get_current_user()
    chat_log = db.session.get(ChatLog, chat_log_id) if chat_log_id else None
    if chat_log_id and not chat_log:
        return fail("咨询日志不存在", 404)

    ensure_category(category, category_description)
    item = QaKnowledge(
        question=question,
        answer=answer,
        category=category,
        keywords=normalize_keywords(payload.get("keywords")),
        source=source,
        status=status,
        created_by=current_user.id,
        updated_by=current_user.id,
    )

    db.session.add(item)
    if chat_log:
        chat_log.answer = answer
        chat_log.category = category or "未分类"
        chat_log.hit_status = "已命中"
        chat_log.need_human = False
        chat_log.similarity = max(float(chat_log.similarity or 0), 0.86)

    refresh_category_question_count(category)
    db.session.commit()

    return success(item.to_dict(), "新增成功")


@admin_qa_bp.put("/update/<int:qa_id>")
@admin_required
def update_qa(qa_id):
    item = db.session.get(QaKnowledge, qa_id)
    if not item:
        return fail("问答不存在", 404)

    payload = request.get_json(silent=True) or {}
    old_category = item.category
    category_description = (payload.get("categoryDescription") or "").strip()

    if "question" in payload:
        question = (payload.get("question") or "").strip()
        if not question:
            return fail("问题不能为空")
        item.question = question

    if "answer" in payload:
        answer = (payload.get("answer") or "").strip()
        if not answer:
            return fail("答案不能为空")
        item.answer = answer

    if "category" in payload:
        item.category = (payload.get("category") or "").strip()
        ensure_category(item.category, category_description)
    elif category_description:
        ensure_category(item.category, category_description)

    if "keywords" in payload:
        item.keywords = normalize_keywords(payload.get("keywords"))

    if "source" in payload:
        item.source = (payload.get("source") or "").strip()

    if "status" in payload:
        item.status = (payload.get("status") or "").strip()

    current_user = get_current_user()
    item.updated_by = current_user.id

    refresh_category_question_count(old_category)
    refresh_category_question_count(item.category)
    db.session.commit()

    return success(item.to_dict(), "修改成功")


@admin_qa_bp.delete("/delete/<int:qa_id>")
@admin_required
def delete_qa(qa_id):
    item = db.session.get(QaKnowledge, qa_id)
    if not item:
        return fail("问答不存在", 404)

    hard = (request.args.get("hard") or "").lower() in ("true", "1", "yes")
    category = item.category

    if hard:
        db.session.delete(item)
        db.session.commit()
        return success(message="已永久删除")
    else:
        current_user = get_current_user()
        item.status = "已停用"
        item.updated_by = current_user.id
        refresh_category_question_count(category)
        db.session.commit()
        return success(item.to_dict(), "删除成功")


@admin_qa_bp.post("/batch-delete")
@admin_required
def batch_delete_qa():
    payload = request.get_json(silent=True) or {}
    ids = payload.get("ids")
    hard = bool(payload.get("hard"))

    if not isinstance(ids, list) or not ids:
        return fail("请提供问答ID列表")

    items = QaKnowledge.query.filter(QaKnowledge.id.in_(ids)).all()
    if not items:
        return fail("未找到指定问答")

    categories = set()
    if hard:
        for item in items:
            categories.add(item.category)
            db.session.delete(item)
    else:
        current_user = get_current_user()
        for item in items:
            item.status = "已停用"
            item.updated_by = current_user.id
            categories.add(item.category)

    db.session.commit()
    for cat in categories:
        refresh_category_question_count(cat)

    action = "永久删除" if hard else "停用"
    return success({"deletedCount": len(items)}, f"已{action} {len(items)} 条问答")


@admin_qa_bp.post("/batch-status")
@admin_required
def batch_update_qa_status():
    payload = request.get_json(silent=True) or {}
    ids = payload.get("ids")
    status = (payload.get("status") or "").strip()

    valid_statuses = {"已发布", "草稿", "待审核", "已停用"}
    if not isinstance(ids, list) or not ids:
        return fail("请提供问答ID列表")
    if status not in valid_statuses:
        return fail("状态值无效")

    current_user = get_current_user()
    items = QaKnowledge.query.filter(QaKnowledge.id.in_(ids)).all()
    categories = set()
    for item in items:
        categories.add(item.category)
        item.status = status
        item.updated_by = current_user.id

    db.session.commit()
    for cat in categories:
        refresh_category_question_count(cat)

    return success({"updatedCount": len(items)}, f"已更新 {len(items)} 条问答状态")
