import ast

from app.repository_intelligence.models import (
    ParsedFile,
    Relationship,
    RelationshipType,
    RepositoryAnalysis,
    Symbol,
    SymbolType,
)

from app.repository_intelligence.graph.resolvers.symbol_resolver import (
    SymbolResolver,
)


class CallBuilder:

    def __init__(
        self,
        symbol_resolver: SymbolResolver,
    ) -> None:

        self.symbol_resolver = symbol_resolver

    def build(
        self,
        analysis: RepositoryAnalysis,
        parsed_files: list[ParsedFile],
    ) -> None:

        for parsed_file in parsed_files:

            file_symbols = [
                symbol
                for symbol in analysis.symbols.values()
                if symbol.file_path
                == parsed_file.project_file.path
            ]

            for node in ast.walk(
                parsed_file.ast_tree
            ):

                if not isinstance(node, ast.Call):
                    continue

                called_name = self._get_called_name(node)

                if called_name is None:
                    continue

                source_symbol = (
                    self.symbol_resolver.find_enclosing_symbol(
                        file_symbols,
                        node.lineno,
                    )
                )

                if source_symbol is None:
                    continue

                target_symbol = (
                    self._resolve_call_target(
                        analysis,
                        called_name,
                        parsed_file.project_file.path,
                    )
                )

                if target_symbol is None:
                    continue

                if source_symbol.id == target_symbol.id:
                    continue

                relationship = Relationship(
                    source_symbol=source_symbol.id,
                    target_symbol=target_symbol.id,
                    relationship_type=RelationshipType.CALLS,
                )

                if relationship not in analysis.relationships:
                    analysis.relationships.append(
                        relationship
                    )

    def _resolve_call_target(
        self,
        analysis: RepositoryAnalysis,
        called_name: str,
        source_file,
    ) -> Symbol | None:

        local_candidates = [
            symbol
            for symbol in analysis.symbols.values()
            if (
                symbol.file_path == source_file
                and symbol.name == called_name
                and symbol.type in {
                    SymbolType.FUNCTION,
                    SymbolType.METHOD,
                    SymbolType.CLASS,
                }
            )
        ]

        if local_candidates:
            return local_candidates[0]

        repository_candidates = [
            symbol
            for symbol in analysis.symbols.values()
            if (
                symbol.name == called_name
                and symbol.type in {
                    SymbolType.FUNCTION,
                    SymbolType.METHOD,
                    SymbolType.CLASS,
                }
            )
        ]

        if repository_candidates:
            return repository_candidates[0]

        return None

    def _get_called_name(
        self,
        node: ast.Call,
    ) -> str | None:

        if isinstance(node.func, ast.Name):
            return node.func.id

        if isinstance(node.func, ast.Attribute):
            return node.func.attr

        return None