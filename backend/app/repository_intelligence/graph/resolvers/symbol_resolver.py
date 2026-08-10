from pathlib import Path

from app.repository_intelligence.models import (
    RepositoryAnalysis,
    Symbol,
    SymbolType,
)


class SymbolResolver:

    def find_symbol(
        self,
        analysis: RepositoryAnalysis,
        file_path: Path,
        name: str,
        line_number: int,
        symbol_type: SymbolType,
    ) -> Symbol | None:

        candidates = [
            symbol
            for symbol in analysis.symbols.values()
            if (
                symbol.file_path == file_path
                and symbol.name == name
                and symbol.type == symbol_type
            )
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda symbol: abs(
                symbol.line_number - line_number
            ),
        )

    def find_symbol_by_name(
        self,
        analysis: RepositoryAnalysis,
        name: str,
        symbol_type: SymbolType | None = None,
    ) -> Symbol | None:

        candidates = [
            symbol
            for symbol in analysis.symbols.values()
            if (
                symbol.name == name
                and (
                    symbol_type is None
                    or symbol.type == symbol_type
                )
            )
        ]

        if not candidates:
            return None

        return candidates[0]

    def find_module_symbol(
        self,
        analysis: RepositoryAnalysis,
        file_path: Path,
    ) -> Symbol | None:

        candidates = [
            symbol
            for symbol in analysis.symbols.values()
            if (
                symbol.file_path == file_path
                and symbol.type == SymbolType.MODULE
            )
        ]

        if not candidates:
            return None

        return candidates[0]

    def find_enclosing_symbol(
        self,
        symbols: list[Symbol],
        line_number: int,
    ) -> Symbol | None:

        candidates = [
            symbol
            for symbol in symbols
            if (
                symbol.line_number <= line_number
                and symbol.type in {
                    SymbolType.FUNCTION,
                    SymbolType.METHOD,
                    SymbolType.CLASS,
                }
            )
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda symbol: symbol.line_number,
        )