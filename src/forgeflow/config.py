"""Unified configuration for ForgeFlow.

This module centralizes all configuration values and magic numbers,
replacing the previous split between defaults.py and loop.py Config.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ---------- Module-level defaults (used by cli.py) ----------
DEFAULT_POLL_INTERVAL = 10
DEFAULT_INPUT_PROMPT_TIMEOUT = 1000
DEFAULT_LOG_FILE = "forgeflow.log"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_CLI_TYPE = "claude_code"

# ---------- Timing constants (seconds) ----------
SESSION_CREATE_DELAY = 2.0
CLI_START_DELAY = 5.0
COMMAND_EXECUTION_DELAY = 2.0
RECOVERY_STEP_DELAY = 0.5
SEND_KEY_DELAY = 0.1

# ---------- Recovery parameters ----------
MAX_RECOVERY_ATTEMPTS = 20
INITIAL_BACKSPACE_COUNT = 10
MAX_BACKSPACE_COUNT = 200
BACKSPACE_INCREMENT = 10

# ---------- Output detection ----------
UNCHANGED_OUTPUT_THRESHOLD = 5
NO_PROCESSING_THRESHOLD = 3

# ---------- Logging ----------
LOG_COMMAND_TRUNCATE_LENGTH = 120

# ---------- History ----------
OUTPUT_HISTORY_SIZE = 10

# ---------- Window dimensions (Codex) ----------
CODEX_MIN_WIDTH = 120
CODEX_MIN_HEIGHT = 40

# ---------- Directory names ----------
DIR_TASKS = "tasks"
DIR_CONFIGS = "configs"


class Config(BaseModel):
    """ForgeFlow runtime configuration — user-configurable fields only."""

    session: str
    workdir: str
    ai_cmd: str = ""
    poll_interval: int = Field(default=DEFAULT_POLL_INTERVAL, ge=1)
    input_prompt_timeout: int = Field(default=DEFAULT_INPUT_PROMPT_TIMEOUT, ge=1)
    log_file: str = DEFAULT_LOG_FILE
    log_to_console: bool = True
    project: str | None = None
    task: str | None = None
    cli_type: str = DEFAULT_CLI_TYPE
    log_level: str = DEFAULT_LOG_LEVEL
