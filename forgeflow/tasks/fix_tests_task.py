import json
import logging
import os
from pathlib import Path
from typing import Any

from forgeflow.core.rules import Rule

logger = logging.getLogger("forgeflow")

# ---------- Constants ----------
TESTS_PASSED_INDICATOR = "[TESTS_PASSED]"
RESPOND_WITH_TESTS_PASSED = f'respond with "{TESTS_PASSED_INDICATOR}"'
RESPOND_WITH_TESTS_PASSED_SINGLE_QUOTE = f"respond with '{TESTS_PASSED_INDICATOR}'"


# ---------- Task Configuration ----------
def load_task_config(task_name: str, workdir: str) -> dict[str, Any]:
    """Load task configuration from a JSON file.

    The function will look for a file named `{task_name}_config.json` in this order:
    1. Current working directory
    2. user_custom_rules/tasks directory
    3. forgeflow/default_rules directory (built-in configurations)
    4. examples/tasks directory (for backward compatibility)

    Args:
        task_name: Name of the task
        workdir: Working directory where the project is running

    Returns:
        Dictionary containing task configuration
    """
    config_file = os.path.join(workdir, f"{task_name}_config.json")

    # If not found in workdir, try user custom rules tasks directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            user_custom_rules_dir = (repo_root / "user_custom_rules" / "tasks").resolve()
            config_file = os.path.join(user_custom_rules_dir, f"{task_name}_config.json")
        except Exception:
            # Best effort; if not available, continue with next option
            pass

    # If not found in user custom rules tasks directory, try default rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            default_rules_dir = (pkg_dir / "tasks" / "configs").resolve()
            config_file = os.path.join(default_rules_dir, f"{task_name}_config.json")
        except Exception:
            # Best effort; if not available, continue with next option
            pass

    # If not found in default rules directory, try examples tasks directory (for backward compatibility)
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            examples_dir = (repo_root / "examples" / "tasks").resolve()
            config_file = os.path.join(examples_dir, f"{task_name}_config.json")
        except Exception:
            # Best effort; if not available, continue with next option
            pass

    if not os.path.exists(config_file):
        return {}  # type: ignore

    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception:
        # If there's an error reading the config file, return empty dict
        return {}  # type: ignore


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
        Rule(check=check_all_tests_passed, command=None),
        # Handle test failures
        Rule(
            check=check_test_failures,
            command=config.get(
                "fix_test_cases_prompt",
                "Please analyze the test failures and fix the issues in the code. Make sure to re-run the tests after each fix to verify they pass.",
            ),
        ),
        # Default task prompt
        Rule(check=lambda out: True, command=get_fix_test_cases_prompt(config)),
    ]
