from __future__ import annotations

from app.repository_intelligence.extractors.symbol_visitor import SymbolVisitor
from app.repository_intelligence.models import (ParsedFile, RepositoryAnalysis, Symbol, SymbolType)

class SymbolExtractor:

    def extract(
        self,
        parsed_files: list[ParsedFile],
        analysis: RepositoryAnalysis,
    ) -> None:

 
        for parsed_file in parsed_files:

            module_name = parsed_file.project_file.path.stem

            module_symbol = Symbol(
                id=f"{parsed_file.project_file.path}:module:0",
                name=module_name,
                type=SymbolType.MODULE,
                file_path=parsed_file.project_file.path,
                line_number=0,
                column_number=0,
            )

            analysis.symbols[module_symbol.id] = module_symbol

            visitor = SymbolVisitor(
                parsed_file.project_file,
                analysis,
            )

            visitor.visit(parsed_file.ast_tree)