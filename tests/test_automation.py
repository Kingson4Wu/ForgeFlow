import logging

from forgeflow.core.automation import (
    Config,
    _handle_input_with_text,
    _initialize_session,
    _progressive_backspace_until_prompt,
    _recover_from_timeout,
    _send_command,
    _send_continue_and_return_timestamp,
    _send_escape_and_wait,
    is_task_processing,
    setup_logger,
)
from forgeflow.core.cli_adapters.factory import get_cli_adapter


def test_config_defaults() -> None:
    """Test Config dataclass with default values."""
    config = Config(session="test_session", workdir="/tmp", ai_cmd="test_cmd")
    assert config.session == "test_session"
    assert config.workdir == "/tmp"
    assert config.ai_cmd == "test_cmd"
    assert config.poll_interval == 10
    assert config.input_prompt_timeout == 2000
    assert config.log_file == "forgeflow.log"
    assert config.log_to_console is True
    assert config.project is None
    assert config.task is None
    assert config.cli_type == "gemini"
    assert config.log_level == "INFO"


def test_config_custom_values() -> None:
    """Test Config dataclass with custom values."""
    config = Config(
        session="test_session",
        workdir="/tmp",
        ai_cmd="test_cmd",
        poll_interval=5,
        input_prompt_timeout=1000,
        log_file="custom.log",
        log_to_console=False,
        project="test_project",
        task="test_task",
        cli_type="codex",
        log_level="DEBUG",
    )
    assert config.poll_interval == 5
    assert config.input_prompt_timeout == 1000
    assert config.log_file == "custom.log"
    assert config.log_to_console is False
    assert config.project == "test_project"
    assert config.task == "test_task"
    assert config.cli_type == "codex"
    assert config.log_level == "DEBUG"


def test_is_task_processing() -> None:
    """Test is_task_processing function."""
    # Get a CLI adapter for testing
    cli_adapter = get_cli_adapter("gemini")

    # Test with empty output
    assert is_task_processing("", cli_adapter) is False

    # Test with output that doesn't indicate task processing
    output = "Some regular output"
    assert is_task_processing(output, cli_adapter) is False


def test_is_task_processing_unchanged_output_tracking() -> None:
    """Test is_task_processing function with unchanged output tracking."""
    from forgeflow.core.automation import reset_unchanged_output_tracking

    # Get a CLI adapter for testing
    cli_adapter = get_cli_adapter("gemini")

    # Reset tracking to ensure clean state
    reset_unchanged_output_tracking()

    # Test output that indicates task processing
    processing_output = "(esc to cancel...)"

    # First check should return True (assuming the CLI adapter recognizes it as processing)
    result1 = is_task_processing(processing_output, cli_adapter)

    # For the next 4 checks with the same output, it should still return True
    result2 = is_task_processing(processing_output, cli_adapter)
    result3 = is_task_processing(processing_output, cli_adapter)
    result4 = is_task_processing(processing_output, cli_adapter)
    result5 = is_task_processing(processing_output, cli_adapter)

    # All should be True
    assert result1 is True
    assert result2 is True
    assert result3 is True
    assert result4 is True
    assert result5 is True

    # The 5th consecutive check with the same output should return False
    result6 = is_task_processing(processing_output, cli_adapter)
    assert result6 is False

    # Reset tracking
    reset_unchanged_output_tracking()

    # After changing the output, it should return True again
    different_output = "(esc to cancel - different)"
    result7 = is_task_processing(different_output, cli_adapter)
    assert result7 is True

    # Reset tracking for clean state
    reset_unchanged_output_tracking()


def test_setup_logger() -> None:
    """Test setup_logger function."""
    logger = setup_logger("/tmp/test.log", to_console=False, level="DEBUG")
    assert logger.name == "forgeflow"
    assert logger.level == 10  # DEBUG level

    # Test with default values
    logger = setup_logger("/tmp/test2.log")
    assert logger.name == "forgeflow"
    assert logger.level == 20  # INFO level


