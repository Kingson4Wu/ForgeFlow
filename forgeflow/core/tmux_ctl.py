from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass


@dataclass
class TmuxConfig:
    session: str
    workdir: str


class TmuxCtl:
    def __init__(self, cfg: TmuxConfig) -> None:
        self.cfg = cfg
        self._ensure_tmux_available()

    @staticmethod
    def _run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
        # nosec B603
        return subprocess.run(cmd, capture_output=True, text=True, check=check)

    @staticmethod
    def _ensure_tmux_available() -> None:
        try:
            # nosec B603
            subprocess.run(["tmux", "-V"], capture_output=True, text=True, check=True)
        except Exception as e:
            raise RuntimeError(
                "tmux is required but not found. Please install tmux and ensure it is on PATH."
            ) from e

    def session_exists(self) -> bool:
        res = self._run(["tmux", "has-session", "-t", self.cfg.session])
        return res.returncode == 0

    def create_session(self, cli_type: str = "gemini") -> None:
        if not self.session_exists():
            # Build the command to create session
            cmd = ["tmux", "new-session", "-d", "-s", self.cfg.session, "-c", self.cfg.workdir]

            # For codex CLI type, ensure window width is at least 120
            if cli_type == "codex":
                if self._should_set_codex_width():
                    cmd.extend(["-x", "120"])

            # nosec B603
            subprocess.run(cmd, check=False)
            time.sleep(2)
        else:
            # Session already exists, check if we need to resize for codex
            if cli_type == "codex":
                self._ensure_codex_window_width()

    def _should_set_codex_width(self) -> bool:
        """Check if we should set the window width to 120 for codex.

        Returns:
            bool: True if terminal width is less than 120 or can't be determined.
        """
        try:
            # nosec B603
            result = subprocess.run(["tput", "cols"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                current_width = int(result.stdout.strip())
                # If current width is less than 120, we should set width to 120
                return current_width < 120
        except Exception:
            pass

        # If we can't determine terminal width, default to setting it to 120
        return True

    def _get_window_width(self) -> int:
        """Get the current window width of the session.

        Returns:
            int: The current window width, or -1 if unable to determine.
        """
        try:
            # nosec B603
            result = subprocess.run(
                ["tmux", "display-message", "-p", "-t", self.cfg.session, "#{window_width}"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return int(result.stdout.strip())
        except (ValueError, subprocess.SubprocessError):
            pass

        return -1

    def _resize_window_width(self, width: int) -> bool:
        """Resize the window width of the session.

        Args:
            width: The desired width to set.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # nosec B603
            result = subprocess.run(
                ["tmux", "resize-window", "-t", self.cfg.session, "-x", str(width)], check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def _ensure_codex_window_width(self) -> None:
        """Ensure window width is at least 120 for codex sessions."""
        current_width = self._get_window_width()
        # If current width is valid and less than 120, resize window to 120
        if 0 <= current_width < 120:
            self._resize_window_width(120)

    def send_text_then_enter(self, text: str) -> None:
        # Send text and enter separately to avoid race conditions
        # nosec B603
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, text], check=False)
        time.sleep(0.1)
        # nosec B603
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-m"], check=False)  # Enter

    def send_enter(self) -> None:
        # nosec B603
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-m"], check=False)  # Enter

    def send_escape(self) -> None:
        # nosec B603
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "Escape"], check=False)  # ESC

    def send_backspace(self, count: int = 10) -> None:
        for _ in range(count):
            # nosec B603
            subprocess.run(
                ["tmux", "send-keys", "-t", self.cfg.session, "C-h"], check=False
            )  # Backspace

    def capture_output(self, include_ansi: bool = False) -> str:
        # -p to print to stdout; -e to include escape sequences (ANSI)
        cmd = ["tmux", "capture-pane", "-t", self.cfg.session, "-p"]
        if include_ansi:
            cmd.insert(2, "-e")
        res = self._run(cmd)
        return str(res.stdout)
