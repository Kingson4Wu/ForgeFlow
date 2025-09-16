from __future__ import annotations

from abc import ABC, abstractmethod


class CLIAdapter(ABC):
    """Base class for CLI adapters that define CLI-specific behavior."""

    @abstractmethod
    def is_input_prompt(self, output: str) -> bool:
        """Check if the output contains an input prompt."""
        pass

    @abstractmethod
    def is_input_prompt_with_text(self, output: str) -> bool:
        """Check if the output contains an input prompt with text already entered."""
        pass

    @abstractmethod
    def is_task_processing(self, output: str) -> bool:
        """Check if a task is currently being processed."""
        pass

    @abstractmethod
    def is_ai_cli_exist(self, output: str) -> bool:
        """Check if the AI CLI is running."""
        pass

    def wants_ansi(self) -> bool:
        """Whether this adapter prefers capturing ANSI escape sequences from tmux.

        If True, the automation will capture pane output with ANSI codes preserved
        (tmux `capture-pane -e`). Default False.
        """
        return False
