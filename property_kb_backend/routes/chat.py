from flask import Blueprint, request

from models.chat_log import ChatLog
from rag.rag_service import rag_answer
from utils.auth import get_current_user, login_required_user
from utils.response import fail, success


chat_bp = Blueprint("chat", __name__)


@chat_bp.post("")
@login_required_user
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()

    if not question:
        return fail("问题不能为空")

    current_user = get_current_user()
    result = rag_answer(question, current_user)

    return success(result, "查询成功")


@chat_bp.get("/my-history")
@login_required_user
def my_history():
    current_user = get_current_user()
    records = (
        ChatLog.query.filter_by(user_id=current_user.id)
        .order_by(ChatLog.created_at.desc(), ChatLog.id.desc())
        .all()
    )

    return success([item.to_history_dict() for item in records], "查询成功")
