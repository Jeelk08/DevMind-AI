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

def test_semantic_retrieval_results():
    tool = RepositoryContextTool()

    results = tool._retriever.semantic_retriever.retrieve(
        query="Where is ToolRegistry implemented?",
        top_k=10,
    )

    print("\n========== SEMANTIC RESULTS ==========")

    for result in results:
        print(
            f"score={result.score:.4f} "
            f"path={result.chunk.path}"
        )

    print("======================================")