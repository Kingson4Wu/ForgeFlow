from forgeflow.core.rules import Rule


def is_processing(output: str) -> bool:
    return not is_task_completed(output) and not is_final_verification(output)


# Example 1: Simple custom rule that checks for a specific message
def is_task_completed(output: str) -> bool:
    if not output:
        return False
    if 'otherwise, return "All tasks have been completed."' in output:
        return False
    return "All tasks have been completed." in output


def is_final_verification(output: str) -> bool:
    if not output:
        return False
    if '**"All test cases are executed successfully."**' in output:
        return False
    return "All test cases are executed successfully." in output


# Example 2: Custom rule that checks for a pattern in the output
def check_custom_pattern(output: str) -> bool:
    """Custom check for a specific pattern in the output."""
    import re

    pattern = re.compile(r"My project pattern: .*")
    return bool(pattern.search(output))


# Custom prompt messages for the AI
def final_verification_prompt() -> str:
    return r"""
Check all test cases, fix any failures, and ensure all tests pass.
If all conditions are satisfied, return:
**"All test cases are executed successfully."**
"""


def task_prompt() -> str:
    return """
Check if there are any pending optimization tasks; 
if yes, continue execution; 
otherwise, return "All tasks have been completed."
"""


# Build custom rules
def build_rules() -> list[Rule]:
    """Build a list of custom rules for my project."""
    return [
        Rule(check=is_processing, command=task_prompt()),
        Rule(check=is_task_completed, command=final_verification_prompt()),
        Rule(check=is_final_verification, command=None),
        # Custom error handling rules
        Rule(
            check=lambda out: "✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter" in out,
            command="/clear",
        ),
        Rule(check=lambda out: "✕ [API Error: terminated]" in out, command="continue"),
        Rule(check=lambda out: "API Error" in out, command="continue"),
    ]
