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
            "planner",
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

            # Repository / development concepts
            "backend",
            "frontend",
            "api",
            "endpoint",
            "route",
            "database",
            "schema",
            "model",
            "service",
            "controller",
            "middleware",
            "dependency",
            "configuration",
            "config",
            "integration",
            "parser",
            "loader",
            "filter",
            "chunk",
            "chunker",
            "vectorstore",
            "retrieval",
            "rag",
            "context",
            "knowledge",
            "index",
            "cache",
            "session",
            "memory",
            "registry",
            "executor",
            "request",
            "response",
            "repositorycontext",

            # Code structure / behavior
            "variable",
            "constant",
            "attribute",
            "property",
            "parameter",
            "argument",
            "return",
            "logic",
            "workflow",
            "process",
            "behavior",
            "purpose",
            "role",
            "responsibility",
            "dependency",
            "relationship",
            "connection",
            "integration",
            "configuration",
            "implementation",
            "interaction",
            "communication",
        ]



        has_repository_keyword = any(
            keyword in message
            for keyword in repository_keywords
        )

        has_project_context = any(
            phrase in message
            for phrase in [
                "in this project",
                "in this codebase",
                "in the project",
                "in the codebase",
                "in our project",
                "in our code",
                "in this repository",
                "in the repository",
            ]
        )

        has_repository_question = any(
            phrase in message
            for phrase in [
                "how does",
                "what does",
                "why does",
                "where is",
                "how is",
                "purpose of",
                "role of",
            ]
        )

        if (
            has_project_context
            or (
                has_repository_keyword
                and has_repository_question
            )
        ):
            return ToolRequest(
                tool_id="repository_context",
                session_id=session_id,
                input=message,
                context={}
            )

        repository_specific_terms = [
            "memorymanager",
            "toolregistry",
            "devmindagent",
            "repositorycontext",
            "planner",
            "indexer",
            "retriever",
            "vectorstore",
            "incrementalindexmanager",
            "geminiclient",
            "toolregistry",
        ]

        has_repository_specific_term = any(
            term in message
            for term in repository_specific_terms
        )

        has_repository_question = any(
            phrase in message
            for phrase in [
                "how does",
                "what does",
                "why does",
                "where is",
                "how is",
                "explain",
                "purpose of",
                "role of",
            ]
        )

        has_what_is_question = (
            "what is" in message
            and has_repository_specific_term
        )

        if (
            has_project_context
            or (
                has_repository_keyword
                and has_repository_question
            )
            or has_what_is_question
        ):
            return ToolRequest(
                tool_id="repository_context",
                session_id=session_id,
                input=message,
                context={}
            )