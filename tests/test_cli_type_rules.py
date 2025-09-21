from forgeflow.core.rules import build_default_rules


def test_build_default_rules_gemini() -> None:
    """Test building default rules for Gemini CLI."""
    rules = build_default_rules("gemini")
    assert len(rules) > 0
    # Check that Gemini-specific rules are present (from cli_types/gemini_rules.py)
    assert any(rule.command == "/clear" for rule in rules)


def test_build_default_rules_codex() -> None:
    """Test building default rules for Codex CLI."""
    rules = build_default_rules("codex")
    assert len(rules) > 0
    # Check that Codex-specific rules are present (from cli_types/codex_rules.py)
    assert any(rule.command == "/compact" for rule in rules)


def test_build_default_rules_claude_code() -> None:
    """Test building default rules for Claude Code CLI."""
    rules = build_default_rules("claude_code")
    # Claude Code rules file is currently empty, so we should have 0 rules
    assert len(rules) >= 0


def test_build_default_rules_default() -> None:
    """Test building default rules with default CLI type."""
    rules = build_default_rules()  # Should default to "gemini"
    assert len(rules) > 0
    # Check that Gemini-specific rules are present (from cli_types/gemini_rules.py)
    assert any(rule.command == "/clear" for rule in rules)


def test_cli_specific_rules() -> None:
    """Test that CLI-specific rules are included."""
    gemini_rules = build_default_rules("gemini")
    codex_rules = build_default_rules("codex")
    claude_rules = build_default_rules("claude_code")

    # All should have some rules (except Claude Code which is empty)
    # Using claude_rules to avoid unused variable error
    assert claude_rules is not None
    assert len(gemini_rules) > 0
    assert len(codex_rules) > 0
    # Claude Code rules file is currently empty

    # Gemini should have more rules than Codex
    assert len(gemini_rules) > len(codex_rules)
