from threading import RLock
from pathlib import Path

from rag.config import EMBEDDING_MODEL_NAME, SENTENCE_TRANSFORMERS_CACHE_PATH


_embedding_model = None
_embedding_lock = RLock()


def get_cached_embedding_model_path():
    model_path = Path(EMBEDDING_MODEL_NAME)
    if model_path.exists():
        return model_path

    try:
        from huggingface_hub import snapshot_download

        return Path(
            snapshot_download(
                EMBEDDING_MODEL_NAME,
                cache_dir=str(SENTENCE_TRANSFORMERS_CACHE_PATH),
                local_files_only=True,
            )
        )
    except Exception:
        return None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    with _embedding_lock:
        if _embedding_model is None:
            from langchain_huggingface import HuggingFaceEmbeddings

            SENTENCE_TRANSFORMERS_CACHE_PATH.mkdir(parents=True, exist_ok=True)
            cached_model_path = get_cached_embedding_model_path()
            _embedding_model = HuggingFaceEmbeddings(
                model_name=str(cached_model_path or EMBEDDING_MODEL_NAME),
                cache_folder=str(SENTENCE_TRANSFORMERS_CACHE_PATH),
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

    return _embedding_model


def preload_embedding_model():
    return get_embedding_model()
