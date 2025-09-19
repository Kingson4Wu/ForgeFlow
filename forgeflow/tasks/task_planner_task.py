import json
import logging
import os
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
            pass

    # If not found in user custom rules tasks directory, try default rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            default_rules_dir = (pkg_dir / "tasks" / "configs").resolve()
            config_file = os.path.join(default_rules_dir, f"{task_name}_config.json")
        except Exception:
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
            pass

    if not os.path.exists(config_file):
        return {}

    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception:
        # If there's an error reading the config file, return empty dict
        return {}


# ---------- Task Rules ----------
def check_task_completed(output: str, config: dict[str, Any]) -> bool:
    """Check if a task has been completed based on the output and config."""
    # Get task completion indicators from config, with defaults
    completion_indicators = config.get(
        "task_completion_indicators",
        ["task completed"],
    )

    output_lower = output.lower()

    # Check if any completion indicator is present (case-insensitive)
    has_completion_indicator = any(
        indicator.lower() in output_lower for indicator in completion_indicators
    )

    # Prevent false positives by checking that this isn't just part of our own prompt
    # If we're seeing our own instruction text, it's not a real completion
    is_instruction_text = (
        'respond with "task completed"' in output_lower
        or "respond with 'task completed'" in output_lower
        or 'say "task completed"' in output_lower
        or "say 'task completed'" in output_lower
        or "when you've completed the current task" in output_lower
        or "please say 'task completed' when done" in output_lower
    )

    return has_completion_indicator and not is_instruction_text


def check_all_tasks_done(output: str) -> bool:
    """Check if all tasks are done."""
    target_text = "all tasks have been completed"
    output_lower = output.lower()

    # Check if the target text is present
    has_target_text = target_text in output_lower

    # Prevent false positives by checking that this isn't just part of our own prompt
    # If we're seeing our own instruction text, it's not a real completion
    is_instruction_text = (
        'return the message: "all tasks have been completed"' in output_lower
        or "return the message: 'all tasks have been completed'" in output_lower
        or 'respond with "all tasks have been completed"' in output_lower
        or "respond with 'all tasks have been completed'" in output_lower
        or "all tasks have been completed." in output_lower
        and (
            "respond with" in output_lower
            or "return the message" in output_lower
            or "please say" in output_lower
        )
    )

    return has_target_text and not is_instruction_text


def get_next_task_prompt(config: dict[str, Any]) -> str:
    """Get the prompt for the next task."""
    todo_file = config.get("todo_file", "TODO.md")

    return f"""
Task Planning Task:

0. Check for abnormal interruption.
   * If the previous task was abnormally interrupted, resume and complete it before proceeding.

1. Check the TODO file ({todo_file}) to see the list of tasks.

2. Identify the first incomplete task.
   * If the current task is not completed, continue working on it.

3. Work on completing that task.
   * Follow any specific instructions in the task description.
   * Ensure code quality and testing standards.
   * Make sure the implementation meets requirements.

4. Verify against completion standards.
   * Only when the task fully meets your project’s own completion standards and best practices, you may proceed (for example, ensure tests are written and pass, and code follows style and review guidelines).
   * If it does not fully follow the guidelines, continue refining the task.

5. Mark and commit the task properly.
   * Once the task meets both the implementation plan and best practices:
     * Commit the code to the local repository, ensuring the commit follows the rules in your git commit standard.
     * Mark the task as completed in the TODO file.

6. Move to the next task.
   * Repeat steps 1–5 until all tasks are done.

Use the following indicators to determine if a task is complete:
If you've completed the current task, respond with "[TASK_COMPLETED]" and wait for further instructions.
If you've completed ALL tasks in the TODO file, respond with "[ALL_TASKS_COMPLETED]".
"""


def build_rules(config: dict[str, Any]) -> list[Rule]:
    """Build rules for task planner task."""
    return [
        # Stop when all tasks are completed
        Rule(check=check_all_tasks_done, command=None),
        # Handle task completion
        Rule(
            check=lambda out: check_task_completed(out, config),
            command=config.get(
                "next_task_prompt",
                "Please proceed with the next task in the TODO list, ensuring it meets your project’s completion standards and best practices (for example, tests are written and pass, and code follows style and review guidelines).",
            ),
        ),
        # Default task prompt
        Rule(check=lambda out: True, command=lambda: get_next_task_prompt(config)),
    ]
