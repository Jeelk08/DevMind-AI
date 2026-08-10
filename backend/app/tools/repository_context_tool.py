from pathlib import Path

from app.tools.base_tool import BaseTool
from app.tools.tool_request import ToolRequest
from app.tools.tool_response import ToolResponse

from app.project_knowledge.loader.repository_loader import RepositoryLoader
from app.project_knowledge.loader.file_filter import FileFilter
from app.project_knowledge.parser.generic_chunker import GenericChunker
from app.project_knowledge.embeddings.gemini_embedding_service import (
    GeminiEmbeddingService,
)
from app.project_knowledge.retriever.simple_retriever import SimpleRetriever
from app.project_knowledge.vectorstore.in_memory_vector_store import (
    InMemoryVectorStore,
)

from app.integrations.ai.gemini_client import GeminiClient
from app.core.config import GEMINI_API_KEY

from app.repository_intelligence.analyzers.python_repository_analyzer import (
    PythonRepositoryAnalyzer,
)
from app.repository_intelligence.extractors.ast_extractor import ASTExtractor
from app.repository_intelligence.extractors.symbol_extractor import (
    SymbolExtractor,
)
from app.repository_intelligence.extractors.import_extractor import (
    ImportExtractor,
)
from app.repository_intelligence.graph.relationship_graph import (
    RelationshipGraph,
)


class RepositoryContextTool(BaseTool):

    def __init__(self) -> None:

        self._repository_root = Path.cwd()

        self._vector_store = InMemoryVectorStore()

        client = GeminiClient(
            api_key=GEMINI_API_KEY,
        )

        self._embedding_service = GeminiEmbeddingService(
            client=client,
        )

        self._retriever = SimpleRetriever(
            embedding_service=self._embedding_service,
            vector_store=self._vector_store,
        )

        self._index_repository()

    @property
    def id(self) -> str:
        return "repository_context"

    @property
    def name(self) -> str:
        return "Repository Context"

    @property
    def description(self) -> str:
        return (
            "Retrieves relevant repository code and expands "
            "the result using structural relationships."
        )

    def _index_repository(self) -> None:

        loader = RepositoryLoader(
            file_filter=FileFilter(),
        )

        chunker = GenericChunker()

        project_files = loader.load(
            self._repository_root,
        )

        for project_file in project_files:

            chunks = chunker.chunk(
                project_file,
            )

            if not chunks:
                continue

            embedded_chunks = (
                self._embedding_service.embed_chunks(
                    chunks,
                )
            )

            if embedded_chunks:
                self._vector_store.store(
                    embedded_chunks,
                )

    def execute(
        self,
        request: ToolRequest,
    ) -> ToolResponse:

        try:

            chunks = self._retriever.retrieve(
                query=request.input,
                top_k=5,
            )

            analysis = self._analyze_repository()

            context = self._build_context(
                chunks,
                analysis,
            )

            return ToolResponse(
                result=[
                    {
                        "role": "user",
                        "content": context,
                    }
                ]
            )

        except Exception as e:

            return ToolResponse(
                error=str(e),
            )

    def _analyze_repository(self):

        loader = RepositoryLoader(
            file_filter=FileFilter(),
        )

        project_files = loader.load(
            self._repository_root,
        )

        analyzer = PythonRepositoryAnalyzer(
            ast_extractor=ASTExtractor(),
            symbol_extractor=SymbolExtractor(),
            import_extractor=ImportExtractor(),
            relationship_graph=RelationshipGraph(),
        )

        return analyzer.analyze(
            project_files=project_files,
            repository_root=self._repository_root,
        )

    def _build_context(
        self,
        chunks,
        analysis,
    ) -> str:

        lines = [
            "Repository Context:",
            "",
            "Relevant Code:",
        ]

        relevant_paths = set()

        for chunk in chunks:

            relevant_paths.add(
                chunk.path
            )

            lines.append(
                f"\n--- {chunk.path} ---\n"
                f"{chunk.content}"
            )

        lines.append(
            "\n\nRepository Relationships:"
        )

        for symbol in analysis.symbols.values():

            if symbol.file_path not in relevant_paths:
                continue

            relationships = (
                analysis.relationships
            )

            for relationship in relationships:

                if (
                    relationship.source_symbol
                    == symbol.id
                ):

                    target = analysis.symbols.get(
                        relationship.target_symbol
                    )

                    if target:

                        lines.append(
                            f"- {symbol.name} "
                            f"{relationship.relationship_type.value} "
                            f"{target.name}"
                        )

        return "\n".join(lines)