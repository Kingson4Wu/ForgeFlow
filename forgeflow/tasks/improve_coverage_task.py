import logging
import re
from typing import Any

from forgeflow.core.rules import Rule

logger = logging.getLogger("forgeflow")

# ---------- Constants ----------
COVERAGE_TARGET_REACHED_INDICATOR = "[COVERAGE_TARGET_REACHED]"
RESPOND_WITH_COVERAGE_TARGET_REACHED = f'respond with "{COVERAGE_TARGET_REACHED_INDICATOR}"'
RESPOND_WITH_COVERAGE_TARGET_REACHED_SINGLE_QUOTE = (
    f"respond with '{COVERAGE_TARGET_REACHED_INDICATOR}'"
)


# ---------- Task Rules ----------
def _is_instruction_text_in_coverage_output(output_lower: str) -> bool:
    """Check if the output contains instruction text that should be ignored for coverage completion."""
    return (
        RESPOND_WITH_COVERAGE_TARGET_REACHED.lower() in output_lower
        or RESPOND_WITH_COVERAGE_TARGET_REACHED_SINGLE_QUOTE.lower() in output_lower
    )


def check_coverage_below_threshold(output: str, threshold: int = 80) -> bool:
    """Check if test coverage is below the specified threshold."""
    # More robust check for coverage information

    # Look for coverage percentage in the output
    coverage_match = re.search(r"coverage[:\s]+(\d+)%?", output.lower())
    if coverage_match:
        coverage = int(coverage_match.group(1))
        is_below_threshold = coverage < threshold
    else:
        # Fallback to keyword-based check
        output_lower = output.lower()
        is_below_threshold = f"coverage: {threshold}%" not in output_lower and (
            "coverage below threshold" in output_lower or "coverage:" in output_lower
        )

    # Prevent false positives by checking that this isn't just part of our own prompt
    is_instruction_text = _is_instruction_text_in_coverage_output(output.lower())

    return is_below_threshold and not is_instruction_text


def check_coverage_target_reached(output: str, target_coverage: int = 80) -> bool:
    """Check if the target coverage has been reached."""
    # Check for our indicator
    target_text = COVERAGE_TARGET_REACHED_INDICATOR
    output_lower = output.lower()

    # Check if the target text is present (case-insensitive)
    has_target_text = target_text.lower() in output_lower

    # If we found our specific indicator, use that
    if has_target_text:
        # Prevent false positives by checking that this isn't just part of our own prompt
        is_instruction_text = _is_instruction_text_in_coverage_output(output_lower)
        return has_target_text and not is_instruction_text

    # Otherwise, check for coverage percentage in the output
    import re

    coverage_match = re.search(r"coverage[:\s]+(\d+)%?", output_lower)
    if coverage_match:
        coverage = int(coverage_match.group(1))
        return coverage >= target_coverage

    # We don't check for natural language expressions like "coverage target reached"
    # because they are not part of our prompt and shouldn't be relied upon

    return False


def get_improve_test_coverage_prompt(config: dict[str, Any]) -> str:
    """Task prompt for improving test coverage."""
    target_coverage = config.get("target_coverage", 80)
    return (
        f"""
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

When you've reached the target coverage of {target_coverage}%, """
        + RESPOND_WITH_COVERAGE_TARGET_REACHED
        + """ as the last line of your output.
"""
    )


def build_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for improving test coverage task."""
    # Get target coverage from config, default to 80
    target_coverage = config.get("target_coverage", 80)

    return [
        # Stop when target coverage is reached
        Rule(
            check=lambda out: check_coverage_target_reached(out, target_coverage),
            command=None,
            description="Target test coverage reached - stop automation",
        ),
        # Handle low coverage
        Rule(
            check=lambda out: check_coverage_below_threshold(out, target_coverage),
            command=config.get(
                "improve_coverage_prompt",
                "Please analyze the test coverage report and write additional test cases to improve coverage. Focus on areas with the lowest coverage first.",
            ),
            description="Test coverage below threshold - improve coverage",
        ),
        # Default task prompt
        Rule(
            check=lambda out: True,
            command=get_improve_test_coverage_prompt(config),
            description="Default improve coverage prompt - continue improving coverage",
        ),
    ]
