from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.agents.devmind_agent import DevMindAgent
from app.integrations.ai.exceptions import (
    AIRateLimitException,
    AIClientException,
)

router = APIRouter()
agent = DevMindAgent()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    try:
        response = agent.chat(
            request.session_id,
            request.message,
            request.project_id,
        )

        return response

    except AIRateLimitException as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        ) from exc

    except AIClientException as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc