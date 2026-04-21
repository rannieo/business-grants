from abc import ABC, abstractmethod


class LLMDriver(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Send a fully-rendered prompt and return the raw text response."""
        ...
