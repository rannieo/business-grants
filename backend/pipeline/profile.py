import re
from dataclasses import dataclass


@dataclass
class ConversationProfile:
    employee_count: int | None = None
    local_entity: bool | None = None
    new_market: bool | None = None
    applicant_type: str | None = None
    revenue_band: str | None = None


class ConversationProfileExtractor:
    def extract(self, message: str, history: list[dict]) -> ConversationProfile:
        text = self._full_text(message, history).lower()
        return ConversationProfile(
            employee_count=self._extract_employee_count(text),
            local_entity=self._extract_local_entity(text),
            new_market=self._extract_new_market(text),
            applicant_type=self._extract_applicant_type(text),
            revenue_band=self._extract_revenue_band(text),
        )

    def _extract_employee_count(self, text: str) -> int | None:
        matches: list[tuple[int, int]] = []

        for m in re.finditer(r"\b(\d{1,5})\s*[–-]\s*(\d{1,5})\s*employees?\b", text):
            matches.append((m.start(), int(m.group(1))))

        for m in re.finditer(r"\b(\d{1,5})\+\s*employees?\b", text):
            matches.append((m.start(), int(m.group(1))))

        for m in re.finditer(r"(?<![-–])\b(\d{1,5})[\s-]*(?:employee|employees|staff|people|person|headcount|pax)\b", text):
            matches.append((m.start(), int(m.group(1))))

        for m in re.finditer(r"\bteam\s+of\s+(\d{1,5})\b", text):
            matches.append((m.start(), int(m.group(1))))

        if not matches:
            return None
        return max(matches, key=lambda x: x[0])[1]

    def _extract_local_entity(self, text: str) -> bool | None:
        return self._extract_bool_from_clauses(
            text,
            negatives=[
                "not based in singapore",
                "not registered in singapore",
                "outside singapore",
                "no, we are not based in singapore",
                "not a singapore company",
                "not in singapore",
            ],
            positives=[
                "registered in singapore",
                "based in singapore",
                "singapore company",
                "singapore business",
                "singapore startup",
                "yes, we are registered in singapore",
                "local entity",
                "singapore",
            ],
        )

    def _extract_new_market(self, text: str) -> bool | None:
        return self._extract_bool_from_clauses(
            text,
            negatives=[
                "not a new market",
                "not new market",
                "not first time",
                "already in this market",
                "already in the market",
                "existing market",
            ],
            positives=[
                "first time",
                "new market",
                "new overseas market",
                "entering a new market",
                "expand overseas",
                "overseas expansion",
            ],
        )

    def _extract_applicant_type(self, text: str) -> str | None:
        for clause in self._reverse_clauses(text):
            if any(token in clause for token in ["non-sme", "non_sme", "large enterprise", "mnc"]):
                return "non_sme"
            if any(token in clause for token in ["small medium enterprise", "small business", "startup", "sme"]):
                return "sme"
        return None

    def _extract_revenue_band(self, text: str) -> str | None:
        for clause in self._reverse_clauses(text):
            if any(token in clause for token in ["over 100m", "above 100m", ">100m", "more than 100m"]):
                return "over_100m"
            if any(token in clause for token in ["under 100m", "below 100m", "<100m", "less than 100m"]):
                return "under_100m"
        return None

    def _extract_bool_from_clauses(
        self,
        text: str,
        negatives: list[str],
        positives: list[str],
    ) -> bool | None:
        for clause in self._reverse_clauses(text):
            if any(token in clause for token in negatives):
                return False
            if any(token in clause for token in positives):
                return True
        return None

    def _reverse_clauses(self, text: str) -> list[str]:
        clauses = [c.strip() for c in re.split(r"[.!?\n;]", text) if c.strip()]
        clauses.reverse()
        return clauses

    def _full_text(self, message: str, history: list[dict]) -> str:
        past = " ".join(m["content"] for m in history if m["role"] == "user")
        return f"{past} {message}"
