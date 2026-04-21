import asyncio
import subprocess
import tempfile
from pathlib import Path

from .base import LLMDriver, LLMDriverError


class CodexCLIDriver(LLMDriver):
    def __init__(self, timeout_seconds: float = 45.0, model: str | None = None):
        self.timeout_seconds = timeout_seconds
        self.model = model.strip() if model else None

    async def complete(self, prompt: str) -> str:
        with tempfile.NamedTemporaryFile(prefix="codex-last-message-", suffix=".txt", delete=False) as temp_file:
            output_path = Path(temp_file.name)

        cmd = [
            "codex",
            "exec",
            "--ephemeral",
            "--output-last-message",
            str(output_path),
        ]
        if self.model:
            cmd.extend(["--model", self.model])
        cmd.append(prompt)

        try:
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except FileNotFoundError as exc:
                raise LLMDriverError("command_missing", "Codex CLI executable was not found on PATH") from exc

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_seconds)
            except asyncio.TimeoutError as exc:
                proc.kill()
                await proc.wait()
                raise LLMDriverError("timeout", f"Codex CLI timed out after {self.timeout_seconds}s") from exc

            if proc.returncode != 0:
                stderr_text = stderr.decode().strip() or stdout.decode().strip()
                raise LLMDriverError("non_zero_exit", f"Codex CLI failed: {stderr_text}")

            try:
                result = output_path.read_text().strip()
            except OSError as exc:
                raise LLMDriverError("invalid_response", "Codex CLI did not write an output message") from exc

            if not result:
                raise LLMDriverError("invalid_response", "Codex CLI returned an empty response")

            return result
        finally:
            output_path.unlink(missing_ok=True)
