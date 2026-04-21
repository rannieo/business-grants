import re
from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _grant_document(grant: dict) -> str:
    parts = [
        grant.get("name", ""),
        grant.get("summary", ""),
        # business goals — underscore → space so "overseas_expansion" → "overseas expansion"
        " ".join(g.replace("_", " ") for g in grant.get("business_goals", [])),
        " ".join(grant.get("supports", [])),
        " ".join(grant.get("notes", [])),
        # applicant type — "sme" stays as "sme", "non_sme" → "non sme large enterprise"
        " ".join(
            "sme small medium enterprise" if t == "sme" else "non sme large enterprise"
            for t in grant.get("applicant_type", [])
        ),
        # eligibility signals as readable text so queries can match them
        "first time new market overseas entry" if grant.get("requires_new_market") else "",
        "singapore registered local entity" if grant.get("requires_local_entity") else "",
        # revenue band
        "under 100 million revenue" if "under_100m" in grant.get("revenue_band", []) else "",
        # employee floor as a searchable phrase
        f"minimum {grant['employee_count_min']} employees staff headcount"
        if grant.get("employee_count_min") else "",
    ]
    return " ".join(p for p in parts if p)


class Retriever:
    def __init__(self, grants: list[dict]):
        self.grants = grants
        corpus = [_tokenize(_grant_document(g)) for g in grants]
        self._bm25 = BM25Okapi(corpus)

    def retrieve(self, message: str, history: list[dict], k: int = 5) -> list[dict]:
        query = _tokenize(self._full_text(message, history))
        scores = self._bm25.get_scores(query)
        ranked = sorted(range(len(self.grants)), key=lambda i: scores[i], reverse=True)
        return [self.grants[i] for i in ranked[:k]]

    def _full_text(self, message: str, history: list[dict]) -> str:
        past = " ".join(m["content"] for m in history if m["role"] == "user")
        return f"{past} {message}"
