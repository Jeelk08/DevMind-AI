
from abc import ABC, abstractmethod
from app.project_knowledge.models import Chunk, ProjectFile

class BaseChunker(ABC):

    @abstractmethod
    def chunk(self, project_file: ProjectFile) -> list[Chunk]:
        """
        Splits a project file into meaningful chunks. 
        """
        pass


    