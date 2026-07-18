from app.tools.tool_request import ToolRequest

class Planner:
    
    def plan(
        self, 
        message: str,
        session_id: str,

    ) -> ToolRequest | None:
        
        message = message.lower()

        keywords = [
            "history",
            "remember",
            "previous",
            "earlier",
        ]
        if any(keyword in message for keyword in keywords):

            return ToolRequest(
                tool_id="memory",
                session_id=session_id,
                input=message,
                context={
                    "operation": "retrieve"
                }
            ) 
    
        return None

