import json
from pathlib import Path

from app.project_knowledge.models import Chunk, EmbeddedChunk
from app.project_knowledge.vectorstore.in_memory_vector_store import (
    InMemoryVectorStore,
)
from app.project_knowledge.indexer.incremental_index_manager import (
    IncrementalIndexManager,
)


class FakeChunker:
    """Creates one deterministic chunk per project file."""

    def chunk(self, project_file):
        return [
            Chunk(
                content=project_file.content,
                path=project_file.path,
                start_offset=0,
                end_offset=len(project_file.content),
            )
        ]


class FakeEmbeddingService:
    """Deterministic embedding service used so tests never consume Gemini quota."""

    def __init__(self):
        self.calls = []

    def embed_chunks(self, chunks):
        self.calls.append(list(chunks))

        embedded = []
        for chunk in chunks:
            # Deterministic vector based on content length.
            value = float(len(chunk.content) or 1)
            embedded.append(
                EmbeddedChunk(
                    chunk=chunk,
                    vector=[value, 1.0],
                )
            )

        return embedded


def make_project_file(path: Path, content: str):
    """
    Create a lightweight ProjectFile-compatible object.

    IncrementalIndexManager only requires .path and .content during update(),
    so we don't need to depend on a particular ProjectFile constructor here.
    """
    return type(
        "TestProjectFile",
        (),
        {"path": path, "content": content},
    )()


