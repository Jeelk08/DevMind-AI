"""Embedding adapter for Hugging Face Text Embeddings Inference (TEI).

Works with a TEI server on localhost during development or a remote TEI
service in production. The backend, not the browser, calls this service.
"""
from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.project_knowledge.models import Chunk, EmbeddedChunk
from .base_embedding_service import BaseEmbeddingService


class TEIEmbeddingError(RuntimeError):
    pass


class TEIEmbeddingService(BaseEmbeddingService):
    def __init__(
        self,
        base_url: str | None = None,
        model_id: str | None = None,
        api_key: str | None = None,
        batch_size: int = 16,
        max_batch_chars: int = 24000,
        timeout: int = 120,
        max_retries: int = 3,
    ) -> None:
        self.base_url = (base_url or os.getenv("EMBEDDING_BASE_URL", "http://127.0.0.1:8081")).rstrip("/")
        self.model_id = model_id or os.getenv("EMBEDDING_MODEL_ID", "BAAI/bge-m3")
        self.api_key = api_key or os.getenv("EMBEDDING_API_KEY")
        self.batch_size = max(1, batch_size)
        self.max_batch_chars = max(1000, max_batch_chars)
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def fingerprint(self) -> str:
        # Include model identity so cached vectors are never mixed across models.
        return f"tei:{self.model_id}:dense-v1"

    def _post(self, texts: list[str]) -> list[list[float]]:
        payload = json.dumps({"inputs": texts}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(f"{self.base_url}/embed", data=payload, headers=headers, method="POST")

        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    result = json.loads(response.read().decode("utf-8"))
                # TEI /embed returns a list of vectors, one per input.
                if not isinstance(result, list) or len(result) != len(texts):
                    raise TEIEmbeddingError("TEI returned an unexpected embedding count.")
                vectors = []
                for vector in result:
                    if not isinstance(vector, list) or not vector:
                        raise TEIEmbeddingError("TEI returned an invalid embedding vector.")
                    vectors.append([float(value) for value in vector])
                dimensions = {len(vector) for vector in vectors}
                if len(dimensions) != 1:
                    raise TEIEmbeddingError("TEI returned vectors with inconsistent dimensions.")
                return vectors
            except HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code in (429, 503) and attempt < self.max_retries:
                    retry_after = exc.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else min(2 ** attempt, 15)
                    time.sleep(delay)
                    continue
                raise TEIEmbeddingError(f"TEI HTTP {exc.code}: {body[:1000]}") from exc
            except (URLError, TimeoutError) as exc:
                if attempt < self.max_retries:
                    time.sleep(min(2 ** attempt, 10))
                    continue
                raise TEIEmbeddingError(f"Could not reach embedding server at {self.base_url}: {exc}") from exc
        raise TEIEmbeddingError("Embedding request exhausted retries.")

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        output: list[list[float]] = []
        batch: list[str] = []
        chars = 0
        for text in texts:
            if not text.strip():
                raise ValueError("Embedding input cannot be empty.")
            if batch and (len(batch) >= self.batch_size or chars + len(text) > self.max_batch_chars):
                output.extend(self._post(batch))
                batch, chars = [], 0
            batch.append(text)
            chars += len(text)
        if batch:
            output.extend(self._post(batch))
        return output

    def embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        valid = [chunk for chunk in chunks if chunk.content.strip()]
        vectors = self._embed_texts([chunk.content for chunk in valid])
        return [EmbeddedChunk(chunk=chunk, vector=vector) for chunk, vector in zip(valid, vectors)]

    def embed_query(self, query: str) -> list[float]:
        vectors = self._embed_texts([query])
        return vectors[0]
