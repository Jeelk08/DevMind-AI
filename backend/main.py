from fastapi import FastAPI

app = FastAPI(
    title="DevMind AI API"
)

@app.get("/")
def home():
    return {
        "message": "DevMind AI backend running 🚀"
    }