from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    repository_path: str


class ProjectResponse(BaseModel):
    id: str
    name: str
    repository_path: str