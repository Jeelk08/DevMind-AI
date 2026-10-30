from pathlib import Path

from app.project_knowledge.models import ProjectFile
from app.project_knowledge.retriever.path_retriever import PathRetriever


def create_files() -> list[ProjectFile]:
    return [
        ProjectFile(
            path=Path("app/hooks/useDevMind.js"),
            content="import React from 'react';",
        ),
        ProjectFile(
            path=Path("app/hooks/useChat.js"),
            content="export function useChat() {}",
        ),
        ProjectFile(
            path=Path("app/memory/memory_manager.py"),
            content="class MemoryManager: pass",
        ),
    ]


def test_path_retriever_finds_exact_path():
    retriever = PathRetriever(create_files())
    results = retriever.retrieve("app/hooks/useDevMind.js")
    assert len(results) == 1
    assert results[0].path == Path("app/hooks/useDevMind.js")


def test_path_retriever_finds_filename_inside_natural_language_query():
    retriever = PathRetriever(create_files())
    results = retriever.retrieve("What imports does useDevMind.js use?")
    assert len(results) == 1
    assert results[0].path == Path("app/hooks/useDevMind.js")


def test_path_retriever_marks_explicit_filename_as_exact():
    retriever = PathRetriever(create_files())
    results = retriever.retrieve_with_match_type(
        "Explain app/hooks/useDevMind.js"
    )
    assert len(results) == 1
    assert results[0][0].path == Path("app/hooks/useDevMind.js")
    assert results[0][1] is True


def test_path_retriever_returns_empty_for_unknown_file():
    retriever = PathRetriever(create_files())
    assert retriever.retrieve("unknown.py") == []
