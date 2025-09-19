from forgeflow.core.automation import (
    Config,
    _recover_from_timeout,
    is_task_processing,
    setup_logger,
)
from forgeflow.core.cli_adapters.factory import get_cli_adapter


def test_config_defaults():
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


def test_config_custom_values():
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


def test_is_task_processing():
    """Test is_task_processing function."""
    # Get a CLI adapter for testing
    cli_adapter = get_cli_adapter("gemini")

    # Test with empty output
    assert is_task_processing("", cli_adapter) is False

    # Test with output that doesn't indicate task processing
    output = "Some regular output"
    assert is_task_processing(output, cli_adapter) is False


def test_setup_logger():
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
    def __init__(self):
        self.calls = []

    def send_escape(self):
        self.calls.append("send_escape")

    def send_backspace(self, count):
        self.calls.append(f"send_backspace({count})")

    def send_text_then_enter(self, text):
        self.calls.append(f"send_text_then_enter({text})")

    def capture_output(self, include_ansi=False):
        self.calls.append(f"capture_output(include_ansi={include_ansi})")
        # Return output that indicates input prompt for the first few calls,
        # then return output that doesn't indicate input prompt to test the loop
        if len([c for c in self.calls if "capture_output" in c]) <= 2:
            return "> Type your message"
        return "Some other output"


class MockLogger:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)


def test_recover_from_timeout():
    """Test _recover_from_timeout function."""
    tmux = MockTmuxCtl()
    cli_adapter = get_cli_adapter("gemini")
    logger = MockLogger()

    result = _recover_from_timeout(tmux, cli_adapter, logger)

    # Check that the function returned a timestamp (float)
    assert isinstance(result, float)

    # Check that the expected methods were called
    assert "send_escape" in tmux.calls
    assert any("send_backspace" in call for call in tmux.calls)
    assert "send_text_then_enter(continue)" in tmux.calls
