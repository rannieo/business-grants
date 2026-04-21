import asyncio
import subprocess

from .base import LLMDriver, LLMDriverError


class ClaudeCLIDriver(LLMDriver):
    def __init__(self, timeout_seconds: float = 45.0):
        self.timeout_seconds = timeout_seconds

    async def complete(self, prompt: str) -> str:
        try:
            proc = await asyncio.create_subprocess_exec(
                "claude", "-p", prompt,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise LLMDriverError("command_missing", "Claude CLI executable was not found on PATH") from exc

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_seconds)
        except asyncio.TimeoutError as exc:
            proc.kill()
            await proc.wait()
            raise LLMDriverError("timeout", f"Claude CLI timed out after {self.timeout_seconds}s") from exc

        if proc.returncode != 0:
            stderr_text = stderr.decode().strip()
            raise LLMDriverError("non_zero_exit", f"Claude CLI failed: {stderr_text}")
        return stdout.decode().strip()
