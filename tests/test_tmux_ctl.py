from unittest.mock import MagicMock, patch

import pytest

from forgeflow.core.tmux_ctl import TmuxConfig, TmuxCtl


@pytest.fixture
def tmux_config() -> TmuxConfig:
    return TmuxConfig(session="test_session", workdir="/tmp")


@pytest.fixture
def tmux_ctl(tmux_config) -> TmuxCtl:
    return TmuxCtl(tmux_config)


def test_tmux_config() -> None:
    """Test TmuxConfig dataclass."""
    config = TmuxConfig(session="test_session", workdir="/tmp")
    assert config.session == "test_session"
    assert config.workdir == "/tmp"


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_tmux_available_success(mock_run, tmux_ctl) -> None:
    """Test _ensure_tmux_available when tmux is available."""
    mock_run.return_value = MagicMock(returncode=0)
    # This should not raise an exception
    tmux_ctl._ensure_tmux_available()


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_tmux_available_failure(mock_run, tmux_ctl) -> None:
    """Test _ensure_tmux_available when tmux is not available."""
    mock_run.side_effect = Exception("tmux not found")

    with pytest.raises(RuntimeError) as excinfo:
        tmux_ctl._ensure_tmux_available()

    assert "tmux is required but not found" in str(excinfo.value)


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_session_exists_true(mock_run, tmux_ctl) -> None:
    """Test session_exists when session exists."""
    mock_run.return_value = MagicMock(returncode=0)
    assert tmux_ctl.session_exists() is True


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_session_exists_false(mock_run, tmux_ctl) -> None:
    """Test session_exists when session does not exist."""
    mock_run.return_value = MagicMock(returncode=1)
    assert tmux_ctl.session_exists() is False


@patch("forgeflow.core.tmux_ctl.subprocess.run")
@patch.object(TmuxCtl, "session_exists")
def test_create_session_new(mock_session_exists, mock_run, tmux_ctl) -> None:
    """Test create_session when session does not exist."""
    mock_session_exists.return_value = False
    tmux_ctl.create_session()
    # Check that subprocess.run was called to create a new session
    assert mock_run.called


@patch("forgeflow.core.tmux_ctl.subprocess.run")
@patch.object(TmuxCtl, "session_exists")
def test_create_session_exists(mock_session_exists, mock_run, tmux_ctl) -> None:
    """Test create_session when session already exists."""
    mock_session_exists.return_value = True
    tmux_ctl.create_session()
    # Check that subprocess.run was not called to create a new session
    mock_run.assert_not_called()


@patch("forgeflow.core.tmux_ctl.subprocess.run")
@patch.object(TmuxCtl, "session_exists")
@patch.object(TmuxCtl, "_ensure_codex_window_width")
def test_create_session_exists_codex(
    mock_ensure_width, mock_session_exists, mock_run, tmux_ctl
) -> None:
    """Test create_session when session already exists with codex type."""
    mock_session_exists.return_value = True
    tmux_ctl.create_session("codex")
    # Check that _ensure_codex_window_width was called for codex type
    mock_ensure_width.assert_called_once()


