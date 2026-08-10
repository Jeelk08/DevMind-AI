from app.repository_intelligence.models import (
    ParsedFile,
    RepositoryAnalysis,
)

from app.repository_intelligence.graph.builders.definition_builder import (
    DefinitionBuilder,
)

from app.repository_intelligence.graph.builders.inheritance_builder import (
    InheritanceBuilder,
)

from app.repository_intelligence.graph.builders.call_builder import (
    CallBuilder,
)

from app.repository_intelligence.graph.builders.import_builder import (
    ImportBuilder,
)

from app.repository_intelligence.graph.resolvers.symbol_resolver import (
    SymbolResolver,
)

from app.repository_intelligence.graph.resolvers.import_resolver import (
    ImportResolver,
)

from app.repository_intelligence.graph.graph_query import (
    GraphQuery,
)


class RelationshipGraph:

    def __init__(self) -> None:

        symbol_resolver = SymbolResolver()

        import_resolver = ImportResolver(
            symbol_resolver,
        )

        self.definition_builder = DefinitionBuilder()

        self.inheritance_builder = InheritanceBuilder(
            symbol_resolver,
        )

        self.call_builder = CallBuilder(
            symbol_resolver,
        )

        self.import_builder = ImportBuilder(
            symbol_resolver,
            import_resolver,
        )

        self.query = GraphQuery()

    def build(
        self,
        analysis: RepositoryAnalysis,
        parsed_files: list[ParsedFile],
    ) -> None:

        self.definition_builder.build(
            analysis,
        )

        self.inheritance_builder.build(
            analysis,
            parsed_files,
        )

        self.import_builder.build(
            analysis,
        )

        self.call_builder.build(
            analysis,
            parsed_files,
        )

    def get_relationships(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
        relationship_type=None,
    ):

        return self.query.get_relationships(
            analysis,
            symbol_id,
            relationship_type,
        )

    def get_callees(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ):

        return self.query.get_callees(
            analysis,
            symbol_id,
        )

    def get_callers(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ):

        return self.query.get_callers(
            analysis,
            symbol_id,
        )

    def get_dependencies(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ):

        return self.query.get_dependencies(
            analysis,
            symbol_id,
        )

    def get_dependents(
        self,
        analysis: RepositoryAnalysis,
        symbol_id: str,
    ):

        return self.query.get_dependents(
            analysis,
            symbol_id,
        )