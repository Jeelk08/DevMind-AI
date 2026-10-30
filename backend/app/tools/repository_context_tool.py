from pathlib import Path
import re

from app.tools.base_tool import BaseTool
from app.tools.tool_request import ToolRequest
from app.tools.tool_response import ToolResponse

from app.project_knowledge.loader.repository_loader import (
    RepositoryLoader,
)
from app.project_knowledge.loader.file_filter import (
    FileFilter,
)
from app.project_knowledge.parser.generic_chunker import (
    GenericChunker,
)
from app.project_knowledge.embeddings.factory import (
    create_embedding_service,
)
from app.project_knowledge.retriever.simple_retriever import (
    SimpleRetriever,
)
from app.project_knowledge.retriever.symbol_retriever import (
    SymbolRetriever,
)
from app.project_knowledge.retriever.path_retriever import (
    PathRetriever,
)
from app.project_knowledge.retriever.intelligent_retriever import (
    IntelligentRetriever,
)

from app.project_knowledge.vectorstore.in_memory_vector_store import (
    InMemoryVectorStore,
)

from app.repository_intelligence.analyzers.python_repository_analyzer import (
    PythonRepositoryAnalyzer,
)
from app.repository_intelligence.extractors.ast_extractor import (
    ASTExtractor,
)
from app.repository_intelligence.extractors.symbol_extractor import (
    SymbolExtractor,
)
from app.repository_intelligence.extractors.import_extractor import (
    ImportExtractor,
)
from app.repository_intelligence.graph.relationship_graph import (
    RelationshipGraph,
)
from app.project_knowledge.indexer.incremental_index_manager import (
    IncrementalIndexManager,
)
from app.repository_intelligence.extractors.universal_file_extractor import (
    UniversalFileExtractor,
)

from app.repository_intelligence.dependency_index import RepositoryDependencyIndex


