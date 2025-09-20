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
    output = "stream error: stream disconnected before completion: Your input exceeds the context window of this model"

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
