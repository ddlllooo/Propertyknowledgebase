from datetime import datetime, time, timedelta

from flask import Blueprint, request
from sqlalchemy import func
from sqlalchemy import or_

from extensions.db import db
from models.category import Category
from models.chat_log import ChatLog
from models.qa import QaKnowledge
from services.feedback_metrics import get_helpful_rate_summary
from utils.response import fail, success


qa_bp = Blueprint("qa", __name__)


def get_positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


@qa_bp.get("/list")
def list_qa():
    keyword = (request.args.get("keyword") or "").strip()
    category = (request.args.get("category") or "").strip()
    status = (request.args.get("status") or "").strip()
    page = get_positive_int(request.args.get("page"), 1)
    page_size = get_positive_int(request.args.get("pageSize"), 10)

    query = QaKnowledge.query

    if status:
        query = query.filter(QaKnowledge.status == status)
    else:
        query = query.filter(QaKnowledge.status != "已停用")

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


@qa_bp.get("/detail/<int:qa_id>")
def qa_detail(qa_id):
    item = db.session.get(QaKnowledge, qa_id)
    if not item:
        return fail("问答不存在", 404)

    item.view_count += 1
    db.session.commit()

    return success(item.to_dict(), "查询成功")


@qa_bp.get("/categories")
def categories():
    records = (
        Category.query.filter(Category.status == "启用")
        .order_by(Category.sort_order.asc(), Category.id.asc())
        .all()
    )
    return success([item.to_dict() for item in records], "查询成功")


@qa_bp.get("/home-summary")
def home_summary():
    today = datetime.now().date()
    start = datetime.combine(today, time.min)
    end = start + timedelta(days=1)

    consult_category_records = (
        ChatLog.query.with_entities(
            ChatLog.category.label("name"),
            func.count(ChatLog.id).label("count"),
        )
        .filter(ChatLog.category != "")
        .group_by(ChatLog.category)
        .order_by(func.count(ChatLog.id).desc(), ChatLog.category.asc())
        .all()
    )
    consult_categories = [
        {
            "name": name or "未分类",
            "count": count,
        }
        for name, count in consult_category_records
    ]

    knowledge_category_records = (
        QaKnowledge.query.with_entities(
            QaKnowledge.category.label("name"),
            func.count(QaKnowledge.id).label("count"),
        )
        .filter(QaKnowledge.status != "已停用")
        .group_by(QaKnowledge.category)
        .order_by(func.count(QaKnowledge.id).desc(), QaKnowledge.category.asc())
        .all()
    )
    knowledge_categories = [
        {
            "name": name or "未分类",
            "count": count,
        }
        for name, count in knowledge_category_records
    ]

    hot_question_records = (
        ChatLog.query.with_entities(
            ChatLog.question.label("question"),
            func.count(ChatLog.id).label("count"),
        )
        .group_by(ChatLog.question)
        .order_by(func.count(ChatLog.id).desc(), func.max(ChatLog.created_at).desc())
        .limit(6)
        .all()
    )
    hot_questions = [
        {
            "question": question,
            "count": count,
        }
        for question, count in hot_question_records
    ]

    helpful_summary = get_helpful_rate_summary()
    top_category = consult_categories[0]["name"] if consult_categories else "暂无"

    return success(
        {
            "knowledgeCount": QaKnowledge.query.filter(
                QaKnowledge.status != "已停用"
            ).count(),
            "todayConsultCount": ChatLog.query.filter(
                ChatLog.created_at >= start,
                ChatLog.created_at < end,
            ).count(),
            "topCategory": top_category,
            "categories": knowledge_categories,
            "consultCategories": consult_categories,
            "hotQuestions": hot_questions,
            "hitQuestionCount": helpful_summary["hitQuestionCount"],
            "missedQuestionCount": helpful_summary["missedQuestionCount"],
            "helpfulRate": helpful_summary["helpfulRate"],
            "helpfulRateText": helpful_summary["helpfulRateText"],
        },
        "查询成功",
    )
