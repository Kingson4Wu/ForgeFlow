from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass

from forgeflow.config import SEND_KEY_DELAY, SESSION_CREATE_DELAY

logger = logging.getLogger("forgeflow")


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
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
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

                if cli_type == "codex":
                    from forgeflow.tmux.window import WindowManager

                    wm = WindowManager(self.cfg.session)
                    wm.ensure_codex_width()

            time.sleep(SESSION_CREATE_DELAY)
        else:
            logger.info(f"Session {self.cfg.session} already exists")
            # Session already exists, check if we need to resize for codex
            if cli_type == "codex":
                from forgeflow.tmux.window import WindowManager

                wm = WindowManager(self.cfg.session)
                wm.ensure_codex_width()
            else:
                logger.debug(f"CLI type is {cli_type}, not adjusting window width")

    def send_text_then_enter(self, text: str) -> None:
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, text], check=False)
        time.sleep(SEND_KEY_DELAY)
        # nosec B603
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-m"], check=False)  # Enter

    def send_enter(self) -> None:
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-m"], check=False)

    def send_escape(self) -> None:
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "Escape"], check=False)

    def send_backspace(self, count: int = 10) -> None:
        for _ in range(count):
            subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-h"], check=False)

    def capture_output(self, include_ansi: bool = False) -> str:
        # -p to print to stdout; -e to include escape sequences (ANSI)
        cmd = ["tmux", "capture-pane", "-t", self.cfg.session, "-p"]
        if include_ansi:
            cmd.insert(2, "-e")
        res = self._run(cmd)
        return str(res.stdout)
