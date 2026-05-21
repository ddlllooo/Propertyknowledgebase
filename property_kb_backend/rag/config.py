import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent


def backend_path_from_env(env_name, default_relative_path):
    raw_path = os.getenv(env_name, default_relative_path)
    path = Path(raw_path)
    return path if path.is_absolute() else BASE_DIR / path


def load_env_files():
    if not load_dotenv:
        return

    for env_path in (ROOT_DIR / ".env", BASE_DIR / ".env"):
        if env_path.exists():
            load_dotenv(env_path, override=False)


load_env_files()


BIGMODEL_API_KEY = os.getenv("BIGMODEL_API_KEY", "")
BIGMODEL_BASE_URL = os.getenv("BIGMODEL_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
BIGMODEL_MODEL = os.getenv("BIGMODEL_MODEL", "GLM-4.5-Air")

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "embedding-3",
)
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))

FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "storage/faiss_index")
FAISS_INDEX_PATH = BASE_DIR / FAISS_INDEX_DIR

HF_CACHE_PATH = backend_path_from_env("HF_CACHE_DIR", "storage/hf_cache")
HF_HUB_CACHE_PATH = HF_CACHE_PATH / "hub"
SENTENCE_TRANSFORMERS_CACHE_PATH = HF_CACHE_PATH / "sentence_transformers"
TRANSFORMERS_CACHE_PATH = HF_CACHE_PATH / "transformers"

os.environ.setdefault("HF_HOME", str(HF_CACHE_PATH))
os.environ.setdefault("HF_HUB_CACHE", str(HF_HUB_CACHE_PATH))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(HF_HUB_CACHE_PATH))
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(SENTENCE_TRANSFORMERS_CACHE_PATH))
os.environ.setdefault("TRANSFORMERS_CACHE", str(TRANSFORMERS_CACHE_PATH))

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
RAG_MAX_DISTANCE_THRESHOLD = float(os.getenv("RAG_MAX_DISTANCE_THRESHOLD", "1.2"))
RAG_PRELOAD_EMBEDDINGS = os.getenv("RAG_PRELOAD_EMBEDDINGS", "true").lower() not in {
    "0",
    "false",
    "no",
    "off",
}
