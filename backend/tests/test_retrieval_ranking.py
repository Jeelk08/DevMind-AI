import pytest   
from pathlib import Path

from app.project_knowledge.models import Chunk
from app.project_knowledge.retriever.intelligent_retriever import (
    RetrievalCandidate,
)


def make_candidate(
    semantic_score: float = 0.0,
    symbol_match: bool = False,
    path_match: bool = False,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk=Chunk(
            content="test",
            path=Path("test.py"),
            start_offset=0,
            end_offset=10,
        ),
        semantic_score=semantic_score,
        symbol_match=symbol_match,
        path_match=path_match,
    )


def test_semantic_score_alone():
    candidate = make_candidate(
        semantic_score=0.75,
    )

    assert candidate.final_score == 0.75


def test_symbol_match_gets_bonus():
    candidate = make_candidate(
        semantic_score=0.60,
        symbol_match=True,
    )

    assert candidate.final_score == 1.60


def test_path_match_gets_bonus():
    candidate = make_candidate(
        semantic_score=0.70,
        path_match=True,
    )

    assert candidate.final_score == 1.00


def test_symbol_and_path_matches_combine():
    candidate = make_candidate(
        semantic_score=0.60,
        symbol_match=True,
        path_match=True,
    )

    assert candidate.final_score == pytest.approx(1.90)


def test_symbol_match_beats_higher_semantic_score():
    symbol_candidate = make_candidate(
        semantic_score=0.60,
        symbol_match=True,
    )

    semantic_candidate = make_candidate(
        semantic_score=0.95,
    )

    assert symbol_candidate.final_score > semantic_candidate.final_score