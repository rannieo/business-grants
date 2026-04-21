import json

SYSTEM_INSTRUCTIONS = """You are a grant advisor for Singapore-based businesses.

Respond ONLY with valid JSON — no markdown fences, no prose outside the JSON.

If you need ONE more piece of information to make a confident recommendation:
{"type": "question", "question": "<one targeted question>"}

If you have enough information:
{
  "type": "recommendation",
  "grants": [
    {
      "id": "<grant id>",
      "name": "<grant name>",
      "fit": "high" | "medium" | "low",
      "reason": "<natural language explanation>",
      "cited": {"<field>": "<value from database>"},
      "caveats": "<conditions or warnings>"
    }
  ],
  "tradeoffs": "<explanation when grants overlap>"
}

Rules:
1. Ask at most ONE question — the one whose answer most changes your recommendation.
2. Only recommend grants the business qualifies for (check employee_count_min, revenue_band, applicant_type, requires_local_entity, requires_new_market).
3. Always cite specific field(s) from the grants data in the "cited" block.
4. Explain tradeoffs when multiple grants overlap.
5. Never invent grant details not present in the provided data.
"""


class PromptBuilder:
    def build(self, grants: list[dict], history: list[dict], user_message: str) -> str:
        grants_block = json.dumps(grants, indent=2)
        history_block = self._format_history(history)

        return (
            f"{SYSTEM_INSTRUCTIONS}\n\n"
            f"GRANTS DATA (retrieved, relevant subset):\n{grants_block}\n\n"
            f"CONVERSATION SO FAR:\n{history_block}\n\n"
            f"USER:\n{user_message}"
        )

    def _format_history(self, history: list[dict]) -> str:
        if not history:
            return "(no prior messages)"
        lines = []
        for msg in history:
            role = "USER" if msg["role"] == "user" else "AGENT"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
