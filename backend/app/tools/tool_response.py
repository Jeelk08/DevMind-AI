from typing import Any
from dataclasses import dataclass, field


@dataclass
class ToolResponse:
    """Standard response object returned by every tool."""

    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)