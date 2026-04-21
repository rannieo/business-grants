import json
import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock

from services.matcher import GrantMatcherService
from drivers.base import LLMDriver


@pytest.fixture
def grants():
    path = Path(__file__).parent.parent.parent / "grants.json"
    return json.loads(path.read_text())


def make_service(grants, llm_response: str = None) -> GrantMatcherService:
    """Return a GrantMatcherService with a mocked LLM driver."""
    mock_driver = AsyncMock(spec=LLMDriver)
    if llm_response is not None:
        mock_driver.complete.return_value = llm_response
    return GrantMatcherService(mock_driver, grants)


# --- Vague query: no LLM call ---

@pytest.mark.asyncio
async def test_vague_query_returns_question_without_llm(grants):
    service = make_service(grants)
    result = await service.chat("session-1", "hi")
    assert result["type"] == "question"
    service.driver.complete.assert_not_called()


@pytest.mark.asyncio
async def test_short_message_returns_clarification(grants):
    service = make_service(grants)
    result = await service.chat("s1", "help me")
    assert result["type"] == "question"
    service.driver.complete.assert_not_called()


# --- Borderline query: targeted clarification, no LLM ---

@pytest.mark.asyncio
async def test_borderline_returns_question_without_llm(grants):
    service = make_service(grants)
    result = await service.chat("s2", "We are a small Singapore firm.")
    assert result["type"] == "question"
    service.driver.complete.assert_not_called()


# --- Clear query: LLM is called ---

@pytest.mark.asyncio
async def test_clear_query_calls_llm(grants):
    llm_resp = json.dumps({
        "type": "recommendation",
        "grants": [{
            "id": "mra", "name": "Market Readiness Assistance",
            "fit": "high", "reason": "New market entry.",
            "cited": {"requires_new_market": True}, "caveats": "",
        }],
        "tradeoffs": "",
    })
    service = make_service(grants, llm_resp)
    result = await service.chat(
        "s3",
        "We are a 12-person Singapore SME software company with annual revenue under 100M wanting to expand overseas to Malaysia for the first time."
    )
    assert result["type"] == "recommendation"
    service.driver.complete.assert_called_once()


# --- History accumulation ---

@pytest.mark.asyncio
async def test_history_accumulates_across_turns(grants):
    llm_resp = json.dumps({
        "type": "recommendation",
        "grants": [{
            "id": "edg_npd", "name": "EDG NPD",
            "fit": "high", "reason": "New product.",
            "cited": {"business_goals": ["new_product_development"]}, "caveats": "",
        }],
        "tradeoffs": "",
    })
    service = make_service(grants, llm_resp)

    # First turn: borderline (no LLM)
    await service.chat("s4", "We are a Singapore startup.")

    # Second turn: clear after context
    await service.chat("s4", "We want to build a new product and hire engineers.")

    # History for session should have 4 entries (2 turns × 2 messages)
    history = service._sessions["s4"]
    assert len(history) == 4


# --- Clear session ---

@pytest.mark.asyncio
async def test_clear_resets_session(grants):
    service = make_service(grants)
    await service.chat("s5", "hi")
    service.clear("s5")
    assert "s5" not in service._sessions


# --- Validator retry ---

@pytest.mark.asyncio
async def test_invalid_llm_response_retries_once(grants):
    mock_driver = AsyncMock(spec=LLMDriver)
    # First call returns garbage, second returns valid JSON
    valid = json.dumps({
        "type": "recommendation",
        "grants": [{
            "id": "mra", "name": "Market Readiness Assistance", "fit": "high",
            "reason": "Good fit.", "cited": {"requires_new_market": True}, "caveats": "",
        }],
        "tradeoffs": "",
    })
    mock_driver.complete.side_effect = ["not json", valid]
    service = GrantMatcherService(mock_driver, grants)

    result = await service.chat(
        "s6",
        "We are a 15-person Singapore SME company with annual revenue under 100M and this is our first time expanding overseas."
    )
    assert result["type"] == "recommendation"
    assert mock_driver.complete.call_count == 2


@pytest.mark.asyncio
async def test_no_eligible_recommendations_returns_missing_signal_question(grants):
    llm_resp = json.dumps({
        "type": "recommendation",
        "grants": [{
            "id": "mra", "name": "Market Readiness Assistance",
            "fit": "high", "reason": "New market entry.",
            "cited": {"requires_new_market": True}, "caveats": "",
        }],
        "tradeoffs": "",
    })
    service = make_service(grants, llm_resp)
    result = await service.chat(
        "s8",
        "We are a 12-person Singapore company wanting to expand overseas."
    )
    assert result["type"] == "question"
    assert "SME" in " ".join(result.get("options", [])) or "revenue" in result["question"].lower()


@pytest.mark.asyncio
async def test_two_invalid_responses_returns_clarification(grants):
    mock_driver = AsyncMock(spec=LLMDriver)
    mock_driver.complete.return_value = "not json at all"
    service = GrantMatcherService(mock_driver, grants)

    result = await service.chat(
        "s7",
        "We are a 10-person Singapore SME company with annual revenue under 100M and this is our first time expanding overseas."
    )

    assert result["type"] == "question"
    assert "one more detail" in result["question"].lower() or "could you share" in result["question"].lower()
    assert mock_driver.complete.call_count == 2
