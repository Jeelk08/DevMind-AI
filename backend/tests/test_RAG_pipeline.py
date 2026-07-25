from pathlib import Path
import os

from dotenv import load_dotenv

from app.integrations.ai.gemini_client import GeminiClient

from app.project_knowledge.loader.file_filter import FileFilter
from app.project_knowledge.loader.repository_loader import RepositoryLoader

from app.project_knowledge.parser.generic_chunker import GenericChunker

from app.project_knowledge.embeddings.gemini_embedding_service import (
    GeminiEmbeddingService,
)

from app.project_knowledge.vectorstore.in_memory_vector_store import (
    InMemoryVectorStore,
)

from app.project_knowledge.retriever.simple_retriever import (
    SimpleRetriever,
)

from app.project_knowledge.indexer.project_indexer import (
    ProjectIndexer,
)


def main():

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key is None:
        raise RuntimeError("GEMINI_API_KEY not found in .env")

    print("=" * 70)
    print("DEVMIND AI RAG PIPELINE TEST")
    print("=" * 70)

    project_path = Path(".")

    # ---------- Dependencies ----------

    client = GeminiClient(
        api_key=api_key,
    )

    file_filter = FileFilter()

    loader = RepositoryLoader(
        file_filter=file_filter,
    )

    chunker = GenericChunker()

    embedding_service = GeminiEmbeddingService(
        client=client,
    )

    vector_store = InMemoryVectorStore()

    indexer = ProjectIndexer(
        loader=loader,
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    retriever = SimpleRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # ---------- Index ----------

    print("\nIndexing project...\n")

    result = indexer.index(project_path)

    print("\nIndexing Complete!\n")

    print(f"Files Indexed : {result.files_indexed}")
    print(f"Chunks Created: {result.chunks_created}")
    print(f"Skipped Files : {result.skipped_files}")

    # ---------- Queries ----------

    questions = [
        "What is MemoryManager?",
        "Explain DevMindAgent.",
        "How does ToolRegistry work?",
        "Where is GeminiClient implemented?",
    ]

    for question in questions:

        print("\n" + "=" * 70)
        print(question)
        print("=" * 70)

        chunks = retriever.retrieve(
            query=question,
            top_k=3,
        )

        if not chunks:
            print("No relevant chunks found.")
            continue

        for i, chunk in enumerate(chunks, start=1):

            print(f"\nChunk {i}")
            print("-" * 70)

            print("Path:")
            print(chunk.path)

            print("\nOffsets:")
            print(chunk.start_offset, "-", chunk.end_offset)

            print("\nContent:\n")
            print(chunk.content)

            print("-" * 70)


if __name__ == "__main__":
    main()