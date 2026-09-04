from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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


class ProjectKnowledgeStats(BaseModel):
    indexed_files: int
    chunks: int


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
            connected=bool(project["connected"]),
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
            connected=bool(project["connected"]),
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
            connected=bool(project["connected"]),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.get(
    "/projects/{project_id}/stats",
    response_model=ProjectKnowledgeStats,
)
def get_project_knowledge_stats(
    project_id: str,
):
    try:
        return project_manager.get_project_knowledge_stats(
            project_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )




@router.get(
    "/projects/{project_id}/changes",
)
def get_project_changes(
    project_id: str,
):
    try:
        return project_manager.get_project_changes(
            project_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )




@router.post(
    "/projects/{project_id}/knowledge/update",
)
def update_project_knowledge(
    project_id: str,
):
    try:
        return project_manager.update_project_knowledge(
            project_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )




@router.post(
    "/projects/{project_id}/disconnect",
)
def disconnect_project(
    project_id: str,
):
    try:
        project_manager.disconnect_project(
            project_id
        )

        return {
            "message": "Project disconnected successfully."
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.post(
    "/projects/{project_id}/reconnect",
)
def reconnect_project(
    project_id: str,
):
    try:
        project_manager.reconnect_project(
            project_id
        )

        return {
            "message": "Project reconnected successfully."
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.delete(
    "/projects/{project_id}/knowledge",
    response_model=ProjectResponse,
)
def remove_project_knowledge(
    project_id: str,
):
    try:
        project = project_manager.remove_project_knowledge(
            project_id
        )

        return ProjectResponse(
            id=project["id"],
            name=project["name"],
            repository_path=project["repository_path"],
            connected=bool(project["connected"]),
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
            connected=bool(project["connected"]),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )