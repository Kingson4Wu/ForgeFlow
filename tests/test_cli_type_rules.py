from forgeflow.core.rules import build_default_rules


def test_build_default_rules_gemini() -> None:
    """Test building default rules for Gemini CLI."""
    rules = build_default_rules("gemini")
    assert len(rules) > 0
    # Check that common rules are present
    assert any(rule.command == "/clear" for rule in rules)
    # Check that the default task prompt is present as the last rule
    assert rules[-1].command is not None and "All test cases are fully covered" in rules[-1].command


def test_build_default_rules_codex() -> None:
    """Test building default rules for Codex CLI."""
    rules = build_default_rules("codex")
    assert len(rules) > 0
    # Check that common rules are present
    assert any(rule.command == "/clear" for rule in rules)
    # Check that the default task prompt is present as the last rule
    assert rules[-1].command is not None and "All test cases are fully covered" in rules[-1].command


def test_build_default_rules_claude_code() -> None:
    """Test building default rules for Claude Code CLI."""
    rules = build_default_rules("claude_code")
    assert len(rules) > 0
    # Check that common rules are present
    assert any(rule.command == "/clear" for rule in rules)
    # Check that the default task prompt is present as the last rule
    assert rules[-1].command is not None and "All test cases are fully covered" in rules[-1].command


def test_build_default_rules_default() -> None:
    """Test building default rules with default CLI type."""
    rules = build_default_rules()  # Should default to "gemini"
    assert len(rules) > 0
    # Check that common rules are present
    assert any(rule.command == "/clear" for rule in rules)
    # Check that the default task prompt is present as the last rule
    assert rules[-1].command is not None and "All test cases are fully covered" in rules[-1].command


def test_cli_specific_rules() -> None:
    """Test that CLI-specific rules are included."""
    gemini_rules = build_default_rules("gemini")
    codex_rules = build_default_rules("codex")
    claude_rules = build_default_rules("claude_code")

    # All should have some rules
    assert len(gemini_rules) > 0
    assert len(codex_rules) > 0
    assert len(claude_rules) > 0

    # Gemini should have more rules than Codex and Claude Code
    # because it has specific rules defined, while Codex and Claude Code are empty
    assert len(gemini_rules) > len(codex_rules)
    assert len(gemini_rules) > len(claude_rules)

    # Codex and Claude Code should have the same number of rules
    # because they both have empty rule lists
    assert len(codex_rules) == len(claude_rules)
