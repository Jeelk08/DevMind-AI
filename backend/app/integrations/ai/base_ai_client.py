"""

Purpose:
    Defines the interface that every AI provider
    (Gemini, OpenAI, Ollama, etc.) must implement.

Why it exists:
    Keeps the rest of DevMind independent from any
    specific AI provider.
    
    Business services (ChatService, EmbeddingService)
    interact with this interface instead of talking
    directly to Gemini or any other provider.
"""

from abc import ABC, abstractmethod

class BaseAIClient(ABC):

    #Generates a text response from the AI, used by the chat service.
    @abstractmethod
    def generate_response(self, prompt: str,) -> str: 
        pass 

    #Generates embeddings for multiple texts. Used during project Indexing
    @abstractmethod
    def create_embeddings(self, texts: list[str],) -> list[list[float]]:
        pass