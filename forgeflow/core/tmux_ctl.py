from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


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
        logger.debug(f"Creating session: {self.cfg.session}, CLI type: {cli_type}")
        if not self.session_exists():
            logger.info(f"Session {self.cfg.session} does not exist, creating new session")
            # Build the command to create session
            cmd = ["tmux", "new-session", "-d", "-s", self.cfg.session, "-c", self.cfg.workdir]
            logger.debug(f"Base command: {' '.join(cmd)}")

            # For codex CLI type, ensure window width is at least 120
            resize_needed = False
            if cli_type == "codex":
                logger.debug("CLI type is codex, checking if window width should be set to 120")
                should_set_width = self._should_set_codex_width()
                logger.debug(f"Should set codex width: {should_set_width}")
                if should_set_width:
                    resize_needed = True
                    logger.info("Will resize window to 120x40 after creation")
                else:
                    logger.info("Not resizing window")

            # nosec B603
            logger.debug(f"Executing tmux command: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                logger.warning(f"Failed to create tmux session with command: {' '.join(cmd)}")
                logger.warning(
                    f"Return code: {result.returncode}, Stderr: {result.stderr.decode() if isinstance(result.stderr, bytes) else result.stderr}"
                )
            else:
                logger.info(f"Successfully created tmux session: {self.cfg.session}")

                # If we need to resize for codex, do it now
                if resize_needed:
                    logger.info("Resizing window to 120x40 for codex CLI")
                    resize_result = self._resize_window_width(120)
                    if resize_result:
                        # Also resize height to 40
                        try:
                            subprocess.run(
                                ["tmux", "resize-window", "-t", self.cfg.session, "-y", "40"],
                                check=False,
                            )
                            logger.info("Successfully resized window to 120x40 for codex CLI")
                        except Exception as e:
                            logger.warning(f"Failed to set window height to 40: {e}")
                    else:
                        logger.warning("Failed to resize window width for codex CLI")
            time.sleep(2)
        else:
            logger.info(f"Session {self.cfg.session} already exists")
            # Session already exists, check if we need to resize for codex
            if cli_type == "codex":
                logger.info("CLI type is codex, ensuring window width is at least 120")
                self._ensure_codex_window_width()
            else:
                logger.debug(f"CLI type is {cli_type}, not adjusting window width")

    def _should_set_codex_width(self) -> bool:
        """Check if we should set the window width to 120 for codex.

        Returns:
            bool: True if terminal width is less than 120 or can't be determined.
        """
        logger.debug("Checking if codex window width should be set to 120")
        try:
            # nosec B603
            result = subprocess.run(["tput", "cols"], capture_output=True, text=True, check=False)
            logger.debug(
                f"tput cols result - return code: {result.returncode}, stdout: '{result.stdout.strip()}', stderr: '{result.stderr.strip()}'"
            )
            if result.returncode == 0:
                current_width = int(result.stdout.strip())
                logger.debug(f"Current terminal width: {current_width}")
                # If current width is less than 120, we should set width to 120
                should_set = current_width < 120
                logger.debug(
                    f"Should set width to 120: {should_set} (current: {current_width} < 120)"
                )
                return should_set
            else:
                logger.warning(
                    f"Failed to determine terminal width, return code: {result.returncode}"
                )
        except Exception as e:
            logger.warning(f"Failed to determine terminal width: {e}")
            logger.debug("Exception details", exc_info=True)

        # If we can't determine terminal width, default to setting it to 120
        logger.debug(
            "Defaulting to set width to 120 because terminal width could not be determined"
        )
        return True

    def _get_window_width(self) -> int:
        """Get the current window width of the session.

        Returns:
            int: The current window width, or -1 if unable to determine.
        """
        logger.debug(f"Getting window width for session: {self.cfg.session}")
        try:
            # nosec B603
            result = subprocess.run(
                ["tmux", "display-message", "-p", "-t", self.cfg.session, "#{window_width}"],
                capture_output=True,
                text=True,
                check=False,
            )

            logger.debug(
                f"tmux display-message result - return code: {result.returncode}, stdout: '{result.stdout.strip()}', stderr: '{result.stderr.strip()}'"
            )

            if result.returncode == 0:
                width = int(result.stdout.strip())
                logger.debug(f"Current window width for session {self.cfg.session}: {width}")
                return width
            else:
                logger.warning(
                    f"Failed to get window width for session {self.cfg.session}, return code: {result.returncode}"
                )
        except (ValueError, subprocess.SubprocessError) as e:
            logger.warning(f"Failed to get window width for session {self.cfg.session}: {e}")
            logger.debug("Exception details", exc_info=True)
        except Exception as e:
            logger.warning(
                f"Unexpected error when getting window width for session {self.cfg.session}: {e}"
            )
            logger.debug("Exception details", exc_info=True)

        logger.debug(f"Returning -1 for window width of session {self.cfg.session}")
        return -1

    def _resize_window_width(self, width: int) -> bool:
        """Resize the window width of the session.

        Args:
            width: The desired width to set.

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.debug(f"Resizing window width for session {self.cfg.session} to {width}")
        try:
            # nosec B603
            result = subprocess.run(
                ["tmux", "resize-window", "-t", self.cfg.session, "-x", str(width)], check=False
            )
            logger.debug(f"tmux resize-window result - return code: {result.returncode}")
            success = result.returncode == 0
            if success:
                logger.info(
                    f"Successfully resized window width for session {self.cfg.session} to {width}"
                )
            else:
                logger.warning(
                    f"Failed to resize window width for session {self.cfg.session} to {width}, return code: {result.returncode}"
                )
            return success
        except Exception as e:
            logger.warning(
                f"Failed to resize window width for session {self.cfg.session} to {width}: {e}"
            )
            logger.debug("Exception details", exc_info=True)
            return False

    def _ensure_codex_window_width(self) -> None:
        """Ensure window width is at least 120 for codex sessions."""
        logger.debug(f"Ensuring codex window width for session: {self.cfg.session}")
        current_width = self._get_window_width()
        logger.debug(f"Current window width: {current_width}")
        # If we can't determine the current width, try to resize anyway
        # If current width is valid and less than 120, resize window to 120
        if current_width < 0 or (0 <= current_width < 120):
            logger.info(f"Window width {current_width} is less than 120, resizing to 120")
            success = self._resize_window_width(120)
            if not success:
                logger.warning("Failed to resize window width to 120 for codex session")
            else:
                logger.info("Successfully resized window width to 120 for codex session")
        else:
            logger.debug(f"Window width {current_width} is already >= 120, no resize needed")

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
