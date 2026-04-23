from forgeflow.core.cli_adapters.gemini import GeminiCLIAdapter


def test_is_ai_cli_exist_with_prompt():
    """Test that is_ai_cli_exist returns True when prompt is detected."""
    adapter = GeminiCLIAdapter()
    output = "YOLO mode (ctrl + y to toggle)"
    assert adapter.is_ai_cli_exist(output) is True


def test_is_ai_cli_exist_without_prompt():
    """Test that is_ai_cli_exist returns False when no prompt is detected."""
    adapter = GeminiCLIAdapter()
    output = "Some other output"
    assert adapter.is_ai_cli_exist(output) is False


def test_is_ai_cli_exist_empty_output():
    """Test that is_ai_cli_exist returns False for empty output."""
    adapter = GeminiCLIAdapter()
    assert adapter.is_ai_cli_exist("") is False
    assert adapter.is_ai_cli_exist("   ") is False
