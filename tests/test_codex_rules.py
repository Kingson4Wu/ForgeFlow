from forgeflow.core.cli_types.codex_rules import CodexCommandPostProcessor, build_rules
from forgeflow.core.rules import next_command


def test_codex_rules_compact_context_window_error_1() -> None:
    """Test Codex rule for context window error pattern 1."""
    rules = build_rules()
    output = """■ stream disconnected before completion: Your input exceeds the context window of this model. 
    Please reduce the length of the input or messages and try again."""

    command = next_command(output, rules, "codex")
    assert command == "/compact"


def test_codex_rules_compact_context_window_error_2() -> None:
    """Test Codex rule for context window error pattern 2."""
    rules = build_rules()
    output = "stream error: stream disconnected before completion: Your input exceeds the context window of this model"

    command = next_command(output, rules, "codex")
    assert command == "/compact"


def test_codex_rules_compact_task_completed() -> None:
    """Test that /compact is not sent when task is already completed."""
    rules = build_rules()
    output = """■ stream disconnected before completion: Your input exceeds the context window of this model.
    Compact task completed."""

    command = next_command(output, rules, "codex")
    # Should continue since compact task is already completed
    assert command == "continue"


def test_codex_rules_usage_limit() -> None:
    """Test Codex rule for usage limit."""
    rules = build_rules()
    output = "You've hit your usage limit"

    command = next_command(output, rules, "codex")
    # The rule returns None, but next_command defaults to "continue"
    assert command == "continue"


def test_codex_command_post_processor_compact_to_new() -> None:
    """Test that CodexCommandPostProcessor converts /compact to /new after 3 times."""
    post_processor = CodexCommandPostProcessor()

    # First two times should return None (no change)
    result1 = post_processor.post_process_command("test output", "/compact")
    assert result1 is None

    result2 = post_processor.post_process_command("test output", "/compact")
    assert result2 is None

    # Third time should return "/new"
    result3 = post_processor.post_process_command("test output", "/compact")
    assert result3 == "/new"


def test_codex_command_post_processor_reset_on_non_compact() -> None:
    """Test that CodexCommandPostProcessor resets counter on non-compact commands."""
    post_processor = CodexCommandPostProcessor()

    # Set counter to 2 by sending two "/compact" commands
    post_processor.post_process_command("test output", "/compact")
    post_processor.post_process_command("test output", "/compact")

    # Send a non-compact command (should reset counter)
    result = post_processor.post_process_command("test output", "continue")
    assert result is None  # Should return None (no change)

    # Next "/compact" should not trigger "/new" because counter was reset
    result2 = post_processor.post_process_command("test output", "/compact")
    assert result2 is None  # Should return None (no change)
