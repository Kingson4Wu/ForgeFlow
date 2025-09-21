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


def build_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for web project."""
    return [
        # Stop when web project is completed
        Rule(
            check=lambda out: "Web project completed" in out,
            command=None,
            description="Web project completed - stop automation",
        ),
        # Handle build errors
        Rule(
            check=check_build_error,
            command="npm run clean && npm run build",
            description="Build error detected - clean and rebuild",
        ),
        # Handle server restart
        Rule(
            check=lambda out: "Server needs restart" in out,
            command="npm run restart",
            description="Server needs restart - restart server",
        ),
        # Run tests when server is running
        Rule(
            check=check_server_running, command="npm test", description="Server running - run tests"
        ),
        # Default task prompt
        Rule(
            check=lambda out: True,
            command=web_dev_task_prompt(),
            description="Default web project prompt - continue with web development task",
        ),
    ]


# Add alias for backward compatibility
build_web_project_rules = build_rules
