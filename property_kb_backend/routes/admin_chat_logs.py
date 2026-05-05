from flask import Blueprint, request
from sqlalchemy import or_

from models.chat_log import ChatLog
from utils.auth import admin_required
from utils.response import success


admin_chat_logs_bp = Blueprint("admin_chat_logs", __name__)


def get_positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def parse_bool(value):
    if value is None or value == "":
        return None

    normalized = str(value).strip().lower()
    if normalized in ("true", "1", "yes", "y"):
        return True
    if normalized in ("false", "0", "no", "n"):
        return False
    return None


@admin_chat_logs_bp.get("/chat-logs")
@admin_required
def list_chat_logs():
    keyword = (request.args.get("keyword") or "").strip()
    category = (request.args.get("category") or "").strip()
    hit_status = (request.args.get("hitStatus") or "").strip()
    need_human = parse_bool(request.args.get("needHuman"))
    page = get_positive_int(request.args.get("page"), 1)
    page_size = get_positive_int(request.args.get("pageSize"), 10)

    query = ChatLog.query

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                ChatLog.question.like(pattern),
                ChatLog.answer.like(pattern),
            )
        )

    if category:
        query = query.filter(ChatLog.category == category)

    if hit_status:
        query = query.filter(ChatLog.hit_status == hit_status)

    if need_human is not None:
        query = query.filter(ChatLog.need_human == need_human)

    total = query.count()
    records = (
        query.order_by(ChatLog.created_at.desc(), ChatLog.id.desc())
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

