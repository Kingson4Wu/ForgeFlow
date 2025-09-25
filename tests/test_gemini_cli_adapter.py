from unittest.mock import MagicMock, patch

from forgeflow.core.cli_adapters.gemini import GeminiCLIAdapter


def test_is_ai_cli_exist_with_prompt():
    """Test that is_ai_cli_exist returns True when prompt is detected."""
    adapter = GeminiCLIAdapter()
    output = "YOLO mode (ctrl + y to toggle)"
    assert adapter.is_ai_cli_exist(output) is True


@patch("forgeflow.core.cli_adapters.gemini.subprocess.run")
def test_is_ai_cli_exist_without_prompt(mock_subprocess):
    """Test that is_ai_cli_exist returns False when no prompt is detected."""
    # Mock the subprocess result to simulate no Qwen or Gemini in pane titles
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "0 12345 Some Other CLI\n1 12346 Another Pane"
    mock_subprocess.return_value = mock_result

    adapter = GeminiCLIAdapter()
    output = "Some other output"
    assert adapter.is_ai_cli_exist(output) is False


@patch("forgeflow.core.cli_adapters.gemini.subprocess.run")
def test_is_ai_cli_exist_with_qwen_in_tmux(mock_subprocess):
    """Test that is_ai_cli_exist returns True when Qwen is in tmux pane titles."""
    # Mock the subprocess result to simulate Qwen in pane titles
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "0 12345 Qwen CLI\n1 12346 Other Pane"
    mock_subprocess.return_value = mock_result

    adapter = GeminiCLIAdapter()
    output = "Some other output"  # No prompt detected
    assert adapter.is_ai_cli_exist(output) is True


@patch("forgeflow.core.cli_adapters.gemini.subprocess.run")
def test_is_ai_cli_exist_with_gemini_in_tmux(mock_subprocess):
    """Test that is_ai_cli_exist returns True when Gemini is in tmux pane titles."""
    # Mock the subprocess result to simulate Gemini in pane titles
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "0 12345 Gemini CLI\n1 12346 Other Pane"
    mock_subprocess.return_value = mock_result

    adapter = GeminiCLIAdapter()
    output = "Some other output"  # No prompt detected
    assert adapter.is_ai_cli_exist(output) is True


@patch("forgeflow.core.cli_adapters.gemini.subprocess.run")
def test_is_ai_cli_exist_with_no_qwen_or_gemini_in_tmux(mock_subprocess):
    """Test that is_ai_cli_exist returns False when neither Qwen nor Gemini is in tmux pane titles."""
    # Mock the subprocess result to simulate no Qwen or Gemini in pane titles
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "0 12345 Some Other CLI\n1 12346 Another Pane"
    mock_subprocess.return_value = mock_result

    adapter = GeminiCLIAdapter()
    output = "Some other output"  # No prompt detected
    assert adapter.is_ai_cli_exist(output) is False


@patch("forgeflow.core.cli_adapters.gemini.subprocess.run")
def test_is_ai_cli_exist_with_tmux_command_failure(mock_subprocess):
    """Test that is_ai_cli_exist handles tmux command failure gracefully."""
    # Mock the subprocess result to simulate command failure
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_subprocess.return_value = mock_result

    adapter = GeminiCLIAdapter()
    output = "Some other output"  # No prompt detected
    assert adapter.is_ai_cli_exist(output) is False


@patch("forgeflow.core.cli_adapters.gemini.subprocess.run")
def test_is_ai_cli_exist_with_exception(mock_subprocess):
    """Test that is_ai_cli_exist handles exceptions gracefully."""
    # Mock the subprocess to raise an exception
    mock_subprocess.side_effect = Exception("Test exception")

    adapter = GeminiCLIAdapter()
    output = "Some other output"  # No prompt detected
    assert adapter.is_ai_cli_exist(output) is False
