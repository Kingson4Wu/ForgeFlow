from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass

from .cli_adapters.factory import get_cli_adapter
from .rule_loader import get_rules
from .rules import next_command
from .tmux_ctl import TmuxConfig, TmuxCtl


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

    # Get the appropriate CLI adapter
    cli_adapter = get_cli_adapter(cfg.cli_type)

    # 1) Ensure session exists and start AI CLI
    tmux.create_session()
    time.sleep(1.0)
    output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
    if not cli_adapter.is_ai_cli_exist(output):
        log.info(f"Ensuring AI CLI running: {cfg.ai_cmd}")
        tmux.send_text_then_enter(cfg.ai_cmd)
        time.sleep(5.0)

    rules = get_rules(cfg)
    last_output = ""
    last_input_prompt_time = time.time()

    log.info("Automation started.")

    try:
        while True:
            output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
            if output != last_output:
                last_output = output

            if cli_adapter.is_input_prompt(output) and not is_task_processing(output, cli_adapter):
                last_input_prompt_time = time.time()
                cmd = next_command(output, rules)
                if cmd is None:
                    log.info("No more commands to execute. Stopping.")
                    break
                # Handle both string commands and callable commands
                if callable(cmd):
                    # Execute the callable to get the actual command string
                    cmd = cmd()
                    log.info(f"Sending command: {cmd[:120]}...")
                else:
                    log.info(f"Sending command: {cmd[:120]}...")
                tmux.send_text_then_enter(cmd)
                time.sleep(2.0)

            elif cli_adapter.is_input_prompt_with_text(output) and not is_task_processing(
                output, cli_adapter
            ):
                log.info("Input line already has text → sending Enter")
                tmux.send_enter()
                time.sleep(2.0)

            else:
                # Timeout recovery or wait
                if time.time() - last_input_prompt_time > cfg.input_prompt_timeout:
                    last_input_prompt_time = _recover_from_timeout(tmux, cli_adapter, log)
                else:
                    log.info("Not in input prompt, waiting...")
                time.sleep(cfg.poll_interval)

    except KeyboardInterrupt:
        log.info("KeyboardInterrupt received. Exiting gracefully.")
    except Exception as e:
        log.exception(f"Unhandled error: {e}")
        return 1

    log.info("Automation finished.")
    return 0


def is_task_processing(output: str, cli_adapter) -> bool:
    """Check if a task is currently being processed using the provided CLI adapter."""
    return cli_adapter.is_task_processing(output)


def _recover_from_timeout(tmux: TmuxCtl, cli_adapter, log: logging.Logger) -> float:
    """Attempt to recover when input prompt seems stuck.

    Strategy: ESC → progressive backspace until prompt appears → send "continue".
    Returns the new timestamp for last_input_prompt_time.
    """
    log.info("Input prompt timeout exceeded, trying ESC/backspace recovery → continue")
    tmux.send_escape()
    time.sleep(0.5)

    backspace_num = 10
    for _ in range(20):  # cap iterations to avoid infinite loop
        tmux.send_backspace(backspace_num)
        time.sleep(0.5)
        output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
        if cli_adapter.is_input_prompt(output):
            break
        backspace_num = min(backspace_num + 10, 200)

    tmux.send_text_then_enter("continue")
    return time.time()
