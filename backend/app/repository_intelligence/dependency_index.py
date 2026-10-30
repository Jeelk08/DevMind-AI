"""Build a lightweight, repository-wide file dependency index.

The index uses UniversalFileExtractor references and resolves local paths.
It intentionally ignores external packages and URLs that cannot be mapped to
files inside the repository.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
# import re

from app.project_knowledge.models import ProjectFile
from app.repository_intelligence.extractors.universal_file_extractor import (
    UniversalFileExtractor,
)


@dataclass(frozen=True)
class FileDependency:
    source_path: Path
    target_path: Path
    reference: str


class RepositoryDependencyIndex:
    RESOLUTION_SUFFIXES = (
        "", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
        ".py", ".html", ".css", ".scss", ".json", ".xml",
        ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".java",
    )
    INDEX_NAMES = (
        "index.js", "index.jsx", "index.ts", "index.tsx",
        "__init__.py",
    )

    def __init__(
        self,
        files: list[ProjectFile],
        extractor: UniversalFileExtractor | None = None,
    ) -> None:
        self.files = files
        self.extractor = extractor or UniversalFileExtractor()
        self._by_normalized_path = {
            self._normalize_path(item.path): item.path for item in files
        }
        self.dependencies: list[FileDependency] = []
        self._outgoing: dict[str, list[FileDependency]] = {}
        self._incoming: dict[str, list[FileDependency]] = {}
        self._build()

    @staticmethod
    def _normalize_path(path: Path | str) -> str:
        """
        Normalize paths consistently across Windows and POSIX.

        Avoid resolving against the current working directory because
        repository paths may have their own root.
        """
        normalized = os.path.normpath(str(path))
        return normalized.replace("\\", "/").casefold()

    def _resolve_reference(
        self,
        source: Path,
        reference: str,
    ) -> Path | None:

        ref = reference.strip().replace("\\", "/")

        if not ref:
            return None

        if ref.startswith((
            "http://",
            "https://",
            "//",
            "data:",
            "#",
            "mailto:",
            "javascript:",
        )):
            return None

        # Only resolve relative local references.
        if not (
            ref.startswith("./")
            or ref.startswith("../")
        ):
            return None

        # Normalize lexically instead of using .resolve().
        # This prevents Windows from adding the current drive
        # to repository-rooted paths such as /repo/src/file.js.
        base = Path(
            os.path.normpath(
                str(source.parent / ref)
            )
        )

        candidates = [base]

        if not base.suffix:
            candidates.extend(
                Path(str(base) + suffix)
                for suffix in self.RESOLUTION_SUFFIXES
                if suffix
            )

            candidates.extend(
                base / name
                for name in self.INDEX_NAMES
            )

        for candidate in candidates:

            key = self._normalize_path(candidate)

            matched = self._by_normalized_path.get(key)

            if matched is not None:
                return matched

        return None

    def _build(self) -> None:
        for project_file in self.files:
            insights = self.extractor.extract(
                project_file.path, project_file.content
            )
            for reference in insights.references:
                target = self._resolve_reference(project_file.path, reference)
                if target is None:
                    continue
                dependency = FileDependency(
                    source_path=project_file.path,
                    target_path=target,
                    reference=reference,
                )
                self.dependencies.append(dependency)
                self._outgoing.setdefault(
                    self._normalize_path(project_file.path), []
                ).append(dependency)
                self._incoming.setdefault(
                    self._normalize_path(target), []
                ).append(dependency)

    def get_dependencies(self, file_path: Path | str) -> list[FileDependency]:
        """Return files directly referenced by file_path."""
        return list(self._outgoing.get(self._normalize_path(file_path), []))

    def get_dependents(self, file_path: Path | str) -> list[FileDependency]:
        """Return repository files that directly reference file_path."""
        return list(self._incoming.get(self._normalize_path(file_path), []))

    def find_file(self, file_path: Path | str) -> Path | None:
        """Resolve an indexed path or filename to its canonical Path."""
        candidate = Path(file_path)
        key = self._normalize_path(candidate)
        if key in self._by_normalized_path:
            return self._by_normalized_path[key]
        matches = [
            path for path in self._by_normalized_path.values()
            if path.name.casefold() == candidate.name.casefold()
        ]
        return matches[0] if len(matches) == 1 else None
