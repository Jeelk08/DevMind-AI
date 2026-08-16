from pathlib import Path

from app.project_knowledge.models import ProjectFile


class PathRetriever:
    def __init__(self, files: list[ProjectFile]):
        self.files = files

    def retrieve(self, query: str) -> list[ProjectFile]:
        query = query.strip().lower()

        if not query:
            return []

        results = []

        for project_file in self.files:
            path = str(project_file.path).lower()
            filename = project_file.path.name.lower()

            if query == path or query == filename:
                results.append(project_file)
                continue

            if filename in query:
                results.append(project_file)

        return results