import ast

from app.repository_intelligence.models import (
    ParsedFile,
    Relationship,
    RelationshipType,
    RepositoryAnalysis,
    SymbolType,
)

from app.repository_intelligence.graph.resolvers.symbol_resolver import (
    SymbolResolver,
)


class InheritanceBuilder:

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

            for node in ast.walk(parsed_file.ast_tree):

                if not isinstance(node, ast.ClassDef):
                    continue

                class_symbol = self.symbol_resolver.find_symbol(
                    analysis,
                    parsed_file.project_file.path,
                    node.name,
                    node.lineno,
                    SymbolType.CLASS,
                )

                if class_symbol is None:
                    continue

                for base in node.bases:

                    base_name = self._get_name(base)

                    if base_name is None:
                        continue

                    target_symbol = (
                        self.symbol_resolver.find_symbol_by_name(
                            analysis,
                            base_name,
                            SymbolType.CLASS,
                        )
                    )

                    if target_symbol is None:
                        continue

                    relationship = Relationship(
                        source_symbol=class_symbol.id,
                        target_symbol=target_symbol.id,
                        relationship_type=RelationshipType.INHERITS,
                    )

                    analysis.relationships.append(
                        relationship
                    )

    def _get_name(
        self,
        node: ast.AST,
    ) -> str | None:

        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            return node.attr

        return None