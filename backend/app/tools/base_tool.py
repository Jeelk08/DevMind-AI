from abc import ABC, abstractmethod
from app.tools.tool_request import ToolRequest
from app.tools.tool_response import ToolResponse

class BaseTool(ABC):


    @property
    @abstractmethod
    def id(self) -> str:
        """Unique tool id."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short desription of what the tool does."""
        pass

    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResponse:
        pass