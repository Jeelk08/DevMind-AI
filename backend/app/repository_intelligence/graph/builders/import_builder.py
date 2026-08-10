from app.repository_intelligence.models import (
    Relationship,
    RelationshipType,
    RepositoryAnalysis,
)

from app.repository_intelligence.graph.resolvers.symbol_resolver import (
    SymbolResolver,
)

from app.repository_intelligence.graph.resolvers.import_resolver import (
    ImportResolver,
)


class ImportBuilder:

    def __init__(
        self,
        symbol_resolver: SymbolResolver,
        import_resolver: ImportResolver,
    ) -> None:

        self.symbol_resolver = symbol_resolver
        self.import_resolver = import_resolver

    def build(
        self,
        analysis: RepositoryAnalysis,
    ) -> None:

        for import_statement in analysis.imports:

            if import_statement.source_file is None:
                continue

            source_symbol = (
                self.symbol_resolver.find_module_symbol(
                    analysis,
                    import_statement.source_file,
                )
            )

            if source_symbol is None:
                continue

            target_symbol = (
                self.import_resolver.resolve(
                    analysis,
                    import_statement,
                )
            )

            if target_symbol is None:
                continue

            relationship = Relationship(
                source_symbol=source_symbol.id,
                target_symbol=target_symbol.id,
                relationship_type=RelationshipType.IMPORTS,
            )

            if relationship not in analysis.relationships:
                analysis.relationships.append(
                    relationship
                )