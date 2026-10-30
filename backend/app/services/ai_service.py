from app.core.personality import SYSTEM_PROMPT
from app.integrations.ai.provider_factory import create_ai_provider


class AIService:

    def __init__(self, provider=None):
        self.provider = provider or create_ai_provider()

    def get_response(self, history: list):

        conversation = ""

        for msg in history:
            conversation += (
                f"{msg['role'].capitalize()}: "
                f"{msg['content']}\n"
            )

        prompt = f"""
        {SYSTEM_PROMPT}

        Conversation:
        {conversation}

        Respond as DevMind AI.
        """

        return self.provider.generate_response(prompt)