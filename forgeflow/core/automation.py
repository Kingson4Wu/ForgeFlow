from __future__ import annotations

import logging
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass

from .cli_adapters.base import CLIAdapter
from .cli_adapters.factory import get_cli_adapter
from .notifier import send_notification
from .rule_loader import get_rules
from .rules import next_command
from .tmux_ctl import TmuxConfig, TmuxCtl

# Constants for timing and behavior
SESSION_CREATE_DELAY = 1.0
CLI_START_DELAY = 5.0
COMMAND_EXECUTION_DELAY = 2.0
RECOVERY_STEP_DELAY = 0.5
MAX_RECOVERY_ATTEMPTS = 20
INITIAL_BACKSPACE_COUNT = 10
MAX_BACKSPACE_COUNT = 200
BACKSPACE_INCREMENT = 10
LOG_COMMAND_TRUNCATE_LENGTH = 120

# Constants for tracking unchanged outputs
UNCHANGED_OUTPUT_THRESHOLD = 5

# Module-level variables for tracking consecutive unchanged outputs
_previous_output = ""
_consecutive_unchanged_count = 0


@dataclass
class Config:
    session: str
    workdir: str
    ai_cmd: str
    poll_interval: int = 10
    input_prompt_timeout: int = 2000  # seconds
    log_file: str = "forgeflow.log"
    log_to_console: bool = True
    project: str | None = None
    task: str | None = None
    cli_type: str = "gemini"  # Default to gemini
    log_level: str = "INFO"


