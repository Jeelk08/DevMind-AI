from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService

router = APIRouter()

ai_service = AIService()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = ai_service.get_response(request.message)
    return ChatResponse(response = response)