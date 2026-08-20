from pathlib import Path

from app.core.config import GEMINI_API_KEY
from app.integrations.ai.gemini_client import GeminiClient
from app.project_knowledge.embeddings.gemini_embedding_service import (
    GeminiEmbeddingService,
)
from app.project_knowledge.indexer.incremental_index_manager import (
    IncrementalIndexManager,
)
from app.project_knowledge.parser.generic_chunker import GenericChunker
from app.project_knowledge.retriever.simple_retriever import SimpleRetriever
from app.project_knowledge.vectorstore.in_memory_vector_store import (
    InMemoryVectorStore,
)


def make_project_file(path: Path, content: str):
    return type(
        "TestProjectFile",
        (),
        {
            "path": path,
            "content": content,
        },
    )()


def test_retrieval_reflects_incremental_update(tmp_path):

    repository_root = tmp_path / "repo"
    repository_root.mkdir()

    client = GeminiClient(
        api_key=GEMINI_API_KEY,
    )

    embedding_service = GeminiEmbeddingService(
        client=client,
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

    retriever = SimpleRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # --------------------------------------------------
    # 1. Initial project knowledge
    # --------------------------------------------------

    auth_file = make_project_file(
        repository_root / "auth.py",
        """
def authenticate_user(username, password):
    # DevMind test version:
    # Passwords are verified using bcrypt.
    return bcrypt.verify(password)
""",
    )

    first = manager.update([auth_file])

    print("\nFIRST INDEX")
    print(first)

    assert first["added"] == 1
    assert first["indexed"] == 1
    assert first["failed"] == 0

    # --------------------------------------------------
    # 2. Retrieve the original knowledge
    # --------------------------------------------------

    original_results = retriever.retrieve(
        query="Which password hashing algorithm is used?",
        top_k=1,
    )

    assert original_results

    original_content = original_results[0].chunk.content

    print("\nORIGINAL RETRIEVAL")
    print(original_content)

    assert "bcrypt" in original_content

    # --------------------------------------------------
    # 3. Modify the source file
    # --------------------------------------------------

    modified_auth_file = make_project_file(
        repository_root / "auth.py",
        """
def authenticate_user(username, password):
    # DevMind test version:
    # Passwords are now verified using Argon2.
    return argon2.verify(password)
""",
    )

    second = manager.update(
        [modified_auth_file]
    )

    print("\nAFTER MODIFICATION")
    print(second)

    assert second["modified"] == 1
    assert second["indexed"] == 1
    assert second["failed"] == 0

    # --------------------------------------------------
    # 4. Retrieve again
    # --------------------------------------------------

    updated_results = retriever.retrieve(
        query="Which password hashing algorithm is used?",
        top_k=1,
    )

    assert updated_results

    updated_content = updated_results[0].chunk.content

    print("\nUPDATED RETRIEVAL")
    print(updated_content)

    # The old knowledge must be gone.
    assert "bcrypt" not in updated_content

    # The new knowledge must be retrievable.
    assert "Argon2" in updated_content