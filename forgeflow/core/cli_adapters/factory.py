from __future__ import annotations

from .base import CLIAdapter
from .claude_code import ClaudeCodeCLIAdapter
from .gemini import GeminiCLIAdapter


def get_cli_adapter(cli_type: str = "gemini") -> CLIAdapter:
    """
    Factory function to get the appropriate CLI adapter based on the client type.

    Args:
        cli_type: The type of CLI client ("gemini", "claude_code", etc.)

    Returns:
        CLIAdapter: The appropriate CLI adapter instance

    Raises:
        ValueError: If the cli_type is not supported
    """
    if cli_type == "gemini":
        return GeminiCLIAdapter()
    elif cli_type == "claude_code":
        return ClaudeCodeCLIAdapter()
    else:
        raise ValueError(f"Unsupported CLI type: {cli_type}")
