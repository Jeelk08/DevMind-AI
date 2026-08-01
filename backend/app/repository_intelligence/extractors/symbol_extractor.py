from __future__ import annotations

from app.repository_intelligence.extractors.symbol_visitor import SymbolVisitor
from app.repository_intelligence.models import ParsedFile, RepositoryAnalysis

class SymbolExtractor:

    def extract(
        self,
        parsed_files: list[ParsedFile],
        analysis: RepositoryAnalysis,
    ) -> None:

        for parsed_file in parsed_files:
            visitor = SymbolVisitor(
                parsed_file.project_file,
                analysis,
            )

            visitor.visit(parsed_file.ast_tree)