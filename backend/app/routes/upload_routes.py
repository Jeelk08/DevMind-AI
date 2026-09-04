from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.database.connection import DatabaseConnection
from app.database.project_repository import ProjectRepository
from app.services.project_manager import ProjectManager
from app.core.dependencies import get_repository_context_tool


router = APIRouter()


project_manager = ProjectManager(
    ProjectRepository(
        DatabaseConnection()
    )
)


ALLOWED_EXTENSIONS = {
    ".py",
    ".java",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".json",
    ".md",
    ".yml",
    ".yaml",
}


MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post(
    "/projects/{project_id}/uploads",
)
async def upload_files(
    project_id: str,
    files: list[UploadFile] = File(...),
):
    try:
        project = project_manager.get_project(
            project_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    if not bool(project["connected"]):
        raise HTTPException(
            status_code=400,
            detail="Project is disconnected.",
        )

    repository_root = Path(
        project["repository_path"]
    ).resolve()

    upload_root = (
        repository_root
        / ".devmind"
        / "uploads"
    )

    upload_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_files = []

    for upload in files:

        if not upload.filename:
            continue

        filename = Path(
            upload.filename
        ).name

        extension = Path(
            filename
        ).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type: "
                    f"{filename}"
                ),
            )

        content = await upload.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"File '{filename}' exceeds "
                    "the 10 MB limit."
                ),
            )

        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"File '{filename}' is not "
                    "a valid UTF-8 text file."
                ),
            )

        file_directory = (
            upload_root
            / str(uuid4())
        )

        file_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            file_directory
            / filename
        )

        destination.write_bytes(
            content
        )

        saved_files.append(
            {
                "file_name": filename,
                "file_path": str(destination),
                "size": len(content),
            }
        )

    if not saved_files:
        raise HTTPException(
            status_code=400,
            detail="No valid files were uploaded.",
        )

    try:
        repository_context_tool = (
            get_repository_context_tool(
                project_id
            )
        )

        stats = (
            repository_context_tool.refresh_index()
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Files were uploaded, but "
                f"indexing failed: {error}"
            ),
        )

    return {
        "message": "Files uploaded and indexed successfully.",
        "files": saved_files,
        "index": stats,
    }