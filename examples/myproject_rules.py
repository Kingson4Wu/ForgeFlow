"""
Example of how to create a custom rule file for your project.

To use this rule file:
1. Save it as `myproject_rules.py` in your project directory
2. Run ForgeFlow with `--project myproject`

The rule loader will automatically find and load this file.
"""

from forgeflow.core.rules import Rule


# Example 1: Simple custom rule that checks for a specific message
def check_project_specific_message(output: str) -> bool:
    """Custom check for a project-specific message."""
    return "PROJECT_SPECIFIC_MESSAGE" in output


# Example 2: Custom rule that checks for a pattern in the output
def check_custom_pattern(output: str) -> bool:
    """Custom check for a specific pattern in the output."""
    import re

    pattern = re.compile(r"My project pattern: .*")
    return bool(pattern.search(output))


# Custom prompt messages for the AI
def my_project_task_prompt() -> str:
    """Custom task prompt for the project."""
    return """
My Project Task Instructions:
1. Follow the project-specific guidelines
2. Handle custom error cases
3. Return the expected output format
"""


def my_verification_prompt() -> str:
    """Custom verification prompt for the project."""
    return """
My Project Verification Steps:
1. Verify that all project conditions are met
2. Check for specific error patterns
3. Confirm the output format is correct
"""


# Build custom rules
def build_myproject_rules() -> list[Rule]:
    """Build a list of custom rules for my project."""
    return [
        # Stop rule - when this condition is met, automation stops
        Rule(check=lambda out: "My project tasks completed" in out, command=None),
        # Custom error handling rules
        Rule(check=check_project_specific_message, command="/clear"),
        Rule(check=lambda out: "Another Project Error" in out, command="retry"),
        # Pattern-based rules
        Rule(check=check_custom_pattern, command=my_project_task_prompt()),
        # Default rule that always matches (acts as a fallback)
        Rule(check=lambda out: True, command=my_project_task_prompt()),
    ]