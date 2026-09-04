from pathlib import Path
from uuid import uuid4
import json
import hashlib

from app.database.project_repository import ProjectRepository
from app.core.dependencies import (
    get_repository_context_tool,
    remove_repository_context_tool,
)

from app.project_knowledge.loader.file_filter import FileFilter
from app.project_knowledge.loader.repository_loader import RepositoryLoader
from app.project_knowledge.security.secret_protector import SecretProtector


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

    def get_project_knowledge_stats(
        self,
        project_id: str,
    ):
        """
        Return statistics for the project's persistent
        repository knowledge index.

        The index is stored at:

            <repository_parent>/.devmind/repository_index.json

        Returns:
            {
                "indexed_files": int,
                "chunks": int,
            }

        This method only reads the existing cache.
        It does not trigger a re-index.
        """

        project = self.get_project(
            project_id
        )

        repository_root = Path(
            project["repository_path"]
        ).resolve()

        cache_path = (
            repository_root.parent
            / ".devmind"
            / "repository_index.json"
        )

        if not cache_path.exists():
            return {
                "indexed_files": 0,
                "chunks": 0,
            }

        try:
            with cache_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                cache = json.load(file)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {
                "indexed_files": 0,
                "chunks": 0,
            }

        files = cache.get(
            "files",
            {}
        )

        if not isinstance(files, dict):
            return {
                "indexed_files": 0,
                "chunks": 0,
            }

        total_chunks = 0

        # Count valid indexed file entries.
        indexed_files = 0

        # Track actual file paths represented by chunks.
        # This provides a reliable fallback if the cache
        # structure contains chunk data but its file entries
        # are incomplete.
        chunk_file_paths = set()

        for file_path, file_data in files.items():

            if not isinstance(file_data, dict):
                continue

            chunks = file_data.get(
                "chunks",
                []
            )

            if not isinstance(chunks, list):
                continue

            # The file is a valid indexed entry even when
            # it produced zero chunks.
            indexed_files += 1

            total_chunks += len(chunks)

            for chunk in chunks:
                if not isinstance(chunk, dict):
                    continue

                chunk_path = chunk.get("path")

                if chunk_path:
                    chunk_file_paths.add(
                        str(chunk_path)
                    )

        # Normally len(files) is the correct number.
        # If the cache contains chunks but the file-entry
        # count is unexpectedly empty, use the unique chunk
        # paths as a fallback.
        if indexed_files == 0 and chunk_file_paths:
            indexed_files = len(
                chunk_file_paths
            )

        return {
            "indexed_files": indexed_files,
            "chunks": total_chunks,
        }






    def get_project_changes(
        self,
        project_id: str,
    ):
        """
        Detect changes between the current repository state
        and the last persisted repository index.

        This method ONLY reads the repository and existing cache.
        It does not perform indexing or create embeddings.
        """

        project = self.get_project(
            project_id
        )

        repository_root = Path(
            project["repository_path"]
        ).resolve()

        # --------------------------------------------------
        # Repository availability
        # --------------------------------------------------

        if not repository_root.exists():
            raise ValueError(
                f"Project location '{repository_root}' is unavailable."
            )

        if not repository_root.is_dir():
            raise ValueError(
                f"Project location '{repository_root}' is not a directory."
            )

        # --------------------------------------------------
        # Persistent index location
        # --------------------------------------------------

        cache_path = (
            repository_root.parent
            / ".devmind"
            / "repository_index.json"
        )

        # --------------------------------------------------
        # Load previous index
        # --------------------------------------------------

        if not cache_path.exists():
            # No previous index means the project has not
            # been indexed yet.
            loader = RepositoryLoader(
                file_filter=FileFilter(),
                secret_protector=SecretProtector(),
            )

            current_files = loader.load(
                repository_root
            )

            return {
                "status": "not_indexed",
                "added": [
                    self._relative_project_path(
                        file.path,
                        repository_root,
                    )
                    for file in current_files
                ],
                "modified": [],
                "deleted": [],
                "added_count": len(current_files),
                "modified_count": 0,
                "deleted_count": 0,
                "total_changes": len(current_files),
            }

        try:
            with cache_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                cache = json.load(file)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {
                "status": "not_indexed",
                "added": [],
                "modified": [],
                "deleted": [],
                "added_count": 0,
                "modified_count": 0,
                "deleted_count": 0,
                "total_changes": 0,
            }

        cached_files = cache.get(
            "files",
            {}
        )

        if not isinstance(
            cached_files,
            dict,
        ):
            cached_files = {}

        # --------------------------------------------------
        # Load current repository state
        # --------------------------------------------------

        loader = RepositoryLoader(
            file_filter=FileFilter(),
            secret_protector=SecretProtector(),
        )

        current_files = loader.load(
            repository_root
        )

        current_file_map = {
            self._relative_project_path(
                project_file.path,
                repository_root,
            ): project_file
            for project_file in current_files
        }

        # --------------------------------------------------
        # Detect changes
        # --------------------------------------------------

        added = []
        modified = []
        deleted = []

        # Added / modified
        for relative_path, project_file in current_file_map.items():

            current_hash = hashlib.sha256(
                project_file.content.encode(
                    "utf-8"
                )
            ).hexdigest()

            cached = cached_files.get(
                relative_path
            )

            if cached is None:
                added.append(
                    relative_path
                )

            elif not isinstance(
                cached,
                dict,
            ):
                modified.append(
                    relative_path
                )

            elif cached.get("hash") != current_hash:
                modified.append(
                    relative_path
                )

        # Deleted
        for relative_path in cached_files:

            if relative_path not in current_file_map:
                deleted.append(
                    relative_path
                )

        # Keep UI ordering deterministic.
        added.sort()
        modified.sort()
        deleted.sort()

        total_changes = (
            len(added)
            + len(modified)
            + len(deleted)
        )

        return {
            "status": (
                "changes_detected"
                if total_changes > 0
                else "up_to_date"
            ),
            "added": added,
            "modified": modified,
            "deleted": deleted,
            "added_count": len(added),
            "modified_count": len(modified),
            "deleted_count": len(deleted),
            "total_changes": total_changes,
        }





    def update_project_knowledge(
        self,
        project_id: str,
    ):
        """
        Incrementally update the project's knowledge.

        The existing RepositoryContextTool and
        IncrementalIndexManager perform the actual indexing.
        """

        project = self.get_project(
            project_id
        )

        if not bool(
            project["connected"]
        ):
            raise ValueError(
                "This project is disconnected."
            )

        repository_root = Path(
            project["repository_path"]
        ).resolve()

        if not repository_root.exists():
            raise ValueError(
                f"Project location '{repository_root}' is unavailable."
            )

        if not repository_root.is_dir():
            raise ValueError(
                f"Project location '{repository_root}' is not a directory."
            )

        context_tool = (
            get_repository_context_tool(
                project_id
            )
        )

        stats = context_tool.refresh_index()

        return stats




    @staticmethod
    def _relative_project_path(
        file_path: Path,
        repository_root: Path,
    ) -> str:

        try:
            return str(
                file_path.relative_to(
                    repository_root
                )
            )

        except ValueError:
            return str(file_path)







    def disconnect_project(
        self,
        project_id: str,
    ):

        self.get_project(
            project_id
        )

        self.repository.disconnect(
            project_id
        )

        return self.repository.get_by_id(
            project_id
        )

    def reconnect_project(
        self,
        project_id: str,
    ):

        self.get_project(
            project_id
        )

        self.repository.reconnect(
            project_id
        )

        return self.repository.get_by_id(
            project_id
        )

    def remove_project_knowledge(
        self,
        project_id: str,
    ):

        project = self.get_project(
            project_id
        )

        repository_path = Path(
            project["repository_path"]
        )

        cache_path = (
            repository_path.parent
            / ".devmind"
            / "repository_index.json"
        )

        if cache_path.exists():
            cache_path.unlink()

        remove_repository_context_tool(
            project_id
        )

        return self.repository.get_by_id(
            project_id
        )

    def delete_project(
        self,
        project_id: str,
    ):

        project = self.get_project(
            project_id
        )

        repository_path = Path(
            project["repository_path"]
        )

        cache_path = (
            repository_path.parent
            / ".devmind"
            / "repository_index.json"
        )

        if cache_path.exists():
            cache_path.unlink()

        remove_repository_context_tool(
            project_id
        )

        self.repository.delete(
            project_id
        )

        return project