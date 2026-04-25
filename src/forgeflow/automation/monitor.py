from __future__ import annotations

import logging
import time

from forgeflow.adapters.base import CLIAdapter
from forgeflow.adapters.registry import get_adapter
from forgeflow.config import (
    NO_PROCESSING_THRESHOLD,
    OUTPUT_HISTORY_SIZE,
    UNCHANGED_OUTPUT_THRESHOLD,
    Config,
)
from forgeflow.notifier import send_notification
from forgeflow.state import UnchangedTracker
from forgeflow.tmux.ctl import TmuxConfig, TmuxCtl

logger = logging.getLogger("forgeflow")


def run_monitor_mode(cfg: Config) -> int:
    log = logging.getLogger("forgeflow")
    tmux = TmuxCtl(TmuxConfig(session=cfg.session, workdir=cfg.workdir or ""))
    cli_adapter = get_adapter(cfg.cli_type)

    tmux.create_session(cfg.cli_type)

    if cfg.cli_type == "gemini":
        log.info(
            "Using default Gemini CLI adapter. If monitoring a session with a different AI CLI tool, "
            "specify the appropriate --cli-type parameter for accurate monitoring."
        )

    log.info("Monitor mode started. Only monitoring task processing status.")

    was_processing = False
    no_processing_count = 0
    output_history: list[str] = []
    max_history = OUTPUT_HISTORY_SIZE
    unchanged_tracker = UnchangedTracker(UNCHANGED_OUTPUT_THRESHOLD)

    try:
        while True:
            output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
            output_history.append(output)
            output_history = output_history[-max_history:]
            is_processing = _is_task_processing(
                output, cli_adapter, output_history, unchanged_tracker
            )

            if is_processing:
                if not was_processing:
                    log.info("Task processing started")
                was_processing = True
                no_processing_count = 0
            else:
                if was_processing:
                    no_processing_count += 1
                    if no_processing_count >= NO_PROCESSING_THRESHOLD:
                        _send_task_stopped_notification(log)
                        was_processing = False
                        no_processing_count = 0
                else:
                    no_processing_count = 0

            time.sleep(cfg.poll_interval)

    except KeyboardInterrupt:
        log.info("KeyboardInterrupt received. Exiting gracefully.")
        return 0
    except Exception as e:
        log.exception(f"Unhandled error: {e}")
        return 1

    log.info("Monitor mode finished.")
    return 0


def _is_task_processing(
    output: str,
    cli_adapter: CLIAdapter,
    history: list[str],
    tracker: UnchangedTracker,
) -> bool:
    if tracker.is_unchanged_too_long(output):
        return False
    return cli_adapter.is_task_processing(history)


def _send_task_stopped_notification(log: logging.Logger) -> None:
    message = "ForgeFlow task has stopped processing. Please check what happened."
    log.info(f"Task stopped. Sending notification: {message}")
    send_notification("ForgeFlow Task Stopped", message)
