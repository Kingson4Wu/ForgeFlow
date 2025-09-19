from unittest.mock import MagicMock, patch

import pytest

from forgeflow.core.tmux_ctl import TmuxConfig, TmuxCtl


@pytest.fixture
def tmux_config():
    return TmuxConfig(session="test_session", workdir="/tmp")


@pytest.fixture
def tmux_ctl(tmux_config):
    return TmuxCtl(tmux_config)


def test_tmux_config():
    """Test TmuxConfig dataclass."""
    config = TmuxConfig(session="test_session", workdir="/tmp")
    assert config.session == "test_session"
    assert config.workdir == "/tmp"


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_tmux_available_success(mock_run, tmux_ctl):
    """Test _ensure_tmux_available when tmux is available."""
    mock_run.return_value = MagicMock(returncode=0)
    # This should not raise an exception
    tmux_ctl._ensure_tmux_available()


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_tmux_available_failure(mock_run, tmux_ctl):
    """Test _ensure_tmux_available when tmux is not available."""
    mock_run.side_effect = Exception("tmux not found")

    with pytest.raises(RuntimeError) as excinfo:
        tmux_ctl._ensure_tmux_available()

    assert "tmux is required but not found" in str(excinfo.value)


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_session_exists_true(mock_run, tmux_ctl):
    """Test session_exists when session exists."""
    mock_run.return_value = MagicMock(returncode=0)
    assert tmux_ctl.session_exists() is True


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_session_exists_false(mock_run, tmux_ctl):
    """Test session_exists when session does not exist."""
    mock_run.return_value = MagicMock(returncode=1)
    assert tmux_ctl.session_exists() is False


@patch("forgeflow.core.tmux_ctl.subprocess.run")
@patch.object(TmuxCtl, "session_exists")
def test_create_session_new(mock_session_exists, mock_run, tmux_ctl):
    """Test create_session when session does not exist."""
    mock_session_exists.return_value = False
    tmux_ctl.create_session()
    # Check that subprocess.run was called to create a new session
    assert mock_run.called


@patch("forgeflow.core.tmux_ctl.subprocess.run")
@patch.object(TmuxCtl, "session_exists")
def test_create_session_exists(mock_session_exists, mock_run, tmux_ctl):
    """Test create_session when session already exists."""
    mock_session_exists.return_value = True
    tmux_ctl.create_session()
    # Check that subprocess.run was not called to create a new session
    mock_run.assert_not_called()


@patch("forgeflow.core.tmux_ctl.subprocess.run")
@patch("forgeflow.core.tmux_ctl.time.sleep")
def test_send_text_then_enter(mock_sleep, mock_run, tmux_ctl):
    """Test send_text_then_enter method."""
    tmux_ctl.send_text_then_enter("test command")
    # Check that subprocess.run was called twice
    assert mock_run.call_count == 2
    # Check that time.sleep was called
    assert mock_sleep.called


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_send_enter(mock_run, tmux_ctl):
    """Test send_enter method."""
    tmux_ctl.send_enter()
    mock_run.assert_called_once_with(
        ["tmux", "send-keys", "-t", "test_session", "C-m"], check=False
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_send_escape(mock_run, tmux_ctl):
    """Test send_escape method."""
    tmux_ctl.send_escape()
    mock_run.assert_called_once_with(
        ["tmux", "send-keys", "-t", "test_session", "Escape"], check=False
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_send_backspace(mock_run, tmux_ctl):
    """Test send_backspace method."""
    tmux_ctl.send_backspace(3)
    # Check that subprocess.run was called 3 times
    assert mock_run.call_count == 3
    mock_run.assert_called_with(["tmux", "send-keys", "-t", "test_session", "C-h"], check=False)


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_capture_output(mock_run, tmux_ctl):
    """Test capture_output method."""
    mock_run.return_value = MagicMock(stdout="test output")
    result = tmux_ctl.capture_output()
    mock_run.assert_called_once_with(
        ["tmux", "capture-pane", "-t", "test_session", "-p"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result == "test output"


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_capture_output_with_ansi(mock_run, tmux_ctl):
    """Test capture_output method with ANSI codes."""
    mock_run.return_value = MagicMock(stdout="test output with ansi")
    result = tmux_ctl.capture_output(include_ansi=True)
    mock_run.assert_called_once_with(
        ["tmux", "capture-pane", "-e", "-t", "test_session", "-p"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result == "test output with ansi"
