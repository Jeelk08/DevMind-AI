from app.project_knowledge.models import Chunk
from app.project_knowledge.retriever.path_retriever import PathRetriever
from app.project_knowledge.retriever.simple_retriever import SimpleRetriever
from app.project_knowledge.retriever.symbol_retriever import SymbolRetriever
from dataclasses import dataclass



@dataclass
class RetrievalCandidate:
    chunk: Chunk
    semantic_score: float = 0.0
    symbol_match: bool = False
    path_match: bool = False

    @property
    def final_score(self) -> float:
        score = self.semantic_score

        if self.symbol_match:
            score += 1.0

        if self.path_match:
            score += 0.3

        return score
    @property
    def chunk_key(self) -> tuple[str, int, int]:
        return (
            str(self.chunk.path),
            self.chunk.start_offset,
            self.chunk.end_offset,
    )
class IntelligentRetriever:

    def __init__(
        self,
        semantic_retriever: SimpleRetriever,
        symbol_retriever: SymbolRetriever,
        path_retriever: PathRetriever,
    ):
        self.semantic_retriever = semantic_retriever
        self.symbol_retriever = symbol_retriever
        self.path_retriever = path_retriever

    def _chunk_key(self, chunk: Chunk) -> tuple[str, int, int]:
        return (
            str(chunk.path),
            chunk.start_offset,
            chunk.end_offset,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Chunk]:

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        candidates: dict[tuple[str, int, int], RetrievalCandidate] = {}
        symbol_paths: set[str] = set()
        path_matches: set[str] = set()

        # 1. Symbol matches
        for symbol in self.symbol_retriever.retrieve(query):
            path = str(symbol.file_path)
            chunk = Chunk(
                content=symbol.docstring or symbol.name,
                path=symbol.file_path,
                start_offset=0,
                end_offset=0,
            )

            key = self._chunk_key(chunk)
            if key in candidates:
                candidates[key].symbol_match = True
                continue
            candidates[key] = RetrievalCandidate(
                chunk=chunk,
                symbol_match=True,
            )

            symbol_paths.add(path)


        # 2. Path matches
        for project_file in self.path_retriever.retrieve(query):

            path = str(project_file.path)

            chunk = Chunk(
                content=project_file.content,
                path=project_file.path,
                start_offset=0,
                end_offset=len(project_file.content),
            )

            key = self._chunk_key(chunk)

            if key in candidates:
                candidates[key].path_match = True
                continue

            candidates[key] = RetrievalCandidate(
                chunk=chunk,
                path_match=True,
            )

            path_matches.add(path)
         

        # 3. Semantic retrieval
        semantic_top_k = max(top_k * 3, 10)

        semantic_results = self.semantic_retriever.retrieve(
            query=query,
            top_k=semantic_top_k,
        )

        for result in semantic_results:

            chunk = result.chunk if hasattr(result, "chunk") else result

            semantic_score = (
                result.score
                if hasattr(result, "score")
                else 0.0
            )

            path = str(chunk.path)
            key = self._chunk_key(chunk)
            if key in candidates:

                if semantic_score > candidates[key].semantic_score:
                    candidates[key].chunk = chunk
                    candidates[key].semantic_score = semantic_score

                continue

            candidates[key] = RetrievalCandidate(
                chunk=chunk,
                semantic_score=semantic_score,
                symbol_match=path in symbol_paths,
                path_match=path in path_matches,
            )

        # 4. Final ranking
        ranked_candidates = sorted(
            candidates.values(),
            key=lambda candidate: candidate.final_score,
            reverse=True,
        )

        return [
            candidate.chunk
            for candidate in ranked_candidates[:top_k]
        ]
