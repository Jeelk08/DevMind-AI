from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectFile:
    path: Path
    content: str

@dataclass
class Chunk:
    content: str
    path: Path
    start_offset: int
    end_offset: int



# An EmbeddedChunk keeps both the original chunk and its vector.
@dataclass
class EmbeddedChunk:

    #The original chunk that was Embedded
    chunk: Chunk

    #Numerical representaion of chunk (Embedded Chunk)
    vector: list[float]




@dataclass
class IndexResult:
    files_indexed: int
    chunks_created: int
    skipped_files: int



@dataclass
class SearchResult:
    """
    Represents a semantic search result.
    """
    #The retrieved chunk.
    chunk: Chunk

    #Similarity Score
    score: float

