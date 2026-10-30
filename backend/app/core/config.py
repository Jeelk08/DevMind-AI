import os
from dotenv import load_dotenv

load_dotenv()

# API keys
GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

# AI provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# Gemini models
CHAT_MODEL = os.getenv(
    "CHAT_MODEL",
    "gemini-2.5-flash"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "gemini-embedding-001"
)