from forgeflow.core.rules import Rule


# Example: Project-specific rules for a web development project
def check_build_error(output: str) -> bool:
    """Check for build errors in a web development project."""
    return "Build failed" in output or "Compilation error" in output


def check_server_running(output: str) -> bool:
    """Check if the development server is running."""
    return "Server running on" in output


def web_dev_task_prompt() -> str:
    """Task prompt for web development projects."""
    return """
Web Development Task:
1. Implement the requested feature
2. Ensure responsive design
3. Follow accessibility guidelines
4. Run tests and fix any failures
"""


def build_rules() -> list[Rule]:
    """Build rules specific to web development projects."""
    return [
        # Stop when project is complete
        Rule(check=lambda out: "Web project completed" in out, command=None),
        # Handle build errors
        Rule(check=check_build_error, command="npm run clean && npm run build"),
        # Restart server if needed
        Rule(check=lambda out: "Server needs restart" in out, command="npm run restart"),
        # Verify server is running
        Rule(check=check_server_running, command="npm test"),
        # Default task prompt
        Rule(check=lambda out: True, command=web_dev_task_prompt()),
    ]


# Add alias for backward compatibility
build_web_project_rules = build_rules
