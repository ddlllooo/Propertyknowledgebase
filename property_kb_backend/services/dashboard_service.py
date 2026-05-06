from datetime import datetime, time, timedelta

from sqlalchemy import func

from extensions.db import db
from models.chat_log import ChatLog
from models.feedback import Feedback
from models.qa import QaKnowledge
from services.feedback_metrics import get_helpful_rate_summary


def percent(part, total):
    if not total:
        return 0
    return round(part * 100 / total, 2)


def get_overview():
    today = datetime.now().date()
    start = datetime.combine(today, time.min)
    end = start + timedelta(days=1)

    knowledge_count = QaKnowledge.query.count()
    published_count = QaKnowledge.query.filter_by(status="已发布").count()
    today_consult_count = ChatLog.query.filter(
        ChatLog.created_at >= start,
        ChatLog.created_at < end,
    ).count()
    total_consult_count = ChatLog.query.count()
    hit_count = ChatLog.query.filter_by(hit_status="已命中").count()
    helpful_summary = get_helpful_rate_summary()

    return {
        "knowledgeCount": knowledge_count,
        "publishedCount": published_count,
        "todayConsultCount": today_consult_count,
        "totalConsultCount": total_consult_count,
        "hitRate": percent(hit_count, total_consult_count),
        "hitQuestionCount": helpful_summary["hitQuestionCount"],
        "missedQuestionCount": helpful_summary["missedQuestionCount"],
        "helpfulRate": helpful_summary["helpfulRate"],
        "helpfulRateText": helpful_summary["helpfulRateText"],
        "pendingFeedback": Feedback.query.filter_by(status="待处理").count(),
        "needHumanCount": ChatLog.query.filter_by(need_human=True).count(),
    }


def get_daily_trend(days=7):
    today = datetime.now().date()
    start_date = today - timedelta(days=days - 1)
    start_dt = datetime.combine(start_date, time.min)

    consult_rows = (
        db.session.query(
            func.date(ChatLog.created_at).label("day"),
            func.count(ChatLog.id).label("cnt"),
        )
        .filter(ChatLog.created_at >= start_dt)
        .group_by(func.date(ChatLog.created_at))
        .all()
    )
    consult_map = {str(row.day): row.cnt for row in consult_rows}

    feedback_rows = (
        db.session.query(
            func.date(Feedback.created_at).label("day"),
            func.count(Feedback.id).label("cnt"),
        )
        .filter(Feedback.created_at >= start_dt)
        .group_by(func.date(Feedback.created_at))
        .all()
    )
    feedback_map = {str(row.day): row.cnt for row in feedback_rows}

    result = []
    for offset in range(days):
        day = today - timedelta(days=days - 1 - offset)
        key = day.strftime("%Y-%m-%d")
        result.append(
            {
                "date": day.strftime("%m-%d"),
                "consultCount": consult_map.get(key, 0),
                "feedbackCount": feedback_map.get(key, 0),
            }
        )

    return result


def get_hit_rate_trend(days=7):
    today = datetime.now().date()
    start_date = today - timedelta(days=days - 1)
    start_dt = datetime.combine(start_date, time.min)

    rows = (
        db.session.query(
            func.date(ChatLog.created_at).label("day"),
            func.count(ChatLog.id).label("total"),
            func.sum(
                func.if_(ChatLog.hit_status == "已命中", 1, 0)
            ).label("hits"),
        )
        .filter(ChatLog.created_at >= start_dt)
        .group_by(func.date(ChatLog.created_at))
        .all()
    )
    trend_map = {str(row.day): (row.total, row.hits or 0) for row in rows}

    result = []
    for offset in range(days):
        day = today - timedelta(days=days - 1 - offset)
        key = day.strftime("%Y-%m-%d")
        total, hits = trend_map.get(key, (0, 0))
        result.append(
            {
                "date": day.strftime("%m-%d"),
                "hitRate": percent(hits, total),
            }
        )

    return result


def get_hot_questions(limit=10):
    records = (
        ChatLog.query.with_entities(
            ChatLog.question.label("question"),
            func.count(ChatLog.id).label("count"),
        )
        .group_by(ChatLog.question)
        .order_by(func.count(ChatLog.id).desc(), func.max(ChatLog.created_at).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "question": question,
            "count": count,
        }
        for question, count in records
    ]


def get_category_ratio():
    records = (
        ChatLog.query.with_entities(
            ChatLog.category.label("name"),
            func.count(ChatLog.id).label("value"),
        )
        .group_by(ChatLog.category)
        .order_by(func.count(ChatLog.id).desc())
        .all()
    )

    return [
        {
            "name": name or "未分类",
            "value": value,
        }
        for name, value in records
    ]


def get_feedback_status():
    records = (
        Feedback.query.with_entities(
            Feedback.status.label("status"),
            func.count(Feedback.id).label("count"),
        )
        .group_by(Feedback.status)
        .order_by(func.count(Feedback.id).desc())
        .all()
    )

    return [
        {
            "status": status,
            "count": count,
        }
        for status, count in records
    ]


def get_unmatched_questions():
    records = (
        ChatLog.query.with_entities(
            ChatLog.question.label("question"),
            ChatLog.category.label("category"),
            func.count(ChatLog.id).label("count"),
        )
        .filter(ChatLog.hit_status == "未命中")
        .group_by(ChatLog.question, ChatLog.category)
        .order_by(func.count(ChatLog.id).desc())
        .all()
    )

    return [
        {
            "question": question,
            "count": count,
            "category": category or "未分类",
        }
        for question, category, count in records
    ]
