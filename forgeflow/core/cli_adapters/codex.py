from __future__ import annotations

import re

from .base import CLIAdapter


class CodexCLIAdapter(CLIAdapter):
    """CLI adapter for Open AI's Codex CLI."""

    # ---------- Input Prompt Detection ----------
    PROMPT_RE = re.compile(r"^▌.*", re.MULTILINE)
    # Match input lines enclosed in vertical bars (as loose as possible)
    PROMPT_WITH_TEXT_RE = re.compile(r"\u2502 > .*? \u2502")
    PROMPT_TASK_PROCESSING = re.compile(r"• Esc to interrupt\)")
    PROMPT_AI_CLI_EXIST = re.compile(r"^\s*⏎ send\s+⌃J newline\s+⌃T transcript\s+⌃C quit", re.MULTILINE)

    def is_input_prompt(self, output: str) -> bool:
        if not output:
            return False
        return bool(self.PROMPT_RE.search(output))

    def is_input_prompt_with_text(self, output: str) -> bool:
        if not output:
            return False
        return bool(self.PROMPT_WITH_TEXT_RE.search(output))

    def is_task_processing(self, output: str) -> bool:
        for line in output.splitlines():
            if self.PROMPT_TASK_PROCESSING.search(line):
                return True
        return False

    def is_ai_cli_exist(self, output: str) -> bool:
        for line in output.splitlines():
            if self.PROMPT_AI_CLI_EXIST.match(line.strip()):
                return True
        return False
