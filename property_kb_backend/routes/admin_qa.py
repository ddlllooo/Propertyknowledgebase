from flask import Blueprint, request
from sqlalchemy import or_

from extensions.db import db
from models.category import Category
from models.qa import QaKnowledge
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


def refresh_category_question_count(category_name):
    if not category_name:
        return

    category = Category.query.filter_by(name=category_name).first()
    if not category:
        return

    category.question_count = QaKnowledge.query.filter(
        QaKnowledge.category == category_name,
        QaKnowledge.status != "已停用",
    ).count()


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


@admin_qa_bp.post("/create")
@admin_required
def create_qa():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    answer = (payload.get("answer") or "").strip()
    category = (payload.get("category") or "").strip()
    source = (payload.get("source") or "").strip()
    status = (payload.get("status") or "已发布").strip()

    if not question:
        return fail("问题不能为空")
    if not answer:
        return fail("答案不能为空")

    current_user = get_current_user()
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

    current_user = get_current_user()
    item.status = "已停用"
    item.updated_by = current_user.id

    refresh_category_question_count(item.category)
    db.session.commit()

    return success(item.to_dict(), "删除成功")

