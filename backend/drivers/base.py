from abc import ABC, abstractmethod


class LLMDriverError(RuntimeError):
    """Raised when an LLM driver fails in a classified way."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


class LLMDriver(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Send a fully-rendered prompt and return the raw text response."""
        ...
