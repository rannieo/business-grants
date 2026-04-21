import pytest
from pipeline.clarifier import Clarifier


@pytest.fixture
def clarifier():
    return Clarifier()


def test_for_vague_returns_question_type(clarifier):
    result = clarifier.for_vague()
    assert result["type"] == "question"
    assert isinstance(result["question"], str)
    assert len(result["question"]) > 0


def test_for_missing_goal_asks_about_goal(clarifier):
    result = clarifier.for_missing(["business_goal"])
    assert result is not None
    assert result["type"] == "question"
    assert "achieve" in result["question"].lower() or "goal" in result["question"].lower()


def test_for_missing_employee_count_asks_about_size(clarifier):
    result = clarifier.for_missing(["employee_count"])
    assert result is not None
    assert result["type"] == "question"
    assert "employee" in result["question"].lower() or "staff" in result["question"].lower()


def test_for_missing_local_entity_asks_about_singapore(clarifier):
    result = clarifier.for_missing(["local_entity"])
    assert result is not None
    assert result["type"] == "question"
    assert "singapore" in result["question"].lower() or "registered" in result["question"].lower()


def test_for_missing_prioritises_goal_over_size(clarifier):
    result = clarifier.for_missing(["employee_count", "business_goal"])
    assert result is not None
    # business_goal is the most impactful missing field
    assert "achieve" in result["question"].lower() or "goal" in result["question"].lower()


def test_for_missing_empty_list_returns_none(clarifier):
    assert clarifier.for_missing([]) is None


def test_for_missing_unknown_fields_returns_none(clarifier):
    assert clarifier.for_missing(["revenue", "sector"]) is None
