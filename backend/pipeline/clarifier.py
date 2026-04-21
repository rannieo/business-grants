VAGUE_QUESTION = (
    "To find the right grants for you, could you tell me about your business? "
    "For example: what industry you're in, how many employees you have, "
    "and what you're trying to achieve — such as expanding overseas, automating operations, "
    "hiring new staff, or building a new product."
)

MISSING_FIELD_QUESTIONS = {
    "business_goal": (
        "What's the main thing you're trying to achieve? "
        "(e.g. expand to a new market, automate processes, develop a new product, hire and train staff)"
    ),
    "employee_count": "How many employees does your company currently have?",
    "local_entity": "Is your company registered and operating in Singapore?",
}


class Clarifier:
    def for_vague(self) -> dict:
        return {"type": "question", "question": VAGUE_QUESTION}

    def for_missing(self, missing_fields: list[str]) -> dict | None:
        for field in ["business_goal", "employee_count", "local_entity"]:
            if field in missing_fields:
                return {"type": "question", "question": MISSING_FIELD_QUESTIONS[field]}
        return None
