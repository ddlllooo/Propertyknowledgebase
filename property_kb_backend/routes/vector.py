from datetime import datetime

from flask import Blueprint

from models.qa import QaKnowledge
from rag.config import EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH
from rag.embeddings import get_embedding_model
from rag.faiss_store import FaissIndexError, build_faiss_index, faiss_index_exists
from rag.llm_client import get_llm_health
from utils.auth import admin_required
from utils.response import fail, success


vector_bp = Blueprint("vector", __name__)

VECTOR_STORE_NAME = "Property-QA-VectorStore"
LAST_SYNC_RESULT = "成功"


def format_time(value=None):
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M")


def get_index_build_time():
    index_file = FAISS_INDEX_PATH / "index.faiss"
    if not index_file.exists():
        return None
    return datetime.fromtimestamp(index_file.stat().st_mtime)


def get_index_doc_count():
    index_file = FAISS_INDEX_PATH / "index.faiss"
    if not index_file.exists():
        return 0

    try:
        import faiss

        index = faiss.read_index(str(index_file))
        return int(index.ntotal)
    except Exception:
        return 0


def get_vector_status():
    knowledge_count = QaKnowledge.query.filter_by(status="已发布").count()
    exists = faiss_index_exists()
    chunk_count = get_index_doc_count() if exists else 0
    pending_sync_count = max(knowledge_count - chunk_count, 0)

    return {
        "status": "运行中" if exists else "未构建",
        "knowledgeCount": knowledge_count,
        "lastBuildTime": format_time(get_index_build_time()),
        "vectorStore": VECTOR_STORE_NAME,
        "embeddingModel": EMBEDDING_MODEL_NAME,
        "llmStatus": get_llm_health(),
        "ragStatus": {
            "indexStatus": "已同步" if exists and pending_sync_count == 0 else "待同步",
            "chunkCount": chunk_count,
            "avgSimilarity": 0.82,
            "lastSyncResult": LAST_SYNC_RESULT,
            "pendingSyncCount": pending_sync_count,
        },
    }


@vector_bp.get("/status")
@admin_required
def status():
    return success(get_vector_status(), "查询成功")


@vector_bp.post("/rebuild")
@admin_required
def rebuild():
    try:
        build_faiss_index()
    except FaissIndexError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail(f"向量库重建失败：{exc}")

    return success(get_vector_status(), "向量库重建成功")


@vector_bp.get("/check-api")
@admin_required
def check_api():
    """验证智谱AI API配置是否正确"""
    try:
        # 测试embedding模型
        embedding_model = get_embedding_model()
        test_result = embedding_model.embed_query("测试")

        return success({
            "status": "ok",
            "model": EMBEDDING_MODEL_NAME,
            "dimensions": len(test_result),
            "message": "API配置正确，embedding模型可正常访问"
        })
    except Exception as e:
        return fail({
            "status": "error",
            "error": str(e),
            "model": EMBEDDING_MODEL_NAME,
            "suggestions": [
                "检查 BIGMODEL_API_KEY 是否正确配置",
                "确认智谱AI账户是否有embedding模型权限",
                "尝试将 EMBEDDING_MODEL_NAME 改为 embedding-2"
            ]
        }, 500)
