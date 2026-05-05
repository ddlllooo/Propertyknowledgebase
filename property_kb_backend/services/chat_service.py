import re
import time
from datetime import datetime

from extensions.db import db
from models.chat_log import ChatLog
from models.qa import QaKnowledge


DEFAULT_FALLBACK_ANSWER = (
    "您好，该问题暂未在知识库中找到明确答案，建议联系人工客服进一步核实。"
)
HIT_THRESHOLD = 5
STOPWORDS = {
    "可以",
    "如何",
    "怎么",
    "怎样",
    "什么",
    "哪些",
    "是否",
    "请问",
    "哪里",
    "一下",
    "办理",
    "需要",
}


def split_keywords(keywords):
    if not keywords:
        return []
    return [item.strip().lower() for item in keywords.split(",") if item.strip()]


def normalize_text(value):
    return (value or "").strip().lower()


def get_match_tokens(text):
    normalized = normalize_text(text)
    tokens = set(re.findall(r"[a-z0-9]+", normalized))
    chinese_chunks = re.findall(r"[\u4e00-\u9fff]+", normalized)

    for chunk in chinese_chunks:
        if len(chunk) == 1:
            tokens.add(chunk)
            continue

        for size in (2, 3):
            if len(chunk) < size:
                continue
            for index in range(len(chunk) - size + 1):
                token = chunk[index : index + size]
                if token not in STOPWORDS:
                    tokens.add(token)

    return {token for token in tokens if token and token not in STOPWORDS}


def calculate_score(user_question, qa_item):
    question_text = normalize_text(user_question)
    score = 0

    for keyword in split_keywords(qa_item.keywords):
        if keyword and (keyword in question_text or question_text in keyword):
            score += 5

    user_tokens = get_match_tokens(user_question)
    title_tokens = get_match_tokens(qa_item.question)
    answer_tokens = get_match_tokens(qa_item.answer)

    score += len(user_tokens & title_tokens) * 3
    score += len(user_tokens & answer_tokens)

    return score


def score_to_hit_similarity(score):
    return round(min(0.95, 0.75 + score * 0.02), 2)


def score_to_miss_similarity(score):
    return round(min(0.55, 0.35 + score * 0.03), 2)


def find_best_match(question):
    records = QaKnowledge.query.filter_by(status="已发布").all()
    best_item = None
    best_score = 0

    for item in records:
        score = calculate_score(question, item)
        if score > best_score:
            best_item = item
            best_score = score

    return best_item, best_score


def ask_question(user, question):
    started_at = time.perf_counter()
    best_item, best_score = find_best_match(question)
    is_hit = bool(best_item and best_score >= HIT_THRESHOLD)

    if is_hit:
        answer = best_item.answer
        category = best_item.category
        matched_question = best_item.question
        similarity = score_to_hit_similarity(best_score)
        hit_status = "已命中"
        need_human = False
        best_item.ask_count += 1
    else:
        answer = DEFAULT_FALLBACK_ANSWER
        category = "未分类"
        matched_question = ""
        similarity = score_to_miss_similarity(best_score)
        hit_status = "未命中"
        need_human = True

    response_time = round(time.perf_counter() - started_at, 2)
    chat_log = ChatLog(
        user_id=user.id,
        username=user.username,
        question=question,
        answer=answer,
        category=category,
        similarity=similarity,
        hit_status=hit_status,
        need_human=need_human,
        response_time=response_time,
        created_at=datetime.now(),
    )

    db.session.add(chat_log)
    db.session.commit()

    return {
        "answer": answer,
        "category": category,
        "matchedQuestion": matched_question,
        "similarity": similarity,
        "hitStatus": hit_status,
        "needHuman": need_human,
        "chatLogId": chat_log.id,
    }

