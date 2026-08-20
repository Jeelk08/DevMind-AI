from pathlib import Path

from app.integrations.ai.gemini_client import GeminiClient
from app.core.config import GEMINI_API_KEY
from app.project_knowledge.embeddings.gemini_embedding_service import (
    GeminiEmbeddingService,
)
from app.project_knowledge.indexer.incremental_index_manager import (
    IncrementalIndexManager,
)
from app.project_knowledge.parser.generic_chunker import GenericChunker
from app.project_knowledge.vectorstore.in_memory_vector_store import (
    InMemoryVectorStore,
)


def create_project_file(path: Path, content: str):
    return type(
        "TestProjectFile",
        (),
        {
            "path": path,
            "content": content,
        },
    )()


def test_real_incremental_indexing(tmp_path):

    repository_root = tmp_path / "repo"
    repository_root.mkdir()

    client = GeminiClient(
        api_key=GEMINI_API_KEY
    )

    embedding_service = GeminiEmbeddingService(
        client
    )

    chunker = GenericChunker(
        max_chunk_size=1000,
        chunk_overlap=100,
    )

    vector_store = InMemoryVectorStore()

    manager = IncrementalIndexManager(
        repository_root=repository_root,
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # --------------------------------------------------
    # 1. First indexing
    # --------------------------------------------------

    a = create_project_file(
        repository_root / "a.py",
        "def hello():\n    return 'hello'",
    )

    b = create_project_file(
        repository_root / "b.py",
        "def add(a, b):\n    return a + b",
    )

    first = manager.update([a, b])

    print("\nFIRST INDEX")
    print(first)
    print("Vectors:", len(vector_store._chunks))

    assert first["added"] == 2
    assert first["indexed"] == 2
    assert first["failed"] == 0
    assert len(vector_store._chunks) > 0

    first_vector_count = len(vector_store._chunks)

    # --------------------------------------------------
    # 2. No changes
    # --------------------------------------------------

    second = manager.update([a, b])

    print("\nNO-CHANGE REINDEX")
    print(second)
    print("Vectors:", len(vector_store._chunks))

    assert second["reused"] == 2
    assert second["indexed"] == 0
    assert second["modified"] == 0
    assert second["deleted"] == 0
    assert second["failed"] == 0

    # No duplicate vectors.
    assert len(vector_store._chunks) == first_vector_count

    # --------------------------------------------------
    # 3. Modify one file
    # --------------------------------------------------

    modified_a = create_project_file(
        repository_root / "a.py",
        "def hello():\n"
        "    return 'hello from modified file'",
    )

    third = manager.update(
        [modified_a, b]
    )

    print("\nMODIFIED FILE")
    print(third)
    print("Vectors:", len(vector_store._chunks))

    assert third["modified"] == 1
    assert third["reused"] == 1
    assert third["indexed"] == 1
    assert third["failed"] == 0

    assert len(vector_store._chunks) > 0

    # --------------------------------------------------
    # 4. Delete one file
    # --------------------------------------------------

    fourth = manager.update(
        [modified_a]
    )

    print("\nDELETED FILE")
    print(fourth)
    print("Vectors:", len(vector_store._chunks))

    assert fourth["deleted"] == 1
    assert fourth["reused"] == 1
    assert fourth["failed"] == 0

    remaining_paths = {
        str(item.chunk.path)
        for item in vector_store._chunks
    }

    assert str(repository_root / "b.py") not in remaining_paths
    assert str(repository_root / "a.py") in remaining_paths