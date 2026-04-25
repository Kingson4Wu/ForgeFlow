import logging
import re
from typing import Any

from forgeflow.rules.base import Rule
from forgeflow.tasks.common import build_standard_rules, instruction_phrases, is_instruction_text

logger = logging.getLogger("forgeflow")

COVERAGE_TARGET_REACHED_INDICATOR = "[COVERAGE_TARGET_REACHED]"
_COVERAGE_INSTRUCTIONS = instruction_phrases(COVERAGE_TARGET_REACHED_INDICATOR)

_DEFAULT_THRESHOLD = 80


def check_coverage_below_threshold(output: str, threshold: int) -> bool:
    output_lower = output.lower()
    match = re.search(r"coverage[:\s]+(\d+)%?", output_lower)
    if match:
        is_below = int(match.group(1)) < threshold
    else:
        is_below = f"coverage: {threshold}%" not in output_lower and (
            "coverage below threshold" in output_lower or "coverage:" in output_lower
        )
    return is_below and not is_instruction_text(output_lower, _COVERAGE_INSTRUCTIONS)


def check_coverage_target_reached(output: str, target: int) -> bool:
    output_lower = output.lower()
    has_indicator = COVERAGE_TARGET_REACHED_INDICATOR.lower() in output_lower
    if has_indicator:
        return has_indicator and not is_instruction_text(output_lower, _COVERAGE_INSTRUCTIONS)

    match = re.search(r"coverage[:\s]+(\d+)%?", output_lower)
    if match:
        return int(match.group(1)) >= target

    return False


def get_improve_test_coverage_prompt(config: dict[str, Any]) -> str:
    target = config.get("target_coverage", _DEFAULT_THRESHOLD)
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
4. Aim for {target}% coverage
5. Run tests and verify improved coverage
6. Reassess and continue improving until target is reached

When you've reached the target coverage of {target}%, """
        + _COVERAGE_INSTRUCTIONS[0]
        + """ as the last line of your output.
"""
    )


def build_rules(config: dict[str, Any]) -> list[Rule]:
    target = config.get("target_coverage", _DEFAULT_THRESHOLD)
    default_prompt = get_improve_test_coverage_prompt(config)
    condition_prompt = config.get(
        "improve_coverage_prompt",
        "Please analyze the test coverage report and write additional test cases to improve coverage. Focus on areas with the lowest coverage first.",
    )

    return build_standard_rules(
        stop_check=lambda out: check_coverage_target_reached(out.lower(), target),
        condition_check=lambda out: check_coverage_below_threshold(out.lower(), target),
        default_prompt=default_prompt,
        condition_prompt=condition_prompt,
        stop_desc="Target test coverage reached - stop automation",
        condition_desc="Test coverage below threshold - improve coverage",
        default_desc="Default improve coverage prompt - continue improving coverage",
    )
