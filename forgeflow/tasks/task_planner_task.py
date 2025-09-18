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

    The function will look for a file named `{task_name}_config.json` in the workdir.
    If not found, it returns an empty dict.

    Args:
        task_name: Name of the task
        workdir: Working directory where the project is running

    Returns:
        Dictionary containing task configuration
    """
    config_file = os.path.join(workdir, f"{task_name}_config.json")

    # If not found in workdir, try examples directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            examples_dir = (repo_root / "examples").resolve()
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

    # Check if any completion indicator is present
    has_completion_indicator = any(indicator in output_lower for indicator in completion_indicators)

    # Prevent false positives by checking that this isn't just part of our own prompt
    # If we're seeing our own instruction text, it's not a real completion
    is_instruction_text = (
        'respond with "task completed"' in output_lower
        or "respond with 'task completed'" in output_lower
        or 'say "task completed"' in output_lower
        or "say 'task completed'" in output_lower
    )

    return has_completion_indicator and not is_instruction_text


def check_all_tasks_done(output: str) -> bool:
    """Check if all tasks are done."""
    target_text = "All tasks have been completed."
    output_lower = output.lower()

    # Check if the target text is present
    has_target_text = target_text in output

    # Prevent false positives by checking that this isn't just part of our own prompt
    # If we're seeing our own instruction text, it's not a real completion
    is_instruction_text = (
        'return the message: "all tasks have been completed."' in output_lower
        or "return the message: 'all tasks have been completed.'" in output_lower
        or 'respond with "all tasks have been completed."' in output_lower
        or "respond with 'all tasks have been completed.'" in output_lower
    )

    return has_target_text and not is_instruction_text


def get_next_task_prompt(config: dict[str, Any]) -> str:
    """Get the prompt for the next task."""
    todo_file = config.get("todo_file", "TODO.md")

    return f"""
Task Planning Task:
1. Check the TODO file ({todo_file}) to see the list of tasks
2. Identify the first incomplete task
3. Work on completing that task:
   - Follow any specific instructions in the task description
   - Ensure code quality and testing standards
   - Make sure the implementation meets requirements
4. When the task is complete, mark it as completed in the TODO file
5. Commit your changes with an appropriate message
6. Move on to the next task

If your project has specific standards or guidelines, please check and follow them.

Use the following indicators to determine if a task is complete:
- Clear statement of task completion
- Updated TODO file with completed task marked
- Any other specific indicators defined in the task configuration

If you've completed the current task, respond with "Task completed" and 
wait for further instructions.

If you've completed ALL tasks in the TODO file, respond with "All tasks have been completed."
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
                "next_task_prompt", "Please proceed with the next task in the TODO list."
            ),
        ),
        # Default task prompt
        Rule(check=lambda out: True, command=lambda: get_next_task_prompt(config)),
    ]
