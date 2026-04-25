from unittest.mock import patch

from forgeflow.tmux.window import WindowManager


class TestWindowManager:
    def test_should_resize_when_width_below_min(self):
        mgr = WindowManager("test_session")
        with patch("forgeflow.tmux.window.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "80\n"
            assert mgr.should_resize_for_codex() is True

    def test_should_not_resize_when_width_above_min(self):
        mgr = WindowManager("test_session")
        with patch("forgeflow.tmux.window.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "150\n"
            assert mgr.should_resize_for_codex() is False

    def test_resize_window_calls_tmux(self):
        mgr = WindowManager("test_session")
        with patch("forgeflow.tmux.window.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            assert mgr.resize_window(120) is True
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == "tmux"
            assert "resize-window" in cmd

    def test_ensure_codex_width_resizes_when_needed(self):
        mgr = WindowManager("test_session")
        with patch.object(mgr, "get_window_width", return_value=80):
            with patch.object(mgr, "resize_window", return_value=True) as mock_resize:
                mgr.ensure_codex_width()
                mock_resize.assert_called_once_with(120, 40)

    def test_ensure_codex_width_skips_when_large_enough(self):
        mgr = WindowManager("test_session")
        with patch.object(mgr, "get_window_width", return_value=150):
            with patch.object(mgr, "resize_window") as mock_resize:
                mgr.ensure_codex_width()
                mock_resize.assert_not_called()
