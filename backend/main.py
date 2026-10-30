
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat_routes import router
from app.routes.project_routes import router as project_router
from app.routes.context_routes import router as context_router
from app.routes.upload_routes import router as upload_router
from app.routes.folder_import_routes import router as folder_import_router


app = FastAPI(title="DevMind AI")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://devmind-ai-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(context_router)
app.include_router(folder_import_router)
app.include_router(project_router)
app.include_router(upload_router)
