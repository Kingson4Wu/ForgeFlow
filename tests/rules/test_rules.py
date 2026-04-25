from forgeflow.rules.base import Command, Rule, RuleEngine


def test_next_command_stop_automation() -> None:
    """Test that RuleEngine returns None when a rule explicitly returns None to stop automation."""
    rules = [
        Rule(
            check=lambda out: "stop automation" in out,
            command=Command(None),
            description="Test rule to stop automation",
        ),
        Rule(
            check=lambda out: True,
            command=Command("continue"),
            description="Default continue rule",
        ),
    ]

    engine = RuleEngine(rules, {})
    # When the first rule matches and returns None, automation should stop
    result = engine.resolve("stop automation", "gemini")
    assert result is None


def test_next_command_default_continue() -> None:
    """Test that RuleEngine defaults to 'continue' when no rules match."""
    rules = [
        Rule(
            check=lambda out: "match this" in out,
            command=Command("some command"),
            description="Test matching rule",
        ),
    ]

    engine = RuleEngine(rules, {})
    # When no rules match, should default to "continue"
    result = engine.resolve("no match", "gemini")
    assert result == "continue"


def test_next_command_rule_match() -> None:
    """Test that RuleEngine returns the command when a rule matches."""
    rules = [
        Rule(
            check=lambda out: "match this" in out,
            command=Command("matched command"),
            description="Test matching rule",
        ),
    ]

    engine = RuleEngine(rules, {})
    # When a rule matches, should return that command
    result = engine.resolve("match this", "gemini")
    assert result == "matched command"


def test_next_command_with_post_processing() -> None:
    """Test that RuleEngine applies post-processing when available."""
    rules = [
        Rule(
            check=lambda out: "test match" in out,
            command=Command("original command"),
            description="Test rule with description",
        ),
    ]

    # Create a simple post-processor for testing
    class TestPostProcessor:
        def post_process_command(self, output: str, initial_command: str | None) -> str:
            return "modified command"

    post_processors = {"test": TestPostProcessor()}
    engine = RuleEngine(rules, post_processors)

    # Test with post-processing
    result = engine.resolve("test match", "test")
    assert result == "modified command"
