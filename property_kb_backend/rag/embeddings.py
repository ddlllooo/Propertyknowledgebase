from threading import RLock

from langchain_core.embeddings import Embeddings

from rag.config import BIGMODEL_API_KEY, EMBEDDING_DIMENSIONS, EMBEDDING_MODEL_NAME


class ZhipuEmbeddings(Embeddings):
    def __init__(self, api_key, model, dimensions=None):
        from zai import ZhipuAiClient

        self._client = ZhipuAiClient(api_key=api_key)
        self._model = model
        self._dimensions = dimensions

    def embed_documents(self, texts):
        """批量生成文档向量，智谱API单次最多25条，自动分批"""
        all_embeddings = []
        batch_size = 25
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            kwargs = {"model": self._model, "input": batch}
            if self._dimensions:
                kwargs["dimensions"] = self._dimensions
            resp = self._client.embeddings.create(**kwargs)
            all_embeddings.extend([d.embedding for d in resp.data])
        return all_embeddings

    def embed_query(self, text):
        """生成单条查询向量"""
        return self.embed_documents([text])[0]


_embedding_model = None
_embedding_lock = RLock()


def get_embedding_model():
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    with _embedding_lock:
        if _embedding_model is None:
            _embedding_model = ZhipuEmbeddings(
                api_key=BIGMODEL_API_KEY,
                model=EMBEDDING_MODEL_NAME,
                dimensions=EMBEDDING_DIMENSIONS,
            )

    return _embedding_model


def preload_embedding_model():
    return get_embedding_model()
