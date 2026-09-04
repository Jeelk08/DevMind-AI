from pathlib import Path
from threading import Lock

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

# Prevent two simultaneous requests from creating and indexing
# the same project's RepositoryContextTool at the same time.
_repository_context_tools_lock = Lock()


def get_repository_context_tool(
    project_id: str,
) -> RepositoryContextTool:

    # Fast path: already initialized.
    if project_id in _repository_context_tools:
        return _repository_context_tools[
            project_id
        ]

    # Only one request may initialize a missing project tool
    # at a time. This prevents concurrent repository indexing
    # against the same .devmind cache.
    with _repository_context_tools_lock:

        # Check again after acquiring the lock because another
        # request may have initialized the tool while we waited.
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
def remove_repository_context_tool(
    project_id: str,
) -> None:

    with _repository_context_tools_lock:

        _repository_context_tools.pop(
            project_id,
            None,
        )