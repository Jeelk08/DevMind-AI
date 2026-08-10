from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import ast
from app.project_knowledge.models import ProjectFile



class SymbolType(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    PACKAGE = "package"


class RelationshipType(Enum):
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    DEFINES  = "defines"
    REFERENCES = "references"
    OVERRIDES = "overrides"


class Language(Enum):
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


@dataclass
class RepositoryMetadata:
    root_path: Path
    language: Language
    files_analyzed: int = 0
    analysis_duration: float = 0.0

@dataclass
class Symbol:
    id: str
    name: str
    type: SymbolType

    file_path: Path
    line_number: int
    column_number: int
    docstring: str | None = None
    parent_symbol: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ImportStatement:
    imported_module: str
    source_symbol: str | None = None
    imported_name: str | None = None
    source_file: Path | None = None
    

@dataclass
class SymbolDependency:
    source_symbol: str
    target_symbol: str

@dataclass
class Relationship:
    source_symbol: str
    target_symbol: str
    relationship_type: RelationshipType

@dataclass
class RepositoryAnalysis:
    metadata: RepositoryMetadata

    symbols: dict[str, Symbol] = field(default_factory=dict)

    imports: list[ImportStatement] = field(default_factory=list)

    dependencies: list[SymbolDependency] = field(default_factory=list)

    relationships: list[Relationship] = field(default_factory=list)

@dataclass
class ParsedFile:
    project_file: ProjectFile
    ast_tree: ast.Module