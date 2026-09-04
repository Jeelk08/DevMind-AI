import hashlib
import json
from pathlib import Path
from threading import Lock

from app.project_knowledge.embeddings.base_embedding_service import (
    BaseEmbeddingService,
)
from app.project_knowledge.models import EmbeddedChunk, ProjectFile
from app.project_knowledge.parser.base_chunker import BaseChunker
from app.project_knowledge.vectorstore.in_memory_vector_store import (
    InMemoryVectorStore,
)


class IncrementalIndexManager:

    CACHE_VERSION = 1
    _cache_locks = {}
    _cache_locks_lock = Lock()
    def __init__(
        self,
        repository_root: Path,
        chunker: BaseChunker,
        embedding_service: BaseEmbeddingService,
        vector_store: InMemoryVectorStore,
    ) -> None:

        self.repository_root = repository_root
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store

        self.cache_path = (
            repository_root.parent
            / ".devmind"
            / "repository_index.json"
        )

    def update(
        self,
        project_files: list[ProjectFile],
    ) -> dict:

        lock = self._get_cache_lock()
        with lock:

            return self._update_locked(
                project_files
            )


    def _update_locked(
        self,
        project_files: list[ProjectFile],
    ) -> dict:

        current_files = {
            self._relative_path(project_file.path): project_file
            for project_file in project_files
        }

        cache = self._load_cache()
        cached_files = cache.get("files", {})

        indexed = 0
        reused = 0
        modified = 0
        added = 0
        deleted = 0
        failed = 0

        # Build the complete vector set for the CURRENT project state.
        # We only replace the vector store after all files have been processed.
        final_chunks: list[EmbeddedChunk] = []
        new_cache: dict[str, dict] = {}

        # --------------------------------------------------
        # Detect deleted files
        # --------------------------------------------------

        for path in cached_files:
            if path not in current_files:
                deleted += 1

        # --------------------------------------------------
        # Process current files
        # --------------------------------------------------

        for path, project_file in current_files.items():

            current_hash = self._hash_content(
                project_file.content
            )

            cached = cached_files.get(path)

            # Existing and unchanged -> reuse cached embeddings.
            if cached and cached["hash"] == current_hash:

                embedded_chunks = self._deserialize_chunks(
                    cached["chunks"]
                )

                final_chunks.extend(embedded_chunks)
                new_cache[path] = cached
                reused += 1
                continue

            # New or modified file.
            if cached:
                modified += 1

            else:
                added += 1

            try:
                chunks = self.chunker.chunk(project_file)

                # File produced no chunks. It is still considered
                # successfully processed, but there is nothing to store.
                if not chunks:
                    new_cache[path] = {
                        "hash": current_hash,
                        "chunks": [],
                    }
                    indexed += 1
                    continue

                embedded_chunks = (
                    self.embedding_service.embed_chunks(
                        chunks
                    )
                )

                final_chunks.extend(embedded_chunks)

                new_cache[path] = {
                    "hash": current_hash,
                    "chunks": self._serialize_chunks(
                        embedded_chunks
                    ),
                }

                indexed += 1

            except Exception as e:

                failed += 1

                print(
                    f"\nFailed to index {project_file.path}"
                )
                print(type(e).__name__)
                print(e)

                # If a previously indexed file failed to update,
                # preserve its old knowledge and old cache entry.
                # This prevents a temporary embedding/API failure
                # from destroying otherwise valid project knowledge.
                if cached:
                    old_chunks = self._deserialize_chunks(
                        cached["chunks"]
                    )

                    final_chunks.extend(old_chunks)
                    new_cache[path] = cached

        # --------------------------------------------------
        # Replace vector store with the exact current state
        # --------------------------------------------------

        self.vector_store.clear()

        if final_chunks:
            self.vector_store.store(final_chunks)

        # --------------------------------------------------
        # Save cache
        # --------------------------------------------------

        self._save_cache(
            {
                "version": self.CACHE_VERSION,
                "files": new_cache,
            }
        )

        return {
            "indexed": indexed,
            "reused": reused,
            "modified": modified,
            "added": added,
            "deleted": deleted,
            "failed": failed,
        }


    # ------------------------------------------------------
    # Concurrency
    # ------------------------------------------------------

    def _get_cache_lock(self) -> Lock:

        cache_key = str(
            self.cache_path.resolve()
        )

        with self._cache_locks_lock:

            lock = self._cache_locks.get(
                cache_key
            )

            if lock is None:
                lock = Lock()

                self._cache_locks[
                    cache_key
                ] = lock

            return lock


    # ------------------------------------------------------
    # Hashing
    # ------------------------------------------------------

    def _hash_content(self, content: str) -> str:

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    # ------------------------------------------------------
    # Paths
    # ------------------------------------------------------

    def _relative_path(self, path: Path) -> str:

        try:
            return str(
                path.relative_to(self.repository_root)
            )

        except ValueError:
            return str(path)

    # ------------------------------------------------------
    # Serialization
    # ------------------------------------------------------

    def _serialize_chunks(
        self,
        embedded_chunks: list[EmbeddedChunk],
    ) -> list[dict]:

        return [
            {
                "content": embedded_chunk.chunk.content,
                "path": str(
                    embedded_chunk.chunk.path
                ),
                "start_offset":
                    embedded_chunk.chunk.start_offset,
                "end_offset":
                    embedded_chunk.chunk.end_offset,
                "vector": embedded_chunk.vector,
            }
            for embedded_chunk in embedded_chunks
        ]

    def _deserialize_chunks(
        self,
        chunks: list[dict],
    ) -> list[EmbeddedChunk]:

        from app.project_knowledge.models import Chunk

        return [
            EmbeddedChunk(
                chunk=Chunk(
                    content=item["content"],
                    path=Path(item["path"]),
                    start_offset=item["start_offset"],
                    end_offset=item["end_offset"],
                ),
                vector=item["vector"],
            )
            for item in chunks
        ]

    # ------------------------------------------------------
    # Cache
    # ------------------------------------------------------

    def _load_cache(self) -> dict:

        if not self.cache_path.exists():
            return {
                "version": self.CACHE_VERSION,
                "files": {},
            }

        try:

            with self.cache_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                cache = json.load(file)

            if cache.get("version") != self.CACHE_VERSION:

                return {
                    "version": self.CACHE_VERSION,
                    "files": {},
                }

            return cache

        except Exception:

            print(
                "Warning: Could not load repository index cache."
            )

            return {
                "version": self.CACHE_VERSION,
                "files": {},
            }

    def _save_cache(self, cache: dict) -> None:

        self.cache_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = self.cache_path.with_suffix(
            ".tmp"
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                cache,
                file,
                indent=2,
            )

        temporary_path.replace(
            self.cache_path
        )