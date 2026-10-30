from app.agents.planner import Planner


def test_project_questions_always_use_repository_context_when_project_active():
    planner = Planner()
    questions = [
        "What imports does useDevMind.js use?",
        "List the files responsible for indexing.",
        "Can you explain this?",
        "How are conversations stored?",
        "What is the purpose of the Planner?",
        "Show me the flow after I send a message.",
    ]

    for message in questions:
        request = planner.plan(
            message=message,
            session_id="test-session",
            project_id="project-123",
        )
        assert request is not None
        assert request.tool_id == "repository_context"
        assert request.input == message


def test_explicit_conversation_history_request_uses_memory():
    planner = Planner()
    request = planner.plan(
        message="What did we discuss earlier?",
        session_id="test-session",
        project_id="project-123",
    )
    assert request is not None
    assert request.tool_id == "memory"


def test_general_question_without_active_project_stays_general_chat():
    planner = Planner()
    request = planner.plan(
        message="What is FastAPI?",
        session_id="test-session",
    )
    assert request is None
