from sqlalchemy import func

from extensions.db import db
from models.chat_log import ChatLog

MISS_SCORE = 0.20


def get_helpful_rate_summary():
    total = ChatLog.query.count()
    if not total:
        return {
            "hitQuestionCount": 0,
            "missedQuestionCount": 0,
            "totalConsultCount": 0,
            "helpfulRate": 0,
            "helpfulRateText": "暂无数据",
        }

    hit_count = ChatLog.query.filter_by(hit_status="已命中").count()
    missed_count = total - hit_count

    hit_similarity_sum = (
        db.session.query(func.coalesce(func.sum(ChatLog.similarity), 0))
        .filter(ChatLog.hit_status == "已命中")
        .scalar()
    )

    total_score = hit_similarity_sum + missed_count * MISS_SCORE
    helpful_rate = round(total_score * 100 / total, 2)

    return {
        "hitQuestionCount": hit_count,
        "missedQuestionCount": missed_count,
        "totalConsultCount": total,
        "helpfulRate": helpful_rate,
        "helpfulRateText": f"{helpful_rate:g}%",
    }
