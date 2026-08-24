from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str | None = None
    project_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str