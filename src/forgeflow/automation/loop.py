from __future__ import annotations

import logging
import time

from forgeflow.adapters.base import CLIAdapter
from forgeflow.adapters.registry import get_adapter
from forgeflow.automation.recovery import recover_from_timeout
from forgeflow.config import (
    CLI_START_DELAY,
    COMMAND_EXECUTION_DELAY,
    LOG_COMMAND_TRUNCATE_LENGTH,
    OUTPUT_HISTORY_SIZE,
    SESSION_CREATE_DELAY,
    UNCHANGED_OUTPUT_THRESHOLD,
    Config,
)
from forgeflow.logging_config import setup_logger
from forgeflow.rules.base import CommandPostProcessor, RuleEngine
from forgeflow.state import UnchangedTracker
from forgeflow.tmux.ctl import TmuxConfig, TmuxCtl

logger = logging.getLogger("forgeflow")


def run_automation(cfg: Config) -> int:
    log = setup_logger(cfg.log_file, cfg.log_to_console, cfg.log_level)
    tmux = TmuxCtl(TmuxConfig(session=cfg.session, workdir=cfg.workdir))
    cli_adapter = get_adapter(cfg.cli_type)

    _initialize_session(tmux, cli_adapter, cfg, log)
    return _run_automation_loop(tmux, cli_adapter, cfg, log)


def _initialize_session(
    tmux: TmuxCtl, cli_adapter: CLIAdapter, cfg: Config, log: logging.Logger
) -> None:
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
    from forgeflow.automation.monitor import _is_task_processing
    from forgeflow.rules.loader import get_rules

    rules = get_rules(cfg)
    post_processors = _build_post_processors()
    engine = RuleEngine(rules, post_processors)

    last_output = ""
    last_input_prompt_time = time.time()
    output_history: list[str] = []
    max_history = OUTPUT_HISTORY_SIZE
    unchanged_tracker = UnchangedTracker(UNCHANGED_OUTPUT_THRESHOLD)

    log.info("Automation started.")

    try:
        while True:
            output = tmux.capture_output(include_ansi=cli_adapter.wants_ansi())
            output_history.append(output)
            output_history = output_history[-max_history:]
            if output != last_output:
                last_output = output

            is_processing = _is_task_processing(
                output, cli_adapter, output_history, unchanged_tracker
            )

            if cli_adapter.is_input_prompt(output) and not is_processing:
                last_input_prompt_time = time.time()
                cmd = engine.resolve(output, cfg.cli_type)
                if cmd is None:
                    log.info("No more commands to execute. Stopping.")
                    break
                _send_command(tmux, cmd, cfg, log)
                time.sleep(COMMAND_EXECUTION_DELAY)

            elif cli_adapter.is_input_prompt_with_text(output) and not is_processing:
                log.info("Input line already has text → sending Enter")
                tmux.send_enter()
                time.sleep(COMMAND_EXECUTION_DELAY)

            else:
                if time.time() - last_input_prompt_time > cfg.input_prompt_timeout:
                    last_input_prompt_time = recover_from_timeout(tmux, cli_adapter)
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


def _build_post_processors() -> dict[str, CommandPostProcessor]:
    """Build post-processors from built-in CLI type rule modules."""
    result: dict[str, CommandPostProcessor] = {}
    try:
        from forgeflow.rules.builtin.claude_code import ClaudeCodeCommandPostProcessor

        result["claude_code"] = ClaudeCodeCommandPostProcessor()
    except Exception:
        logger.warning("Failed to load claude_code post-processor", exc_info=True)
    try:
        from forgeflow.rules.builtin.codex import CodexCommandPostProcessor

        result["codex"] = CodexCommandPostProcessor()
    except Exception:
        logger.warning("Failed to load codex post-processor", exc_info=True)
    return result


def _send_command(tmux: TmuxCtl, cmd: str, cfg: Config, log: logging.Logger) -> None:
    log.info(f"Sending command: {cmd[:LOG_COMMAND_TRUNCATE_LENGTH]}...")
    tmux.send_text_then_enter(cmd)
