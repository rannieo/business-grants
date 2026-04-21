import re
from enum import Enum


class QueryClass(Enum):
    VAGUE = "vague"
    BORDERLINE = "borderline"
    CLEAR = "clear"


GOAL_KEYWORDS = [
    "expand", "overseas", "market", "automate", "automation",
    "hire", "hiring", "product", "develop", "innovation", "r&d",
    "training", "reskill", "digital", "certification", "compliance",
    "transform", "new market", "export",
]

SIZE_PATTERNS = [
    r"\d+[\s-]*(?:employee|staff|people|person|headcount|pax)",
    r"(?:small|medium|large)\s+(?:company|business|team|firm)",
    r"team\s+of\s+\d+",
]

BUSINESS_CONTEXT_WORDS = [
    "company", "business", "startup", "firm", "we are", "we're",
    "our", "sme", "enterprise",
]


class QueryAnalyzer:
    def analyze(self, message: str, history: list[dict]) -> QueryClass:
        text = self._full_text(message, history).lower()
        word_count = len(message.split())

        if word_count < 6:
            return QueryClass.VAGUE

        has_goal = any(kw in text for kw in GOAL_KEYWORDS)
        has_context = any(kw in text for kw in BUSINESS_CONTEXT_WORDS)

        if has_goal and has_context:
            return QueryClass.CLEAR
        if has_goal or has_context:
            return QueryClass.BORDERLINE
        return QueryClass.VAGUE

    def missing_fields(self, message: str, history: list[dict]) -> list[str]:
        text = self._full_text(message, history).lower()
        missing = []
        if not any(re.search(p, text) for p in SIZE_PATTERNS):
            missing.append("employee_count")
        if not any(kw in text for kw in GOAL_KEYWORDS):
            missing.append("business_goal")
        if "singapore" not in text and " sg " not in text and "local" not in text:
            missing.append("local_entity")
        return missing

    def _full_text(self, message: str, history: list[dict]) -> str:
        past = " ".join(m["content"] for m in history if m["role"] == "user")
        return f"{past} {message}"
