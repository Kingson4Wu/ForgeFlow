from __future__ import annotations

import logging
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass

from .cli_adapters.base import CLIAdapter
from .cli_adapters.factory import get_cli_adapter
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


def _initialize_session(
    tmux: TmuxCtl, cli_adapter: CLIAdapter, cfg: Config, log: logging.Logger
) -> None:
    """Initialize tmux session and ensure AI CLI is running."""
    tmux.create_session()
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

    log.info("Automation started.")

    try:
        while True:
            output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
            if output != last_output:
                last_output = output

            is_processing = is_task_processing(output, cli_adapter)
            if cli_adapter.is_input_prompt(output) and not is_processing:
                last_input_prompt_time = time.time()
                cmd = next_command(output, rules)
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
    """Check if a task is currently being processed using the provided CLI adapter."""
    return cli_adapter.is_task_processing(output)


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
