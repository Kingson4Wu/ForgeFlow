import logging
from typing import Any

from forgeflow.core.rules import Rule

logger = logging.getLogger("forgeflow")

# ---------- Constants ----------
TESTS_PASSED_INDICATOR = "[TESTS_PASSED]"
RESPOND_WITH_TESTS_PASSED = f'respond with "{TESTS_PASSED_INDICATOR}"'
RESPOND_WITH_TESTS_PASSED_SINGLE_QUOTE = f"respond with '{TESTS_PASSED_INDICATOR}'"


# ---------- Task Rules ----------
def _is_instruction_text_in_test_output(output_lower: str) -> bool:
    """Check if the output contains instruction text that should be ignored for test completion."""
    return (
        RESPOND_WITH_TESTS_PASSED.lower() in output_lower
        or RESPOND_WITH_TESTS_PASSED_SINGLE_QUOTE.lower() in output_lower
    )


def check_test_failures(output: str) -> bool:
    """Check for test failures in the output."""
    # More comprehensive check for test failures
    failure_indicators = [
        "test failed",
        "failed test:",
        "failed tests:",
        "tests failed",
        "failure:",
        "error:",
        "assertionerror",
        "pytest failed",
        "unittest failed",
    ]
    output_lower = output.lower()
    # Ensure we're not mistaking a task completion message as a test failure
    has_failure_indicators = (
        any(indicator in output_lower for indicator in failure_indicators)
        and "task completed" not in output_lower
    )

    # Prevent false positives by checking that this isn't just part of our own prompt
    is_instruction_text = _is_instruction_text_in_test_output(output_lower)

    return has_failure_indicators and not is_instruction_text


def check_all_tests_passed(output: str) -> bool:
    """Check if all tests have passed."""
    # Check for our indicator
    target_text = TESTS_PASSED_INDICATOR
    output_lower = output.lower()

    # Check if the target text is present (case-insensitive)
    has_target_text = target_text.lower() in output_lower

    # If we found our specific indicator, use that
    if has_target_text:
        # Prevent false positives by checking that this isn't just part of our own prompt
        is_instruction_text = _is_instruction_text_in_test_output(output_lower)
        return has_target_text and not is_instruction_text

    # We don't check for natural language expressions like "all tests passed"
    # because they are not part of our prompt and shouldn't be relied upon

    return False


def get_fix_test_cases_prompt(config: dict[str, Any]) -> str:
    """Task prompt for fixing test cases."""
    return (
        """
Test Case Fixing Task:
1. Identify the failing tests from the output
2. Analyze the cause of each failure:
   - For assertion errors, check the expected vs actual values
   - For runtime errors, examine the stack trace to find the issue
   - For import errors, verify module paths and dependencies
3. Fix the test cases or implementation code as needed:
   - Correct assertion logic
   - Fix implementation bugs
   - Handle edge cases properly
4. Re-run tests to verify fixes
5. Ensure all tests pass before continuing
6. If tests are still failing after several attempts, consider if there's 
   a deeper architectural issue

When all tests have passed, """
        + RESPOND_WITH_TESTS_PASSED
        + """ as the last line of your output.
"""
    )


def build_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for fixing test cases task."""
    return [
        # Stop when all tests pass
        Rule(
            check=check_all_tests_passed,
            command=None,
            description="All tests passed - stop automation",
        ),
        # Handle test failures
        Rule(
            check=check_test_failures,
            command=config.get(
                "fix_test_cases_prompt",
                "Please analyze the test failures and fix the issues in the code. Make sure to re-run the tests after each fix to verify they pass.",
            ),
            description="Test failures detected - fix test cases",
        ),
        # Default task prompt
        Rule(
            check=lambda out: True,
            command=get_fix_test_cases_prompt(config),
            description="Default fix tests prompt - continue fixing tests",
        ),
    ]
