import time
from datetime import datetime

from extensions.db import db
from models.chat_log import ChatLog
from models.qa import QaKnowledge
from rag.config import RAG_MAX_DISTANCE_THRESHOLD, RAG_TOP_K
from rag.faiss_store import FaissIndexError, search_similar_docs
from rag.llm_client import LLMClientError, call_llm
from rag.prompt import FALLBACK_ANSWER, build_prompt


def distance_to_hit_similarity(distance):
    ratio = min(max(distance / RAG_MAX_DISTANCE_THRESHOLD, 0), 1)
    return round(0.95 - ratio * 0.2, 2)


def distance_to_miss_similarity(distance=None):
    if distance is None:
        return 0.35
    ratio = min(max(distance / max(RAG_MAX_DISTANCE_THRESHOLD, 0.01), 0), 2)
    return round(min(0.55, 0.35 + ratio * 0.1), 2)


def save_chat_log(user, question, answer, category, similarity, hit_status, need_human, response_time):
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
    return chat_log


def build_miss_result(user, question, started_at, distance=None, reason="未检索到可用知识"):
    response_time = round(time.perf_counter() - started_at, 2)
    similarity = distance_to_miss_similarity(distance)
    chat_log = save_chat_log(
        user=user,
        question=question,
        answer=FALLBACK_ANSWER,
        category="未分类",
        similarity=similarity,
        hit_status="未命中",
        need_human=True,
        response_time=response_time,
    )

    return {
        "answer": FALLBACK_ANSWER,
        "category": "未分类",
        "matchedQuestion": "",
        "similarity": similarity,
        "hitStatus": "未命中",
        "needHuman": True,
        "chatLogId": chat_log.id,
        "llmUsed": False,
        "answerSource": "知识库",
        "generationMode": "未命中",
        "ragTrace": reason,
    }


def rag_answer(question, current_user):
    question = (question or "").strip()
    if not question:
        raise ValueError("问题不能为空")

    started_at = time.perf_counter()

    try:
        search_results = search_similar_docs(question, k=RAG_TOP_K)
    except (FaissIndexError, ValueError) as exc:
        return build_miss_result(current_user, question, started_at, reason=str(exc))

    if not search_results:
        return build_miss_result(current_user, question, started_at)

    top_doc, top_distance = search_results[0]
    top_distance = float(top_distance)

    if top_distance > RAG_MAX_DISTANCE_THRESHOLD:
        return build_miss_result(
            current_user,
            question,
            started_at,
            top_distance,
            reason="检索结果相似度低于命中阈值",
        )

    context = "\n\n---\n\n".join(doc.page_content for doc, _score in search_results)
    prompt = build_prompt(context, question)
    metadata = top_doc.metadata or {}

    llm_used = True
    generation_mode = "质谱大模型生成"
    llm_error = ""
    try:
        answer = call_llm(prompt)
        if not answer:
            raise LLMClientError("质谱大模型返回内容为空")
    except LLMClientError as exc:
        answer = metadata.get("answer") or FALLBACK_ANSWER
        llm_used = False
        generation_mode = "知识库"
        llm_error = str(exc)

    qa_id = metadata.get("qa_id")
    if qa_id:
        qa = db.session.get(QaKnowledge, int(qa_id))
        if qa:
            qa.ask_count += 1

    category = metadata.get("category") or "未分类"
    matched_question = metadata.get("question") or ""
    similarity = distance_to_hit_similarity(top_distance)
    response_time = round(time.perf_counter() - started_at, 2)
    chat_log = save_chat_log(
        user=current_user,
        question=question,
        answer=answer,
        category=category,
        similarity=similarity,
        hit_status="已命中",
        need_human=False,
        response_time=response_time,
    )

    return {
        "answer": answer,
        "category": category,
        "matchedQuestion": matched_question,
        "similarity": similarity,
        "hitStatus": "已命中",
        "needHuman": False,
        "chatLogId": chat_log.id,
        "llmUsed": llm_used,
        "answerSource": "智能客服",
        "generationMode": generation_mode,
        "ragTrace": "质谱大模型调用成功" if llm_used else llm_error,
    }
