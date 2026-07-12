from app.services.ai_service import AIService
from app.memory.memory_manager import MemoryManager

class DevMindAgent: 
    
    def __init__(self):
        self.ai_service = AIService()
        self.memory = MemoryManager()

    def chat(self, session_id: str | None, message: str):

        if session_id is None:#creates a new session_id if doesn't exist
            session_id = self.memory.create_session()
        

        self.memory.save_message( #save the message with new session_id user(role)
            session_id,
            "user",
            message
        )

        history = self.memory.get_history(session_id) 
        #now when we fetch history the user message will already be there 
        #as it is saved  

        response = self.ai_service.get_response(history)

        self.memory.save_message( #save the AI response
            session_id,
            "assistant",
            response
        )

        return {#return the response after saving
            "session_id": session_id,
            "response": response
        }