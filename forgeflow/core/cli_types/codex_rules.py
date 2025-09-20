import re

from forgeflow.core.rules import CommandPostProcessor, Rule


class CodexCommandPostProcessor(CommandPostProcessor):
    """Command post-processor for Codex CLI.

    Implements logic to send "/new" instead of "/compact" after 3 consecutive "/compact" commands.
    """

    def __init__(self) -> None:
        self._compact_counter = 0

    def post_process_command(self, output: str, initial_command: str | None) -> str | None:
        """Post-process a command for Codex CLI.

        If "/compact" has been sent 3 times consecutively and the initial command is "/compact",
        return "/new" instead.

        Args:
            output: The AI CLI output that the command is responding to
            initial_command: The command determined by the rules

        Returns:
            "/new" if 3 consecutive "/compact" commands have been sent and the initial command
            is "/compact", otherwise None to keep the initial command unchanged
        """
        # Check if the initial command is "/compact"
        if initial_command == "/compact":
            # Increment the counter
            self._compact_counter += 1
            # If we've sent "/compact" 3 times consecutively, return "/new"
            if self._compact_counter >= 3:
                # Reset the counter
                self._compact_counter = 0
                return "/new"
            return None
        else:
            # Reset the counter when we're not sending "/compact"
            self._compact_counter = 0
            return None


def build_rules() -> list[Rule]:
    """Build rules specific to Codex CLI."""
    return [
        Rule(
            check=lambda out: bool(
                re.search(
                    r"■ stream disconnected before completion: Your input exceeds the context window of this model.*",
                    out,
                    re.DOTALL,
                )
            )
            and "Compact task completed" not in out,
            command="/compact",
        ),
        Rule(
            check=lambda out: (
                "stream error: stream disconnected before completion: "
                "Your input exceeds the context window of this model" in out.replace("\n", " ")
                and "Compact task completed" not in out
            ),
            command="/compact",
        ),
        Rule(
            check=lambda out: ("You've hit your usage limit" in out),
            command=None,
        ),
    ]
