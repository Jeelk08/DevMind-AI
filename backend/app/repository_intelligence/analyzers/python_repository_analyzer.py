from __future__ import annotations
from pathlib import Path
from app.project_knowledge.models import ProjectFile

from app.repository_intelligence.analyzers.base_repository_analyzer import (
    BaseRepositoryAnalyzer,
)
from app.repository_intelligence.extractors.ast_extractor import ASTExtractor
from app.repository_intelligence.extractors.symbol_extractor import SymbolExtractor
from app.repository_intelligence.extractors.import_extractor import ImportExtractor
from app.repository_intelligence.graph.relationship_graph import RelationshipGraph
from app.repository_intelligence.models import (
    Language,
    RepositoryAnalysis,
    RepositoryMetadata,
    
)


class PythonRepositoryAnalyzer(BaseRepositoryAnalyzer):

    def __init__(
            self, 
            ast_extractor: ASTExtractor,
            symbol_extractor: SymbolExtractor,
            import_extractor: ImportExtractor,
            relationship_graph: RelationshipGraph,
    )-> None:

        self.ast_extractor = ast_extractor
        self.symbol_extractor = symbol_extractor
        self.import_extractor =  import_extractor
        self.relationship_graph = relationship_graph


    def analyze(
            self, 
            project_files: list[ProjectFile],
            repository_root: Path,
    )-> RepositoryAnalysis:
        analysis = RepositoryAnalysis(
            metadata=RepositoryMetadata(
                root_path=repository_root,
                language = Language.PYTHON,
                files_analyzed=len(project_files),
            )
        )

        parsed_files= self.ast_extractor.parse(project_files)        

        self.symbol_extractor.extract(
            parsed_files,
            analysis,
        )        

        self.import_extractor.extract(
            parsed_files,
            analysis,
        )

        self.relationship_graph.build(
            analysis,
            parsed_files,
        )

        return analysis
