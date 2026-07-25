from abc import ABC, abstractmethod
from app.project_knowledge.models import SearchResult

class BaseRetriever(ABC):

    @abstractmethod
    def retrieve(
        self, 
        query: str,
        top_k: int
    )-> list[SearchResult]:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: User's search query.
            top_k: Number of results to retrieve.

        Returns:
            List of search results.
        """
        pass