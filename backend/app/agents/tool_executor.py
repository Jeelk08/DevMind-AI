from app.tools.base_tool import BaseTool
from app.tools.tool_request import ToolRequest
from app.tools.tool_response import ToolResponse
from app.tools.tool_registry import ToolRegistry


class ToolExecutor:

    def __init__(
        self,
        registry: ToolRegistry,
    ):
        self.registry = registry

    def execute(
        self,
        request: ToolRequest,
        tool: BaseTool | None = None,
    ) -> ToolResponse:

        if tool is None:
            tool = self.registry.get(
                request.tool_id
            )

        return tool.execute(request)