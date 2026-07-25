"""
Purpose:
    Handles all communication with Google's Gemini API.

Why it exists:
    Keeps Gemini-specific code isolated from the rest
    of DevMind.

    Business services should interact with this class
    instead of directly using the Google SDK.
"""


from google import genai
from app.core.config import (CHAT_MODEL, EMBEDDING_MODEL)
from .exceptions import GeminiClientException
from .base_ai_client import BaseAIClient

class GeminiClient(BaseAIClient):

    def __init__(self, api_key: str,):

        # The client is created only once and reused for every request.
        # This avoids repeated initialization and keeps the application efficient.
        
        self.client = genai.Client(
            api_key = api_key,
        )


    def generate_response(
            self, 
            prompt: str,
    )-> str:
 
        try:
            #Send the prompt to Gemini
            response = self.client.models.generate_content(
                model = CHAT_MODEL,
                contents = prompt,
            )

            #Return only the genrated text
            return response.text

        except Exception as e:
            raise GeminiClientException(
                "Failed to communicate with Gemini."
            )from e

    def create_embeddings(
            self,
            texts: list[str],
    )-> list[list[float]]:

        """
        Create embeddings for multiple texts.

        Args:
        texts:
            A list of text strings to embed.

        Returns:
        A list of embedding vectors.

        Raises:
        GeminiClientException:
            If embedding creation fails.
        """

        try:
            response = self.client.models.embed_content(
                model = EMBEDDING_MODEL,
                contents = texts,
            )

            return [
                embedding.values
                for embedding in response.embeddings
            ]
        
            #Equivalent to this
            #vectors = []
            # for embedding in response.embeddings:
            #     vectors.append(
            #         embedding.values
            #     )
            # return vectors

        except Exception as e:
            print(e)
            raise GeminiClientException(
                "Failed to create embeddings."
            )from e