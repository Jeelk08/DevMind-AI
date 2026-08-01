from __future__ import annotations
from abc import ABC, abstractmethod
from app.repository_intelligence.models import RepositoryAnalysis
from app.project_knowledge.models import ProjectFile
from pathlib import Path

class BaseRepositoryAnalyzer(ABC):


    @abstractmethod
    def analyze(
            self, 
            project_files: list[ProjectFile],
            repository_root: Path,
        ) -> RepositoryAnalysis:
        raise NotImplementedError