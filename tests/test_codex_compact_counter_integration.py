from forgeflow.core.cli_types.codex_rules import CodexCommandPostProcessor


def test_codex_compact_counter_integration():
    """Integration test for the Codex compact counter functionality."""
    # Create a post-processor and test the counter functionality
    post_processor = CodexCommandPostProcessor()

    # Simulate the scenario where we send "/compact" three times
    # First two times should return None (no change to "/compact")
    result1 = post_processor.post_process_command("test", "/compact")
    assert result1 is None

    result2 = post_processor.post_process_command("test", "/compact")
    assert result2 is None

    # Third time should return "/new" to replace "/compact"
    result3 = post_processor.post_process_command("test", "/compact")
    assert result3 == "/new"

    # Counter should be reset, so next "/compact" should return None again
    result4 = post_processor.post_process_command("test", "/compact")
    assert result4 is None


def test_codex_compact_counter_reset_on_other_commands():
    """Test that the counter resets when other commands are sent."""
    post_processor = CodexCommandPostProcessor()

    # Send two "/compact" commands
    post_processor.post_process_command("test", "/compact")
    post_processor.post_process_command("test", "/compact")

    # Send a different command (should reset counter)
    result = post_processor.post_process_command("test", "continue")
    assert result is None

    # Next "/compact" should not trigger "/new" because counter was reset
    result2 = post_processor.post_process_command("test", "/compact")
    assert result2 is None
