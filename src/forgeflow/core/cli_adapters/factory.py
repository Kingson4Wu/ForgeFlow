from __future__ import annotations

from .base import CLIAdapter
from .claude_code import ClaudeCodeCLIAdapter
from .codex import CodexCLIAdapter
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
    # Handle None or empty string by using default
    if not cli_type:
        cli_type = "gemini"

    key = cli_type.strip().lower()
    if key == "gemini":
        return GeminiCLIAdapter()
    elif key == "codex":
        return CodexCLIAdapter()
    elif key == "claude_code":
        return ClaudeCodeCLIAdapter()
    else:
        supported = ["gemini", "codex", "claude_code"]
        raise ValueError(f"Unsupported CLI type: {cli_type}. Supported: {', '.join(supported)}")


def list_supported_cli_types() -> list[str]:
    return ["gemini", "codex", "claude_code"]
