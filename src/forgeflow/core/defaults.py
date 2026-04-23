"""Default configuration values for ForgeFlow.

This module centralizes all magic numbers and hardcoded defaults,
making the project more configurable and maintainable.
"""

from __future__ import annotations

# ---------- Timing Constants (seconds) ----------

SESSION_CREATE_DELAY = 2.0  # tmux session creation settle time
CLI_START_DELAY = 5.0
COMMAND_EXECUTION_DELAY = 2.0
RECOVERY_STEP_DELAY = 0.5
SEND_KEY_DELAY = 0.1

# ---------- Recovery Parameters ----------

MAX_RECOVERY_ATTEMPTS = 20
INITIAL_BACKSPACE_COUNT = 10
MAX_BACKSPACE_COUNT = 200
BACKSPACE_INCREMENT = 10

# ---------- Output Detection ----------

UNCHANGED_OUTPUT_THRESHOLD = 5
NO_PROCESSING_THRESHOLD = 3

# ---------- CLI Adapter Defaults ----------

DEFAULT_CLI_TYPE = "claude_code"

# ---------- Logging ----------

LOG_COMMAND_TRUNCATE_LENGTH = 120
DEFAULT_LOG_FILE = "forgeflow.log"
DEFAULT_LOG_LEVEL = "INFO"

# ---------- Config Defaults ----------

DEFAULT_POLL_INTERVAL = 10
DEFAULT_INPUT_PROMPT_TIMEOUT = 1000  # seconds

# ---------- Window Dimensions (Codex) ----------

CODEX_MIN_WIDTH = 120
CODEX_MIN_HEIGHT = 40

# ---------- Directory Names ----------

DIR_EXAMPLES = "examples"
DIR_USER_CUSTOM_RULES = "user_custom_rules"
DIR_DEFAULT_RULES = "default_rules"
DIR_TASKS = "tasks"
DIR_CONFIGS = "configs"
