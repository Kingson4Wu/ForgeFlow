"""Tests for forgeflow.config."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from forgeflow.config import (
    BACKSPACE_INCREMENT,
    CLI_START_DELAY,
    CODEX_MIN_HEIGHT,
    CODEX_MIN_WIDTH,
    COMMAND_EXECUTION_DELAY,
    DIR_CONFIGS,
    DIR_TASKS,
    INITIAL_BACKSPACE_COUNT,
    LOG_COMMAND_TRUNCATE_LENGTH,
    MAX_BACKSPACE_COUNT,
    MAX_RECOVERY_ATTEMPTS,
    NO_PROCESSING_THRESHOLD,
    OUTPUT_HISTORY_SIZE,
    RECOVERY_STEP_DELAY,
    SEND_KEY_DELAY,
    SESSION_CREATE_DELAY,
    UNCHANGED_OUTPUT_THRESHOLD,
    Config,
)


class TestConstants:
    """Verify that module-level constants match expected values."""

    def test_timing_constants(self) -> None:
        assert SESSION_CREATE_DELAY == 2.0
        assert CLI_START_DELAY == 5.0
        assert COMMAND_EXECUTION_DELAY == 2.0
        assert RECOVERY_STEP_DELAY == 0.5
        assert SEND_KEY_DELAY == 0.1

    def test_recovery_parameters(self) -> None:
        assert MAX_RECOVERY_ATTEMPTS == 20
        assert INITIAL_BACKSPACE_COUNT == 10
        assert MAX_BACKSPACE_COUNT == 200
        assert BACKSPACE_INCREMENT == 10

    def test_output_detection(self) -> None:
        assert UNCHANGED_OUTPUT_THRESHOLD == 5
        assert NO_PROCESSING_THRESHOLD == 3

    def test_logging(self) -> None:
        assert LOG_COMMAND_TRUNCATE_LENGTH == 120

    def test_history(self) -> None:
        assert OUTPUT_HISTORY_SIZE == 10

    def test_window_dimensions(self) -> None:
        assert CODEX_MIN_WIDTH == 120
        assert CODEX_MIN_HEIGHT == 40

    def test_directory_names(self) -> None:
        assert DIR_TASKS == "tasks"
        assert DIR_CONFIGS == "configs"


class TestConfigDefaults:
    """Verify that Config default values are correct."""

    def test_default_runtime_fields(self) -> None:
        cfg = Config(session="s", workdir="w")
        assert cfg.ai_cmd == ""
        assert cfg.poll_interval == 10
        assert cfg.input_prompt_timeout == 1000
        assert cfg.log_file == "forgeflow.log"
        assert cfg.log_to_console is True
        assert cfg.project is None
        assert cfg.task is None
        assert cfg.cli_type == "claude_code"
        assert cfg.log_level == "INFO"


class TestConfigValidation:
    """Verify Pydantic validation rules."""

    def test_poll_interval_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Config(session="s", workdir="w", poll_interval=0)

    def test_input_prompt_timeout_zero_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Config(session="s", workdir="w", input_prompt_timeout=0)

    def test_ai_cmd_defaults_to_empty_string(self) -> None:
        cfg = Config(session="s", workdir="w")
        assert cfg.ai_cmd == ""
