from __future__ import annotations

import ast
import logging

from app.repository_intelligence.models import ParsedFile
from app.project_knowledge.models import ProjectFile

logger = logging.getLogger(__name__)
class ASTExtractor: 

    def parse(
            self, 
            project_files: list[ProjectFile],
    )-> list[ParsedFile]:

        parsed_files: list[ParsedFile] = []
        for project_file in project_files:
            try:
                ast_tree = ast.parse(
                    project_file.content,
                    filename=str(project_file.path),
                )
                parsed_files.append(
                    ParsedFile(
                        project_file=project_file,
                        ast_tree=ast_tree,
                    )
                )
            except SyntaxError as error:
                logger.warning(
                    "Failed to parse '%s' : %s",
                    project_file.path,
                    error,
                )

        return parsed_files
    