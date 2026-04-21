KEEP_FIELDS = [
    "id", "name", "summary", "applicant_type",
    "employee_count_min", "revenue_band", "business_goals",
    "requires_local_entity", "requires_new_market", "notes",
]


class Compressor:
    def compress(self, grants: list[dict]) -> list[dict]:
        return [{k: g[k] for k in KEEP_FIELDS if k in g} for g in grants]
