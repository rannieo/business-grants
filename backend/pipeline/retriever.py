class Retriever:
    def __init__(self, grants: list[dict]):
        self.grants = grants

    def retrieve(self, message: str, history: list[dict], k: int = 5) -> list[dict]:
        text = self._full_text(message, history).lower()
        scored = []

        for grant in self.grants:
            score = 0
            for goal in grant.get("business_goals", []):
                if goal.replace("_", " ") in text:
                    score += 3
            for phrase in grant.get("supports", []):
                if any(word in text for word in phrase.lower().split()):
                    score += 1
            scored.append((score, grant))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [g for _, g in scored[:k]]

    def _full_text(self, message: str, history: list[dict]) -> str:
        past = " ".join(m["content"] for m in history if m["role"] == "user")
        return f"{past} {message}"
