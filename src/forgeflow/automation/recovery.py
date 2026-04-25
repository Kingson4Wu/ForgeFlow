from __future__ import annotations

import logging
import time

from forgeflow.adapters.base import CLIAdapter
from forgeflow.config import (
    BACKSPACE_INCREMENT,
    INITIAL_BACKSPACE_COUNT,
    MAX_BACKSPACE_COUNT,
    MAX_RECOVERY_ATTEMPTS,
    RECOVERY_STEP_DELAY,
)
from forgeflow.tmux.ctl import TmuxCtl

logger = logging.getLogger("forgeflow")


def recover_from_timeout(tmux: TmuxCtl, adapter: CLIAdapter) -> float:
    """Attempt recovery when input prompt seems stuck.
    Returns the new timestamp for last_input_prompt_time."""
    logger.info("Input prompt timeout exceeded, trying ESC/backspace recovery → continue")
    _send_escape_and_wait(tmux)
    _progressive_backspace_until_prompt(tmux, adapter)
    return _send_continue_and_return_timestamp(tmux)


def _send_escape_and_wait(tmux: TmuxCtl) -> None:
    tmux.send_escape()
    time.sleep(RECOVERY_STEP_DELAY)


def _progressive_backspace_until_prompt(tmux: TmuxCtl, adapter: CLIAdapter) -> None:
    backspace_num = INITIAL_BACKSPACE_COUNT
    for _ in range(MAX_RECOVERY_ATTEMPTS):
        tmux.send_backspace(backspace_num)
        time.sleep(RECOVERY_STEP_DELAY)
        output = tmux.capture_output(include_ansi=adapter.wants_ansi())
        if adapter.is_input_prompt(output):
            break
        backspace_num = min(backspace_num + BACKSPACE_INCREMENT, MAX_BACKSPACE_COUNT)


def _send_continue_and_return_timestamp(tmux: TmuxCtl) -> float:
    tmux.send_text_then_enter("continue")
    return time.time()
