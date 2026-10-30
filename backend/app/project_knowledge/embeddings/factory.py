"""Central provider selection for repository embeddings."""
import os

from .base_embedding_service import BaseEmbeddingService
from .gemini_embedding_service import GeminiEmbeddingService
from .tei_embedding_service import TEIEmbeddingService


def create_embedding_service() -> BaseEmbeddingService:
    provider = os.getenv("EMBEDDING_PROVIDER", "tei").strip().lower()

    if provider in {"tei", "huggingface", "local"}:
        return TEIEmbeddingService()

    if provider == "gemini":
        from app.core.config import GEMINI_API_KEY
        from app.integrations.ai.gemini_client import GeminiClient

        if not GEMINI_API_KEY:
            raise RuntimeError("EMBEDDING_PROVIDER=gemini requires GEMINI_API_KEY.")
        return GeminiEmbeddingService(client=GeminiClient(api_key=GEMINI_API_KEY))

    raise ValueError(
        f"Unsupported EMBEDDING_PROVIDER '{provider}'. Choose 'tei' or 'gemini'."
    )
