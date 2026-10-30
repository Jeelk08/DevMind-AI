from pathlib import Path, PurePosixPath, PureWindowsPath
from shutil import rmtree
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.dependencies import get_repository_context_tool
from app.database.connection import DatabaseConnection
from app.database.project_repository import ProjectRepository
from app.project_knowledge.loader.file_filter import FileFilter
from app.project_knowledge.security.secret_protector import SecretProtector
from app.services.project_manager import ProjectManager


router = APIRouter()
project_manager = ProjectManager(ProjectRepository(DatabaseConnection()))

MAX_FILES = 1000
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_TOTAL_SIZE = 100 * 1024 * 1024

IGNORED_DIRS = FileFilter.IGNORED_DIRS
IGNORED_FILES = FileFilter.IGNORED_FILES
file_filter = FileFilter()
secret_protector = SecretProtector()


def _safe_relative_path(raw_path: str) -> Path:
    """Validate a browser-provided relative path before writing it."""
    normalized = (raw_path or "").replace("\\", "/").strip()

    if not normalized or normalized.startswith("/"):
        raise ValueError("Every uploaded file must have a relative path.")

    windows_path = PureWindowsPath(normalized)
    posix_path = PurePosixPath(normalized)

    if windows_path.is_absolute() or windows_path.drive:
        raise ValueError("Absolute file paths are not allowed.")

    parts = posix_path.parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise ValueError("Invalid relative file path.")

    if any(part in IGNORED_DIRS for part in parts[:-1]):
        raise ValueError("Files inside excluded directories cannot be imported.")

    filename = parts[-1]
    if filename in IGNORED_FILES or secret_protector.should_exclude_file(Path(filename)):
        raise ValueError("Sensitive or excluded files cannot be imported.")

    relative = Path(*parts)
    if file_filter.should_ignore(relative):
        raise ValueError(f"Unsupported or excluded file: {filename}")

    return relative


@router.post("/projects/import")
async def import_project_folder(
    name: str = Form(...),
    files: list[UploadFile] = File(...),
    relative_paths: list[str] = Form(...),
):
    """Create a managed project from files selected in the user's browser."""
    project_name = (name or "").strip()
    if not project_name:
        raise HTTPException(status_code=400, detail="Project name is required.")

    if not files:
        raise HTTPException(status_code=400, detail="The selected folder contains no supported files.")

    if len(files) != len(relative_paths):
        raise HTTPException(
            status_code=400,
            detail="The uploaded files and relative paths do not match.",
        )

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files. The limit is {MAX_FILES}.",
        )

    backend_root = Path(__file__).resolve().parents[2]
    storage_root = backend_root / "data" / "imported_projects"
    import_id = str(uuid4())
    repository_root = storage_root / import_id
    repository_root.mkdir(parents=True, exist_ok=False)

    total_size = 0
    saved_count = 0
    project = None

    try:
        for upload, raw_relative_path in zip(files, relative_paths):
            try:
                relative_path = _safe_relative_path(raw_relative_path)
            except ValueError as error:
                raise HTTPException(status_code=400, detail=str(error))

            content = await upload.read(MAX_FILE_SIZE + 1)
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File '{relative_path.name}' exceeds the 10 MB limit.",
                )

            total_size += len(content)
            if total_size > MAX_TOTAL_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="The selected folder exceeds the 100 MB total upload limit.",
                )

            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError:
                # Skip binary/non-text files rather than failing the whole import.
                continue

            destination = (repository_root / relative_path).resolve()
            try:
                destination.relative_to(repository_root.resolve())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid file path.")

            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(decoded, encoding="utf-8")
            saved_count += 1

        if saved_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No supported UTF-8 text files were found in the selected folder.",
            )

        project = project_manager.create_project(
            name=project_name,
            repository_path=str(repository_root),
        )

        # Checkpoint 007 lifecycle: explicitly create without automatic
        # indexing, then perform exactly one explicit initial refresh.
        context_tool = get_repository_context_tool(
            project["id"],
            auto_index=False,
        )
        index_stats = context_tool.refresh_index()

        return {
            "project": {
                "id": project["id"],
                "name": project["name"],
                "repository_path": project["repository_path"],
                "connected": bool(project["connected"]),
            },
            "files_received": len(files),
            "files_saved": saved_count,
            "total_bytes": total_size,
            "index": index_stats,
            "message": "Folder imported and indexed successfully.",
        }

    except HTTPException:
        if project is not None:
            try:
                project_manager.delete_project(project["id"])
            except Exception:
                pass
        rmtree(repository_root, ignore_errors=True)
        raise
    except Exception as error:
        if project is not None:
            try:
                project_manager.delete_project(project["id"])
            except Exception:
                pass
        rmtree(repository_root, ignore_errors=True)
        raise HTTPException(
            status_code=500,
            detail=f"Folder import failed: {error}",
        )
