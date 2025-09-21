from __future__ import annotations

import re
import subprocess

from .base import CLIAdapter


class GeminiCLIAdapter(CLIAdapter):
    """CLI adapter for Google's Gemini CLI."""

    # ---------- Input Prompt Detection ----------
    PROMPT_RE = re.compile(r">.*Type your message or @[\w/]+(?:\.\w+)?")
    # Match input lines enclosed in vertical bars (as loose as possible)
    PROMPT_WITH_TEXT_RE = re.compile(r"\u2502 > .*? \u2502")
    PROMPT_TASK_PROCESSING = re.compile(r"\(esc to cancel.*\)")
    PROMPT_AI_CLI_EXIST = re.compile(r"^YOLO mode \(ctrl \+ y to toggle\)(.*)?$")

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
            if self.PROMPT_TASK_PROCESSING.search(line.strip()):
                return True
        return False

    def is_ai_cli_exist(self, output: str) -> bool:
        # First check the existing prompt-based detection
        for line in output.splitlines():
            if self.PROMPT_AI_CLI_EXIST.match(line.strip()):
                return True

        # If that fails, check for Qwen or Gemini in tmux pane titles
        try:
            # Execute tmux command to list panes with specific format
            result = subprocess.run(
                [
                    "tmux",
                    "list-panes",
                    "-t",
                    "auto_session",
                    "-F",
                    "#{pane_index} #{pane_pid} #{pane_title}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            # If command succeeded, check for Qwen or Gemini in the output
            if result.returncode == 0:
                if "Qwen" in result.stdout or "Gemini" in result.stdout:
                    return True
        except Exception:
            # If any error occurs, we continue with the original logic
            pass

        return False
