from forgeflow.core.rules import CommandPostProcessor, Rule


class ClaudeCodeCommandPostProcessor(CommandPostProcessor):
    """Command post-processor for Claude Code CLI."""

    def post_process_command(self, output: str, initial_command: str | None) -> str | None:
        return None


def build_rules() -> list[Rule]:
    """Build rules specific to Claude Code CLI."""
    return [
        Rule(
            check=lambda out: "You're out of credits" in out,
            command=None,
            description="Out of credits - stop automation",
        ),
        Rule(
            check=lambda out: "credit usage: 100%" in out.lower(),
            command=None,
            description="Credits exhausted - stop automation",
        ),
        Rule(
            check=lambda out: "MCP server" in out and "failed" in out.lower(),
            command=None,
            description="MCP server failed - stop automation",
        ),
        Rule(
            check=lambda out: "context window" in out.lower() and "exceeded" in out.lower(),
            command="/compact",
            description="Context window exceeded - send /compact command",
        ),
        Rule(
            check=lambda out: "rate limit" in out.lower() or "too many requests" in out.lower(),
            command=None,
            description="Rate limit hit - stop automation",
        ),
        Rule(
            check=lambda out: "error" in out.lower() and "retry" in out.lower(),
            command="continue",
            description="Retryable error - continue execution",
        ),
    ]
