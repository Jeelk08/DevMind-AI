from fastapi import APIRouter, HTTPException

from app.database.connection import DatabaseConnection
from app.database.project_repository import ProjectRepository
from app.models.project import (
    ProjectCreate,
    ProjectResponse,
)
from app.services.project_manager import ProjectManager


router = APIRouter()

project_manager = ProjectManager(
    ProjectRepository(
        DatabaseConnection()
    )
)


@router.post(
    "/projects",
    response_model=ProjectResponse,
)
def create_project(
    request: ProjectCreate,
):
    try:
        project = project_manager.create_project(
            name=request.name,
            repository_path=request.repository_path,
        )

        return ProjectResponse(
            id=project["id"],
            name=project["name"],
            repository_path=project["repository_path"],
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def get_projects():

    projects = project_manager.get_projects()

    return [
        ProjectResponse(
            id=project["id"],
            name=project["name"],
            repository_path=project["repository_path"],
        )
        for project in projects
    ]


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: str,
):
    try:
        project = project_manager.get_project(
            project_id
        )

        return ProjectResponse(
            id=project["id"],
            name=project["name"],
            repository_path=project["repository_path"],
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.delete(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def delete_project(
    project_id: str,
):
    try:
        project = project_manager.delete_project(
            project_id
        )

        return ProjectResponse(
            id=project["id"],
            name=project["name"],
            repository_path=project["repository_path"],
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )