import shutil
import threading

from rag.config import FAISS_INDEX_PATH, RAG_TOP_K, EMBEDDING_MODEL_NAME, BIGMODEL_API_KEY
from rag.document_builder import load_published_qa_documents
from rag.embeddings import get_embedding_model


_cached_vector_store = None
_cache_lock = threading.RLock()


class FaissIndexError(RuntimeError):
    pass


def faiss_index_exists():
    return FAISS_INDEX_PATH.exists() and (FAISS_INDEX_PATH / "index.faiss").exists()


def build_faiss_index():
    global _cached_vector_store

    documents = load_published_qa_documents()
    if not documents:
        raise FaissIndexError("没有已发布知识，无法构建向量库")

    if FAISS_INDEX_PATH.exists():
        shutil.rmtree(FAISS_INDEX_PATH)

    FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    from langchain_community.vectorstores import FAISS

    try:
        embedding_model = get_embedding_model()
        vector_store = FAISS.from_documents(documents, embedding_model)
        vector_store.save_local(str(FAISS_INDEX_PATH))

        with _cache_lock:
            _cached_vector_store = vector_store

        return vector_store
    except Exception as e:
        error_msg = str(e)
        # 检查是否是API相关错误
        if "1211" in error_msg or "模型不存在" in error_msg:
            diagnostic = {
                "error_type": "API_MODEL_ERROR",
                "model_name": EMBEDDING_MODEL_NAME,
                "api_key_configured": bool(BIGMODEL_API_KEY),
                "api_key_length": len(BIGMODEL_API_KEY) if BIGMODEL_API_KEY else 0,
                "suggestions": [
                    "检查智谱AI账户是否有embedding模型权限",
                    "确认API密钥是否有效且未过期",
                    "尝试将 EMBEDDING_MODEL_NAME 改为 embedding-2"
                ]
            }
            raise FaissIndexError(f"向量库重建失败: {error_msg}\n诊断信息: {diagnostic}") from e
        raise FaissIndexError(f"向量库重建失败: {error_msg}") from e


def load_faiss_index():
    global _cached_vector_store

    with _cache_lock:
        if _cached_vector_store is not None:
            return _cached_vector_store

    if not faiss_index_exists():
        raise FaissIndexError("FAISS 向量库不存在，请先重建向量库")

    from langchain_community.vectorstores import FAISS

    vector_store = FAISS.load_local(
        str(FAISS_INDEX_PATH),
        get_embedding_model(),
        allow_dangerous_deserialization=True,
    )

    with _cache_lock:
        _cached_vector_store = vector_store

    return vector_store


def search_similar_docs(question, k=RAG_TOP_K):
    if not question or not question.strip():
        raise ValueError("检索问题不能为空")

    vector_store = load_faiss_index()
    return vector_store.similarity_search_with_score(question.strip(), k=k)


def preload_faiss_index():
    if not faiss_index_exists():
        return
    try:
        load_faiss_index()
    except Exception:
        pass
