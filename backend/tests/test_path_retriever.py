from pathlib import Path

from app.project_knowledge.models import ProjectFile
from app.project_knowledge.retriever.path_retriever import PathRetriever


def create_files() -> list[ProjectFile]:
    return [
        ProjectFile(
            path=Path("app/tools/tool_registry.py"),
            content="class ToolRegistry: pass",
        ),
        ProjectFile(
            path=Path("app/memory/memory_manager.py"),
            content="class MemoryManager: pass",
        ),
    ]

def test_path_retriever_finds_exact_path():
    retriever = PathRetriever(create_files())

    results = retriever.retrieve("app/tools/tool_registry.py")

    assert len(results) == 1
    assert results[0].path == Path("app/tools/tool_registry.py")


def test_path_retriever_finds_filename():
    retriever = PathRetriever(create_files())

    results = retriever.retrieve("tool_registry.py")

    assert len(results) == 1
    assert results[0].path == Path("app/tools/tool_registry.py")


def test_path_retriever_finds_filename_inside_query():
    retriever = PathRetriever(create_files())

    results = retriever.retrieve("Find tool_registry.py")

    assert len(results) == 1
    assert results[0].path == Path("app/tools/tool_registry.py")


def test_path_retriever_returns_empty_for_unknown_file():
    retriever = PathRetriever(create_files())

    results = retriever.retrieve("unknown.py")

    assert results == []