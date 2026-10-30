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
import re
import time

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

        from .exceptions import AIRateLimitException

        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                response = self.client.models.generate_content(
                    model=CHAT_MODEL,
                    contents=prompt,
                )

                if not response.text:
                    raise GeminiClientException(
                        "Gemini returned an empty response."
                    )

                return response.text

            except Exception as exc:
                error_message = str(exc)
                normalized = error_message.upper()

                status_code = (
                    getattr(exc, "status_code", None)
                    or getattr(exc, "code", None)
                )

                is_rate_limited = (
                    status_code == 429
                    or "429" in normalized
                    or "RESOURCE_EXHAUSTED" in normalized
                )

                is_unavailable = (
                    status_code == 503
                    or "503" in normalized
                    or "UNAVAILABLE" in normalized
                )

                if is_rate_limited:
                    raise AIRateLimitException(
                        "Gemini API quota exhausted or rate limit reached. "
                        "Please try again later."
                    ) from exc

                if is_unavailable and attempt < max_attempts - 1:
                    delay = 2 ** (attempt + 1)
                    time.sleep(delay)
                    continue

                raise GeminiClientException(
                    f"Failed to communicate with Gemini: {error_message}"
                ) from exc

        raise GeminiClientException(
            "Gemini request failed after multiple attempts."
        )

    def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Create embeddings in bounded batches with quota-aware retries."""
        if not texts:
            return []

        all_vectors: list[list[float]] = []
        try:
            for start in range(0, len(texts), self.EMBEDDING_BATCH_SIZE):
                batch = texts[start:start + self.EMBEDDING_BATCH_SIZE]
                for attempt in range(4):
                    try:
                        response = self.client.models.embed_content(
                            model=EMBEDDING_MODEL,
                            contents=batch,
                        )
                        batch_vectors = [item.values for item in response.embeddings]
                        if len(batch_vectors) != len(batch):
                            raise GeminiClientException(
                                "Gemini returned an unexpected number of embedding vectors."
                            )
                        all_vectors.extend(batch_vectors)
                        break
                    except Exception as exc:
                        message = str(exc)
                        is_rate_limited = "429" in message or "RESOURCE_EXHAUSTED" in message
                        if not is_rate_limited or attempt == 3:
                            raise
                        # Honour Google's retry hint when present; otherwise back off.
                        match = re.search(r"retry in ([0-9]+(?:\.[0-9]+)?)s", message, re.I)
                        delay = float(match.group(1)) if match else min(2 ** (attempt + 1), 30)
                        time.sleep(min(delay, 90))

            if len(all_vectors) != len(texts):
                raise GeminiClientException(
                    "Embedding count does not match input count."
                )
            return all_vectors
        except GeminiClientException:
            raise
        except Exception as exc:
            # Keep the provider's original error in the exception chain/logs.
            raise GeminiClientException(
                f"Failed to create embeddings: {exc}"
            ) from exc
