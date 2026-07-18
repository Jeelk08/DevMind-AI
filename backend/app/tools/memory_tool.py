from app.memory.memory_manager import MemoryManager
from app.tools.base_tool import BaseTool
from app.tools.tool_request import ToolRequest
from app.tools.tool_response import ToolResponse


class MemoryTool(BaseTool):
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    @property
    def id(self) -> str:
        return "memory"

    @property 
    def name(self) -> str:
        return "Memory Tool"

    @property
    def description(self) -> str:
        return "Retrieves conversation memory."

    def execute(self, request: ToolRequest) -> ToolResponse:

        operation = request.context.get("operation")

        if operation == "retrieve":
            history = self.memory_manager.get_history(request.session_id)
            return ToolResponse(result = history)
        else:
            return ToolResponse(
                error=f"Unsupported operation: {operation}"
                )
