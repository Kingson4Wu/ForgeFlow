from forgeflow.core.cli_types.codex_rules import build_rules
from forgeflow.core.rules import next_command


def test_codex_rules_compact_context_window_error_1() -> None:
    """Test Codex rule for context window error pattern 1."""
    rules = build_rules()
    output = """■ stream disconnected before completion: Your input exceeds the context window of this model. 
    Please reduce the length of the input or messages and try again."""

    command = next_command(output, rules)
    assert command == "/compact"


def test_codex_rules_compact_context_window_error_2() -> None:
    """Test Codex rule for context window error pattern 2."""
    rules = build_rules()
    output = """stream error: stream disconnected before completion: 
    Your input exceeds the context window of this model"""

    command = next_command(output, rules)
    assert command == "/compact"


def test_codex_rules_compact_task_completed() -> None:
    """Test that /compact is not sent when task is already completed."""
    rules = build_rules()
    output = """■ stream disconnected before completion: Your input exceeds the context window of this model.
    Compact task completed."""

    command = next_command(output, rules)
    # Should continue since compact task is already completed
    assert command == "continue"


def test_codex_rules_usage_limit() -> None:
    """Test Codex rule for usage limit."""
    rules = build_rules()
    output = "You've hit your usage limit"

    command = next_command(output, rules)
    assert command is None


def test_codex_rules_compact_counter_reset() -> None:
    """Test that the compact counter resets when other commands are sent."""
    from forgeflow.core.cli_types.codex_rules import (
        _check_and_update_compact_counter,
        _compact_counter,
    )

    # Manually set counter to 2
    _compact_counter = 2

    # Send a non-compact output (should reset counter)
    non_compact_output = "Normal output without context window error"
    result = _check_and_update_compact_counter(non_compact_output)

    # Should not send /new and counter should be reset
    assert result is False
    assert _compact_counter == 0


def test_codex_rules_compact_new_after_three_compacts() -> None:
    """Test that /new is sent after 3 consecutive /compact commands."""
    from forgeflow.core.cli_types.codex_rules import (
        _check_and_update_compact_counter,
        _compact_counter,
    )

    # Reset counter
    _compact_counter = 0

    # Pattern that triggers /compact
    compact_output = """■ stream disconnected before completion: Your input exceeds the context window of this model."""

    # First /compact
    result1 = _check_and_update_compact_counter(compact_output)
    assert result1 is False  # Should not send /new yet
    assert _compact_counter == 1

    # Second /compact
    result2 = _check_and_update_compact_counter(compact_output)
    assert result2 is False  # Should not send /new yet
    assert _compact_counter == 2

    # Third /compact - should trigger /new
    result3 = _check_and_update_compact_counter(compact_output)
    assert result3 is True  # Should send /new
    assert _compact_counter == 0  # Counter should be reset


def test_codex_rules_compact_new_integration() -> None:
    """Test the complete integration of the /new rule."""
    from forgeflow.core.cli_types.codex_rules import _compact_counter

    # Reset counter
    _compact_counter = 0

    rules = build_rules()
    compact_output = """■ stream disconnected before completion: Your input exceeds the context window of this model."""

    # First two times should return /compact
    command1 = next_command(compact_output, rules)
    assert command1 == "/compact"

    command2 = next_command(compact_output, rules)
    assert command2 == "/compact"

    # Third time should return /new
    command3 = next_command(compact_output, rules)
    assert command3 == "/new"

    # Counter should be reset
    assert _compact_counter == 0
