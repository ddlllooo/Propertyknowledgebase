from flask import Blueprint, request

from extensions.db import db
from models.chat_log import ChatLog
from models.feedback import Feedback
from models.qa import QaKnowledge
from utils.auth import get_current_user, login_required_user
from utils.response import fail, success


feedback_bp = Blueprint("feedback", __name__)


def normalize_feedback_type(value):
    feedback_type = (value or "").strip()
    if feedback_type == "需要人工处理":
        return "需要人工"
    return feedback_type


@feedback_bp.post("/create")
@login_required_user
def create_feedback():
    payload = request.get_json(silent=True) or {}
    feedback_type = normalize_feedback_type(payload.get("feedbackType"))
    suggestion = (payload.get("suggestion") or "").strip()
    chat_log_id = payload.get("chatLogId")
    qa_id = payload.get("qaId")

    if not feedback_type:
        return fail("反馈类型不能为空")
    if not chat_log_id and not qa_id:
        return fail("chatLogId 和 qaId 至少传一个")

    current_user = get_current_user()
    user_question = ""
    ai_answer = ""
    category = ""
    similarity = None

    if chat_log_id:
        chat_log = ChatLog.query.filter_by(
            id=chat_log_id,
            user_id=current_user.id,
        ).first()
        if not chat_log:
            return fail("咨询记录不存在", 404)

        user_question = chat_log.question
        ai_answer = chat_log.answer
        category = chat_log.category
        similarity = chat_log.similarity
        qa_id = None
    else:
        try:
            qa_id = int(qa_id)
        except (TypeError, ValueError):
            return fail("qaId 不正确")

        qa = db.session.get(QaKnowledge, qa_id)
        if not qa:
            return fail("知识库问答不存在", 404)

        user_question = qa.question
        ai_answer = qa.answer
        category = qa.category
        similarity = 1.0

    feedback = Feedback(
        user_id=current_user.id,
        username=current_user.username,
        chat_log_id=chat_log_id,
        qa_id=qa_id,
        user_question=user_question,
        ai_answer=ai_answer,
        feedback_type=feedback_type,
        suggestion=suggestion,
        status="待处理",
        category=category,
        similarity=similarity,
        admin_reply="暂无回复",
    )

    db.session.add(feedback)
    db.session.commit()

    return success(feedback.to_dict(), "反馈提交成功")


@feedback_bp.get("/my")
@login_required_user
def my_feedback():
    current_user = get_current_user()
    records = (
        Feedback.query.filter_by(user_id=current_user.id)
        .order_by(Feedback.created_at.desc(), Feedback.id.desc())
        .all()
    )

    return success([item.to_dict() for item in records], "查询成功")
