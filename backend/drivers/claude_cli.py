import asyncio
import subprocess

from .base import LLMDriver


class ClaudeCLIDriver(LLMDriver):
    async def complete(self, prompt: str) -> str:
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"claude CLI error: {stderr.decode().strip()}")
        return stdout.decode().strip()
