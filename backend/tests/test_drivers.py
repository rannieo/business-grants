import pytest

from drivers.base import LLMDriver, LLMDriverError
from drivers.fallback import FallbackLLMDriver


class FakeDriver(LLMDriver):
    def __init__(self, response: str | None = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls = 0

    async def complete(self, prompt: str) -> str:
        self.calls += 1
        if self.error:
            raise self.error
        assert self.response is not None
        return self.response


@pytest.mark.asyncio
async def test_fallback_driver_uses_primary_when_primary_succeeds():
    primary = FakeDriver(response='{"type":"question","question":"ok"}')
    fallback = FakeDriver(response='{"type":"question","question":"fallback"}')
    driver = FallbackLLMDriver(primary, fallback, "claude_cli", "codex_cli")

    result = await driver.complete("prompt")
    assert "ok" in result
    assert primary.calls == 1
    assert fallback.calls == 0


@pytest.mark.asyncio
async def test_fallback_driver_calls_fallback_once_after_primary_failure():
    primary = FakeDriver(error=LLMDriverError("timeout", "timed out"))
    fallback = FakeDriver(response='{"type":"question","question":"fallback"}')
    driver = FallbackLLMDriver(primary, fallback, "claude_cli", "codex_cli")

    result = await driver.complete("prompt")
    assert "fallback" in result
    assert primary.calls == 1
    assert fallback.calls == 1


@pytest.mark.asyncio
async def test_fallback_driver_raises_when_both_drivers_fail():
    primary = FakeDriver(error=LLMDriverError("command_missing", "missing"))
    fallback = FakeDriver(error=LLMDriverError("non_zero_exit", "bad request"))
    driver = FallbackLLMDriver(primary, fallback, "claude_cli", "codex_cli")

    with pytest.raises(LLMDriverError, match="fallback driver"):
        await driver.complete("prompt")
