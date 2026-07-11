from fastapi import FastAPI
from app.routes.chat_routes import router

app = FastAPI(title = "DevMind AI")

app.include_router(router)
