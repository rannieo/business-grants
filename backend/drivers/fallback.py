import logging

from .base import LLMDriver, LLMDriverError

logger = logging.getLogger(__name__)


class FallbackLLMDriver(LLMDriver):
    def __init__(
        self,
        primary: LLMDriver,
        fallback: LLMDriver,
        primary_name: str,
        fallback_name: str,
    ):
        self.primary = primary
        self.fallback = fallback
        self.primary_name = primary_name
        self.fallback_name = fallback_name

    async def complete(self, prompt: str) -> str:
        try:
            return await self.primary.complete(prompt)
        except Exception as exc:
            primary_err = self._as_driver_error(exc)
            logger.warning(
                "Primary LLM driver failed; attempting fallback",
                extra={
                    "primary_driver": self.primary_name,
                    "error_kind": primary_err.kind,
                },
            )

        try:
            return await self.fallback.complete(prompt)
        except Exception as exc:
            fallback_err = self._as_driver_error(exc)
            logger.exception(
                "Fallback LLM driver failed",
                extra={
                    "primary_driver": self.primary_name,
                    "fallback_driver": self.fallback_name,
                    "primary_error_kind": primary_err.kind,
                    "fallback_error_kind": fallback_err.kind,
                },
            )
            raise LLMDriverError(
                "fallback_failed",
                (
                    f"Primary driver '{self.primary_name}' failed with {primary_err.kind}; "
                    f"fallback driver '{self.fallback_name}' failed with {fallback_err.kind}"
                ),
            ) from exc

    def _as_driver_error(self, exc: Exception) -> LLMDriverError:
        if isinstance(exc, LLMDriverError):
            return exc
        return LLMDriverError("unknown_error", str(exc))
