from app.project_knowledge.embeddings.base_embedding_service import BaseEmbeddingService
from app.project_knowledge.models import SearchResult
from app.project_knowledge.vectorstore.base_vector_store import BaseVectorStore

from .base_retriever import BaseRetriever


class SimpleRetriever(BaseRetriever):

    def __init__(
        self,
        embedding_service: BaseEmbeddingService,
        vector_store: BaseVectorStore,
    ):
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int,
    ) -> list[SearchResult]:

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        query_embedding = self._embedding_service.embed_query(query)

        return self._vector_store.search(
            query_embedding,
            top_k,
        )