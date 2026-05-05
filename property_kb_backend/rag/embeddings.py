from threading import RLock

from rag.config import EMBEDDING_MODEL_NAME, SENTENCE_TRANSFORMERS_CACHE_PATH


_embedding_model = None
_embedding_lock = RLock()


def get_embedding_model():
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    with _embedding_lock:
        if _embedding_model is None:
            from langchain_huggingface import HuggingFaceEmbeddings

            SENTENCE_TRANSFORMERS_CACHE_PATH.mkdir(parents=True, exist_ok=True)
            _embedding_model = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                cache_folder=str(SENTENCE_TRANSFORMERS_CACHE_PATH),
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

    return _embedding_model


def preload_embedding_model():
    return get_embedding_model()
