from models.chat_log import ChatLog


def percent(part, total):
    if not total:
        return 0
    return round(part * 100 / total, 2)


def get_helpful_rate_summary():
    total_consult_count = ChatLog.query.count()
    hit_count = ChatLog.query.filter_by(hit_status="已命中").count()
    missed_count = ChatLog.query.filter_by(hit_status="未命中").count()
    helpful_score = hit_count * 0.8 + missed_count * 0.2
    helpful_rate = percent(helpful_score, total_consult_count)

    return {
        "hitQuestionCount": hit_count,
        "missedQuestionCount": missed_count,
        "totalConsultCount": total_consult_count,
        "helpfulRate": helpful_rate,
        "helpfulRateText": f"{helpful_rate:g}%" if total_consult_count else "暂无数据",
    }
