import math

from app.project_knowledge.models import (SearchResult, EmbeddedChunk)
from .base_vector_store import BaseVectorStore


class InMemoryVectorStore(BaseVectorStore):
    """
    An in-memory implementation of a vector store.
    
    Stores embedded chunks in a Python list and performs
    cosine similarity search over them.
    """ 
    def __init__(self):
        self._chunks: list[EmbeddedChunk] = []

    def store(self, chunks: list[EmbeddedChunk])-> None:
        """
        Store embedded chunks.

        Args: 
            chunks: List of embedded chunks to store.
        """
        self._chunks.extend(chunks) #not append because multiple chunks are being added at once

    def search(
            self,
            query_vector: list[float],
            top_k: int
        )-> list[SearchResult]:

            """
            Search for the most similar chunks.

            Args:
                query_vector: Embedding vector of the query.
                top_k: Number of results to return.

            Returns:
                List of SearchResult objects sorted by similarity.
            """
            if top_k <= 0:
                 raise ValueError("top_k must be greater than 0")

            results: list[SearchResult] = []
            for embedded_chunk in self._chunks:
                 similarity = self._cosine_similarity(
                      query_vector,
                      embedded_chunk.vector
                 )
                 results.append(
                      SearchResult(
                           chunk=embedded_chunk.chunk,
                           score=similarity
                      )
                 )
            results.sort(
                 key = lambda result: result.score,
                 reverse= True
            )

            return results[:top_k]

    def clear(self)-> None:
        """
        Remove all stored vectors.
        """
        self._chunks.clear()

        
    def _cosine_similarity(
              self,
              vector1: list[float],
              vector2: list[float]
    )-> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vector1: First embedding vector.
            vector2: Second embedding vector.

        Returns:
            Cosine similarity score.
        """
        if len(vector1) != len(vector2):
            raise ValueError("Embedding vectors must have the same dimensions.")
             
        dot_product = sum(
             a * b for a, b in zip(vector1, vector2)#zip -> pairs elements  with same index
        )

        magnitude1 = math.sqrt(
             sum(a * a for a in vector1)
        )
            
        magnitude2 = math.sqrt(
             sum(b * b for b in vector2)
        )

        if magnitude1 == 0 or magnitude2 == 0:
             return 0.0
        return dot_product / (magnitude1 * magnitude2)