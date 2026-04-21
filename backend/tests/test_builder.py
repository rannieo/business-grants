import json
import pytest
from pipeline.builder import PromptBuilder


@pytest.fixture
def builder():
    return PromptBuilder()


SAMPLE_GRANTS = [
    {
        "id": "mra",
        "name": "Market Readiness Assistance",
        "summary": "Supports overseas market entry.",
        "business_goals": ["overseas_expansion"],
        "notes": ["Best suited for companies entering a new overseas market."],
        "applicant_type": ["sme"],
        "employee_count_min": 1,
        "requires_new_market": True,
        "requires_local_entity": True,
        "revenue_band": ["under_100m"],
    }
]


def test_prompt_contains_grant_id(builder):
    prompt = builder.build(SAMPLE_GRANTS, [], "I want to expand overseas.")
    assert "mra" in prompt


def test_prompt_contains_grant_name(builder):
    prompt = builder.build(SAMPLE_GRANTS, [], "I want to expand overseas.")
    assert "Market Readiness Assistance" in prompt


def test_prompt_contains_user_message(builder):
    msg = "We want to expand into Malaysia for the first time."
    prompt = builder.build(SAMPLE_GRANTS, [], msg)
    assert msg in prompt


def test_prompt_contains_history(builder):
    history = [
        {"role": "user", "content": "We are a SG tech startup."},
        {"role": "assistant", "content": "What are your goals?"},
    ]
    prompt = builder.build(SAMPLE_GRANTS, history, "Expand overseas.")
    assert "We are a SG tech startup." in prompt


def test_prompt_contains_json_output_instruction(builder):
    prompt = builder.build(SAMPLE_GRANTS, [], "hi")
    assert "JSON" in prompt


def test_prompt_contains_recommendation_schema(builder):
    prompt = builder.build(SAMPLE_GRANTS, [], "hi")
    assert "recommendation" in prompt
    assert "question" in prompt


def test_empty_history_shows_no_prior_messages(builder):
    prompt = builder.build(SAMPLE_GRANTS, [], "hello")
    assert "no prior" in prompt.lower()
