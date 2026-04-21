import json
import pytest
from pipeline.validator import Validator


@pytest.fixture
def v():
    return Validator()


# --- Valid question ---

def test_valid_question_response(v):
    raw = json.dumps({"type": "question", "question": "How many employees do you have?"})
    result = v.parse_and_validate(raw)
    assert result is not None
    assert result["type"] == "question"


# --- Valid recommendation ---

def test_valid_recommendation_response(v):
    raw = json.dumps({
        "type": "recommendation",
        "grants": [
            {
                "id": "mra",
                "name": "Market Readiness Assistance",
                "fit": "high",
                "reason": "You are entering a new market.",
                "cited": {"requires_new_market": True},
                "caveats": "Only for new markets.",
            }
        ],
        "tradeoffs": "MRA and EDG-NPD can be pursued together.",
    })
    result = v.parse_and_validate(raw)
    assert result is not None
    assert result["type"] == "recommendation"
    assert len(result["grants"]) == 1


# --- Markdown fence stripping ---

def test_strips_json_markdown_fence(v):
    inner = json.dumps({"type": "question", "question": "What is your goal?"})
    raw = f"```json\n{inner}\n```"
    result = v.parse_and_validate(raw)
    assert result is not None


def test_strips_plain_markdown_fence(v):
    inner = json.dumps({"type": "question", "question": "What is your goal?"})
    raw = f"```\n{inner}\n```"
    result = v.parse_and_validate(raw)
    assert result is not None


# --- Invalid cases ---

def test_invalid_json_returns_none(v):
    assert v.parse_and_validate("not json at all") is None


def test_empty_question_returns_none(v):
    raw = json.dumps({"type": "question", "question": ""})
    assert v.parse_and_validate(raw) is None


def test_missing_question_field_returns_none(v):
    raw = json.dumps({"type": "question"})
    assert v.parse_and_validate(raw) is None


def test_recommendation_with_no_grants_returns_none(v):
    raw = json.dumps({"type": "recommendation", "grants": []})
    assert v.parse_and_validate(raw) is None


def test_recommendation_missing_required_field_returns_none(v):
    raw = json.dumps({
        "type": "recommendation",
        "grants": [{"id": "mra", "name": "MRA", "fit": "high"}],  # missing reason + cited
    })
    assert v.parse_and_validate(raw) is None


def test_invalid_fit_value_returns_none(v):
    raw = json.dumps({
        "type": "recommendation",
        "grants": [
            {
                "id": "mra",
                "name": "MRA",
                "fit": "excellent",  # invalid
                "reason": "Good fit.",
                "cited": {},
                "caveats": "",
            }
        ],
    })
    assert v.parse_and_validate(raw) is None


def test_unknown_type_returns_none(v):
    raw = json.dumps({"type": "unknown"})
    assert v.parse_and_validate(raw) is None
