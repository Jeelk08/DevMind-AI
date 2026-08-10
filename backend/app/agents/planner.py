from app.tools.tool_request import ToolRequest

class Planner:
    
    def plan(
        self, 
        message: str,
        session_id: str,

    ) -> ToolRequest | None:
        
        message = message.lower()

        memory_keywords = [
            "history",
            "remember",
            "previous",
            "earlier",
        ]

        if any(
            keyword in message
            for keyword in memory_keywords
        ):

            return ToolRequest(
                tool_id="memory",
                session_id=session_id,
                input=message,
                context={
                    "operation": "retrieve"
                }
            )


        repository_keywords = [
            "code",
            "repository",
            "repo",
            "function",
            "class",
            "file",
            "architecture",
            "dependency",
            "import",
            "call",
        ]

        if any(
            keyword in message
            for keyword in repository_keywords
        ):

            return ToolRequest(
                tool_id="repository_context",
                session_id=session_id,
                input=message,
                context={}
            )

        return None

