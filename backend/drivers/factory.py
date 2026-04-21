import logging
import os

from .base import LLMDriver
from .claude_cli import ClaudeCLIDriver
from .codex_cli import CodexCLIDriver
from .fallback import FallbackLLMDriver

logger = logging.getLogger(__name__)


def build_driver_from_env() -> LLMDriver:
    primary_name = os.getenv("LLM_PROVIDER", "claude_cli").strip().lower()
    fallback_name = os.getenv("LLM_FALLBACK_PROVIDER", "codex_cli").strip().lower()
    timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))

    primary = _build_single_driver(primary_name, timeout_seconds)

    if fallback_name == primary_name:
        return primary

    fallback = _build_optional_driver(fallback_name, timeout_seconds)
    if fallback is None:
        return primary

    return FallbackLLMDriver(
        primary=primary,
        fallback=fallback,
        primary_name=primary_name,
        fallback_name=fallback_name,
    )


def _build_single_driver(provider_name: str, timeout_seconds: float) -> LLMDriver:
    if provider_name == "claude_cli":
        return ClaudeCLIDriver(timeout_seconds=timeout_seconds)

    if provider_name in {"codex_cli", "codex"}:
        model = os.getenv("CODEX_MODEL", "").strip() or None
        return CodexCLIDriver(timeout_seconds=timeout_seconds, model=model)

    raise ValueError(f"Unsupported LLM provider: {provider_name}")


def _build_optional_driver(provider_name: str, timeout_seconds: float) -> LLMDriver | None:
    if provider_name == "claude_cli":
        return ClaudeCLIDriver(timeout_seconds=timeout_seconds)

    if provider_name in {"codex_cli", "codex"}:
        model = os.getenv("CODEX_MODEL", "").strip() or None
        return CodexCLIDriver(timeout_seconds=timeout_seconds, model=model)

    logger.warning("Unknown fallback provider '%s'; fallback disabled", provider_name)
    return None
