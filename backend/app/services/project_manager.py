from pathlib import Path
from uuid import uuid4

from app.database.project_repository import ProjectRepository


class ProjectManager:

    def __init__(
        self,
        repository: ProjectRepository,
    ):
        self.repository = repository

    def create_project(
        self,
        name: str,
        repository_path: str,
    ):

        path = Path(repository_path).resolve()

        if not path.exists():
            raise ValueError(
                f"Repository path '{repository_path}' does not exist."
            )

        if not path.is_dir():
            raise ValueError(
                f"Repository path '{repository_path}' is not a directory."
            )

        normalized_path = str(path)

        existing_project = (
            self.repository.get_by_repository_path(
                normalized_path
            )
        )

        if existing_project is not None:
            raise ValueError(
                "This repository is already connected "
                f"as project '{existing_project['name']}'."
            )

        project_id = str(uuid4())

        self.repository.create(
            project_id=project_id,
            name=name,
            repository_path=normalized_path,
        )

        return self.repository.get_by_id(
            project_id
        )

    def get_project(
        self,
        project_id: str,
    ):

        project = self.repository.get_by_id(
            project_id
        )

        if project is None:
            raise ValueError(
                f"Project '{project_id}' not found."
            )

        return project

    def get_projects(self):

        return self.repository.get_all()

    def delete_project(
        self,
        project_id: str,
    ):

        project = self.get_project(
            project_id
        )

        self.repository.delete(
            project_id
        )

        return project