@patch("forgeflow.core.tmux_ctl.subprocess.run")
@patch("forgeflow.core.tmux_ctl.time.sleep")
def test_send_text_then_enter(mock_sleep, mock_run, tmux_ctl) -> None:
    """Test send_text_then_enter method."""
    tmux_ctl.send_text_then_enter("test command")
    # Check that subprocess.run was called twice
    assert mock_run.call_count == 2
    # Check that time.sleep was called
    assert mock_sleep.called


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_send_enter(mock_run, tmux_ctl) -> None:
    """Test send_enter method."""
    tmux_ctl.send_enter()
    mock_run.assert_called_once_with(
        ["tmux", "send-keys", "-t", "test_session", "C-m"], check=False
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_send_escape(mock_run, tmux_ctl) -> None:
    """Test send_escape method."""
    tmux_ctl.send_escape()
    mock_run.assert_called_once_with(
        ["tmux", "send-keys", "-t", "test_session", "Escape"], check=False
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_send_backspace(mock_run, tmux_ctl) -> None:
    """Test send_backspace method."""
    tmux_ctl.send_backspace(3)
    # Check that subprocess.run was called 3 times
    assert mock_run.call_count == 3
    mock_run.assert_called_with(["tmux", "send-keys", "-t", "test_session", "C-h"], check=False)


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_capture_output(mock_run, tmux_ctl) -> None:
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
def test_capture_output_with_ansi(mock_run, tmux_ctl) -> None:
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


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_codex_window_width_no_resize(mock_run, tmux_ctl) -> None:
    """Test _ensure_codex_window_width when no resize is needed."""
    # Mock the display-message call to return a width >= 120
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="120\n"),  # display-message
    ]

    # Call the method
    tmux_ctl._ensure_codex_window_width()

    # Check that only display-message was called, no resize
    assert mock_run.call_count == 1
    mock_run.assert_any_call(
        ["tmux", "display-message", "-p", "-t", "test_session", "#{window_width}"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_codex_window_width_with_resize(mock_run, tmux_ctl) -> None:
    """Test _ensure_codex_window_width when resize is needed."""
    # Mock the display-message call to return a width < 120
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="80\n"),  # display-message
        MagicMock(returncode=0),  # resize-window
    ]

    # Call the method
    tmux_ctl._ensure_codex_window_width()

    # Check that both display-message and resize-window were called
    assert mock_run.call_count == 2
    mock_run.assert_any_call(
        ["tmux", "display-message", "-p", "-t", "test_session", "#{window_width}"],
        capture_output=True,
        text=True,
        check=False,
    )
    mock_run.assert_any_call(
        ["tmux", "resize-window", "-t", "test_session", "-x", "120"], check=False
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_codex_window_width_display_error(mock_run, tmux_ctl) -> None:
    """Test _ensure_codex_window_width when display-message fails."""
    # Mock the display-message call to fail
    mock_run.side_effect = [
        MagicMock(returncode=1),  # display-message fails
    ]

    # Call the method - should not raise exception
    tmux_ctl._ensure_codex_window_width()

    # Check that only display-message was attempted
    assert mock_run.call_count == 1


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_ensure_codex_window_width_resize_error(mock_run, tmux_ctl) -> None:
    """Test _ensure_codex_window_width when resize-window fails."""
    # Mock the display-message call to return a width < 120 and resize to fail
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="80\n"),  # display-message
        MagicMock(returncode=1),  # resize-window fails
    ]

    # Call the method - should not raise exception
    tmux_ctl._ensure_codex_window_width()

    # Check that both calls were made
    assert mock_run.call_count == 2


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_get_window_width_success(mock_run, tmux_ctl) -> None:
    """Test _get_window_width when successful."""
    mock_run.return_value = MagicMock(returncode=0, stdout="120\n")
    result = tmux_ctl._get_window_width()
    assert result == 120
    mock_run.assert_called_once_with(
        ["tmux", "display-message", "-p", "-t", "test_session", "#{window_width}"],
        capture_output=True,
        text=True,
        check=False,
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_get_window_width_failure(mock_run, tmux_ctl) -> None:
    """Test _get_window_width when tmux command fails."""
    mock_run.return_value = MagicMock(returncode=1)
    result = tmux_ctl._get_window_width()
    assert result == -1


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_get_window_width_value_error(mock_run, tmux_ctl) -> None:
    """Test _get_window_width when parsing fails."""
    mock_run.return_value = MagicMock(returncode=0, stdout="invalid\n")
    result = tmux_ctl._get_window_width()
    assert result == -1


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_resize_window_width_success(mock_run, tmux_ctl) -> None:
    """Test _resize_window_width when successful."""
    mock_run.return_value = MagicMock(returncode=0)
    result = tmux_ctl._resize_window_width(120)
    assert result is True
    mock_run.assert_called_once_with(
        ["tmux", "resize-window", "-t", "test_session", "-x", "120"], check=False
    )


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_resize_window_width_failure(mock_run, tmux_ctl) -> None:
    """Test _resize_window_width when tmux command fails."""
    mock_run.return_value = MagicMock(returncode=1)
    result = tmux_ctl._resize_window_width(120)
    assert result is False


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_resize_window_width_exception(mock_run, tmux_ctl) -> None:
    """Test _resize_window_width when subprocess raises exception."""
    mock_run.side_effect = Exception("Subprocess error")
    result = tmux_ctl._resize_window_width(120)
    assert result is False


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_should_set_codex_width_success_narrow(mock_run, tmux_ctl) -> None:
    """Test _should_set_codex_width when terminal is narrow."""
    mock_run.return_value = MagicMock(returncode=0, stdout="80\n")
    result = tmux_ctl._should_set_codex_width()
    assert result is True
    mock_run.assert_called_once_with(["tput", "cols"], capture_output=True, text=True, check=False)


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_should_set_codex_width_success_wide(mock_run, tmux_ctl) -> None:
    """Test _should_set_codex_width when terminal is wide enough."""
    mock_run.return_value = MagicMock(returncode=0, stdout="150\n")
    result = tmux_ctl._should_set_codex_width()
    assert result is False


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_should_set_codex_width_tput_failure(mock_run, tmux_ctl) -> None:
    """Test _should_set_codex_width when tput command fails."""
    mock_run.return_value = MagicMock(returncode=1)
    result = tmux_ctl._should_set_codex_width()
    assert result is True


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_should_set_codex_width_value_error(mock_run, tmux_ctl) -> None:
    """Test _should_set_codex_width when parsing fails."""
    mock_run.return_value = MagicMock(returncode=0, stdout="invalid\n")
    result = tmux_ctl._should_set_codex_width()
    assert result is True


@patch("forgeflow.core.tmux_ctl.subprocess.run")
def test_should_set_codex_width_exception(mock_run, tmux_ctl) -> None:
    """Test _should_set_codex_width when subprocess raises exception."""
    mock_run.side_effect = Exception("Subprocess error")
    result = tmux_ctl._should_set_codex_width()
    assert result is True
