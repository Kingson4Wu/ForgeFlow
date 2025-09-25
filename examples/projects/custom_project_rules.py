from forgeflow.core.rules import Rule


# Example 1: Simple custom rule that checks for a specific error message
def check_specific_error(output: str) -> bool:
    """Custom check for a specific error message."""
    return "Specific Error Message" in output


# Example 2: Custom rule that checks for a pattern in the output
def check_custom_pattern(output: str) -> bool:
    """Custom check for a specific pattern in the output."""
    import re

    pattern = re.compile(r"Custom pattern: .*")
    return bool(pattern.search(output))


# Example 3: Custom rule that combines multiple conditions
def check_complex_condition(output: str) -> bool:
    """Custom check that combines multiple conditions."""
    return "Condition 1" in output and "Condition 2" in output


# Custom prompt messages for the AI
def custom_task_prompt() -> str:
    """Custom task prompt for the AI."""
    return """
Custom task instructions for the AI:
1. Follow these specific guidelines
2. Handle the custom error cases
3. Return the expected output format
"""


def custom_verification_prompt() -> str:
    """Custom verification prompt for the AI."""
    return """
Custom verification steps:
1. Verify that all custom conditions are met
2. Check for specific error patterns
3. Confirm the output format is correct
"""


# Build custom rules
def build_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for custom project."""
    return [
        # Stop when all custom tasks are completed
        Rule(
            check=lambda out: "All custom tasks completed" in out,
            command=None,
            description="Custom project tasks completed - stop automation",
        ),
        # Handle specific errors
        Rule(
            check=check_specific_error,
            command="/clear",
            description="Specific error detected - clear session",
        ),
        # Handle another error
        Rule(
            check=lambda out: "Another Error" in out,
            command="retry",
            description="Another error detected - retry",
        ),
        # Handle custom patterns
        Rule(
            check=check_custom_pattern,
            command=custom_task_prompt(),
            description="Custom pattern detected - execute custom task",
        ),
        # Handle complex conditions
        Rule(
            check=check_complex_condition,
            command=custom_verification_prompt(),
            description="Complex condition met - execute custom verification",
        ),
        # Default task prompt
        Rule(
            check=lambda out: True,
            command=custom_task_prompt(),
            description="Default custom project prompt - continue with custom task",
        ),
    ]
