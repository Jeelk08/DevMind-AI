from app.repository_intelligence.models import RepositoryAnalysis, Symbol


class SymbolRetriever:
    def __init__(self, analysis: RepositoryAnalysis):
        self.analysis = analysis

    def retrieve(self, query: str) -> list[Symbol]:
        query = query.strip().lower()

        if not query:
            return []

        results = []

        for symbol in self.analysis.symbols.values():
            symbol_name = symbol.name.lower()

            if symbol_name == query:
                results.append(symbol)
                continue

            if symbol_name in query:
                results.append(symbol)

        return results