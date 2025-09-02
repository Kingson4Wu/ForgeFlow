from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

# ---------- Input Prompt Detection ----------
PROMPT_RE = re.compile(r">.*Type your message or @[\w/]+(?:\.\w+)?")
# Match input lines enclosed in vertical bars (as loose as possible)
PROMPT_WITH_TEXT_RE = re.compile(r"\u2502 > .*? \u2502")
PROMPT_TASK_PROCESSING = re.compile(r"^\(esc to cancel.*\)$")


def is_input_prompt(output: str) -> bool:
    if not output:
        return False
    return bool(PROMPT_RE.search(output))


def is_input_prompt_with_text(output: str) -> bool:
    if not output:
        return False
    return bool(PROMPT_WITH_TEXT_RE.search(output))


def is_task_processing(output: str) -> bool:
    for line in output.splitlines():
        if PROMPT_TASK_PROCESSING.match(line.strip()):
            return True
    return False


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


def build_default_rules() -> list[Rule]:
    return [
        Rule(check=is_all_task_finished, command=final_verification_prompt()),
        Rule(check=is_final_verification_finished, command=None),  # stop
        Rule(
            check=lambda out: "✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter" in out,
            command="/clear",
        ),
        Rule(check=lambda out: "✕ [API Error: terminated]" in out, command="continue"),
        Rule(check=lambda out: "API Error" in out, command="continue"),
        Rule(check=lambda out: True, command=final_verification_prompt()),
    ]


def next_command(output: str, rules: list[Rule]) -> str | None:
    for rule in rules:
        try:
            if rule.check(output):
                return rule.command
        except Exception:
            # Ignore exceptions in individual rules and continue evaluation
            continue
    return "continue"
