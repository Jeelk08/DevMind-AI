import os
from dotenv import load_dotenv

load_dotenv()

#API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


#Gemini Models
CHAT_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "gemini-embedding-001"