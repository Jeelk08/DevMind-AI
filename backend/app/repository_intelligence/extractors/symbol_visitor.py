from __future__ import annotations

import ast

from app.project_knowledge.models import ProjectFile
from app.repository_intelligence.models import (
    RepositoryAnalysis,
    Symbol,
    SymbolType,
)


class SymbolVisitor(ast.NodeVisitor):

    def __init__(
        self,
        project_file: ProjectFile,
        analysis: RepositoryAnalysis,
    ) -> None:

        self.project_file = project_file
        self.analysis = analysis

        self.current_symbol_id: str | None = None

    def _build_symbol_id(
        self,
        name: str,
        node: ast.AST,
    ) -> str:
        return f"{self.project_file.path}:{name}:{node.lineno}"

    def _create_symbol(
        self,
        name: str,
        symbol_type: SymbolType,
        node: ast.AST,
    ) -> Symbol:

        symbol = Symbol(
            id=self._build_symbol_id(name, node),
            name=name,
            type=symbol_type,
            file_path=self.project_file.path,
            line_number=getattr(node, "lineno", 0),
            column_number=getattr(node, "col_offset", 0),
            parent_symbol=self.current_symbol_id,
        )

        self.analysis.symbols[symbol.id] = symbol

        return symbol

    def visit_ClassDef(
        self,
        node: ast.ClassDef,
    ) -> None:

        previous_class = self.current_symbol_id

        class_symbol = self._create_symbol(
            name=node.name,
            symbol_type=SymbolType.CLASS,
            node=node,
        )

        self.current_symbol_id = class_symbol.id

        self.generic_visit(node)

        self.current_symbol_id = previous_class

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ) -> None:

        symbol_type = (
            SymbolType.METHOD
            if self.current_symbol_id
            else SymbolType.FUNCTION
        )

        self._create_symbol(
            name=node.name,
            symbol_type=symbol_type,
            node=node,
        )

        self.generic_visit(node)