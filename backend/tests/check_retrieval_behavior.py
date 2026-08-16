from app.tools.repository_context_tool import RepositoryContextTool


def check_query(tool, query):
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    # Get the raw semantic results
    semantic_results = tool._retriever.semantic_retriever.retrieve(
        query=query,
        top_k=10,
    )

    print("\nSEMANTIC RESULTS:")
    for i, result in enumerate(semantic_results, 1):
        print(
            f"{i:2}. score={result.score:.4f} "
            f"path={result.chunk.path}"
        )

    # Get final IntelligentRetriever results
    final_results = tool._retriever.retrieve(
        query=query,
        top_k=5,
    )

    print("\nFINAL INTELLIGENT RESULTS:")
    for i, chunk in enumerate(final_results, 1):
        print(f"{i:2}. {chunk.path}")


def main():
    tool = RepositoryContextTool()

    queries = [
        "Where is ToolRegistry implemented?",
        "Where is the Planner implemented?",
        "How are embeddings created?",
        "How does repository context work?",
    ]

    for query in queries:
        check_query(tool, query)


if __name__ == "__main__":
    main()