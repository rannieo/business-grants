from pipeline.analyzer import QueryAnalyzer, QueryClass
from pipeline.clarifier import Clarifier
from pipeline.retriever import Retriever
from pipeline.compressor import Compressor
from pipeline.builder import PromptBuilder
from pipeline.validator import Validator
from drivers.base import LLMDriver


class GrantMatcherService:
    def __init__(self, driver: LLMDriver, grants: list[dict]):
        self.driver = driver
        self.analyzer = QueryAnalyzer()
        self.clarifier = Clarifier()
        self.retriever = Retriever(grants)
        self.compressor = Compressor()
        self.builder = PromptBuilder()
        self.validator = Validator()
        self._sessions: dict[str, list[dict]] = {}

    async def chat(self, session_id: str, user_message: str) -> dict:
        history = self._sessions.setdefault(session_id, [])

        query_class = self.analyzer.analyze(user_message, history)

        if query_class == QueryClass.VAGUE:
            response = self.clarifier.for_vague()
            self._record(history, user_message, response)
            return response

        if query_class == QueryClass.BORDERLINE:
            missing = self.analyzer.missing_fields(user_message, history)
            response = self.clarifier.for_missing(missing)
            if response:
                self._record(history, user_message, response)
                return response

        retrieved = self.retriever.retrieve(user_message, history, k=5)
        compressed = self.compressor.compress(retrieved)
        prompt = self.builder.build(compressed, history, user_message)

        raw = await self.driver.complete(prompt)
        result = self.validator.parse_and_validate(raw)
        if result is None:
            raw = await self.driver.complete(prompt + "\n\nRespond with valid JSON only.")
            result = self.validator.parse_and_validate(raw)
            if result is None:
                raise ValueError("LLM returned invalid response after retry")

        self._record(history, user_message, result)
        return result

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def _record(self, history: list, user_msg: str, response: dict) -> None:
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": str(response)})
