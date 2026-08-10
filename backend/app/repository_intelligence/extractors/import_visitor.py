from __future__ import annotations

import ast

from app.project_knowledge.models import ProjectFile
from app.repository_intelligence.models import (
    ImportStatement,
    RepositoryAnalysis,
)

class ImportVisitor(ast.NodeVisitor):

    def __init__(
        self,
        project_file: ProjectFile,
        analysis: RepositoryAnalysis,
    ) -> None:

        self.project_file = project_file
        self.analysis = analysis

    def visit_Import(
            self,
            node: ast.Import,
    ) -> None:
        
        for alias in node.names:
            import_statement = ImportStatement(
                imported_module=alias.name,
                source_symbol= None,
                imported_name=None,
                source_file=self.project_file.path,
            )

            self.analysis.imports.append(import_statement)
        self.generic_visit(node)

    def visit_ImportFrom(
            self,
            node: ast.ImportFrom,
    ) -> None:

        for alias in node.names:
            import_statement = ImportStatement(
                source_symbol=None,
                imported_module=node.module or "",
                imported_name=alias.name,
                source_file=self.project_file.path,
            )
            self.analysis.imports.append(import_statement)
        self.generic_visit(node)
        