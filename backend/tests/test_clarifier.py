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


def test_for_vague_includes_options(clarifier):
    result = clarifier.for_vague()
    assert "options" in result
    assert len(result["options"]) > 0
    assert all(isinstance(o, str) for o in result["options"])


def test_for_missing_goal_asks_about_goal(clarifier):
    result = clarifier.for_missing(["business_goal"])
    assert result is not None
    assert result["type"] == "question"
    assert "achieve" in result["question"].lower() or "goal" in result["question"].lower()


def test_for_missing_goal_includes_options(clarifier):
    result = clarifier.for_missing(["business_goal"])
    assert "options" in result
    assert len(result["options"]) > 0


def test_for_missing_employee_count_asks_about_size(clarifier):
    result = clarifier.for_missing(["employee_count"])
    assert result is not None
    assert result["type"] == "question"
    assert "employee" in result["question"].lower() or "staff" in result["question"].lower()


def test_for_missing_employee_count_includes_options(clarifier):
    result = clarifier.for_missing(["employee_count"])
    assert "options" in result
    assert any("employee" in o.lower() for o in result["options"])


def test_for_missing_local_entity_asks_about_singapore(clarifier):
    result = clarifier.for_missing(["local_entity"])
    assert result is not None
    assert result["type"] == "question"
    assert "singapore" in result["question"].lower() or "registered" in result["question"].lower()


def test_for_missing_local_entity_includes_yes_no_options(clarifier):
    result = clarifier.for_missing(["local_entity"])
    assert "options" in result
    assert len(result["options"]) == 2


def test_for_missing_prioritises_goal_over_size(clarifier):
    result = clarifier.for_missing(["employee_count", "business_goal"])
    assert result is not None
    assert "achieve" in result["question"].lower() or "goal" in result["question"].lower()


def test_for_missing_empty_list_returns_none(clarifier):
    assert clarifier.for_missing([]) is None


def test_for_missing_unknown_fields_returns_none(clarifier):
    assert clarifier.for_missing(["revenue", "sector"]) is None


def test_for_missing_new_market_returns_targeted_question(clarifier):
    result = clarifier.for_missing(["new_market"])
    assert result is not None
    assert result["type"] == "question"
    assert "first time" in result["question"].lower()


def test_for_missing_applicant_type_returns_targeted_question(clarifier):
    result = clarifier.for_missing(["applicant_type"])
    assert result is not None
    assert any("sme" in o.lower() for o in result["options"])


def test_for_missing_revenue_band_returns_targeted_question(clarifier):
    result = clarifier.for_missing(["revenue_band"])
    assert result is not None
    assert "100m" in result["question"].lower()
