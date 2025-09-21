from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

# ---------- Task and Verification Prompts ----------
ALL_TASKS_DONE_TEXT = "All tasks have been completed."
FINAL_VERIFIED_TEXT = "All test cases are fully covered and executed successfully"


def is_all_task_finished(output: str) -> bool:
    if not output:
        return False
    # Avoid false positives from the instruction text itself
    if "5. If all tasks in `@specifications/TODO.md` are completed, return the message:" in output:
        return False
    return ALL_TASKS_DONE_TEXT in output


def is_final_verification_finished(output: str) -> bool:
    if not output:
        return False
    if '**"All test cases are fully covered and executed successfully without errors."**' in output:
        return False
    return FINAL_VERIFIED_TEXT in output


# ---------- Rule System ----------
@dataclass
class Rule:
    check: Callable[[str], bool]
    command: str | None
    description: str = ""


class CommandPostProcessor:
    """Abstract base class for command post-processing.

    Subclasses can override the post_process_command method to implement
    custom logic for modifying commands after they are determined by rules.
    """

    def post_process_command(self, output: str, initial_command: str | None) -> str | None:
        """Post-process a command after it has been determined by rules.

        Args:
            output: The AI CLI output that the command is responding to
            initial_command: The command determined by the rules

        Returns:
            The post-processed command, or None to keep the initial command unchanged
        """
        return None


def default_task_prompt() -> str:
    return r"""
**Important rule:** Do not commit any code until the task fully meets the guidelines in
`@specifications/best_practices.md`.

0. Check whether the previous task was abnormally interrupted.

   * If it was, resume and complete it before proceeding.

1. Read the current task from `@specifications/TODO.md`.

   * If the task is not completed, continue working on it.

2. Check if the task is completed according to the implementation plan in
   `@specifications/task_specs/`.

   * If it is completed, verify whether it follows the guidelines in
     `@specifications/best_practices.md`.
   * If it does not fully follow the guidelines, continue refining the task.

3. Once the task meets both the implementation plan and the best practices:

   * Commit the code to the local repository, **ensuring the commit follows the rules in
     `@specifications/git_standards.md`**.
   * After committing, execute the script `@scripts/clean_commit.sh`.
   * Mark the task as completed in `@specifications/TODO.md`.

4. Move to the next task and repeat steps 1–3.

5. If all tasks in `@specifications/TODO.md` are completed, return the message:
   "All tasks have been completed."
"""


def final_verification_prompt() -> str:
    return r"""
1. Check all test cases, fix any failures, and ensure all tests pass.
2. Review all projects to confirm that test cases are complete and meet the required coverage
   standards.
3. Verify that all test cases are consistently structured and well-organized, and that all related
   scripts function correctly.

If all conditions are satisfied, return:
**"All test cases are fully covered and executed successfully without errors."**
"""


def build_default_rules(cli_type: str = "gemini") -> list[Rule]:
    # Common rules that apply to all CLI types
    common_rules: list[Rule] = [
        # Rule(check=is_all_task_finished, command=final_verification_prompt()),
        # Rule(check=is_final_verification_finished, command=None),  # stop
        # Rule(
        #     check=lambda out: "✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter" in out,
        #     command="/clear",
        # ),
        # Rule(check=lambda out: "✕ [API Error: terminated]" in out, command="continue"),
        # Rule(check=lambda out: "API Error" in out, command="continue"),
    ]

    # CLI type specific rules
    cli_specific_rules = []
    if cli_type == "gemini":
        cli_specific_rules = _build_gemini_rules()
    elif cli_type == "codex":
        cli_specific_rules = _build_codex_rules()
    elif cli_type == "claude_code":
        cli_specific_rules = _build_claude_code_rules()

    # Combine rules: CLI-specific rules take precedence, followed by common rules
    all_rules = cli_specific_rules + common_rules

    # Add the default task prompt as the last rule
    # all_rules.append(Rule(check=lambda out: True, command=final_verification_prompt()))

    return all_rules


def _build_gemini_rules() -> list[Rule]:
    """Build rules specific to Gemini CLI."""
    # Import the gemini rules module dynamically
    try:
        from .cli_types.gemini_rules import build_rules

        return build_rules()
    except ImportError:
        # Fallback to the previous implementation if the module cannot be imported
        return []


def _build_codex_rules() -> list[Rule]:
    """Build rules specific to Codex CLI."""
    # Import the codex rules module dynamically
    try:
        from .cli_types.codex_rules import build_rules

        return build_rules()
    except ImportError:
        # Fallback to the previous implementation if the module cannot be imported
        return []


def _build_claude_code_rules() -> list[Rule]:
    """Build rules specific to Claude Code CLI."""
    # Import the claude code rules module dynamically
    try:
        from .cli_types.claude_code_rules import build_rules

        return build_rules()
    except ImportError:
        # Fallback to the previous implementation if the module cannot be imported
        return []


def get_command_post_processor(cli_type: str = "gemini") -> CommandPostProcessor | None:
    """Get the command post-processor for the specified CLI type.

    Args:
        cli_type: The CLI type to get the post-processor for

    Returns:
        The command post-processor for the CLI type, or None if none exists
    """
    if cli_type == "codex":
        from .cli_types.codex_rules import CodexCommandPostProcessor

        return CodexCommandPostProcessor()
    # Add other CLI types here as needed
    return None


def next_command(
    output: str,
    rules: list[Rule],
    cli_type: str = "gemini",
    logger: logging.Logger | None = None,
) -> str | None:
    # First, determine the command using the existing rule system
    initial_command = None
    rule_matched = False
    matched_rule = None
    for rule in rules:
        try:
            if rule.check(output):
                initial_command = rule.command
                rule_matched = True
                matched_rule = rule
                break
        except Exception:
            # Ignore exceptions in individual rules and continue evaluation
            # This is a deliberate design choice to ensure robust rule evaluation
            continue

    # If a rule matched, log the description if available
    if rule_matched and matched_rule and matched_rule.description:
        if logger:
            logger.info(f"Rule matched: {matched_rule.description}")

    # If a rule matched and it explicitly returns None, stop automation
    if rule_matched and initial_command is None:
        return None

    # If no rule matched, default to "continue"
    if not rule_matched:
        initial_command = "continue"

    # Get the post-processor for this CLI type
    post_processor = get_command_post_processor(cli_type)

    # If there's a post-processor, let it modify the command
    if post_processor:
        processed_command = post_processor.post_process_command(output, initial_command)
        # If post-processing changed the command, log it
        if processed_command is not None and logger:
            if rule_matched and matched_rule and matched_rule.description:
                logger.info(
                    f"Post-processed command '{initial_command}' to '{processed_command}' based on rule: {matched_rule.description}"
                )
            else:
                logger.info(f"Post-processed command: {processed_command}")
        if processed_command is not None:
            return processed_command

    # Return the initial command if no post-processing occurred
    return initial_command
