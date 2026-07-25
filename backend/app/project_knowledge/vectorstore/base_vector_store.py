from abc import ABC, abstractmethod

from app.project_knowledge.models import EmbeddedChunk, SearchResult


class BaseVectorStore(ABC):

    @abstractmethod
    def store(
        self, 
        chunks: list[EmbeddedChunk],
    )-> None:
        """
        Store embedded Chunks.
        """
        pass

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int,
    )-> list[SearchResult]:
        """
        Search for the most similar chunks.
        """
        pass

    @abstractmethod
    def clear(
        self,
        ) -> None:
        """
        Remove all stored vectors.
        """
        pass

