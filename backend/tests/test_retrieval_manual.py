from app.project_knowledge.retriever.intelligent_retriever import IntelligentRetriever
from app.project_knowledge.retriever.simple_retriever import SimpleRetriever
from app.project_knowledge.retriever.symbol_retriever import SymbolRetriever
from app.project_knowledge.retriever.path_retriever import PathRetriever


def build_retriever():
    # Use the same construction/wiring that RepositoryContextTool uses.
    # If your project already has a factory/helper for these, use that instead.
    raise NotImplementedError("Wire this using your existing retriever setup")