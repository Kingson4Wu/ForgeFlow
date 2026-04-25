import pytest

from forgeflow.adapters.claude_code import ClaudeCodeCLIAdapter
from forgeflow.adapters.codex import CodexCLIAdapter
from forgeflow.adapters.gemini import GeminiCLIAdapter
from forgeflow.adapters.registry import get_adapter, list_adapters


def test_get_cli_adapter_default() -> None:
    """Test that get_adapter returns Gemini adapter by default."""
    adapter = get_adapter("gemini")
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_gemini() -> None:
    """Test that get_adapter returns Gemini adapter when specified."""
    adapter = get_adapter("gemini")
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_codex() -> None:
    """Test that get_adapter returns Codex adapter when specified."""
    adapter = get_adapter("codex")
    assert isinstance(adapter, CodexCLIAdapter)


def test_get_cli_adapter_claude_code() -> None:
    """Test that get_adapter returns Claude Code adapter when specified."""
    adapter = get_adapter("claude_code")
    assert isinstance(adapter, ClaudeCodeCLIAdapter)


def test_get_cli_adapter_case_insensitive() -> None:
    """Test that get_adapter is case insensitive."""
    adapter1 = get_adapter("GEMINI")
    adapter2 = get_adapter("Gemini")
    assert isinstance(adapter1, GeminiCLIAdapter)
    assert isinstance(adapter2, GeminiCLIAdapter)


def test_get_cli_adapter_whitespace_stripped() -> None:
    """Test that get_adapter strips whitespace."""
    adapter = get_adapter(" gemini ")
    assert isinstance(adapter, GeminiCLIAdapter)


def test_get_cli_adapter_unsupported() -> None:
    """Test that get_adapter raises ValueError for unsupported CLI type."""
    with pytest.raises(ValueError) as excinfo:
        get_adapter("unsupported")
    assert "unsupported" in str(excinfo.value)


def test_list_supported_cli_types() -> None:
    """Test that list_adapters returns the correct list."""
    supported = list_adapters()
    assert isinstance(supported, list)
    assert "gemini" in supported
    assert "codex" in supported
    assert "claude_code" in supported
    assert len(supported) >= 3
