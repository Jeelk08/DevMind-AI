from app.tools.tool_request import ToolRequest


class Planner:
    """Routes explicit memory requests and project-scoped questions.

    When a project is active, repository retrieval is the default. This avoids
    brittle keyword matching that silently sends valid repository questions
    straight to the general chat model without code context.
    """

    MEMORY_PHRASES = (
        "what did we discuss",
        "what did i ask",
        "what did you tell me",
        "remember when",
        "our previous conversation",
        "earlier conversation",
        "chat history",
        "conversation history",
    )

    def plan(
        self,
        message: str,
        session_id: str,
        project_id: str | None = None,
    ) -> ToolRequest | None:
        normalized = (message or "").strip().lower()

        if not normalized:
            return None

        # Explicit requests about previous conversation history take priority.
        memory_keywords = ("history", "remember", "previous", "earlier")
        if (
            any(phrase in normalized for phrase in self.MEMORY_PHRASES)
            or any(keyword in normalized for keyword in memory_keywords)
        ):
            return ToolRequest(
                tool_id="memory",
                session_id=session_id,
                input=message,
                context={"operation": "retrieve"},
            )

        # An active project is the strongest signal that a question should be
        # answered from repository knowledge. Do not require magic keywords.
        if project_id:
            return ToolRequest(
                tool_id="repository_context",
                session_id=session_id,
                input=message,
                context={"project_id": project_id},
            )

        # Preserve general-chat behavior when no project is selected.
        return None
