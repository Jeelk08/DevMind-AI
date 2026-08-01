from __future__ import annotations

from app.repository_intelligence.models import(
    Relationship,
    RelationshipType,
    RepositoryAnalysis
)

class RelationshipGraph:

    def build(
            self,
            analysis: RepositoryAnalysis,
    ) -> None:

        for symbol in analysis.symbols.values():

            if symbol.parent_symbol is None:
                continue

            relationship = Relationship(
                source_symbol=symbol.parent_symbol,
                target_symbol=symbol.id,
                relationship_type=RelationshipType.DEFINES,
            )

            analysis.relationships.append(relationship)