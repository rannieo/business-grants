import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from drivers.factory import build_driver_from_env
from services.matcher import GrantMatcherService

logger = logging.getLogger(__name__)

GRANTS_PATH = Path(__file__).parent.parent / "grants.json"
grants = json.loads(GRANTS_PATH.read_text())
service = GrantMatcherService(build_driver_from_env(), grants)

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
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to process chat request right now. Please try again.",
        )


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    service.clear(session_id)
    return {"ok": True}


@app.get("/api/grants")
async def list_grants():
    return grants
