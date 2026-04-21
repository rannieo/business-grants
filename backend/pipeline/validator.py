import json
import re


class Validator:
    def parse_and_validate(self, raw: str) -> dict | None:
        data = self._parse_json(raw)
        if data is None:
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

    def _parse_json(self, raw: str) -> dict | None:
        candidates = self._json_candidates(raw)
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
            except (json.JSONDecodeError, ValueError):
                continue
            if isinstance(parsed, dict):
                return parsed
        return None

    def _json_candidates(self, raw: str) -> list[str]:
        text = raw.strip()
        candidates: list[str] = [text]

        # Full-message code fence cleanup for already well-structured outputs.
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
        if cleaned and cleaned not in candidates:
            candidates.append(cleaned)

        # Extract JSON blocks inside code fences, even when surrounded by prose.
        fence_pattern = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", flags=re.DOTALL | re.IGNORECASE)
        for match in fence_pattern.finditer(text):
            block = match.group(1).strip()
            if block and block not in candidates:
                candidates.append(block)

        # Extract the first balanced JSON object from mixed output text.
        balanced = self._extract_first_balanced_json_object(text)
        if balanced and balanced not in candidates:
            candidates.append(balanced)

        return candidates

    def _extract_first_balanced_json_object(self, text: str) -> str | None:
        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escaped = False

        for i in range(start, len(text)):
            ch = text[i]

            if escaped:
                escaped = False
                continue

            if ch == "\\":
                escaped = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]

        return None
