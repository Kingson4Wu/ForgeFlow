from __future__ import annotations

import re

from .base import CLIAdapter


class ClaudeCodeCLIAdapter(CLIAdapter):
    """CLI adapter for Anthropic's Claude Code CLI."""

    # ---------- Input Prompt Detection ----------
    # TODO: Update with actual Claude Code prompt patterns
    PROMPT_RE = re.compile(r"^.*@\w+:", re.MULTILINE)
    # Match input lines enclosed in vertical bars (as loose as possible)
    PROMPT_WITH_TEXT_RE = re.compile(r"\u2502 > .*? \u2502")
    # TODO: Update with actual Claude Code processing indicator
    PROMPT_TASK_PROCESSING = re.compile(r"^\(processing.*\)$")
    # TODO: Update with actual Claude Code CLI existence indicator
    PROMPT_AI_CLI_EXIST = re.compile(r"^Claude Code CLI.*$", re.MULTILINE)

    def is_input_prompt(self, output: str) -> bool:
        """Check if the output contains an input prompt."""
        if not output:
            return False
        return bool(self.PROMPT_RE.search(output))

    def is_input_prompt_with_text(self, output: str) -> bool:
        """Check if the output contains an input prompt with text already entered."""
        if not output:
            return False
        return bool(self.PROMPT_WITH_TEXT_RE.search(output))

    def is_task_processing(self, output: str) -> bool:
        """Check if a task is currently being processed."""
        for line in output.splitlines():
            if self.PROMPT_TASK_PROCESSING.match(line.strip()):
                return True
        return False

    def is_ai_cli_exist(self, output: str) -> bool:
        """Check if the AI CLI is running."""
        for line in output.splitlines():
            if self.PROMPT_AI_CLI_EXIST.match(line.strip()):
                return True
        return False
