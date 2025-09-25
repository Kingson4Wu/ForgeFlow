import sys
from pathlib import Path

from forgeflow.core.rules import build_default_rules

# Add the project root to the path so we can import forgeflow
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_tool_call_error_rule() -> None:
    """Test the rule for handling tool call errors that require /clear."""
    # Get the gemini rules
    rules = build_default_rules("gemini")

    # Find the rule that handles the tool call error
    tool_call_rule = None
    for rule in rules:
        # Check if this rule matches the tool call error and sends /clear
        if rule.command == "/clear":
            # Test with the error message that mentions tool calls
            test_output = 'An assistant message with "tool_calls" must be followed by tool messages responding to each "tool_call_id"'
            if rule.check(test_output):
                tool_call_rule = rule
                break

    # If we didn't find it with the specific text, try to find any rule that sends /clear
    if tool_call_rule is None:
        for rule in rules:
            if rule.command == "/clear":
                tool_call_rule = rule
                break

    # Assert that we found the rule
    assert tool_call_rule is not None, "Could not find rule for tool call error"

    # Test with the actual error message from the issue
    test_output = """✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter: An assistant
  message with "tool_calls" must be followed by tool messages responding
  to each "tool_call_id". The following tool_call_ids did not have
  response messages: message[733].role]"""

    # The rule should match and return /clear
    assert tool_call_rule.check(test_output), "Rule should match the tool call error"
    assert tool_call_rule.command == "/clear", "Rule should return '/clear' command"

    # Test that it correctly identifies output containing tool_call with specific phrases
    test_output_with_tool_call = (
        "Some error message mentioning tool_call_ids must be followed by responses"
    )
    assert tool_call_rule.check(
        test_output_with_tool_call
    ), "Rule should match output containing tool_call and 'must be followed'"

    # Test another variant
    test_output_with_tool_call2 = "The following tool_call_ids did not have response messages"
    assert tool_call_rule.check(
        test_output_with_tool_call2
    ), "Rule should match output containing tool_call and 'did not have'"
