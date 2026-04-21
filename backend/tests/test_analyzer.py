import pytest
from pipeline.analyzer import QueryAnalyzer, QueryClass


@pytest.fixture
def analyzer():
    return QueryAnalyzer()


# --- VAGUE ---

def test_short_message_is_vague(analyzer):
    assert analyzer.analyze("hi", []) == QueryClass.VAGUE


def test_greeting_is_vague(analyzer):
    assert analyzer.analyze("hello there", []) == QueryClass.VAGUE


def test_generic_question_is_vague(analyzer):
    assert analyzer.analyze("what grants are available", []) == QueryClass.VAGUE


# --- CLEAR ---

def test_goal_plus_business_context_is_clear(analyzer):
    msg = "We're a 12-person Singapore software company building an AI invoice tool and want to expand overseas."
    assert analyzer.analyze(msg, []) == QueryClass.CLEAR


def test_hire_with_company_reference_is_clear(analyzer):
    msg = "Our startup wants to hire 2 engineers and build a new digital product."
    assert analyzer.analyze(msg, []) == QueryClass.CLEAR


def test_automation_with_business_context_is_clear(analyzer):
    msg = "Our business wants to automate our manual invoice processing."
    assert analyzer.analyze(msg, []) == QueryClass.CLEAR


# --- BORDERLINE ---

def test_goal_without_business_context_is_borderline(analyzer):
    msg = "Looking to expand overseas to Malaysia and maybe hire some people."
    assert analyzer.analyze(msg, []) == QueryClass.BORDERLINE


def test_business_context_without_goal_is_borderline(analyzer):
    msg = "We are a small firm with 10 employees based in Singapore."
    assert analyzer.analyze(msg, []) == QueryClass.BORDERLINE


# --- HISTORY ACCUMULATION ---

def test_uses_history_to_upgrade_borderline_to_clear(analyzer):
    history = [
        {"role": "user", "content": "Our company is a Singapore tech startup."},
        {"role": "assistant", "content": "What are you looking to achieve?"},
    ]
    msg = "We want to expand overseas into Malaysia."
    assert analyzer.analyze(msg, history) == QueryClass.CLEAR


# --- MISSING FIELDS ---

def test_missing_employee_count_detected(analyzer):
    msg = "We are a Singapore company wanting to expand overseas."
    missing = analyzer.missing_fields(msg, [])
    assert "employee_count" in missing


def test_missing_goal_detected(analyzer):
    msg = "We are a 15-person company in Singapore."
    missing = analyzer.missing_fields(msg, [])
    assert "business_goal" in missing


def test_missing_local_entity_detected(analyzer):
    msg = "We have 10 staff and want to automate our processes."
    missing = analyzer.missing_fields(msg, [])
    assert "local_entity" in missing


def test_no_missing_fields_when_all_present(analyzer):
    msg = "We are a 12-person Singapore company and want to expand overseas to Malaysia."
    missing = analyzer.missing_fields(msg, [])
    assert "local_entity" not in missing
    assert "business_goal" not in missing
