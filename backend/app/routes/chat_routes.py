from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.agents.devmind_agent import DevMindAgent

router = APIRouter()

agent = DevMindAgent()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = agent.chat(
        request.session_id,
        request.message
    ) 

    return response