class RepositoryContextTool(BaseTool):

    def __init__(
        self,
        repository_root: Path | None = None,
        auto_index: bool = True,
    ) -> None:

        self._repository_root = (
            repository_root
            if repository_root is not None
            else Path.cwd()
        )

        self._vector_store = InMemoryVectorStore()

        # Embeddings are selected independently from the chat model.
        # Default: local/remote Hugging Face TEI (BGE-M3).
        self._embedding_service = create_embedding_service()

        self._project_files = []
        self._analysis = None
        self._file_extractor = UniversalFileExtractor()
        self._retriever = None
        self._is_indexed = False

        # Normal chat/context initialization keeps its existing behavior.
        # Explicit update operations can defer indexing and call refresh_index()
        # exactly once after obtaining the tool.
        if auto_index:
            self.refresh_index()

    @property
    def is_indexed(self) -> bool:
        return self._is_indexed

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

        project_files = loader.load(
            self._repository_root,
        )

        self._project_files = project_files
        self._dependency_index = RepositoryDependencyIndex(
            files=self._project_files,
            extractor=self._file_extractor,
        )
        self._analysis = self._analyze_repository(
            project_files
        )

        index_manager = IncrementalIndexManager(
            repository_root=self._repository_root,
            chunker=GenericChunker(),
            embedding_service=self._embedding_service,
            vector_store=self._vector_store,
        )

        stats = index_manager.update(
            project_files
        )

        print(
            "\n========== REPOSITORY INDEX =========="
        )
        print(
            f"New files indexed : {stats['added']}"
        )
        print(
            f"Modified files    : {stats['modified']}"
        )
        print(
            f"Reused files      : {stats['reused']}"
        )
        print(
            f"Deleted files     : {stats['deleted']}"
        )
        print(
            f"Failed files      : {stats['failed']}"
        )
        print(
            "======================================\n"
        )



    def refresh_index(self) -> dict:
        """
        Re-scan the repository and incrementally update
        the persistent knowledge index.

        The vector store and repository retrievers are rebuilt
        from the resulting current project state.
        """

        self._index_repository()

        self._retriever = IntelligentRetriever(
            semantic_retriever=SimpleRetriever(
                embedding_service=(
                    self._embedding_service
                ),
                vector_store=self._vector_store,
            ),
            symbol_retriever=SymbolRetriever(
                analysis=self._analysis,
            ),
            path_retriever=PathRetriever(
                files=self._project_files,
            ),
        )
        self._is_indexed = True

        return self._get_index_stats()



    def _get_index_stats(self) -> dict:
        """
        Read the current persistent index statistics.
        """

        cache_path = (
            self._repository_root.parent
            / ".devmind"
            / "repository_index.json"
        )

        if not cache_path.exists():
            return {
                "indexed_files": 0,
                "chunks": 0,
            }

        try:
            import json

            with cache_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                cache = json.load(file)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {
                "indexed_files": 0,
                "chunks": 0,
            }

        files = cache.get(
            "files",
            {}
        )

        if not isinstance(files, dict):
            return {
                "indexed_files": 0,
                "chunks": 0,
            }

        total_chunks = 0
        indexed_files = 0

        for file_data in files.values():

            if not isinstance(
                file_data,
                dict,
            ):
                continue

            chunks = file_data.get(
                "chunks",
                []
            )

            if not isinstance(
                chunks,
                list,
            ):
                continue

            indexed_files += 1
            total_chunks += len(chunks)

        return {
            "indexed_files": indexed_files,
            "chunks": total_chunks,
        }


    def retrieve_chunks(
        self,
        query: str,
        top_k: int = 5,
    ):
        if not self._is_indexed or self._retriever is None:
            raise RuntimeError(
                "Repository knowledge has not been indexed yet."
            )

        return self._retriever.retrieve_with_scores(
            query=query,
            top_k=top_k,
        )

    def execute(
        self,
        request: ToolRequest,
    ) -> ToolResponse:
        try:
            if not self._is_indexed or self._retriever is None:
                return ToolResponse(
                    error="Repository knowledge has not been indexed yet."
                )

            # Use a wider semantic window for questions that usually require
            # tracing a workflow or understanding multiple components.
            query = request.input
            broad_query = any(
                term in query.lower()
                for term in (
                    "workflow", "flow", "architecture", "end to end",
                    "end-to-end", "across", "interact", "communicate",
                    "pipeline", "trace", "complete", "whole project",
                )
            )
            top_k = 10 if broad_query else 7

            results = self._retriever.retrieve_with_scores(
                query=query,
                top_k=top_k,
            )
            chunks = [chunk for chunk, _ in results]

            exact_files = self._match_explicit_files(query)
            seed_paths = {str(chunk.path) for chunk in chunks}
            seed_paths.update(str(path) for path in exact_files)

            related_files = self._expand_related_files(
                seed_paths,
                max_related=12 if broad_query else 8,
            )

            context = self._build_context(
                chunks,
                self._analysis,
                query=query,
                exact_files=exact_files,
                related_files=related_files,
            )

            sources_by_path = {}
            for chunk, relevance in results:
                path = Path(chunk.path)
                key = self._normalize_repo_path(path)
                item = sources_by_path.setdefault(
                    key,
                    {
                        "file_name": path.name,
                        "file_path": str(path),
                        "relevance": relevance,
                        "content": chunk.content,
                        "source_type": "retrieved_chunk",
                    },
                )
                if relevance > item["relevance"]:
                    item["relevance"] = relevance

            # Include exact and dependency-expanded files in source metadata,
            # even when semantic retrieval did not return their chunks.
            for project_file in [*exact_files, *related_files]:
                key = self._normalize_repo_path(project_file.path)
                if key not in sources_by_path:
                    sources_by_path[key] = {
                        "file_name": project_file.path.name,
                        "file_path": str(project_file.path),
                        "relevance": None,
                        "content": project_file.content[:5000],
                        "source_type": (
                            "exact_file" if project_file in exact_files
                            else "dependency_context"
                        ),
                    }

            sources = []
            for index, source in enumerate(
                sources_by_path.values(),
                start=1,
            ):
                sources.append({"id": index, **source})

            return ToolResponse(
                result=[
                    {
                        "role": "user",
                        "content": (
                            f"User Question:\\n{query}\\n\\n"
                            f"{context}\\n\\n"
                            "Answer using the supplied repository evidence. "
                            "For multi-file questions, explain the sequence "
                            "and distinguish direct evidence from inference. "
                            "If the repository context is insufficient, say so."
                        ),
                    }
                ],
                metadata={"sources": sources},
            )

        except Exception as e:
            return ToolResponse(error=str(e))

    @staticmethod
    def _normalize_repo_path(path: Path | str) -> str:
        return str(path).replace("\\", "/").casefold()

    def _match_explicit_files(self, query: str):
        """Find indexed files whose filename or repository path is named."""
        matches = []
        query_normalized = query.replace("\\", "/").casefold()

        for project_file in self._project_files:
            path_text = str(project_file.path).replace("\\", "/")
            filename = project_file.path.name

            filename_pattern = (
                r"(?<![\w.-])"
                + re.escape(filename)
                + r"(?![\w.-])"
            )
            full_path = path_text.casefold()

            if (
                re.search(filename_pattern, query, re.IGNORECASE)
                or full_path in query_normalized
            ):
                matches.append(project_file)

        return matches

    def _expand_related_files(
        self,
        seed_paths: set[str],
        max_related: int = 8,
    ):
        """Expand retrieved files by one dependency hop in both directions."""
        selected = {}
        for seed in seed_paths:
            dependencies = self._dependency_index.get_dependencies(seed)
            dependents = self._dependency_index.get_dependents(seed)

            for edge in [*dependencies, *dependents]:
                candidate_path = (
                    edge.target_path
                    if self._normalize_repo_path(edge.source_path)
                    == self._normalize_repo_path(seed)
                    else edge.source_path
                )
                key = self._normalize_repo_path(candidate_path)
                selected[key] = candidate_path

        files_by_path = {
            self._normalize_repo_path(item.path): item
            for item in self._project_files
        }

        related = []
        for key, path in selected.items():
            if key in files_by_path:
                related.append(files_by_path[key])
            if len(related) >= max_related:
                break

        return related

    def _analyze_repository(
        self,
        project_files,
    ):
        python_files = [
            project_file
            for project_file in project_files
            if project_file.path.suffix.lower() == ".py"
        ]

        analyzer = PythonRepositoryAnalyzer(
            ast_extractor=ASTExtractor(),
            symbol_extractor=SymbolExtractor(),
            import_extractor=ImportExtractor(),
            relationship_graph=RelationshipGraph(),
        )

        return analyzer.analyze(
            project_files=python_files,
            repository_root=self._repository_root,
        )

    def _build_context(
        self,
        chunks,
        analysis,
        query: str = "",
        exact_files=None,
        related_files=None,
    ) -> str:
        exact_files = exact_files or []
        related_files = related_files or []

        lines = [
            "Repository Context:",
            "",
            "Relevant Retrieved Code:",
        ]

        relevant_paths = set()
        chunk_paths = set()

        for chunk in chunks:
            path = Path(chunk.path)
            key = self._normalize_repo_path(path)
            relevant_paths.add(key)
            chunk_paths.add(key)
            lines.append(f"\\n--- {path} (retrieved chunk) ---\\n{chunk.content}")

        files_by_path = {
            self._normalize_repo_path(item.path): item
            for item in self._project_files
        }

        exact_keys = {
            self._normalize_repo_path(item.path)
            for item in exact_files
        }
        related_keys = {
            self._normalize_repo_path(item.path)
            for item in related_files
        }

        # Exact filename questions should receive the complete file where
        # practical, not only whichever semantic chunks happened to rank.
        for key in exact_keys:
            project_file = files_by_path.get(key)
            if project_file is None:
                continue
            relevant_paths.add(key)
            if key not in chunk_paths:
                content = project_file.content[:12000]
                lines.append(
                    f"\\n--- {project_file.path} (exact file match) ---\\n"
                    f"{content}"
                )

        # Add a bounded amount of neighbouring file content to support
        # cross-file workflow and architecture explanations.
        for key in related_keys:
            project_file = files_by_path.get(key)
            if project_file is None:
                continue
            relevant_paths.add(key)
            if key not in chunk_paths and key not in exact_keys:
                lines.append(
                    f"\\n--- {project_file.path} (related dependency file) ---\\n"
                    f"{project_file.content[:5000]}"
                )

        lines.append(
            "\\n\\nFile Insights (imports, references and structure):"
        )

        for key in sorted(relevant_paths):
            project_file = files_by_path.get(key)
            if project_file is None:
                continue

            insights = self._file_extractor.extract(
                project_file.path,
                project_file.content,
            )
            lines.append(
                f"\\n[{insights.file_type.upper()}] {project_file.path}"
            )

            if insights.references:
                lines.append(
                    "References / imports: "
                    + ", ".join(insights.references)
                )

            if insights.structures:
                lines.append(
                    "Structure: "
                    + "; ".join(insights.structures[:80])
                )

        lines.append("\\n\\nFile Dependencies:")
        for key in sorted(relevant_paths):
            project_file = files_by_path.get(key)
            if project_file is None:
                continue

            dependencies = self._dependency_index.get_dependencies(
                project_file.path
            )
            dependents = self._dependency_index.get_dependents(
                project_file.path
            )

            if dependencies:
                lines.append(f"\\nFiles referenced by {project_file.path}:")
                for edge in dependencies:
                    lines.append(
                        f"- {edge.target_path} (reference: {edge.reference})"
                    )

            if dependents:
                lines.append(f"\\nFiles that reference {project_file.path}:")
                for edge in dependents:
                    lines.append(
                        f"- {edge.source_path} (reference: {edge.reference})"
                    )

        lines.append("\\n\\nRepository Relationships:")
        if analysis is not None:
            for symbol in analysis.symbols.values():
                symbol_path = self._normalize_repo_path(symbol.file_path)
                if symbol_path not in relevant_paths:
                    continue

                for relationship in analysis.relationships:
                    if relationship.source_symbol != symbol.id:
                        continue

                    target = analysis.symbols.get(
                        relationship.target_symbol
                    )
                    if target:
                        lines.append(
                            f"- {symbol.name} "
                            f"{relationship.relationship_type.value} "
                            f"{target.name}"
                        )

        lines.append(
            "\\n\\nContext guidance: dependency edges show file-level "
            "references, not necessarily runtime call order. Explain a "
            "workflow only to the extent supported by the supplied code."
        )
        return "\\n".join(lines)
