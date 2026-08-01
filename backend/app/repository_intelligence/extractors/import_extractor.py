from __future__ import annotations


 
from app.repository_intelligence.models import (
    ParsedFile,
    RepositoryAnalysis,
)
from app.repository_intelligence.extractors.import_visitor import ImportVisitor 

class ImportExtractor:

    def extract(
        self,
        parsed_files: list[ParsedFile],
        analysis: RepositoryAnalysis,
    ) -> None:

        for parsed_file in parsed_files:
            visitor = ImportVisitor(
                parsed_file.project_file,
                analysis,
            )

            visitor.visit(parsed_file.ast_tree)

