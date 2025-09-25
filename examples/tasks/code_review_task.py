from forgeflow.core.rules import Rule


# Example: Custom task rules for a code review task
def check_review_completed(output: str) -> bool:
    """Check if a code review has been completed."""
    return "code review completed" in output.lower() or "review finished" in output.lower()


def code_review_prompt() -> str:
    """Task prompt for code review task."""
    return """
Code Review Task:
1. Review the code changes for the current task
2. Check for:
   - Code style and formatting issues
   - Potential bugs or edge cases
   - Performance improvements
   - Security vulnerabilities
3. Provide constructive feedback
4. Approve the changes when all issues are addressed
5. When review is complete, respond with "Code review completed"
"""


def build_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for code review task."""
    return [
        # Stop when review is completed
        Rule(
            check=check_review_completed,
            command=None,
            description="Code review completed - stop automation",
        ),
        # Default review prompt
        Rule(
            check=lambda out: True,
            command=code_review_prompt(),
            description="Default code review prompt - continue with code review",
        ),
    ]


# Add alias for backward compatibility
build_code_review_rules = build_rules
