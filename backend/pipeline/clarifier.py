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
    "new_market": "Is this your first time entering that overseas market?",
    "applicant_type": "Would you classify your company as an SME or non-SME/large enterprise?",
    "revenue_band": "Is your company's annual revenue under SGD 100M?",
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
    "new_market": [
        "Yes, this is our first time entering that market",
        "No, we already operate in that market",
    ],
    "applicant_type": [
        "We are an SME",
        "We are a non-SME / large enterprise",
    ],
    "revenue_band": [
        "Our annual revenue is under 100M",
        "Our annual revenue is above 100M",
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
        for field in ["business_goal", "local_entity", "employee_count", "new_market", "applicant_type", "revenue_band"]:
            if field in missing_fields:
                return {
                    "type": "question",
                    "question": MISSING_FIELD_QUESTIONS[field],
                    "options": MISSING_FIELD_OPTIONS[field],
                }
        return None

    def for_no_eligible(self) -> dict:
        return {
            "type": "question",
            "question": (
                "I need one more detail to return only eligible grants. "
                "Could you share your company size, Singapore registration status, and whether this is a new overseas market?"
            ),
            "options": [
                "We are a 1–10 employee SME registered in Singapore",
                "We are a 11–30 employee SME registered in Singapore",
                "This is our first time entering that overseas market",
                "We are a non-SME / large enterprise",
            ],
        }
