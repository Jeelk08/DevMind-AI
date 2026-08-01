from pathlib import Path

from app.project_knowledge.loader.repository_loader import RepositoryLoader
from app.project_knowledge.models import (IndexResult)
from app.project_knowledge.parser.base_chunker import BaseChunker
from app.project_knowledge.embeddings.base_embedding_service import BaseEmbeddingService
from app.project_knowledge.vectorstore.base_vector_store import BaseVectorStore

class ProjectIndexer:

    def __init__(
        self, 
        loader: RepositoryLoader,
        chunker: BaseChunker,
        embedding_service: BaseEmbeddingService,
        vector_store: BaseVectorStore,
    ) -> None:
        self._loader = loader
        self._chunker = chunker
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    def index(self, project_path: Path) -> IndexResult:
        project_files = self._loader.load(project_path)

        files_indexed = 0
        chunks_created = 0
        skipped_files = 0

        for project_file in project_files:

            try:

                chunks = self._chunker.chunk(project_file)

                # if not project_file.content.strip():
                if not chunks:
                    skipped_files += 1
                    continue


                embedded_chunks = self._embedding_service.embed_chunks(chunks)

                if not embedded_chunks:
                    skipped_files += 1
                    continue

                
                self._vector_store.store(embedded_chunks) 

                files_indexed += 1
                chunks_created += len(chunks)



            except Exception as e: 
                print(f"\nFailed: {project_file.path}")
                print(type(e).__name__)
                print(e)
                skipped_files += 1
                continue
        return IndexResult(
            files_indexed= files_indexed,
            chunks_created= chunks_created,
            skipped_files= skipped_files,
        )
    
