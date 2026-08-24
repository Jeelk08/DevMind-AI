from pathlib import Path

from app.database.project_repository import (
    ProjectRepository,
)


class ProjectRegistry:

    def __init__(
        self,
        repository: ProjectRepository,
    ):
        self.repository = repository

    def get_repository_root(
        self,
        project_id: str,
    ) -> Path:

        project = self.repository.get_by_id(
            project_id
        )

        if project is None:
            raise ValueError(
                f"Project '{project_id}' not found."
            )

        return Path(
            project["repository_path"]
        )