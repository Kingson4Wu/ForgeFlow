from __future__ import annotations

import logging
import re
import sys
import time
from dataclasses import dataclass

from .rules import (
    is_input_prompt,
    is_input_prompt_with_text,
    is_task_processing,
    next_command,
)
from .rule_loader import get_rules
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


def setup_logger(path: str, to_console: bool = True) -> logging.Logger:
    logger = logging.getLogger("forgeflow")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
    logger.addHandler(fh)

    if to_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
        logger.addHandler(ch)

    return logger


PROMPT_AI_CLI_EXIST = re.compile(r"^YOLO mode \(ctrl \+ y to toggle\)(.*)?$")


def is_ai_cli_exist(output: str) -> bool:
    for line in output.splitlines():
        if PROMPT_AI_CLI_EXIST.match(line.strip()):
            return True
    return False


def run_automation(cfg: Config) -> int:
    log = setup_logger(cfg.log_file, cfg.log_to_console)
    tmux = TmuxCtl(TmuxConfig(session=cfg.session, workdir=cfg.workdir))

    # 1) Ensure session exists and start AI CLI
    tmux.create_session()
    time.sleep(1.0)
    output = tmux.capture_output()
    if not is_ai_cli_exist(output):
        log.info(f"Ensuring AI CLI running: {cfg.ai_cmd}")
        tmux.send_text_then_enter(cfg.ai_cmd)
        time.sleep(5.0)

    rules = get_rules(cfg)
    last_output = ""
    last_input_prompt_time = time.time()

    log.info("Automation started.")

    try:
        while True:
            output = tmux.capture_output()
            if output != last_output:
                last_output = output

            if is_input_prompt(output) and not is_task_processing(output):
                last_input_prompt_time = time.time()
                cmd = next_command(output, rules)
                if cmd is None:
                    log.info("No more commands to execute. Stopping.")
                    break
                log.info(f"Sending command: {cmd[:120]}...")
                tmux.send_text_then_enter(cmd)
                time.sleep(2.0)

            elif is_input_prompt_with_text(output) and not is_task_processing(output):
                log.info("Input line already has text → sending Enter")
                tmux.send_enter()
                time.sleep(2.0)

            else:
                # Timeout recovery
                if time.time() - last_input_prompt_time > cfg.input_prompt_timeout:
                    log.info(
                        "Input prompt timeout exceeded, trying ESC/backspace recovery → continue"
                    )
                    tmux.send_escape()
                    time.sleep(0.5)

                    backspace_num = 10
                    while True:
                        tmux.send_backspace(backspace_num)
                        time.sleep(0.5)
                        output = tmux.capture_output()
                        if is_input_prompt(output):
                            break
                        backspace_num = min(backspace_num + 10, 200)

                    tmux.send_text_then_enter("continue")
                    last_input_prompt_time = time.time()
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
