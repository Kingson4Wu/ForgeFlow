import pytest

from forgeflow.core.cli_adapters.claude_code import ClaudeCodeCLIAdapter
from forgeflow.core.cli_adapters.codex import CodexCLIAdapter
from forgeflow.core.cli_adapters.factory import get_cli_adapter, list_supported_cli_types
from forgeflow.core.cli_adapters.gemini import GeminiCLIAdapter


def test_get_cli_adapter_default() -> None:
    """Test that get_cli_adapter returns Gemini adapter by default."""
    adapter = get_cli_adapter()
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_gemini() -> None:
    """Test that get_cli_adapter returns Gemini adapter when specified."""
    adapter = get_cli_adapter("gemini")
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_codex() -> None:
    """Test that get_cli_adapter returns Codex adapter when specified."""
    adapter = get_cli_adapter("codex")
    assert isinstance(adapter, CodexCLIAdapter)


def test_get_cli_adapter_claude_code() -> None:
    """Test that get_cli_adapter returns Claude Code adapter when specified."""
    adapter = get_cli_adapter("claude_code")
    assert isinstance(adapter, ClaudeCodeCLIAdapter)


def test_get_cli_adapter_case_insensitive() -> None:
    """Test that get_cli_adapter is case insensitive."""
    adapter1 = get_cli_adapter("GEMINI")
    adapter2 = get_cli_adapter("Gemini")
    assert isinstance(adapter1, GeminiCLIAdapter)
    assert isinstance(adapter2, GeminiCLIAdapter)


def test_get_cli_adapter_whitespace_stripped() -> None:
    """Test that get_cli_adapter strips whitespace."""
    adapter = get_cli_adapter(" gemini ")
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_empty_string() -> None:
    """Test that get_cli_adapter returns default adapter for empty string."""
    adapter = get_cli_adapter("")
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_none() -> None:
    """Test that get_cli_adapter returns default adapter for None."""
    adapter = get_cli_adapter(None)  # type: ignore
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_unsupported() -> None:
    """Test that get_cli_adapter raises ValueError for unsupported CLI type."""
    with pytest.raises(ValueError) as excinfo:
        get_cli_adapter("unsupported")
    assert "Unsupported CLI type: unsupported" in str(excinfo.value)


def test_list_supported_cli_types() -> None:
    """Test that list_supported_cli_types returns the correct list."""
    supported = list_supported_cli_types()
    assert isinstance(supported, list)
    assert "gemini" in supported
    assert "codex" in supported
    assert "claude_code" in supported
    assert len(supported) == 3
