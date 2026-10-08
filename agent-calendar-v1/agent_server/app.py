"""A deliberately bare, stateless browser chat UI and its one API route."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent_server.agent import answer

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Calendar Assistant")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/chat")
async def chat(payload: ChatRequest, request: Request) -> dict[str, str]:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")
    return {
        "response": await answer(
            payload.message, request.headers.get("x-forwarded-access-token")
        )
    }


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
