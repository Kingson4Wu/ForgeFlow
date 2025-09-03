from __future__ import annotations

from .base import CLIAdapter


class ClaudeCodeCLIAdapter(CLIAdapter):
    """CLI adapter for Anthropic's Claude Code CLI (placeholder implementation)."""

    def is_input_prompt(self, output: str) -> bool:
        # TODO: Implement Claude Code specific prompt detection
        return False

    def is_input_prompt_with_text(self, output: str) -> bool:
        # TODO: Implement Claude Code specific prompt detection with text
        return False

    def is_task_processing(self, output: str) -> bool:
        # TODO: Implement Claude Code specific task processing detection
        return False

    def is_ai_cli_exist(self, output: str) -> bool:
        # TODO: Implement Claude Code CLI existence detection
        return False
