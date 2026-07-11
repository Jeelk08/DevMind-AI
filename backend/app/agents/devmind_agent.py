from app.services.ai_service import AIService

class DevMindAgent: 
    
    def __init__(self):
        self.ai_service = AIService()

    def chat(self, message: str):

        return self.ai_service.get_response(message)