import json
from pathlib import Path

import pytest

from pipeline.eligibility import EligibilityGuard
from pipeline.profile import ConversationProfile


@pytest.fixture
def grants():
    path = Path(__file__).parent.parent.parent / "grants.json"
    return json.loads(path.read_text())


@pytest.fixture
def guard(grants):
    return EligibilityGuard(grants)


def test_keeps_recommendation_when_citation_and_eligibility_match(guard, grants):
    response = {
        "type": "recommendation",
        "grants": [
            {
                "id": "mra",
                "name": "Market Readiness Assistance",
                "fit": "high",
                "reason": "Strong fit.",
                "cited": {"requires_new_market": True},
                "caveats": "",
            }
        ],
        "tradeoffs": "",
    }
    profile = ConversationProfile(
        employee_count=12,
        local_entity=True,
        new_market=True,
        applicant_type="sme",
        revenue_band="under_100m",
    )

    decision = guard.enforce(response, profile, grants)
    assert decision.response is not None
    assert len(decision.response["grants"]) == 1


def test_drops_recommendation_when_cited_key_is_invalid(guard, grants):
    response = {
        "type": "recommendation",
        "grants": [
            {
                "id": "mra",
                "name": "Market Readiness Assistance",
                "fit": "high",
                "reason": "Strong fit.",
                "cited": {"not_a_real_field": True},
                "caveats": "",
            }
        ],
        "tradeoffs": "",
    }
    profile = ConversationProfile(
        employee_count=12,
        local_entity=True,
        new_market=True,
        applicant_type="sme",
        revenue_band="under_100m",
    )

    decision = guard.enforce(response, profile, grants)
    assert decision.response is None
    assert decision.missing_signal is None


def test_marks_grant_hard_ineligible_for_employee_floor(guard, grants):
    ctc = next(g for g in grants if g["id"] == "ctc")
    profile = ConversationProfile(
        employee_count=10,
        local_entity=True,
        new_market=False,
        applicant_type="sme",
        revenue_band="under_100m",
    )

    assessment = guard.assess_grant(ctc, profile)
    assert assessment.eligible is False
    assert assessment.hard_ineligible is True


def test_returns_missing_signal_when_only_unknown_blockers_remain(guard, grants):
    response = {
        "type": "recommendation",
        "grants": [
            {
                "id": "mra",
                "name": "Market Readiness Assistance",
                "fit": "high",
                "reason": "Strong fit.",
                "cited": {"requires_new_market": True},
                "caveats": "",
            }
        ],
        "tradeoffs": "",
    }
    profile = ConversationProfile(
        employee_count=12,
        local_entity=None,
        new_market=True,
        applicant_type="sme",
        revenue_band="under_100m",
    )

    decision = guard.enforce(response, profile, grants)
    assert decision.response is None
    assert decision.missing_signal == "local_entity"


def test_missing_signal_prioritizes_highest_impact(guard):
    grants = [
        {
            "id": "g1",
            "requires_local_entity": True,
            "requires_new_market": False,
            "employee_count_min": 1,
            "employee_count_max": None,
            "applicant_type": ["sme"],
            "revenue_band": ["under_100m"],
        },
        {
            "id": "g2",
            "requires_local_entity": True,
            "requires_new_market": False,
            "employee_count_min": 1,
            "employee_count_max": None,
            "applicant_type": ["sme"],
            "revenue_band": ["under_100m"],
        },
        {
            "id": "g3",
            "requires_local_entity": False,
            "requires_new_market": True,
            "employee_count_min": 1,
            "employee_count_max": None,
            "applicant_type": ["sme"],
            "revenue_band": ["under_100m"],
        },
    ]
    profile = ConversationProfile(
        employee_count=10,
        local_entity=None,
        new_market=None,
        applicant_type="sme",
        revenue_band="under_100m",
    )

    assert guard.missing_signal_when_no_eligible(grants, profile) == "local_entity"
