import os

from app.integrations.ai.gemini_client import GeminiClient
from app.project_knowledge.embeddings.gemini_embedding_service import (
    GeminiEmbeddingService,
)


def test_real_gemini_embedding():
    api_key = os.getenv("GEMINI_API_KEY")

    assert api_key, "GEMINI_API_KEY is not configured"

    client = GeminiClient(api_key=api_key)
    embedding_service = GeminiEmbeddingService(client)

    vectors = embedding_service.embed_query(
        "DevMind incremental indexing quota test"
    )

    assert vectors
    assert isinstance(vectors, list)
    assert len(vectors) > 0

    print(f"\nEmbedding succeeded.")
    print(f"Vector dimensions: {len(vectors)}")