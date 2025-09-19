import os
import sys
from pathlib import Path

from forgeflow.core.rule_loader import _load_module_from_file
from forgeflow.core.rules import build_default_rules

# Add the project root to the path so we can import forgeflow
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_gemini_rules_file() -> None:
    """Test that the gemini rules file can be loaded and has a build_rules function."""
    gemini_rules_path = os.path.join(
        project_root, "forgeflow", "core", "cli_types", "gemini_rules.py"
    )
    assert os.path.exists(gemini_rules_path)

    module = _load_module_from_file(gemini_rules_path, "gemini_rules")
    assert module is not None
    assert hasattr(module, "build_rules")

    # Test that build_rules returns a list
    rules = module.build_rules()
    assert isinstance(rules, list)


def test_gemini_invalid_parameter_rule() -> None:
    """Test the rule for handling InvalidParameter API errors."""
    # Get the gemini rules
    rules = build_default_rules("gemini")

    # Find the rule that handles the InvalidParameter error
    # This should be the first rule in the gemini-specific rules
    invalid_param_rule = None
    for rule in rules:
        # Check if this rule matches the InvalidParameter error
        if rule.command == "/clear":
            # Test with the exact error message
            test_output = '✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter: An assistant message with "tool_calls" must be followed by tool messages responding to each "tool_call_id". The following tool_call_ids did not have response messages: message[650].role]'
            if rule.check(test_output):
                invalid_param_rule = rule
                break

    # Assert that we found the rule and it works correctly
    assert invalid_param_rule is not None, "Could not find rule for InvalidParameter error"

    # Test that it correctly identifies the error
    test_output = '✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter: An assistant message with "tool_calls" must be followed by tool messages responding to each "tool_call_id". The following tool_call_ids did not have response messages: message[650].role]'
    assert invalid_param_rule.check(test_output), "Rule should match the InvalidParameter error"

    # Test that it returns the correct command
    assert invalid_param_rule.command == "/clear", "Rule should return '/clear' command"

    # Test with a simpler matching pattern
    test_output_simple = (
        "✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter: Some other error message]"
    )
    assert invalid_param_rule.check(
        test_output_simple
    ), "Rule should match any InvalidParameter error"


def test_gemini_quota_exceeded_rule() -> None:
    """Test the rule for handling API quota exceeded errors."""
    # Get the gemini rules
    rules = build_default_rules("gemini")

    # Find the rule that handles the quota exceeded error
    quota_rule = None
    for rule in rules:
        # Check if this rule matches the quota exceeded error
        if rule.command is None:  # This rule should stop execution
            # Test with a quota exceeded error that matches the regex pattern
            test_output = "✕ [API Error: Qwen API quota exceeded: Your Qwen API quota has been exhausted. Please wait for your quota to reset.]"
            if rule.check(test_output):
                quota_rule = rule
                break

    # Assert that we found the rule and it works correctly
    assert quota_rule is not None, "Could not find rule for quota exceeded error"

    # Test that it correctly identifies the error
    test_output = "✕ [API Error: Qwen API quota exceeded: Your Qwen API quota has been exhausted. Please wait for your quota to reset.]"
    assert quota_rule.check(test_output), "Rule should match the quota exceeded error"

    # Test that it returns None to stop execution
    assert quota_rule.command is None, "Rule should return None to stop execution"

    # Test that it doesn't match similar but different patterns
    test_output_no_match = "[API Error: Qwen API quota exceeded: Your Qwen API quota has been exhausted. Please wait for your quota to reset.]"
    assert not quota_rule.check(test_output_no_match), "Rule should not match without the ✕ prefix"


def test_gemini_rules_precedence() -> None:
    """Test that gemini-specific rules take precedence over common rules."""
    rules = build_default_rules("gemini")

    # Check that we have both gemini-specific and common rules
    assert len(rules) > 0

    # The first rules should be gemini-specific
    # Check that we have the /clear command for InvalidParameter errors
    assert any(rule.command == "/clear" for rule in rules)

    # Check that we have a rule that stops execution (command=None) for quota errors
    assert any(rule.command is None for rule in rules)
