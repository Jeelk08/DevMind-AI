from typing import Any
from dataclasses import dataclass

@dataclass
class ToolResponse:
    """Standard response object returned by every tool."""

    result : Any = None
    error : str | None = None
    