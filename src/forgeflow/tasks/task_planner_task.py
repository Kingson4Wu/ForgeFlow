import logging
from typing import Any

from forgeflow.rules.base import Rule
from forgeflow.tasks.common import build_standard_rules, instruction_phrases, is_instruction_text

logger = logging.getLogger("forgeflow")

TASK_COMPLETED_INDICATOR = "[TASK_COMPLETED]"
ALL_TASKS_COMPLETED_INDICATOR = "[ALL_TASKS_COMPLETED]"

_TASK_INSTRUCTIONS = instruction_phrases(TASK_COMPLETED_INDICATOR)
_ALL_TASKS_INSTRUCTIONS = instruction_phrases(ALL_TASKS_COMPLETED_INDICATOR)


def check_task_completed(output: str, config: dict[str, Any]) -> bool:
    output_lower = output.lower()
    indicators = config.get("task_completion_indicators", [TASK_COMPLETED_INDICATOR])
    has_indicator = any(indicator.lower() in output_lower for indicator in indicators)
    return has_indicator and not is_instruction_text(output_lower, _TASK_INSTRUCTIONS)


def check_all_tasks_done(output: str) -> bool:
    output_lower = output.lower()
    has_indicator = ALL_TASKS_COMPLETED_INDICATOR.lower() in output_lower
    return has_indicator and not is_instruction_text(output_lower, _ALL_TASKS_INSTRUCTIONS)


def get_next_task_prompt(config: dict[str, Any]) -> str:
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
   * Only when the task fully meets your project's own completion standards and best practices, you may proceed (for example, ensure tests are written and pass, and code follows style and review guidelines).
   * If it does not fully follow the guidelines, continue refining the task.

5. Mark and commit the task properly.
   * Once the task meets both the implementation plan and best practices:
     * Commit the code to the local repository, ensuring the commit follows the rules in your git commit standard.
     * Mark the task as completed in the TODO file.

6. Move to the next task.
   * Repeat steps 1-5 until all tasks are done.

Use the following indicators to determine if a task is complete:
If you've completed the current task, {_TASK_INSTRUCTIONS[0]} as the last line of your output and then wait for further instructions.
If you've completed ALL tasks in the TODO file, {_ALL_TASKS_INSTRUCTIONS[0]} as the last line of your output.
"""


def build_rules(config: dict[str, Any]) -> list[Rule]:
    default_prompt = get_next_task_prompt(config)
    condition_prompt = config.get(
        "next_task_prompt",
        "Please proceed with the next task in the TODO list only after ensuring the previous one fully meets your project's completion standards and best practices (for example, tests are written and pass, and code follows style and review guidelines).",
    )

    return build_standard_rules(
        stop_check=lambda out: check_all_tasks_done(out.lower()),
        condition_check=lambda out: check_task_completed(out.lower(), config),
        default_prompt=default_prompt,
        condition_prompt=condition_prompt,
        stop_desc="All tasks completed - stop automation",
        condition_desc="Task completed - proceed to next task",
        default_desc="Default task prompt - continue with current task",
    )
