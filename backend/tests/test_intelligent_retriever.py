from pathlib import Path

from app.project_knowledge.models import Chunk, ProjectFile
from app.project_knowledge.retriever.intelligent_retriever import IntelligentRetriever
from app.project_knowledge.models import SearchResult

class FakeSemanticRetriever:
    def retrieve(self, query: str, top_k: int):
        return [
            SearchResult(
                chunk=Chunk(
                    content="...",
                    path=Path("..."),
                    start_offset=0,
                    end_offset=10,
                ),
                score=0.8,
            ),
        ]


class FakeSymbolRetriever:
    def retrieve(self, query: str):
        class FakeSymbol:
            name = "ToolRegistry"
            file_path = Path("app/tools/tool_registry.py")
            docstring = "Registry for developer tools."

        return [FakeSymbol()]


class FakePathRetriever:
    def retrieve(self, query: str):
        return []


def test_intelligent_retriever_prioritizes_symbol_match():
    retriever = IntelligentRetriever(
        semantic_retriever=FakeSemanticRetriever(),
        symbol_retriever=FakeSymbolRetriever(),
        path_retriever=FakePathRetriever(),
    )

    results = retriever.retrieve(
        query="Where is ToolRegistry implemented?",
        top_k=3,
    )

    paths = [result.path for result in results]

    assert Path("app/tools/tool_registry.py") in paths
    assert paths[0] == Path("app/tools/tool_registry.py")

def test_intelligent_retriever_ranks_semantic_results_by_score():

    class RankedSemanticRetriever:
        def retrieve(self, query: str, top_k: int):
            return [
                SearchResult(
                    chunk=Chunk(
                        content="Low relevance",
                        path=Path("low.py"),
                        start_offset=0,
                        end_offset=10,
                    ),
                    score=0.4,
                ),
                SearchResult(
                    chunk=Chunk(
                        content="High relevance",
                        path=Path("high.py"),
                        start_offset=0,
                        end_offset=10,
                    ),
                    score=0.9,
                ),
            ]

    retriever = IntelligentRetriever(
        semantic_retriever=RankedSemanticRetriever(),
        symbol_retriever=FakePathRetriever(),
        path_retriever=FakePathRetriever(),
    )

    results = retriever.retrieve(
        query="something",
        top_k=2,
    )

    assert results[0].path == Path("high.py")
    assert results[1].path == Path("low.py")