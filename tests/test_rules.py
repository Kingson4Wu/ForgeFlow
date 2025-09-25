from unittest.mock import Mock

from forgeflow.core.rules import (
    Rule,
    is_all_task_finished,
    is_final_verification_finished,
    next_command,
)


def test_is_all_task_finished_ok() -> None:
    out = "... All tasks have been completed. ..."
    assert is_all_task_finished(out)


def test_is_final_verification_finished_ok() -> None:
    out = "... All test cases are fully covered and executed successfully without errors. ..."
    assert is_final_verification_finished(out)


def test_next_command_stop_automation() -> None:
    """Test that next_command returns None when a rule explicitly returns None to stop automation."""
    rules = [
        Rule(
            check=lambda out: "stop automation" in out,
            command=None,
            description="Test rule to stop automation",
        ),
        Rule(
            check=lambda out: True,
            command="continue",
            description="Default continue rule",
        ),
    ]

    # When the first rule matches and returns None, automation should stop
    result = next_command("stop automation", rules)
    assert result is None


def test_next_command_default_continue() -> None:
    """Test that next_command defaults to 'continue' when no rules match."""
    rules = [
        Rule(
            check=lambda out: "match this" in out,
            command="some command",
            description="Test matching rule",
        ),
    ]

    # When no rules match, should default to "continue"
    result = next_command("no match", rules)
    assert result == "continue"


def test_next_command_rule_match() -> None:
    """Test that next_command returns the command when a rule matches."""
    rules = [
        Rule(
            check=lambda out: "match this" in out,
            command="matched command",
            description="Test matching rule",
        ),
    ]

    # When a rule matches, should return that command
    result = next_command("match this", rules)
    assert result == "matched command"


def test_next_command_with_description_logging() -> None:
    """Test that next_command logs rule descriptions when provided."""
    rules = [
        Rule(
            check=lambda out: "test match" in out,
            command="test command",
            description="Test rule with description",
        ),
    ]

    # Create a mock logger
    mock_logger = Mock()

    # When a rule matches, should log the description
    result = next_command("test match", rules, logger=mock_logger)
    assert result == "test command"
    mock_logger.info.assert_called_with("Rule matched: Test rule with description")


def test_next_command_with_post_processing_logging() -> None:
    """Test that next_command logs post-processing information."""
    rules = [
        Rule(
            check=lambda out: "test match" in out,
            command="original command",
            description="Test rule with description",
        ),
    ]

    # Create a mock logger
    mock_logger = Mock()

    # Create a simple post-processor for testing
    class TestPostProcessor:
        def post_process_command(self, output: str, initial_command: str) -> str:
            return "modified command"

    # Mock the get_command_post_processor function to return our test processor
    from forgeflow.core.rules import get_command_post_processor

    original_get_processor = get_command_post_processor
    try:
        # Temporarily replace the function
        def mock_get_processor(cli_type: str):
            if cli_type == "test":
                return TestPostProcessor()
            return None

        # Patch the function
        import forgeflow.core.rules

        forgeflow.core.rules.get_command_post_processor = mock_get_processor

        # Test with post-processing
        result = next_command("test match", rules, cli_type="test", logger=mock_logger)
        assert result == "modified command"

        # Check that both rule matching and post-processing were logged
        mock_logger.info.assert_any_call("Rule matched: Test rule with description")
        mock_logger.info.assert_any_call(
            "Post-processed command 'original command' to 'modified command' based on rule: Test rule with description"
        )
    finally:
        # Restore the original function
        forgeflow.core.rules.get_command_post_processor = original_get_processor
