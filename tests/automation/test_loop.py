import logging

from forgeflow.adapters.registry import get_adapter
from forgeflow.automation.loop import (
    _initialize_session,
    _send_command,
)
from forgeflow.automation.monitor import _is_task_processing
from forgeflow.automation.recovery import (
    _progressive_backspace_until_prompt,
    _send_continue_and_return_timestamp,
    _send_escape_and_wait,
    recover_from_timeout,
)
from forgeflow.config import Config
from forgeflow.logging_config import setup_logger
from forgeflow.state import UnchangedTracker


def test_config_defaults() -> None:
    """Test Config dataclass with default values."""
    config = Config(session="test_session", workdir="/tmp", ai_cmd="test_cmd")
    assert config.session == "test_session"
    assert config.workdir == "/tmp"
    assert config.ai_cmd == "test_cmd"
    assert config.poll_interval == 10
    assert config.input_prompt_timeout == 1000
    assert config.log_file == "forgeflow.log"
    assert config.log_to_console is True
    assert config.project is None
    assert config.task is None
    assert config.cli_type == "claude_code"
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
    """Test _is_task_processing function."""
    # Get a CLI adapter for testing
    cli_adapter = get_adapter("gemini")
    tracker = UnchangedTracker(5)

    # Test with empty output and empty history
    assert _is_task_processing("", cli_adapter, [], tracker) is False

    # Test with output that doesn't indicate task processing
    output = "Some regular output"
    assert _is_task_processing(output, cli_adapter, [output], tracker) is False


def test_is_task_processing_unchanged_output_tracking() -> None:
    """Test _is_task_processing function with unchanged output tracking."""
    cli_adapter = get_adapter("gemini")
    tracker = UnchangedTracker(5)

    processing_output = "(esc to cancel...)"

    # Call 7 times with same output; first 5 return True, 6th returns False
    # (UNCHANGED_OUTPUT_THRESHOLD = 5: False after 5 consecutive unchanged)
    # count=0 initially, first same output doesn't increment (it SETS to 0), so:
    # call 2->count=1, call 3->count=2, call 4->count=3, call 5->count=4, call 6->count=5→False
    results = []
    history: list[str] = []
    for _ in range(7):
        history.append(processing_output)
        results.append(_is_task_processing(processing_output, cli_adapter, history, tracker))

    assert results[0] is True
    assert results[1] is True
    assert results[2] is True
    assert results[3] is True
    assert results[4] is True
    assert results[5] is False  # threshold reached (5 consecutive)
    assert results[6] is False

    # After reset, should be True again
    tracker.reset()
    history = [processing_output]
    result = _is_task_processing(processing_output, cli_adapter, history, tracker)
    assert result is True

    tracker.reset()


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

    def create_session(self, cli_type: str = "gemini") -> None:
        self.calls.append(f"create_session(cli_type={cli_type})")

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
    """Test recover_from_timeout function."""
    tmux = MockTmuxCtl()
    cli_adapter = get_adapter("gemini")

    result = recover_from_timeout(tmux, cli_adapter)

    # Check that the function returned a timestamp (float)
    assert isinstance(result, float)

    # Check that the expected methods were called
    assert "send_escape" in tmux.calls
    assert any("send_backspace" in call for call in tmux.calls)
    assert "send_text_then_enter(continue)" in tmux.calls


def test_send_escape_and_wait() -> None:
    """Test _send_escape_and_wait function."""
    tmux = MockTmuxCtl()
    _send_escape_and_wait(tmux)

    # Check that send_escape was called
    assert "send_escape" in tmux.calls


def test_progressive_backspace_until_prompt() -> None:
    """Test _progressive_backspace_until_prompt function."""
    tmux = MockTmuxCtl()
    cli_adapter = get_adapter("gemini")

    _progressive_backspace_until_prompt(tmux, cli_adapter)

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
def test_initialize_session() -> None:
    """Test _initialize_session function."""
    tmux = MockTmuxCtl()
    cli_adapter = get_adapter("gemini")
    config = Config(session="test_session", workdir="/tmp", ai_cmd="test_cmd", cli_type="gemini")
    logger = logging.getLogger("test")

    _initialize_session(tmux, cli_adapter, config, logger)  # type: ignore

    # Check that create_session was called with cli_type
    assert any("create_session" in call for call in tmux.calls)


def test_send_command() -> None:
    """Test _send_command function."""
    tmux = MockTmuxCtl()
    logger = logging.getLogger("test")
    config = Config(session="test", workdir="/tmp", ai_cmd="test")

    # Test with string command
    _send_command(tmux, "test command", config, logger)  # type: ignore
    assert "send_text_then_enter(test command)" in tmux.calls
