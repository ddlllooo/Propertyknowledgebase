import shutil

from rag.config import FAISS_INDEX_PATH, RAG_TOP_K
from rag.document_builder import load_published_qa_documents
from rag.embeddings import get_embedding_model


class FaissIndexError(RuntimeError):
    pass


def faiss_index_exists():
    return FAISS_INDEX_PATH.exists() and (FAISS_INDEX_PATH / "index.faiss").exists()


def build_faiss_index():
    documents = load_published_qa_documents()
    if not documents:
        raise FaissIndexError("没有已发布知识，无法构建向量库")

    if FAISS_INDEX_PATH.exists():
        shutil.rmtree(FAISS_INDEX_PATH)

    FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    from langchain_community.vectorstores import FAISS

    embedding_model = get_embedding_model()
    vector_store = FAISS.from_documents(documents, embedding_model)
    vector_store.save_local(str(FAISS_INDEX_PATH))

    return vector_store


def load_faiss_index():
    if not faiss_index_exists():
        raise FaissIndexError("FAISS 向量库不存在，请先重建向量库")

    from langchain_community.vectorstores import FAISS

    return FAISS.load_local(
        str(FAISS_INDEX_PATH),
        get_embedding_model(),
        allow_dangerous_deserialization=True,
    )


def search_similar_docs(question, k=RAG_TOP_K):
    if not question or not question.strip():
        raise ValueError("检索问题不能为空")

    vector_store = load_faiss_index()
    return vector_store.similarity_search_with_score(question.strip(), k=k)
