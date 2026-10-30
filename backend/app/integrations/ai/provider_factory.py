from app.core.config import LLM_PROVIDER, GEMINI_API_KEY
from app.integrations.ai.gemini_client import GeminiClient


def create_ai_provider():
    provider = LLM_PROVIDER.lower().strip()

    if provider == "gemini":
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        return GeminiClient(api_key=GEMINI_API_KEY)

    raise ValueError(
        f"Unsupported AI provider: {provider}"
    )