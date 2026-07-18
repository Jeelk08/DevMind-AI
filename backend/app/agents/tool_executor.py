from app.tools.tool_registry import ToolRegistry
from app.tools.tool_request import ToolRequest
from app.tools.tool_response import ToolResponse

class ToolExecutor:

    def __init__(self, registry: ToolRegistry):
        self.registry = registry


    def execute(
            self,
            request: ToolRequest,
    ) -> ToolResponse:
        
        tool = self.registry.get(request.tool_id)
        return tool.execute(request)
