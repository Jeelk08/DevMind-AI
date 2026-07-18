from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolRequest:
    """Standard request object passed to every tool."""

    tool_id: str
    session_id: str
    input: str
    context: dict[str, Any] = field(default_factory=dict) 
    # field used so that python will create a new empty dictionary every time a ToolRequest object is created.

    