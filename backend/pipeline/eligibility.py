from collections import defaultdict
from dataclasses import dataclass, field

from .profile import ConversationProfile


PRIORITY = {
    "local_entity": 0,
    "employee_count": 1,
    "new_market": 2,
    "applicant_type": 3,
    "revenue_band": 4,
}


@dataclass
class GrantAssessment:
    eligible: bool
    hard_ineligible: bool
    missing_signals: set[str] = field(default_factory=set)


@dataclass
class GuardDecision:
    response: dict | None
    missing_signal: str | None = None


class EligibilityGuard:
    def __init__(self, grants: list[dict]):
        self._grants_by_id = {g["id"]: g for g in grants if "id" in g}

    def enforce(
        self,
        response: dict,
        profile: ConversationProfile,
        candidate_grants: list[dict],
    ) -> GuardDecision:
        if response.get("type") != "recommendation":
            return GuardDecision(response=response)

        filtered: list[dict] = []
        for rec in response.get("grants", []):
            grant_id = rec.get("id")
            grant = self._grants_by_id.get(grant_id)
            if grant is None:
                continue
            if not self._cited_matches(rec.get("cited"), grant):
                continue
            assessment = self.assess_grant(grant, profile)
            if assessment.eligible:
                filtered.append(rec)

        if filtered:
            safe_response = dict(response)
            safe_response["grants"] = filtered
            return GuardDecision(response=safe_response)

        return GuardDecision(
            response=None,
            missing_signal=self.missing_signal_when_no_eligible(candidate_grants, profile),
        )

    def missing_signal_when_no_eligible(
        self,
        grants: list[dict],
        profile: ConversationProfile,
    ) -> str | None:
        if any(self.assess_grant(grant, profile).eligible for grant in grants):
            return None

        counts: dict[str, int] = defaultdict(int)
        for grant in grants:
            assessment = self.assess_grant(grant, profile)
            if assessment.hard_ineligible:
                continue
            for signal in assessment.missing_signals:
                counts[signal] += 1

        if not counts:
            return None

        return min(
            counts.items(),
            key=lambda item: (-item[1], PRIORITY.get(item[0], 999)),
        )[0]

    def assess_grant(self, grant: dict, profile: ConversationProfile) -> GrantAssessment:
        missing: set[str] = set()

        if grant.get("requires_local_entity"):
            if profile.local_entity is None:
                missing.add("local_entity")
            elif not profile.local_entity:
                return GrantAssessment(eligible=False, hard_ineligible=True)

        if grant.get("requires_new_market"):
            if profile.new_market is None:
                missing.add("new_market")
            elif not profile.new_market:
                return GrantAssessment(eligible=False, hard_ineligible=True)

        min_count = grant.get("employee_count_min")
        if min_count is not None:
            if profile.employee_count is None:
                missing.add("employee_count")
            elif profile.employee_count < min_count:
                return GrantAssessment(eligible=False, hard_ineligible=True)

        max_count = grant.get("employee_count_max")
        if max_count is not None and profile.employee_count is not None and profile.employee_count > max_count:
            return GrantAssessment(eligible=False, hard_ineligible=True)

        applicant_type = grant.get("applicant_type") or []
        if applicant_type and "any" not in applicant_type:
            if not {"sme", "non_sme"}.issubset(set(applicant_type)):
                if profile.applicant_type is None:
                    missing.add("applicant_type")
                elif profile.applicant_type not in applicant_type:
                    return GrantAssessment(eligible=False, hard_ineligible=True)

        revenue_band = grant.get("revenue_band") or []
        if revenue_band and "any" not in revenue_band:
            if profile.revenue_band is None:
                missing.add("revenue_band")
            elif profile.revenue_band not in revenue_band:
                return GrantAssessment(eligible=False, hard_ineligible=True)

        if missing:
            return GrantAssessment(eligible=False, hard_ineligible=False, missing_signals=missing)

        return GrantAssessment(eligible=True, hard_ineligible=False)

    def _cited_matches(self, cited: dict | None, grant: dict) -> bool:
        if not isinstance(cited, dict) or not cited:
            return False
        for key, cited_value in cited.items():
            if key not in grant:
                return False
            if not self._value_matches(grant[key], cited_value):
                return False
        return True

    def _value_matches(self, expected, actual) -> bool:
        if isinstance(expected, list):
            if isinstance(actual, list):
                expected_set = {str(v).lower() for v in expected}
                actual_set = {str(v).lower() for v in actual}
                return actual_set.issubset(expected_set)
            return str(actual).lower() in {str(v).lower() for v in expected}

        if isinstance(expected, bool):
            if isinstance(actual, bool):
                return actual is expected
            if isinstance(actual, str):
                normalized = actual.strip().lower()
                if normalized in {"true", "false"}:
                    return (normalized == "true") is expected
            return False

        if isinstance(expected, int):
            if isinstance(actual, int):
                return actual == expected
            if isinstance(actual, str) and actual.isdigit():
                return int(actual) == expected
            return False

        if expected is None:
            return actual is None

        return str(actual).strip().lower() == str(expected).strip().lower()
