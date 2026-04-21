import json
import re


class Validator:
    def parse_and_validate(self, raw: str) -> dict | None:
        try:
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
            data = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return None

        t = data.get("type")
        if t == "question":
            return data if data.get("question") else None
        elif t == "recommendation":
            grants = data.get("grants", [])
            required = {"id", "name", "fit", "reason", "cited"}
            valid_fits = {"high", "medium", "low"}
            if not grants:
                return None
            for g in grants:
                if not required.issubset(g.keys()):
                    return None
                if g["fit"] not in valid_fits:
                    return None
            return data
        return None
