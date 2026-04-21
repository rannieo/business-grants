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


def test_extracts_json_from_prose_wrapped_code_fence(v):
    inner = json.dumps({"type": "question", "question": "What is your goal?"})
    raw = f"I can help with that.\\n```json\\n{inner}\\n```\\nLet me know."
    result = v.parse_and_validate(raw)
    assert result is not None
    assert result["type"] == "question"


def test_extracts_first_balanced_json_object_from_mixed_text(v):
    raw = (
        "Here is the result you asked for:\\n"
        '{"type":"question","question":"How many employees do you have?"}'
        "\\nThanks!"
    )
    result = v.parse_and_validate(raw)
    assert result is not None
    assert result["question"] == "How many employees do you have?"


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
