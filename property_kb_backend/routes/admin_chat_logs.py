from datetime import date

from flask import Blueprint, request
from sqlalchemy import func, or_

from extensions.db import db
from models.chat_log import ChatLog
from utils.auth import admin_required
from utils.response import fail, success


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
    start_date = (request.args.get("startDate") or "").strip()
    end_date = (request.args.get("endDate") or "").strip()
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

    if start_date:
        query = query.filter(ChatLog.created_at >= start_date)

    if end_date:
        query = query.filter(ChatLog.created_at < f"{end_date} 23:59:59")

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


@admin_chat_logs_bp.delete("/chat-logs/<int:log_id>")
@admin_required
def delete_chat_log(log_id):
    log = db.session.get(ChatLog, log_id)
    if not log:
        return fail("日志不存在", 404)

    db.session.delete(log)
    db.session.commit()
    return success(message="删除成功")


@admin_chat_logs_bp.post("/chat-logs/batch-delete")
@admin_required
def batch_delete_chat_logs():
    payload = request.get_json(silent=True) or {}
    ids = payload.get("ids")

    if not isinstance(ids, list) or not ids:
        return fail("请提供日志ID列表")

    count = ChatLog.query.filter(ChatLog.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return success({"deletedCount": count}, f"已删除 {count} 条日志")


@admin_chat_logs_bp.get("/chat-logs/stats")
@admin_required
def chat_log_stats():
    today = date.today().isoformat()
    total = ChatLog.query.count()
    today_count = ChatLog.query.filter(ChatLog.created_at >= today).count()
    hit_count = ChatLog.query.filter(ChatLog.hit_status == "已命中").count()
    unmatched_count = ChatLog.query.filter(ChatLog.hit_status == "未命中").count()
    avg_time = db.session.query(func.avg(ChatLog.response_time)).scalar()

    return success(
        {
            "total": total,
            "todayCount": today_count,
            "hitCount": hit_count,
            "unmatchedCount": unmatched_count,
            "avgResponseTime": round(float(avg_time or 0), 2),
        },
        "查询成功",
    )

