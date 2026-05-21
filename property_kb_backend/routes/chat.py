from datetime import datetime

from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt

from extensions.limiter import limiter
from models.chat_log import ChatLog
from rag.rag_service import rag_answer
from utils.auth import get_current_user, guest_or_user_required, login_required_user
from utils.response import fail, success


chat_bp = Blueprint("chat", __name__)

QUESTION_MAX_LENGTH = 200


@chat_bp.post("")
@limiter.limit("10/minute")
@login_required_user
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()

    if not question:
        return fail("问题不能为空")
    if len(question) > QUESTION_MAX_LENGTH:
        return fail(f"问题长度不能超过 {QUESTION_MAX_LENGTH} 个字符")

    current_user = get_current_user()
    result = rag_answer(question, current_user)

    return success(result, "查询成功")


GUEST_DAILY_LIMIT = 10


@chat_bp.post("/guest")
@limiter.limit("10/minute")
@guest_or_user_required
def guest_chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()

    if not question:
        return fail("问题不能为空")
    if len(question) > QUESTION_MAX_LENGTH:
        return fail(f"问题长度不能超过 {QUESTION_MAX_LENGTH} 个字符")

    claims = get_jwt()
    guest_id = claims.get("guest_id", "")
    guest_username = f"游客-{guest_id[:8]}"

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = ChatLog.query.filter(
        ChatLog.is_guest == True,
        ChatLog.created_at >= today_start,
        ChatLog.username == guest_username,
    ).count()

    if today_count >= GUEST_DAILY_LIMIT:
        return fail("游客每日问答次数已达上限（10次），请登录后继续使用", 429)

    result = rag_answer(question, g.current_user, is_guest=True)
    result["remainingCount"] = GUEST_DAILY_LIMIT - today_count - 1

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
