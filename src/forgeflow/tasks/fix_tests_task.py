import logging
from typing import Any

from forgeflow.rules.base import Rule
from forgeflow.tasks.common import build_standard_rules, instruction_phrases, is_instruction_text

logger = logging.getLogger("forgeflow")

TESTS_PASSED_INDICATOR = "[TESTS_PASSED]"
_TESTS_INSTRUCTIONS = instruction_phrases(TESTS_PASSED_INDICATOR)

_FAILURE_INDICATORS = [
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


def check_test_failures(output: str) -> bool:
    output_lower = output.lower()
    has_indicators = (
        any(indicator in output_lower for indicator in _FAILURE_INDICATORS)
        and "task completed" not in output_lower
    )
    return has_indicators and not is_instruction_text(output_lower, _TESTS_INSTRUCTIONS)


def check_all_tests_passed(output: str) -> bool:
    output_lower = output.lower()
    has_indicator = TESTS_PASSED_INDICATOR.lower() in output_lower
    return has_indicator and not is_instruction_text(output_lower, _TESTS_INSTRUCTIONS)


def get_fix_test_cases_prompt(config: dict[str, Any]) -> str:
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
        + _TESTS_INSTRUCTIONS[0]
        + """ as the last line of your output.
"""
    )


def build_rules(config: dict[str, Any]) -> list[Rule]:
    default_prompt = get_fix_test_cases_prompt(config)
    condition_prompt = config.get(
        "fix_test_cases_prompt",
        "Please analyze the test failures and fix the issues in the code. Make sure to re-run the tests after each fix to verify they pass.",
    )

    return build_standard_rules(
        stop_check=lambda out: check_all_tests_passed(out.lower()),
        condition_check=lambda out: check_test_failures(out.lower()),
        default_prompt=default_prompt,
        condition_prompt=condition_prompt,
        stop_desc="All tests passed - stop automation",
        condition_desc="Test failures detected - fix test cases",
        default_desc="Default fix tests prompt - continue fixing tests",
    )
