from fastapi import FastAPI

from app.routes.chat_routes import router
from app.routes.project_routes import router as project_router
from app.routes.context_routes import router as context_router

from app.tools.repository_context_tool import (
    RepositoryContextTool,
)

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="DevMind AI")


repository_context_tool = RepositoryContextTool()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(context_router)
app.include_router(project_router)