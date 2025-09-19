import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from forgeflow.core.rules import Rule

logger = logging.getLogger("forgeflow")


# ---------- Task Configuration ----------
def load_task_config(task_name: str, workdir: str) -> dict[str, Any]:
    """Load task configuration from a JSON file.

    The function will look for a file named `{task_name}_config.json` in this order:
    1. Current working directory
    2. user_custom_rules directory
    3. default_rules/tasks directory
    4. forgeflow/examples directory (for backward compatibility)

    Args:
        task_name: Name of the task
        workdir: Working directory where the project is running

    Returns:
        Dictionary containing task configuration
    """
    config_file = os.path.join(workdir, f"{task_name}_config.json")

    # If not found in workdir, try user custom rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            user_custom_rules_dir = (repo_root / "user_custom_rules").resolve()
            config_file = os.path.join(user_custom_rules_dir, f"{task_name}_config.json")
        except Exception:
            pass

    # If not found in user custom rules directory, try tasks rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            tasks_rules_dir = (repo_root / "default_rules" / "tasks").resolve()
            config_file = os.path.join(tasks_rules_dir, f"{task_name}_config.json")
        except Exception:
            pass

    # If not found in tasks rules directory, try examples directory (for backward compatibility)
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            examples_dir = (repo_root / "examples").resolve()
            config_file = os.path.join(examples_dir, f"{task_name}_config.json")
        except Exception:
            pass

    if not os.path.exists(config_file):
        return {}

    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception:
        # If there's an error reading the config file, return empty dict
        return {}


# ---------- Task Rules ----------
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
    return (
        any(indicator in output_lower for indicator in failure_indicators)
        and "task completed" not in output_lower
    )


def check_all_tests_passed(output: str) -> bool:
    """Check if all tests have passed."""
    # Check for various indicators that all tests have passed
    exact_matches = [
        "all tests passed",
        "passed:",
        "tests passed:",
    ]

    # Special handling for regex patterns
    regex_patterns = [r"ran \d+ tests.*all passed", r"ok.*\d+ tests"]

    output_lower = output.lower()

    # Check for exact matches
    if any(indicator in output_lower for indicator in exact_matches):
        return True

    # Check for regex matches
    return any(re.search(pattern, output_lower) for pattern in regex_patterns)


def fix_test_cases_prompt() -> str:
    """Task prompt for fixing test cases."""
    return """
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
"""


def build_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for fixing test cases task."""
    return [
        # Stop when all tests pass
        Rule(check=check_all_tests_passed, command=None),
        # Handle test failures
        Rule(check=check_test_failures, command=fix_test_cases_prompt()),
        # Default task prompt
        Rule(check=lambda out: True, command=fix_test_cases_prompt()),
    ]
