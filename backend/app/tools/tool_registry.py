from app.tools.base_tool import BaseTool



class ToolRegistry:
    
    def __init__(self):
        """Stores and manages all available tools."""
        self.tools: dict[str, BaseTool] = {}
    

    def register(self, tool: BaseTool) ->None :
        """Register a new tool."""

        if tool.id in self.tools:
            raise ValueError(f"Tool '{tool.id}' is already registered.")        

        self.tools[tool.id] = tool  #if doesn't exist then store "memory" -> MemoryTool()


    def get(self, tool_id: str) -> BaseTool:
        """Retrieve a tool by its id."""

        tool = self.tools.get(tool_id)

        if tool is None:
            raise ValueError(f"Tool '{tool_id}' not found.")
        return tool


    def exists(self, tool_id: str) -> bool:
        """Check whether a tool is registered."""
        return tool_id in self.tools #would return either True or False


    def list_all(self) -> list[BaseTool]:
        """Return all registered tools."""

        return list(self.tools.values()) #returning all the values in a list
    



        