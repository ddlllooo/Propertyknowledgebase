from datetime import datetime

from flask import Blueprint, request
from sqlalchemy import or_

from extensions.db import db
from models.feedback import Feedback
from models.qa import QaKnowledge
from services.category_service import ensure_category, refresh_category_question_count
from utils.auth import admin_required, get_current_user
from utils.response import fail, success


admin_feedback_bp = Blueprint("admin_feedback", __name__)


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


@admin_feedback_bp.get("/list")
@admin_required
def list_feedback():
    status = (request.args.get("status") or "").strip()
    feedback_type = (request.args.get("feedbackType") or "").strip()
    keyword = (request.args.get("keyword") or "").strip()
    page = get_positive_int(request.args.get("page"), 1)
    page_size = get_positive_int(request.args.get("pageSize"), 10)

    query = Feedback.query

    if status:
        query = query.filter(Feedback.status == status)

    if feedback_type:
        query = query.filter(Feedback.feedback_type == feedback_type)

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Feedback.user_question.like(pattern),
                Feedback.ai_answer.like(pattern),
                Feedback.suggestion.like(pattern),
                Feedback.admin_reply.like(pattern),
                Feedback.username.like(pattern),
            )
        )

    total = query.count()
    records = (
        query.order_by(Feedback.created_at.desc(), Feedback.id.desc())
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


@admin_feedback_bp.put("/status/<int:feedback_id>")
@admin_required
def update_feedback_status(feedback_id):
    feedback = db.session.get(Feedback, feedback_id)
    if not feedback:
        return fail("反馈不存在", 404)

    payload = request.get_json(silent=True) or {}
    status = (payload.get("status") or "").strip()
    admin_reply = (payload.get("adminReply") or "").strip()

    if status:
        feedback.status = status
    if admin_reply:
        feedback.admin_reply = admin_reply

    current_user = get_current_user()
    feedback.handled_by = current_user.id
    feedback.handled_at = datetime.now()
    db.session.commit()

    return success(feedback.to_dict(), "处理成功")


@admin_feedback_bp.post("/to-knowledge/<int:feedback_id>")
@admin_required
def feedback_to_knowledge(feedback_id):
    feedback = db.session.get(Feedback, feedback_id)
    if not feedback:
        return fail("反馈不存在", 404)

    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or feedback.user_question or "").strip()
    answer = (payload.get("answer") or feedback.ai_answer or "").strip()
    category = (payload.get("category") or feedback.category or "").strip()

    if not question:
        return fail("问题不能为空")
    if not answer:
        return fail("答案不能为空")

    current_user = get_current_user()
    ensure_category(category)
    qa = QaKnowledge(
        question=question,
        answer=answer,
        category=category,
        keywords=normalize_keywords(payload.get("keywords")),
        source="用户反馈补充",
        status="已发布",
        created_by=current_user.id,
        updated_by=current_user.id,
    )

    db.session.add(qa)
    refresh_category_question_count(category)
    feedback.status = "已处理"
    feedback.admin_reply = "已根据反馈补充至知识库"
    feedback.handled_by = current_user.id
    feedback.handled_at = datetime.now()
    db.session.commit()

    return success(qa.to_dict(), "已补充至知识库")


@admin_feedback_bp.delete("/delete/<int:feedback_id>")
@admin_required
def delete_feedback(feedback_id):
    feedback = db.session.get(Feedback, feedback_id)
    if not feedback:
        return fail("反馈不存在", 404)

    db.session.delete(feedback)
    db.session.commit()
    return success(message="删除成功")


@admin_feedback_bp.post("/batch-status")
@admin_required
def batch_update_feedback_status():
    payload = request.get_json(silent=True) or {}
    ids = payload.get("ids")
    status = (payload.get("status") or "").strip()

    valid_statuses = {"待处理", "处理中", "已处理", "已忽略"}
    if not isinstance(ids, list) or not ids:
        return fail("请提供反馈ID列表")
    if status not in valid_statuses:
        return fail("状态值无效")

    current_user = get_current_user()
    count = Feedback.query.filter(Feedback.id.in_(ids)).update(
        {
            Feedback.status: status,
            Feedback.handled_by: current_user.id,
            Feedback.handled_at: datetime.now(),
        },
        synchronize_session=False,
    )
    db.session.commit()
    return success({"updatedCount": count}, f"已更新 {count} 条反馈状态")
