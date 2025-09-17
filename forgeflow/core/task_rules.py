from __future__ import annotations

import json
import os
import re
from typing import Any

from .rules import Rule


# ---------- Task Configuration ----------
def load_task_config(task_name: str, workdir: str) -> dict[str, Any]:
    """Load task configuration from a JSON file.

    The function will look for a file named `{task_name}_config.json` in the workdir.
    If not found, it returns an empty dict.

    Args:
        task_name: Name of the task
        workdir: Working directory where the project is running

    Returns:
        Dictionary containing task configuration
    """
    config_file = os.path.join(workdir, f"{task_name}_config.json")

    # If not found in workdir, try examples directory
    if not os.path.exists(config_file):
        try:
            from pathlib import Path

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
    import re

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


def check_coverage_below_threshold(output: str, threshold: int = 80) -> bool:
    """Check if test coverage is below the specified threshold."""
    # More robust check for coverage information

    # Look for coverage percentage in the output
    coverage_match = re.search(r"coverage[:\s]+(\d+)%?", output.lower())
    if coverage_match:
        coverage = int(coverage_match.group(1))
        return coverage < threshold

    # Fallback to keyword-based check
    output_lower = output.lower()
    return f"coverage: {threshold}%" not in output_lower and (
        "coverage below threshold" in output_lower or "coverage:" in output_lower
    )


def check_coverage_target_reached(output: str, target: int = 80) -> bool:
    """Check if the target coverage has been reached."""

    # Look for coverage percentage in the output
    coverage_match = re.search(r"coverage[:\s]+(\d+)%?", output.lower())
    if coverage_match:
        coverage = int(coverage_match.group(1))
        return coverage >= target

    # Fallback to keyword-based check
    output_lower = output.lower()
    return f"coverage: {target}%" in output_lower or "coverage target reached" in output_lower


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


def improve_test_coverage_prompt(target_coverage: int = 80) -> str:
    """Task prompt for improving test coverage."""
    return f"""
Test Coverage Improvement Task:
1. Analyze current test coverage report:
   - Identify which files/modules have low coverage
   - Find specific lines or branches that are not covered
2. Prioritize areas for improvement:
   - Focus on critical business logic first
   - Address complex conditional branches
   - Cover error handling paths
3. Write additional test cases to cover these paths:
   - Create unit tests for uncovered functions
   - Add test cases for edge cases and error conditions
   - Use parameterized tests for data-driven scenarios
4. Aim for {target_coverage}% coverage
5. Run tests and verify improved coverage
6. Reassess and continue improving until target is reached
"""


def check_task_completed(output: str, config: dict[str, Any]) -> bool:
    """Check if a task has been completed based on the output and config."""
    # Get task completion indicators from config, with defaults
    completion_indicators = config.get(
        "task_completion_indicators",
        ["task completed", "task finished", "done with task", "finished task"],
    )

    output_lower = output.lower()
    return any(indicator in output_lower for indicator in completion_indicators)


def check_all_tasks_done(output: str) -> bool:
    """Check if all tasks are done."""
    return "All tasks have been completed." in output


def get_next_task_prompt(config: dict[str, Any]) -> str:
    """Get the prompt for the next task."""
    todo_file = config.get("todo_file", "TODO.md")
    return f"""
Task Planning Task:
1. Check the TODO file ({todo_file}) to see the list of tasks
2. Identify the first incomplete task
3. Work on completing that task:
   - Follow any specific instructions in the task description
   - Ensure code quality and testing standards
   - Make sure the implementation meets requirements
4. When the task is complete, mark it as completed in the TODO file
5. Commit your changes with an appropriate message
6. Move on to the next task

Use the following indicators to determine if a task is complete:
- Clear statement of task completion
- Updated TODO file with completed task marked
- Any other specific indicators defined in the task configuration

If you've completed the current task, respond with "Task completed" and 
wait for further instructions.
"""


def build_fix_tests_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for fixing test cases task."""
    return [
        # Stop when all tests pass
        Rule(check=check_all_tests_passed, command=None),
        # Handle test failures
        Rule(check=check_test_failures, command=fix_test_cases_prompt()),
        # Default task prompt
        Rule(check=lambda out: True, command=fix_test_cases_prompt()),
    ]


def build_improve_coverage_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for improving test coverage task."""
    # Get target coverage from config, default to 80
    target_coverage = config.get("target_coverage", 80)

    return [
        # Stop when target coverage is reached
        Rule(
            check=lambda out: check_coverage_target_reached(out, target_coverage),
            command=None,
        ),
        # Handle low coverage
        Rule(
            check=lambda out: check_coverage_below_threshold(out, target_coverage),
            command=lambda: improve_test_coverage_prompt(target_coverage),
        ),
        # Default task prompt
        Rule(check=lambda out: True, command=lambda: improve_test_coverage_prompt(target_coverage)),
    ]


def build_task_planner_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for task planner task."""
    return [
        # Stop when all tasks are completed
        Rule(check=check_all_tasks_done, command=None),
        # Handle task completion
        Rule(
            check=lambda out: check_task_completed(out, config),
            command=config.get(
                "next_task_prompt", "Please proceed with the next task in the TODO list."
            ),
        ),
        # Default task prompt
        Rule(check=lambda out: True, command=lambda: get_next_task_prompt(config)),
    ]


# Map task names to their rule building functions
TASK_RULES_MAP = {
    "fix_tests": build_fix_tests_rules,
    "improve_coverage": build_improve_coverage_rules,
    "task_planner": build_task_planner_rules,
}
