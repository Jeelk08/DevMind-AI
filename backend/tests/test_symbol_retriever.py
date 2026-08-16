from pathlib import Path

from app.project_knowledge.retriever.symbol_retriever import SymbolRetriever
from app.repository_intelligence.models import (
    Language,
    RepositoryAnalysis,
    RepositoryMetadata,
    Symbol,
    SymbolType,
)


def create_analysis() -> RepositoryAnalysis:
    symbol = Symbol(
        id="symbol_1",
        name="ToolRegistry",
        type=SymbolType.CLASS,
        file_path=Path("app/tools/tool_registry.py"),
        line_number=1,
        column_number=0,
    )

    return RepositoryAnalysis(
        metadata=RepositoryMetadata(
            root_path=Path("."),
            language=Language.PYTHON,
        ),
        symbols={
            symbol.id: symbol,
        },
    )


def test_symbol_retriever_finds_exact_symbol():
    retriever = SymbolRetriever(create_analysis())

    results = retriever.retrieve("ToolRegistry")

    assert len(results) == 1
    assert results[0].name == "ToolRegistry"
    assert results[0].file_path == Path("app/tools/tool_registry.py")


def test_symbol_retriever_returns_empty_for_unknown_symbol():
    retriever = SymbolRetriever(create_analysis())

    results = retriever.retrieve("UnknownSymbol")

    assert results == []

def test_symbol_retriever_finds_symbol_inside_query():
    retriever = SymbolRetriever(create_analysis())

    results = retriever.retrieve("Where is ToolRegistry implemented?")

    assert len(results) == 1
    assert results[0].name == "ToolRegistry"


def test_symbol_retriever_finds_symbol_in_natural_language_query():
    retriever = SymbolRetriever(create_analysis())

    results = retriever.retrieve("Find the ToolRegistry class")

    assert len(results) == 1
    assert results[0].name == "ToolRegistry"