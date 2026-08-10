from pathlib import Path

from app.repository_intelligence.models import (
    RepositoryAnalysis,
    Symbol,
)

from app.repository_intelligence.graph.resolvers.symbol_resolver import (
    SymbolResolver,
)


class ImportResolver:

    def __init__(
        self,
        symbol_resolver: SymbolResolver,
    ) -> None:

        self.symbol_resolver = symbol_resolver

    def resolve(
        self,
        analysis: RepositoryAnalysis,
        import_statement,
    ) -> Symbol | None:

        imported_name = import_statement.imported_name
        imported_module = import_statement.imported_module

        if imported_name:

            module_path = self.module_to_file_path(
                analysis,
                imported_module,
            )

            candidates = [
                symbol
                for symbol in analysis.symbols.values()
                if (
                    symbol.name == imported_name
                    and (
                        module_path is None
                        or symbol.file_path == module_path
                    )
                )
            ]

            if candidates:
                return candidates[0]

            return self.symbol_resolver.find_symbol_by_name(
                analysis,
                imported_name,
            )

        module_path = self.module_to_file_path(
            analysis,
            imported_module,
        )

        if module_path is None:
            return None

        return self.symbol_resolver.find_module_symbol(
            analysis,
            module_path,
        )

    def module_to_file_path(
        self,
        analysis: RepositoryAnalysis,
        module_name: str,
    ) -> Path | None:

        root_path = analysis.metadata.root_path

        module_parts = module_name.split(".")

        module_path = root_path.joinpath(
            *module_parts,
        )

        python_file = module_path.with_suffix(".py")

        if python_file.exists():
            return python_file

        init_file = module_path / "__init__.py"

        if init_file.exists():
            return init_file

        return None