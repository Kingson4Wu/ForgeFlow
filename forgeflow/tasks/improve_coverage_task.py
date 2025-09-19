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


def build_rules(config: dict[str, Any]) -> list[Rule]:
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
            command=improve_test_coverage_prompt(target_coverage),
        ),
        # Default task prompt
        Rule(check=lambda out: True, command=improve_test_coverage_prompt(target_coverage)),
    ]
