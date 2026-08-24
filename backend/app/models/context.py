from pydantic import BaseModel


class ContextRequest(BaseModel):

    query: str
    project_id: str


class ContextSource(BaseModel):

    id: int
    file_name: str
    file_path: str
    relevance: float
    content: str


class ContextResponse(BaseModel):

    query: str
    sources: list[ContextSource]