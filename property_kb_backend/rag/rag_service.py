import time
from datetime import datetime

from extensions.db import db
from models.chat_log import ChatLog
from models.qa import QaKnowledge
from rag.config import RAG_MAX_DISTANCE_THRESHOLD, RAG_TOP_K
from rag.faiss_store import FaissIndexError, search_similar_docs
from rag.llm_client import LLMClientError, call_llm
from rag.prompt import FALLBACK_ANSWER, build_prompt


MISS_PATTERNS = [
    "知识库中没有",
    "知识库中暂无",
    "知识库中未收录",
    "知识库未找到",
    "知识库中没有相关",
    "知识库暂无相关",
    "暂无相关规定",
    "暂无相关记录",
    "暂无相关信息",
    "未找到相关",
    "没有相关信息",
    "没有相关记录",
    "没有相关规定",
    "建议您联系",
    "建议联系物业前台",
    "请联系物业前台",
    "请联系人工客服",
    "建议联系人工",
    "无法从知识库中",
    "不确定",
    "不太确定",
]


def is_llm_miss(answer: str) -> bool:
    if not answer:
        return True
    text = answer.strip()
    for pattern in MISS_PATTERNS:
        if pattern in text:
            return True
    return False


def distance_to_hit_similarity(distance):
    ratio = min(max(distance / RAG_MAX_DISTANCE_THRESHOLD, 0), 1)
    return round(0.95 - ratio * 0.2, 2)


def distance_to_miss_similarity(distance=None):
    if distance is None:
        return 0.35
    ratio = min(max(distance / max(RAG_MAX_DISTANCE_THRESHOLD, 0.01), 0), 2)
    return round(min(0.55, 0.35 + ratio * 0.1), 2)


def save_chat_log(user, question, answer, category, similarity, hit_status, need_human, response_time, is_guest=False):
    chat_log = ChatLog(
        user_id=user.id,
        username=user.username,
        question=question,
        answer=answer,
        category=category,
        similarity=similarity,
        hit_status=hit_status,
        need_human=need_human,
        is_guest=is_guest,
        response_time=response_time,
        created_at=datetime.now(),
    )
    db.session.add(chat_log)
    db.session.commit()
    return chat_log


def build_miss_result(user, question, started_at, distance=None, reason="未检索到可用知识", is_guest=False):
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
        is_guest=is_guest,
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


def rag_answer(question, current_user, is_guest=False):
    question = (question or "").strip()
    if not question:
        raise ValueError("问题不能为空")

    started_at = time.perf_counter()

    try:
        search_results = search_similar_docs(question, k=RAG_TOP_K)
    except (FaissIndexError, ValueError) as exc:
        return build_miss_result(current_user, question, started_at, reason=str(exc), is_guest=is_guest)

    if not search_results:
        return build_miss_result(current_user, question, started_at, is_guest=is_guest)

    top_doc, top_distance = search_results[0]
    top_distance = float(top_distance)

    if top_distance > RAG_MAX_DISTANCE_THRESHOLD:
        return build_miss_result(
            current_user,
            question,
            started_at,
            top_distance,
            reason="检索结果相似度低于命中阈值",
            is_guest=is_guest,
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

    # LLM 回答内容二次判断：检索命中但回答实质为"无答案"时，降级为未命中
    llm_miss = llm_used and is_llm_miss(answer)
    if llm_miss:
        hit_status = "未命中"
        need_human = True
        similarity = distance_to_miss_similarity(top_distance)
        rag_trace = "检索命中但回答内容表明知识库无相关内容"
    else:
        hit_status = "已命中"
        need_human = False
        similarity = distance_to_hit_similarity(top_distance)
        rag_trace = "质谱大模型调用成功" if llm_used else llm_error

    response_time = round(time.perf_counter() - started_at, 2)
    chat_log = save_chat_log(
        user=current_user,
        question=question,
        answer=answer,
        category=category,
        similarity=similarity,
        hit_status=hit_status,
        need_human=need_human,
        response_time=response_time,
        is_guest=is_guest,
    )

    return {
        "answer": answer,
        "category": category,
        "matchedQuestion": matched_question,
        "similarity": similarity,
        "hitStatus": hit_status,
        "needHuman": need_human,
        "chatLogId": chat_log.id,
        "llmUsed": llm_used,
        "answerSource": "智能客服",
        "generationMode": generation_mode,
        "ragTrace": rag_trace,
    }