# Mock classes for testing _recover_from_timeout
class MockTmuxCtl:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def send_escape(self) -> None:
        self.calls.append("send_escape")

    def send_backspace(self, count: int) -> None:
        self.calls.append(f"send_backspace({count})")

    def send_text_then_enter(self, text: str) -> None:
        self.calls.append(f"send_text_then_enter({text})")

    def send_enter(self) -> None:
        self.calls.append("send_enter")

    def create_session(self) -> None:
        self.calls.append("create_session")

    def capture_output(self, include_ansi: bool = False) -> str:
        self.calls.append(f"capture_output(include_ansi={include_ansi})")
        # Return output that indicates input prompt for the first few calls,
        # then return output that doesn't indicate input prompt to test the loop
        if len([c for c in self.calls if "capture_output" in c]) <= 2:
            return "> Type your message"
        return "Some other output"


class MockLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str) -> None:
        self.messages.append(message)


def test_recover_from_timeout() -> None:
    """Test _recover_from_timeout function."""
    tmux = MockTmuxCtl()
    cli_adapter = get_cli_adapter("gemini")
    logger = logging.getLogger("test")

    result = _recover_from_timeout(tmux, cli_adapter, logger)  # type: ignore

    # Check that the function returned a timestamp (float)
    assert isinstance(result, float)

    # Check that the expected methods were called
    assert "send_escape" in tmux.calls
    assert any("send_backspace" in call for call in tmux.calls)
    assert "send_text_then_enter(continue)" in tmux.calls


def test_send_escape_and_wait() -> None:
    """Test _send_escape_and_wait function."""
    tmux = MockTmuxCtl()
    _send_escape_and_wait(tmux)  # type: ignore

    # Check that send_escape was called
    assert "send_escape" in tmux.calls


def test_progressive_backspace_until_prompt() -> None:
    """Test _progressive_backspace_until_prompt function."""
    tmux = MockTmuxCtl()
    cli_adapter = get_cli_adapter("gemini")

    _progressive_backspace_until_prompt(tmux, cli_adapter)  # type: ignore

    # Check that send_backspace was called
    assert any("send_backspace" in call for call in tmux.calls)
    assert any("capture_output" in call for call in tmux.calls)


def test_send_continue_and_return_timestamp() -> None:
    """Test _send_continue_and_return_timestamp function."""
    tmux = MockTmuxCtl()

    result = _send_continue_and_return_timestamp(tmux)  # type: ignore

    # Check that the function returned a timestamp (float)
    assert isinstance(result, float)

    # Check that send_text_then_enter was called with "continue"
    assert "send_text_then_enter(continue)" in tmux.calls


# Mock classes for testing new functions
class MockConfig:
    def __init__(self, ai_cmd: str = "test_cmd") -> None:
        self.ai_cmd = ai_cmd


def test_initialize_session() -> None:
    """Test _initialize_session function."""
    tmux = MockTmuxCtl()
    cli_adapter = get_cli_adapter("gemini")
    config = MockConfig()
    logger = logging.getLogger("test")

    _initialize_session(tmux, cli_adapter, config, logger)  # type: ignore

    # Check that create_session was called
    assert "create_session" in str(tmux.calls)


def test_send_command() -> None:
    """Test _send_command function."""
    tmux = MockTmuxCtl()
    logger = logging.getLogger("test")

    # Test with string command
    _send_command(tmux, "test command", logger)  # type: ignore
    assert "send_text_then_enter(test command)" in tmux.calls

    # Test with callable command
    _send_command(tmux, lambda: "callable command", logger)  # type: ignore
    assert "send_text_then_enter(callable command)" in tmux.calls


def test_handle_input_with_text() -> None:
    """Test _handle_input_with_text function."""
    tmux = MockTmuxCtl()
    logger = logging.getLogger("test")

    _handle_input_with_text(tmux, logger)  # type: ignore

    # Check that send_enter was called
    assert "send_enter" in str(tmux.calls)
