from drivers.claude_cli import ClaudeCLIDriver
from drivers.codex_cli import CodexCLIDriver
from drivers.factory import build_driver_from_env
from drivers.fallback import FallbackLLMDriver


def test_factory_returns_primary_when_fallback_is_unknown(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "claude_cli")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "unknown")

    driver = build_driver_from_env()
    assert isinstance(driver, ClaudeCLIDriver)


def test_factory_builds_fallback_driver_when_codex_is_configured(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "claude_cli")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "codex_cli")
    monkeypatch.setenv("CODEX_MODEL", "gpt-5.4-mini")

    driver = build_driver_from_env()
    assert isinstance(driver, FallbackLLMDriver)
    assert isinstance(driver.fallback, CodexCLIDriver)


def test_factory_supports_codex_as_primary_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "codex")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "codex")

    driver = build_driver_from_env()
    assert isinstance(driver, CodexCLIDriver)
