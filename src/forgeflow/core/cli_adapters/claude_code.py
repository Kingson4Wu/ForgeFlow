from __future__ import annotations

import re

from .base import CLIAdapter


class ClaudeCodeCLIAdapter(CLIAdapter):
    """CLI adapter for Anthropic's Claude Code CLI."""

    # ---------- Input Prompt Detection ----------
    # Claude Code prompt: box-drawing character followed by space
    PROMPT_RE = re.compile(r"❯ ")
    PROMPT_WITH_TEXT_RE = re.compile(r"❯ .+")
    # Two play symbols indicate task processing
    PROMPT_TASK_PROCESSING = re.compile(r"⏵⏵")
    # CLI exists if we see the Claude Code version banner
    PROMPT_AI_CLI_EXIST = re.compile(r"Claude Code v")

    def is_input_prompt(self, output: str) -> bool:
        if not output:
            return False
        return bool(self.PROMPT_RE.search(output))

    def is_input_prompt_with_text(self, output: str) -> bool:
        if not output:
            return False
        return bool(self.PROMPT_WITH_TEXT_RE.search(output))

    def is_task_processing(self, output: str) -> bool:
        if not output:
            return False
        return bool(self.PROMPT_TASK_PROCESSING.search(output))

    def is_ai_cli_exist(self, output: str) -> bool:
        if not output:
            return False
        return bool(self.PROMPT_AI_CLI_EXIST.search(output))
