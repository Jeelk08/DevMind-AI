from app.project_knowledge.models import Chunk, ProjectFile
from app.project_knowledge.parser.base_chunker import BaseChunker

class GenericChunker(BaseChunker):

    def __init__(
            self, 
            max_chunk_size: int = 4000,
            chunk_overlap: int = 400,
    ):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap



    def chunk(self, project_file: ProjectFile) -> list[Chunk]:
        chunks = []

        content = project_file.content #just a short reference to project_file.content
        start = 0

        while start < len(content):

            #prevents from going past the end of the file.
            end = min(
                start + self.max_chunk_size,
                len(content),
            )
 

            chunk_content = content[start:end] #slicing 
            chunks.append(
                Chunk(
                    content = chunk_content,
                    path = project_file.path,
                    start_offset= start,
                    end_offset= end,
                )
            )

            if end == len(content):
                break

            start = end - self.chunk_overlap #overlapping
        return chunks
        