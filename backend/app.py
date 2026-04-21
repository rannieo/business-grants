import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from drivers.claude_cli import ClaudeCLIDriver
from services.matcher import GrantMatcherService

GRANTS_PATH = Path(__file__).parent.parent / "grants.json"
grants = json.loads(GRANTS_PATH.read_text())
service = GrantMatcherService(ClaudeCLIDriver(), grants)

app = FastAPI(title="Grant Recommender API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        return await service.chat(req.session_id, req.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    service.clear(session_id)
    return {"ok": True}


@app.get("/api/grants")
async def list_grants():
    return grants
