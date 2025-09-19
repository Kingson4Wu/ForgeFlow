# Task Mode Configuration

ForgeFlow supports task mode, allowing you to define reusable rules for specific types of tasks. Task mode can be used
in conjunction with project mode to provide finer control over specific tasks.

## Using Task Mode

To use task mode, specify the task type using the `--task` parameter:

```bash
forgeflow \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --task fix_tests \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

## Available Task Types

### 1. `fix_tests` - Fix Test Cases

This task type focuses on identifying and fixing failing test cases.

### 2. `improve_coverage` - Improve Test Coverage

This task type focuses on improving the test coverage of the project.

### 3. `task_planner` - Task Planner

This task type follows a TODO file to complete tasks in order, marking them as completed as it goes.

## Creating Custom Task Types

ForgeFlow now supports creating custom task types that can be reused across projects. To create a custom task type:

1. Create a Python file named `{task_name}_task.py` or `{task_name}.py`
2. Implement a `build_rules(config)` function that returns a list of Rule objects
3. Place the file in your project directory, in the `user_custom_rules/` directory, or in the `default_rules/` directory
   for built-in default rules

### Example Custom Task

Here's an example of a custom task for code review:

```python
from forgeflow.core.rules import Rule

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

def build_rules(config: dict) -> list[Rule]:
    """Build rules for code review task."""
    return [
        # Stop when review is completed
        Rule(check=check_review_completed, command=None),
        # Default task prompt
        Rule(check=lambda out: True, command=code_review_prompt()),
    ]
```

Save this as `code_review_task.py` in your project directory, in the `user_custom_rules/` directory, or in
the `default_rules/` directory, and then use it with:

```bash
forgeflow \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --task code_review \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

## Task Configuration

You can create configuration files for tasks to customize their behavior. Configuration files should be placed in the
project's working directory with the filename format `{task_name}_config.json`.

### Example: Improve Coverage Task Configuration

Create a file named `improve_coverage_config.json`:

```json
{
  "target_coverage": 90
}
```

This will set the test coverage target to 90% instead of the default 80%.

### Example: Task Planner Configuration

Create a file named `task_planner_config.json`:

```json
{
  "todo_file": "TODO.md",
  "completed_marker": "✓",
  "pending_marker": "☐",
  "task_pattern": "^\\s*[-*]\\s+\\[(.)\\]\\s+(.+)$",
  "next_task_prompt": "Please proceed with the next task in the TODO list.",
  "task_completion_indicators": [
    "task completed",
    "task finished",
    "done with task",
    "finished task"
  ],
  "commit_message_template": "Complete task: {task_title}"
}
```

This configuration defines:

- The TODO file to use (`TODO.md`)
- Characters to mark completed and pending tasks
- Regex pattern to identify tasks in the TODO file
- Prompt to use when moving to the next task
- Indicators to detect when a task is completed
- Template for commit messages

## Using with Project Mode

Task mode can be used in conjunction with project mode. When both `--project` and `--task` parameters are specified,
task mode rules take precedence over project rules:

```bash
forgeflow \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --project web_project \
  --task fix_tests \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

In this example, the rules for the `fix_tests` task will be used, but if the task rules are not found or fail to load,
the system will fall back to the `web_project` project rules.