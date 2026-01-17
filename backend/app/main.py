from fastapi import FastAPI
from app.api.chat import router

app = FastAPI(title="Humming Minds Bot")

app.include_router(router, prefix="/chat")

@app.get("/")
def health():
    return {"status": "running"}
