from app.services.ai_service import AIService
from app.memory.memory_manager import MemoryManager
from app.agents.planner import Planner
from app.agents.tool_executor import ToolExecutor
from app.tools.memory_tool import MemoryTool
from app.tools.tool_registry import ToolRegistry


class DevMindAgent: 
    
    def __init__(self):
        self.ai_service = AIService()
        self.memory = MemoryManager()
        self.tool_registry = ToolRegistry()

        self.memory_tool = MemoryTool(self.memory)
        self.tool_registry.register(self.memory_tool)
        
        self.planner = Planner()
        self.tool_executor = ToolExecutor(self.tool_registry)


    def chat(self, session_id: str | None, message: str):

        if session_id is None:#creates a new session_id if doesn't exist
            session_id = self.memory.create_session()
        

        self.memory.save_message( #save the message with new session_id user(role)
            session_id,
            "user",
            message
        )

        request = self.planner.plan(
            message,
            session_id
        )

        

        if request is not None:
            tool_response = self.tool_executor.execute(request)

            if tool_response.error:
                history = self.memory.get_history(session_id)
            else:
                history = tool_response.result
        else:
            history = self.memory.get_history(session_id)




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