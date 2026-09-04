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

from app.core.config import CHAT_MODEL, EMBEDDING_MODEL

from .exceptions import GeminiClientException
from .base_ai_client import BaseAIClient


class GeminiClient(BaseAIClient):

    # Gemini accepts at most 100 embedding requests per batch.
    # We deliberately use a smaller batch size so DevMind does
    # not always operate at the API's hard batch limit.
    EMBEDDING_BATCH_SIZE = 50

    def __init__(self, api_key: str):

        # The client is created only once and reused for every request.
        # This avoids repeated initialization and keeps the application efficient.

        self.client = genai.Client(
            api_key=api_key,
        )

    def generate_response(
        self,
        prompt: str,
    ) -> str:

        try:
            # Send the prompt to Gemini
            response = self.client.models.generate_content(
                model=CHAT_MODEL,
                contents=prompt,
            )

            # Return only the generated text
            return response.text

        except Exception as e:
            print(e)

            raise GeminiClientException(
                "Failed to communicate with Gemini."
            ) from e

    def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        """
        Create embeddings for multiple texts.

        Inputs larger than EMBEDDING_BATCH_SIZE are split into
        smaller requests automatically.

        Args:
            texts:
                A list of text strings to embed.

        Returns:
            A list of embedding vectors in the same order
            as the input texts.

        Raises:
            GeminiClientException:
                If embedding creation fails.
        """

        if not texts:
            return []

        all_vectors: list[list[float]] = []

        try:
            for start in range(
                0,
                len(texts),
                self.EMBEDDING_BATCH_SIZE,
            ):

                batch = texts[
                    start:start + self.EMBEDDING_BATCH_SIZE
                ]

                response = self.client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                )

                batch_vectors = [
                    embedding.values
                    for embedding in response.embeddings
                ]

                # Make sure Gemini returned exactly one vector
                # for every input in this batch.
                if len(batch_vectors) != len(batch):
                    raise GeminiClientException(
                        "Gemini returned an unexpected number "
                        "of embedding vectors."
                    )

                all_vectors.extend(batch_vectors)

            # Final safety check: preserve the input/output contract.
            if len(all_vectors) != len(texts):
                raise GeminiClientException(
                    "Embedding count does not match input count."
                )

            return all_vectors

        except GeminiClientException:
            raise

        except Exception as e:
            print(e)

            raise GeminiClientException(
                "Failed to create embeddings."
            ) from e