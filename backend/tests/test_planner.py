from app.agents.planner import Planner


def test_planner_intent_detection():

    planner = Planner()

    test_cases = [
        ("Explain how DevMindAgent works in this project.", "repository_context"),
        ("What is MemoryManager?", "repository_context"),
        ("Where is ToolRegistry implemented?", "repository_context"),
        ("Explain the RAG pipeline in this codebase.", "repository_context"),
        ("How does the project store conversations?", "repository_context"),
        ("What is dependency injection?", None),
        ("What is FastAPI?", None),
        ("What did we discuss earlier?", "memory"),
    ]

    for message, expected_tool in test_cases:

        request = planner.plan(
            message=message,
            session_id="test-session",
        )

        actual_tool = request.tool_id if request else None

        print(
            f"\nQuestion: {message}"
            f"\nExpected: {expected_tool}"
            f"\nActual:   {actual_tool}"
        )

        assert actual_tool == expected_tool