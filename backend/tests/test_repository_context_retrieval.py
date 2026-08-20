from pathlib import Path
from app.tools.repository_context_tool import RepositoryContextTool
from app.tools.tool_request import ToolRequest

# def test_repository_context_finds_tool_registry():
#     tool = RepositoryContextTool()

#     request = ToolRequest(
#     tool_id="repository_context",
#     input="Where is ToolRegistry implemented?",
#     session_id="test-session",
#     )

#     response = tool.execute(request)

#     print("\n========== RETRIEVAL RESULT ==========")
#     print(response.result)
#     print("======================================")

#     assert response.error is None
#     assert response.result

#     context = response.result[0]["content"]

#     assert "app/tools/tool_registry.py" in context
def test_intelligent_retrieval_results():
    tool = RepositoryContextTool()

    results = tool._retriever.retrieve(
        query="Explain DevMindAgent.",
        top_k=5,
    )

    print("\n========== INTELLIGENT RESULTS ==========")

    for i, result in enumerate(results, start=1):
        print(
            f"\nResult {i}"
        )
        print(f"Path: {result.path}")
        print(f"Content:\n{result.content}")

    print("\n==========================================")