def setup_logger(path: str, to_console: bool = True, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("forgeflow")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
    logger.addHandler(fh)

    if to_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
        logger.addHandler(ch)

    return logger


def run_automation(cfg: Config) -> int:
    log = setup_logger(cfg.log_file, cfg.log_to_console, cfg.log_level)
    tmux = TmuxCtl(TmuxConfig(session=cfg.session, workdir=cfg.workdir))
    cli_adapter = get_cli_adapter(cfg.cli_type)

    # Initialize session
    _initialize_session(tmux, cli_adapter, cfg, log)

    # Run main automation loop
    return _run_automation_loop(tmux, cli_adapter, cfg, log)


def run_monitor_mode(cfg: Config) -> int:
    """Run in monitor-only mode that only sends notifications when tasks stop processing."""
    log = setup_logger(cfg.log_file, cfg.log_to_console, cfg.log_level)
    tmux = TmuxCtl(TmuxConfig(session=cfg.session, workdir=cfg.workdir or ""))
    cli_adapter = get_cli_adapter(cfg.cli_type)

    # Initialize session with proper width for codex
    tmux.create_session(cfg.cli_type)

    # Warn if using default Gemini adapter, as user might want to specify a different CLI type
    if cfg.cli_type == "gemini":
        log.info(
            "Using default Gemini CLI adapter. If monitoring a session with a different AI CLI tool, "
            "specify the appropriate --cli-type parameter for accurate monitoring."
        )

    log.info("Monitor mode started. Only monitoring task processing status.")

    # Track task processing state for notifications
    was_processing = False
    # Track consecutive checks with no task processing
    no_processing_count = 0
    # Require 3 consecutive checks with no processing before sending notification
    NO_PROCESSING_THRESHOLD = 3

    try:
        while True:
            output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
            is_processing = is_task_processing(output, cli_adapter)

            # Check for task processing state changes and send notifications
            if is_processing:
                # Task is currently processing
                if not was_processing:
                    # Transition from not processing to processing
                    log.info("Task processing started")
                was_processing = True
                no_processing_count = 0
            else:
                # Task is not currently processing
                if was_processing:
                    # Transition from processing to not processing
                    # Start counting consecutive non-processing checks
                    no_processing_count += 1
                    if no_processing_count >= NO_PROCESSING_THRESHOLD:
                        # Task has been stopped for 3 consecutive checks
                        # log.info(f"Full output: {output}")
                        _send_task_stopped_notification(log)
                        # Reset state after sending notification
                        was_processing = False
                        no_processing_count = 0
                else:
                    # Still not processing
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


def _initialize_session(
    tmux: TmuxCtl, cli_adapter: CLIAdapter, cfg: Config, log: logging.Logger
) -> None:
    """Initialize tmux session and ensure AI CLI is running."""
    tmux.create_session(cfg.cli_type)
    time.sleep(SESSION_CREATE_DELAY)
    output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
    if not cli_adapter.is_ai_cli_exist(output):
        log.info(f"Ensuring AI CLI running: {cfg.ai_cmd}")
        tmux.send_text_then_enter(cfg.ai_cmd)
        time.sleep(CLI_START_DELAY)


def _run_automation_loop(
    tmux: TmuxCtl, cli_adapter: CLIAdapter, cfg: Config, log: logging.Logger
) -> int:
    """Run the main automation loop."""
    rules = get_rules(cfg)
    last_output = ""
    last_input_prompt_time = time.time()
    # Track task processing state for notifications
    was_processing = False

    log.info("Automation started.")

    try:
        while True:
            output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
            if output != last_output:
                last_output = output

            is_processing = is_task_processing(output, cli_adapter)

            # Check for task processing state changes and send notifications
            if was_processing and not is_processing:
                # Task has stopped processing
                _send_task_stopped_notification(log)
            was_processing = is_processing

            if cli_adapter.is_input_prompt(output) and not is_processing:
                last_input_prompt_time = time.time()
                cmd = next_command(output, rules, cfg.cli_type)
                if cmd is None:
                    log.info("No more commands to execute. Stopping.")
                    break
                _send_command(tmux, cmd, log)
                time.sleep(COMMAND_EXECUTION_DELAY)

            elif cli_adapter.is_input_prompt_with_text(output) and not is_processing:
                _handle_input_with_text(tmux, log)
                time.sleep(COMMAND_EXECUTION_DELAY)

            else:
                # Timeout recovery or wait
                if time.time() - last_input_prompt_time > cfg.input_prompt_timeout:
                    last_input_prompt_time = _recover_from_timeout(tmux, cli_adapter, log)
                else:
                    log.info("Not in input prompt, waiting...")
                time.sleep(cfg.poll_interval)

    except KeyboardInterrupt:
        log.info("KeyboardInterrupt received. Exiting gracefully.")
        return 0
    except Exception as e:
        log.exception(f"Unhandled error: {e}")
        return 1

    log.info("Automation finished.")
    return 0


def _send_command(tmux: TmuxCtl, cmd: str | Callable[[], str], log: logging.Logger) -> None:
    """Send command to tmux session."""
    if callable(cmd):
        # Execute the callable to get the actual command string
        cmd = cmd()
        log.info(f"Sending command: {cmd[:LOG_COMMAND_TRUNCATE_LENGTH]}...")
    else:
        log.info(f"Sending command: {cmd[:LOG_COMMAND_TRUNCATE_LENGTH]}...")
    tmux.send_text_then_enter(cmd)


def _handle_input_with_text(tmux: TmuxCtl, log: logging.Logger) -> None:
    """Handle input prompt that already has text."""
    log.info("Input line already has text → sending Enter")
    tmux.send_enter()


def is_task_processing(output: str, cli_adapter: CLIAdapter) -> bool:
    """Check if a task is currently being processed using the provided CLI adapter.

    Returns False if the output hasn't changed for UNCHANGED_OUTPUT_THRESHOLD consecutive checks.
    """
    global _previous_output, _consecutive_unchanged_count

    # Check if output has changed
    if output != _previous_output:
        # Output has changed, reset counter
        _previous_output = output
        _consecutive_unchanged_count = 0
    else:
        # Output hasn't changed, increment counter
        _consecutive_unchanged_count += 1
        # If unchanged for threshold, return False (not processing)
        if _consecutive_unchanged_count >= UNCHANGED_OUTPUT_THRESHOLD:
            return False

    # Use the CLI adapter's original logic
    return cli_adapter.is_task_processing(output)


def reset_unchanged_output_tracking() -> None:
    """Reset the tracking of consecutive unchanged outputs."""
    global _previous_output, _consecutive_unchanged_count
    _previous_output = ""
    _consecutive_unchanged_count = 0


def _recover_from_timeout(tmux: TmuxCtl, cli_adapter: CLIAdapter, log: logging.Logger) -> float:
    """Attempt to recover when input prompt seems stuck.

    Strategy: ESC → progressive backspace until prompt appears → send "continue".
    Returns the new timestamp for last_input_prompt_time.
    """
    log.info("Input prompt timeout exceeded, trying ESC/backspace recovery → continue")
    _send_escape_and_wait(tmux)
    _progressive_backspace_until_prompt(tmux, cli_adapter)
    return _send_continue_and_return_timestamp(tmux)


def _send_escape_and_wait(tmux: TmuxCtl) -> None:
    """Send ESC key and wait briefly."""
    tmux.send_escape()
    time.sleep(RECOVERY_STEP_DELAY)


def _progressive_backspace_until_prompt(tmux: TmuxCtl, cli_adapter: CLIAdapter) -> None:
    """Send progressive backspace until input prompt appears."""
    backspace_num = INITIAL_BACKSPACE_COUNT
    for _ in range(MAX_RECOVERY_ATTEMPTS):  # cap iterations to avoid infinite loop
        tmux.send_backspace(backspace_num)
        time.sleep(RECOVERY_STEP_DELAY)
        output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
        if cli_adapter.is_input_prompt(output):
            break
        backspace_num = min(backspace_num + BACKSPACE_INCREMENT, MAX_BACKSPACE_COUNT)


def _send_continue_and_return_timestamp(tmux: TmuxCtl) -> float:
    """Send continue command and return current timestamp."""
    tmux.send_text_then_enter("continue")
    return time.time()


def _send_task_stopped_notification(log: logging.Logger) -> None:
    """Send a notification when task processing has stopped."""
    message = "ForgeFlow task has stopped processing. Please check what happened."
    log.info(f"Task stopped. Sending notification: {message}")
    send_notification("ForgeFlow Task Stopped", message)
