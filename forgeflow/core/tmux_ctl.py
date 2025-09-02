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

    @staticmethod
    def _run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True, check=check)

    def session_exists(self) -> bool:
        res = self._run(["tmux", "has-session", "-t", self.cfg.session])
        return res.returncode == 0

    def create_session(self) -> None:
        if not self.session_exists():
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", self.cfg.session, "-c", self.cfg.workdir]
            )
            time.sleep(2)

    def send_text_then_enter(self, text: str) -> None:
        # Send text and enter separately to avoid race conditions
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, text])
        time.sleep(0.1)
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-m"])  # Enter

    def send_enter(self) -> None:
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-m"])  # Enter

    def send_escape(self) -> None:
        subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "Escape"])  # ESC

    def send_backspace(self, count: int = 10) -> None:
        for _ in range(count):
            subprocess.run(["tmux", "send-keys", "-t", self.cfg.session, "C-h"])  # Backspace

    def capture_output(self) -> str:
        res = self._run(["tmux", "capture-pane", "-t", self.cfg.session, "-p"])  # -p to print
        return res.stdout
