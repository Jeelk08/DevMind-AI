from fastapi import APIRouter, HTTPException

from app.models.context import (
    ContextRequest,
    ContextResponse,
    ContextSource,
)

from app.core.dependencies import (
    get_repository_context_tool,
)


router = APIRouter()


@router.post(
    "/context",
    response_model=ContextResponse,
)
def retrieve_context(
    request: ContextRequest,
):
    try:

        context_tool = (
            get_repository_context_tool(
                request.project_id
            )
        )

        results = (
            context_tool.retrieve_chunks(
                query=request.query,
                top_k=5,
            )
        )

        sources = []

        for index, (
            chunk,
            relevance,
        ) in enumerate(
            results
        ):
            file_path = str(chunk.path)
            file_name = chunk.path.name

            sources.append(
                ContextSource(
                    id=index + 1,
                    file_name=file_name,
                    file_path=file_path,
                    relevance=relevance,
                    content=chunk.content,
                )
            )

        return ContextResponse(
            query=request.query,
            sources=sources,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )