from pathlib import Path
import re

from app.project_knowledge.models import ProjectFile


class PathRetriever:
    """Find project files explicitly referenced by a natural-language query."""

    def __init__(self, files: list[ProjectFile]):
        self.files = files

    @staticmethod
    def _normalise(value: str) -> str:
        return value.replace("\\", "/").strip().lower()

    def retrieve_with_match_type(
        self, query: str
    ) -> list[tuple[ProjectFile, bool]]:
        """Return (file, exact_reference) pairs, exact references first."""
        query_normalised = self._normalise(query)
        if not query_normalised:
            return []

        exact: list[ProjectFile] = []
        partial: list[ProjectFile] = []

        for project_file in self.files:
            path = self._normalise(str(project_file.path))
            filename = self._normalise(project_file.path.name)

            # An exact path or filename explicitly appears in the question.
            path_mentioned = path and path in query_normalised
            filename_pattern = rf"(?<![\w.-]){re.escape(filename)}(?![\w.-])"
            filename_mentioned = bool(
                re.search(filename_pattern, query_normalised)
            )

            if query_normalised == path or query_normalised == filename:
                exact.append(project_file)
            elif path_mentioned or filename_mentioned:
                exact.append(project_file)
            elif filename and filename in query_normalised:
                partial.append(project_file)

        # Keep deterministic order and avoid duplicates.
        results: list[tuple[ProjectFile, bool]] = []
        seen: set[str] = set()
        for item, is_exact in (
            [(item, True) for item in exact]
            + [(item, False) for item in partial]
        ):
            key = self._normalise(str(item.path))
            if key not in seen:
                results.append((item, is_exact))
                seen.add(key)
        return results

    def retrieve(self, query: str) -> list[ProjectFile]:
        return [
            project_file
            for project_file, _ in self.retrieve_with_match_type(query)
        ]
