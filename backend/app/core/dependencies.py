from pathlib import Path

from app.tools.repository_context_tool import RepositoryContextTool
from app.project_knowledge.project_registry import ProjectRegistry
from app.database.connection import DatabaseConnection
from app.database.project_repository import ProjectRepository


database = DatabaseConnection()

project_repository = ProjectRepository(
    database
)

project_registry = ProjectRegistry(
    project_repository
)

_repository_context_tools = {}


def get_repository_context_tool(
    project_id: str,
) -> RepositoryContextTool:

    if project_id in _repository_context_tools:
        return _repository_context_tools[
            project_id
        ]

    repository_root = (
        project_registry.get_repository_root(
            project_id
        )
    )

    tool = RepositoryContextTool(
        repository_root=repository_root,
    )

    _repository_context_tools[
        project_id
    ] = tool

    return tool