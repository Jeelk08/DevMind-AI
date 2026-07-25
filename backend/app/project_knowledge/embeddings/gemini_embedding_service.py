"""
Gemini Embedding Service

Purpose:
    Converts Chunk objects into EmbeddedChunk objects
    using Gemini embeddings.

Dev Note:
    This service acts as a bridge between our domain
    models (Chunk, EmbeddedChunk) and the GeminiClient.

    GeminiClient knows nothing about Chunk objects.
    It only understands plain text.
"""

from app.project_knowledge.models import Chunk, EmbeddedChunk
from app.integrations.ai.base_ai_client import BaseAIClient

from .base_embedding_service import BaseEmbeddingService

class GeminiEmbeddingService(BaseEmbeddingService):

    def __init__(
            self,
            client: BaseAIClient,
    ):
        """
        Initialize the embedding service.

        Args:
            client:
                AI client responsible for creating embeddings.
        """

        self.client = client

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:

        chunks = [
            chunk
            for chunk in chunks
            if chunk.content.strip()
        ]

        if not chunks:
            return []

        texts = [
            chunk.content
            for chunk in chunks
        ]

        vectors = self.client.create_embeddings(texts)

        return [
            EmbeddedChunk(
                chunk=chunk,
                vector=vector,
            )
            for chunk, vector in zip(chunks, vectors)
        ]

    def embed_query(
            self,
            query: str,
    ) -> list[float]:
        """
        Create an embedding for a search query.
        """

        return self.client.create_embeddings(
            [query]
        )[0]