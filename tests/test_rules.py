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
        ),
        Rule(
            check=lambda out: True,
            command="continue",
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
        ),
    ]

    # When a rule matches, should return that command
    result = next_command("match this", rules)
    assert result == "matched command"
