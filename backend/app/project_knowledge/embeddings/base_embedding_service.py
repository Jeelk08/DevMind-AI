"""
Purpose:
    Defines the interface that every embedding provider
    (Gemini, OpenAI, Ollama, etc.) must implement.

Why it exists:
    Keeps DevMind independent from any specific AI provider.
    This allows us to switch providers in the future without
    changing the rest of the application.
"""


from abc import ABC, abstractmethod

from app.project_knowledge.models import (Chunk, EmbeddedChunk)

class BaseEmbeddingService(ABC):

    #Used while indexing a project. Converts project chunks into vectore embeddings.
    @abstractmethod
    def embed_chunks(
        self, 
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:
        pass

    #Used while searching. Converts the users questions into a vector so it can be compared to against stored chunks.
    @abstractmethod
    def embed_query(
        self, 
        query: str,
    )-> list[float]:
        pass

    