def create_manager(tmp_path):
    repository_root = tmp_path / "repo"
    repository_root.mkdir()

    embedding_service = FakeEmbeddingService()
    vector_store = InMemoryVectorStore()

    manager = IncrementalIndexManager(
        repository_root=repository_root,
        chunker=FakeChunker(),
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    return (
        manager,
        embedding_service,
        vector_store,
        repository_root,
    )


def test_first_index_indexes_all_files(tmp_path):
    manager, embedding_service, vector_store, repository_root = (
        create_manager(tmp_path)
    )

    files = [
        make_project_file(repository_root / "a.py", "aaa"),
        make_project_file(repository_root / "b.py", "bbbb"),
        make_project_file(repository_root / "c.py", "ccccc"),
    ]

    result = manager.update(files)

    assert result["added"] == 3
    assert result["indexed"] == 3
    assert result["reused"] == 0
    assert result["modified"] == 0
    assert result["deleted"] == 0
    assert result["failed"] == 0

    assert len(embedding_service.calls) == 3
    assert len(vector_store._chunks) == 3


def test_second_index_with_no_changes_reuses_cached_vectors(
    tmp_path,
):
    manager, embedding_service, vector_store, repository_root = (
        create_manager(tmp_path)
    )

    files = [
        make_project_file(repository_root / "a.py", "aaa"),
        make_project_file(repository_root / "b.py", "bbbb"),
        make_project_file(repository_root / "c.py", "ccccc"),
    ]

    first = manager.update(files)

    assert first["indexed"] == 3
    assert len(embedding_service.calls) == 3

    second = manager.update(files)

    assert second["reused"] == 3
    assert second["indexed"] == 0
    assert second["added"] == 0
    assert second["modified"] == 0
    assert second["deleted"] == 0
    assert second["failed"] == 0

    # Re-indexing unchanged files must not call the embedding service again.
    assert len(embedding_service.calls) == 3

    # The vector store must not accumulate duplicate vectors.
    assert len(vector_store._chunks) == 3


def test_modified_file_replaces_old_vectors(tmp_path):
    manager, embedding_service, vector_store, repository_root = (
        create_manager(tmp_path)
    )

    a = make_project_file(repository_root / "a.py", "aaa")
    b = make_project_file(repository_root / "b.py", "bbbb")

    manager.update([a, b])

    modified_a = make_project_file(
        repository_root / "a.py",
        "this file has changed",
    )

    result = manager.update([modified_a, b])

    assert result["modified"] == 1
    assert result["reused"] == 1
    assert result["indexed"] == 1
    assert result["added"] == 0
    assert result["deleted"] == 0
    assert result["failed"] == 0

    # Only the modified file should be embedded again.
    assert len(embedding_service.calls) == 3

    # One vector for a.py + one vector for b.py.
    assert len(vector_store._chunks) == 2

    stored_paths = {
        str(embedded.chunk.path)
        for embedded in vector_store._chunks
    }

    assert stored_paths == {
        str(repository_root / "a.py"),
        str(repository_root / "b.py"),
    }

    stored_a = [
        embedded
        for embedded in vector_store._chunks
        if embedded.chunk.path == repository_root / "a.py"
    ]

    assert len(stored_a) == 1
    assert stored_a[0].chunk.content == "this file has changed"


def test_deleted_file_is_removed_from_vector_store(tmp_path):
    manager, embedding_service, vector_store, repository_root = (
        create_manager(tmp_path)
    )

    a = make_project_file(repository_root / "a.py", "aaa")
    b = make_project_file(repository_root / "b.py", "bbbb")
    c = make_project_file(repository_root / "c.py", "ccccc")

    manager.update([a, b, c])

    result = manager.update([a, c])

    assert result["deleted"] == 1
    assert result["reused"] == 2
    assert result["indexed"] == 0
    assert result["modified"] == 0
    assert result["added"] == 0
    assert result["failed"] == 0

    stored_paths = {
        str(embedded.chunk.path)
        for embedded in vector_store._chunks
    }

    assert str(repository_root / "b.py") not in stored_paths
    assert len(vector_store._chunks) == 2


def test_new_file_is_indexed_without_reembedding_existing_files(
    tmp_path,
):
    manager, embedding_service, vector_store, repository_root = (
        create_manager(tmp_path)
    )

    a = make_project_file(repository_root / "a.py", "aaa")
    b = make_project_file(repository_root / "b.py", "bbbb")

    manager.update([a, b])

    c = make_project_file(repository_root / "c.py", "ccccc")

    result = manager.update([a, b, c])

    assert result["added"] == 1
    assert result["indexed"] == 1
    assert result["reused"] == 2
    assert result["modified"] == 0
    assert result["deleted"] == 0
    assert result["failed"] == 0

    # Only c.py should trigger a new embedding call.
    assert len(embedding_service.calls) == 3
    assert len(vector_store._chunks) == 3


def test_failed_embedding_does_not_write_failed_file_to_cache(
    tmp_path,
):
    class FailingEmbeddingService(FakeEmbeddingService):
        def embed_chunks(self, chunks):
            self.calls.append(list(chunks))

            if any("FAIL" in chunk.content for chunk in chunks):
                raise RuntimeError("simulated embedding failure")

            return super().embed_chunks(chunks)

    repository_root = tmp_path / "repo"
    repository_root.mkdir()

    embedding_service = FailingEmbeddingService()
    vector_store = InMemoryVectorStore()

    manager = IncrementalIndexManager(
        repository_root=repository_root,
        chunker=FakeChunker(),
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    good = make_project_file(repository_root / "good.py", "good")
    bad = make_project_file(repository_root / "bad.py", "FAIL")

    result = manager.update([good, bad])

    assert result["indexed"] == 1
    assert result["failed"] == 1
    assert len(vector_store._chunks) == 1

    cache = json.loads(
        manager.cache_path.read_text(encoding="utf-8")
    )

    assert "good.py" in cache["files"]
    assert "bad.py" not in cache["files"]

def test_modified_file_embedding_failure_preserves_old_knowledge(
    tmp_path,
):
    class FailingEmbeddingService(FakeEmbeddingService):
        def embed_chunks(self, chunks):
            if any("FAIL" in chunk.content for chunk in chunks):
                self.calls.append(list(chunks))
                raise RuntimeError("simulated embedding failure")

            return super().embed_chunks(chunks)

    repository_root = tmp_path / "repo"
    repository_root.mkdir()

    embedding_service = FailingEmbeddingService()
    vector_store = InMemoryVectorStore()

    manager = IncrementalIndexManager(
        repository_root=repository_root,
        chunker=FakeChunker(),
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # First successful indexing.
    original = make_project_file(
        repository_root / "app.py",
        "original content",
    )

    first_result = manager.update([original])

    assert first_result["indexed"] == 1
    assert first_result["failed"] == 0

    assert len(vector_store._chunks) == 1
    assert (
        vector_store._chunks[0].chunk.content
        == "original content"
    )

    # Now modify the file, but make embedding fail.
    modified = make_project_file(
        repository_root / "app.py",
        "FAIL modified content",
    )

    second_result = manager.update([modified])

    assert second_result["modified"] == 1
    assert second_result["failed"] == 1
    assert second_result["indexed"] == 0

    # Old knowledge must remain available.
    assert len(vector_store._chunks) == 1
    assert (
        vector_store._chunks[0].chunk.content
        == "original content"
    )

    # Cache must still contain the old successful version.
    cache = json.loads(
        manager.cache_path.read_text(encoding="utf-8")
    )

    assert "app.py" in cache["files"]

    assert (
        cache["files"]["app.py"]["chunks"][0]["content"]
        == "original content"
    )