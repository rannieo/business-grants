import pytest
from fastapi import HTTPException

import app as api_app


class BrokenService:
    async def chat(self, session_id: str, user_message: str):
        raise RuntimeError("sensitive internal error detail")

    def clear(self, session_id: str):
        return None


@pytest.mark.asyncio
async def test_chat_error_response_is_sanitized(monkeypatch):
    monkeypatch.setattr(api_app, "service", BrokenService())

    with pytest.raises(HTTPException) as exc:
        await api_app.chat(api_app.ChatRequest(session_id="s1", message="hello"))

    assert exc.value.status_code == 500
    assert exc.value.detail == "Unable to process chat request right now. Please try again."
    assert "sensitive" not in str(exc.value.detail)
