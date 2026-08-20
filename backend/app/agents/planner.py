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
            "codebase",
            "repository",
            "repo",
            "project",
            "function",
            "class",
            "method",
            "module",
            "file",
            "component",
            "service",
            "agent",
            "tool",
            "architecture",
            "implementation",
            "implemented",
            "import",
            "call",
            "pipeline",
            "retriever",
            "indexer",
            "embedding",
            "vector",
            "memorymanager",
            "toolregistry",
            "devmindagent",
        ]

        project_context_phrases = [
            "in this project",
            "in this codebase",
            "in the project",
            "in the codebase",
            "in our project",
            "in our code",
            "in this repository",
            "in the repository",
            "how does",
            "where is",
            "how is",
            "explain how",
        ]


        if (
            any(keyword in message for keyword in repository_keywords)
            or any(phrase in message for phrase in project_context_phrases)
        ):
            return ToolRequest(
                tool_id="repository_context",
                session_id=session_id,
                input=message,
                context={}
            )