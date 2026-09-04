from pathlib import Path
import os

from app.project_knowledge.exceptions import (
    InvalidProjectPathException,
)
from app.project_knowledge.loader.file_filter import FileFilter
from app.project_knowledge.models import ProjectFile
from app.project_knowledge.security.secret_protector import (
    SecretProtector,
)


class RepositoryLoader:

    def __init__(
        self,
        file_filter: FileFilter,
        secret_protector: SecretProtector | None = None,
    ):
        self.file_filter = file_filter

        self.secret_protector = (
            secret_protector
            if secret_protector is not None
            else SecretProtector()
        )

    def load(
        self,
        project_path: Path,
    ) -> list[ProjectFile]:

        if not project_path.exists():
            raise InvalidProjectPathException(
                f"Project Path '{project_path}' does not exists."
            )

        if not project_path.is_dir():
            raise InvalidProjectPathException(
                f"'{project_path} is not a directory.'"
            )

        project_files: list[ProjectFile] = []

        for root, dirs, filenames in os.walk(project_path):

            root_path = Path(root)

            dirs[:] = [
                d
                for d in dirs
                if not self.file_filter.should_ignore(
                    root_path / d
                )
            ]

            for filename in filenames:

                file_path = root_path / filename

                if self.file_filter.should_ignore(
                    file_path
                ):
                    continue

                # Completely exclude known sensitive files.
                if self.secret_protector.should_exclude_file(
                    file_path
                ):
                    continue

                try:
                    content = file_path.read_text(
                        encoding="utf-8"
                    )
                except UnicodeDecodeError:
                    continue

                # Protect secrets before the content reaches
                # chunking, embedding, analysis, or persistence.
                content = self.secret_protector.sanitize(
                    content
                )

                project_files.append(
                    ProjectFile(
                        path=file_path,
                        content=content,
                    )
                )

        return project_files