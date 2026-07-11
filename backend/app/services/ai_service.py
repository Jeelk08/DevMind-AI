import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.core.personality import SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)


class AIService:

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def get_response(self, message: str):

        prompt = f"""
{SYSTEM_PROMPT}
        
User:
{message}

Respond as DevMind AI.
        """

        response = self.model.generate_content(prompt)
        return response.text