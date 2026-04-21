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

VAGUE_OPTIONS = [
    "We want to expand into a new overseas market",
    "We're building a new product or solution",
    "We want to automate our operations",
    "We need to hire and reskill staff",
    "We want to build digital capabilities",
    "We need a certification or standard",
]

MISSING_FIELD_OPTIONS = {
    "business_goal": [
        "Expand into a new overseas market",
        "Build a new product or solution",
        "Automate or improve our processes",
        "Hire and reskill our team",
        "Build digital capabilities",
        "Achieve a certification or standard",
    ],
    "employee_count": [
        "1–10 employees",
        "11–30 employees",
        "31–100 employees",
        "100+ employees",
    ],
    "local_entity": [
        "Yes, we are registered in Singapore",
        "No, we are not based in Singapore",
    ],
}


class Clarifier:
    def for_vague(self) -> dict:
        return {
            "type": "question",
            "question": VAGUE_QUESTION,
            "options": VAGUE_OPTIONS,
        }

    def for_missing(self, missing_fields: list[str]) -> dict | None:
        for field in ["business_goal", "employee_count", "local_entity"]:
            if field in missing_fields:
                return {
                    "type": "question",
                    "question": MISSING_FIELD_QUESTIONS[field],
                    "options": MISSING_FIELD_OPTIONS[field],
                }
        return None
