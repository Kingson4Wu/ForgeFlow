from __future__ import annotations

import re

from forgeflow.adapters.base import CLIAdapter
from forgeflow.adapters.registry import register

PROMPT_LINE_CHAR = "❯"
SEPARATOR_LINE_PREFIX = "──"
BYPASS_PERMISSIONS_MARKER = "⏵⏵ bypass permissions on (shift+tab to cycle)"


class ClaudeCodeCLIAdapter(CLIAdapter):
    """CLI adapter for Anthropic's Claude Code CLI."""

    # ---------- Input Prompt Detection ----------
    PROMPT_RE = re.compile(r"❯ ")
    PROMPT_WITH_TEXT_RE = re.compile(r"❯ .+")

    # Stability detection constants
    STABILITY_WINDOW_LINES = 100
    STABILITY_THRESHOLD = 3
    PROCESSING_MARKERS = ("⏺", "✻")

    def __init__(self) -> None:
        self._history: list[str] = []
        self._max_history: int = 10
        self._unchanged_count: int = 0
        self._last_100_lines: str = ""

    def _find_prompt_line(self, lines: list[str]) -> int | None:
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith(PROMPT_LINE_CHAR):
                return i
        return None

    def _prompt_framed(self, lines: list[str], idx: int) -> bool:
        prev = lines[idx - 1] if idx > 0 else ""
        next_line = lines[idx + 1] if idx < len(lines) - 1 else ""
        return prev.startswith(SEPARATOR_LINE_PREFIX) and next_line.startswith(
            SEPARATOR_LINE_PREFIX
        )

    def is_input_prompt(self, output: str) -> bool:
        if not output:
            return False
        lines = output.splitlines()
        idx = self._find_prompt_line(lines)
        return idx is not None and self._prompt_framed(lines, idx)

    def is_input_prompt_with_text(self, output: str) -> bool:
        if not output:
            return False
        lines = output.splitlines()
        idx = self._find_prompt_line(lines)
        if idx is None or not self._prompt_framed(lines, idx):
            return False
        after_prompt = lines[idx][len(PROMPT_LINE_CHAR) :]
        return bool(after_prompt.strip())

    def is_task_processing(self, history: list[str]) -> bool:
        if not history:
            return False
        self._history = history[-self._max_history :]
        if len(self._history) < 2:
            return True
        above_curr = self._extract_above_prompt(self._history[-1])
        last_n_lines = above_curr.splitlines()[-self.STABILITY_WINDOW_LINES :]
        last_100_lines_curr = "\n".join(last_n_lines)
        count_curr = sum(1 for line in last_n_lines if line.startswith(self.PROCESSING_MARKERS))
        if last_100_lines_curr == self._last_100_lines:
            self._unchanged_count += 1
        else:
            self._unchanged_count = 0
            self._last_100_lines = last_100_lines_curr
        if self._unchanged_count >= self.STABILITY_THRESHOLD and count_curr == 1:
            return False
        return True

    def _extract_above_prompt(self, output: str) -> str:
        lines = output.splitlines()
        idx = self._find_prompt_line(lines)
        if idx is not None:
            return "\n".join(lines[:idx])
        return output

    def is_ai_cli_exist(self, output: str) -> bool:
        if not output:
            return False
        lines = output.splitlines()
        idx = self._find_prompt_line(lines)
        if idx is None or not self._prompt_framed(lines, idx):
            return False
        below_prompt = "\n".join(lines[idx:])
        if BYPASS_PERMISSIONS_MARKER not in below_prompt:
            return False
        last_line = lines[-1] if lines else ""
        return not (
            re.match(r"^\(.*?\) ➜ .+ git:\([^)]+\)$", last_line.strip())
            or re.match(r"^.+@.+:[^$]+[$➜]", last_line.strip())
        )


register("claude_code", ClaudeCodeCLIAdapter)
