from app.repository_intelligence.models import (
    Relationship,
    RelationshipType,
    RepositoryAnalysis,
    Symbol,
)


class GraphQuery:

    def get_relationships(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
        relationship_type: RelationshipType | None = None,
    ) -> list[Relationship]:

        relationships = [
            relationship
            for relationship in analysis.relationships
            if (
                relationship.source_symbol == symbol_id
                or relationship.target_symbol == symbol_id
            )
        ]

        if relationship_type is not None:

            relationships = [
                relationship
                for relationship in relationships
                if relationship.relationship_type
                == relationship_type
            ]

        return relationships

    def get_callees(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ) -> list[Symbol]:

        return self._resolve_symbols(
            analysis,
            [
                relationship.target_symbol
                for relationship in analysis.relationships
                if (
                    relationship.source_symbol == symbol_id
                    and relationship.relationship_type
                    == RelationshipType.CALLS
                )
            ],
        )

    def get_callers(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ) -> list[Symbol]:

        return self._resolve_symbols(
            analysis,
            [
                relationship.source_symbol
                for relationship in analysis.relationships
                if (
                    relationship.target_symbol == symbol_id
                    and relationship.relationship_type
                    == RelationshipType.CALLS
                )
            ],
        )

    def get_dependencies(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ) -> list[Symbol]:

        return self._resolve_symbols(
            analysis,
            [
                relationship.target_symbol
                for relationship in analysis.relationships
                if relationship.source_symbol == symbol_id
            ],
        )

    def get_dependents(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ) -> list[Symbol]:

        return self._resolve_symbols(
            analysis,
            [
                relationship.source_symbol
                for relationship in analysis.relationships
                if relationship.target_symbol == symbol_id
            ],
        )

    def _resolve_symbols(
        self,
        analysis: RepositoryAnalysis,
        symbol_ids: list[str],
    ) -> list[Symbol]:

        return [
            analysis.symbols[symbol_id]
            for symbol_id in symbol_ids
            if symbol_id in analysis.symbols
        ]