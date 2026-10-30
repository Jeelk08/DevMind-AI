from app.services.ai_service import AIService
from app.memory.memory_manager import MemoryManager
from app.agents.planner import Planner
from app.agents.tool_executor import ToolExecutor
from app.tools.memory_tool import MemoryTool
from app.tools.tool_registry import ToolRegistry
from app.core.dependencies import (
    get_repository_context_tool,
)


class DevMindAgent: 
    
    def __init__(self):
        self.ai_service = AIService()
        self.memory = MemoryManager()
        self.tool_registry = ToolRegistry()

        self.memory_tool = MemoryTool(self.memory)
        self.tool_registry.register(self.memory_tool)
        
        self.planner = Planner()
        self.tool_executor = ToolExecutor(self.tool_registry)
        

    def chat(self, session_id: str | None, message: str, project_id: str,):

        if session_id is None:#creates a new session_id if doesn't exist
            session_id = self.memory.create_session()
        

        self.memory.save_message( #save the message with new session_id user(role)
            session_id,
            "user",
            message
        )

        request = self.planner.plan(
            message,
            session_id,
            project_id,
        )

# ==============================

        if request is not None:

            if request.tool_id == "repository_context":

                repository_context_tool = (
                    get_repository_context_tool(
                        project_id
                    )
                )

                tool_response = (
                    self.tool_executor.execute(
                        request,
                        tool=repository_context_tool,
                    )
                )

            else:

                tool_response = (
                    self.tool_executor.execute(
                        request
                    )
                )

            history = self.memory.get_history(
                session_id
            )

            if tool_response.error:
                # Keep the conversation intact and let the model explain
                # that repository retrieval failed instead of silently
                # answering as if it had inspected the project.
                history.append({
                    "role": "user",
                    "content": (
                        "Repository retrieval could not be completed. "
                        f"Retrieval error: {tool_response.error}"
                    ),
                })
            elif tool_response.result:
                # Add retrieved project context to the existing conversation
                # rather than replacing prior turns. This preserves follow-ups.
                history.extend(tool_response.result)

        else:

            history = self.memory.get_history(
                session_id
            )



# ===============================
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