from pathlib import Path
import os
from app.project_knowledge.exceptions import InvalidProjectPathException
from app.project_knowledge.loader.file_filter import FileFilter
from app.project_knowledge.models import ProjectFile


class RepositoryLoader:
    # passed the file_filer from outside rather than doing 
    # "self.file_filter = FileFilter()" because of dependancy injection 
    # meaning it can take any object (CustomFileFilter(), GitIgnoreFileFilter()) 
    # that can act as an object its called "loose coupling"
    def __init__(self, file_filter: FileFilter):
        self.file_filter = file_filter



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

        for root, dirs, filenames in os.walk(project_path): #os.walk is Python's built-in directory walker. Which returns in string

            root_path = Path(root)
            dirs[:] = [
                d for d in dirs
                if not self.file_filter.should_ignore(root_path / d)
            ]
            
            for filename in filenames:
                file_path = root_path / filename

                if self.file_filter.should_ignore(file_path):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue

                project_files.append(
                    ProjectFile(
                        path=file_path,
                        content=content,
                    )
                )

        return project_files

