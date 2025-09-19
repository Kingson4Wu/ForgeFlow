# ForgeFlow

[![Build Status](https://github.com/Kingson4Wu/ForgeFlow/workflows/CI/badge.svg)](https://github.com/Kingson4Wu/ForgeFlow/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Automatically drives AI CLI to continuously complete programming tasks within a `tmux` session.

## Features

- **Robust Session Management**: Automatically creates/reuses `tmux` sessions, separating text from enter when pasting
  commands.
- **Configurable Rule System**: Rules are evaluated in order, with priority matching taking effect, and custom rules are
  supported.
- **Multi-CLI Support**: Supports different AI CLI tools through an adapter pattern (currently supports Gemini as the
  default, with a placeholder for Claude Code).
- **Reliable Input Detection**: Regular expressions detect "input prompts" and "existing text in input box" specific to
  each CLI tool.
- **Timeout Recovery Strategy**: Long periods without input prompt → send `ESC` → backspace clear → `continue`.
- **Logging and Debugging**: Dual channel file + console logging with timestamps.
- **CI and Testing**: `ruff` + `black` compliance, `pytest` unit tests covering core logic.

## Quick Start

### Clone and Set Up the Project

To clone and set up the project, follow these steps:

1. Clone the repository locally:
   ```bash
   git clone https://github.com/Kingson4Wu/ForgeFlow
   cd ForgeFlow
   ```

### Quick Start for Mac Users

For Mac users, see our [Quick Start Guide for Mac Users](docs/quick_start_mac.md) which provides detailed step-by-step
instructions for setting up and using ForgeFlow on macOS.

### Installation

#### Install with pip

You can quickly install the project dependencies using pip:

```bash
pip install -e .
```

#### Using Conda Environment

If you prefer to use a Conda environment, you can set it up with the following steps:

1. Create a new Conda environment:
   ```bash
   conda create -n forgeflow python=3.9
   ```

2. Activate the Conda environment:
   ```bash
   conda activate forgeflow
   ```

3. Install project dependencies:
   ```bash
   pip install -e .
   ```

### Running

After installation, you can run ForgeFlow with the following command:

```bash
forgeflow \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

Note: By default, ForgeFlow uses the Gemini CLI adapter. To use a different adapter, specify the `--cli-type` parameter.

To use custom rules for a specific project, add the `--project` parameter:

```bash
forgeflow \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --project myproject \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

To use predefined rules for a specific task type, add the `--task` parameter:

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

To specify a different AI CLI tool, use the `--cli-type` parameter (default is "gemini"):

```bash
forgeflow \
  --session claude_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "claude" \
  --cli-type claude_code \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

For example, to use the built-in web development rules:

```bash
forgeflow \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --project web_project \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

### Running the Script Directly (without installation)

If you want to run the script directly without installing the package, you can use the following command:

```bash
python -m forgeflow.cli \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

To specify a different AI CLI tool:

```bash
python -m forgeflow.cli \
  --session qwen_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

Note: When using this method, make sure you're running the command in the project's root directory.

## Development Guide

### Running Test Cases

First, ensure you have installed the development dependencies:

```bash
pip install -e ".[dev]"
```

Then, you can run all test cases with the following command:

```bash
python -m pytest tests/ -v
```

### IDE Debugging

The project includes default test cases for convenient breakpoint debugging in IDEs:

1. `tests/test_prompt_detection.py`:
    - `test_is_input_prompt_false_on_empty()`: Tests input prompt detection with empty string
    - `test_is_input_prompt_with_text_false_on_empty()`: Tests input prompt with text detection with empty string
    - `test_is_input_prompt_true_sample()`: Tests detection of sample input prompt

2. `tests/test_rules.py`:
    - `test_is_all_task_finished_ok()`: Tests detection of task completion status
    - `test_is_final_verification_finished_ok()`: Tests detection of final verification status

These test cases can be run and debugged directly in IDEs to help you quickly verify code changes.

### Custom Rules

ForgeFlow's core design philosophy is to allow users to customize rules according to different project requirements.

#### CLI Type Specific Rules

ForgeFlow now supports CLI type specific default rules. Different AI CLI tools may have different error patterns and
behaviors, so ForgeFlow provides specific default rules for each supported CLI type:

1. **Gemini CLI**: Rules specific to Google's Gemini CLI
2. **Codex CLI**: Rules specific to OpenAI's Codex CLI
3. **Claude Code CLI**: Rules specific to Anthropic's Claude Code CLI

These default rules handle common error patterns and recovery strategies for each CLI type. You can specify the CLI type
using the `--cli-type` parameter when running ForgeFlow.

#### Creating Custom Rule Files

To create custom rules, you need to implement the following components:

1. **Check Functions**: Receive AI output string and return a boolean value
2. **Command Strings**: Instructions to send to the AI when the check function returns True
3. **Rule List**: A list of Rule objects combining check functions and command strings
4. **Build Function**: A function named `build_rules` that returns the list of rules

##### File Naming

Your custom rule file can be named either:

- `{project_name}_rules.py` (e.g., `myproject_rules.py`)
- `{project_name}.py` (e.g., `myproject.py`)

##### Function Naming

The rule-building function should be named `build_rules` for consistency across all projects:

```python
def build_rules() -> list[Rule]:
    # Your custom rules here
    pass
```

See [myproject_rules.py](examples/myproject_rules.py) for a complete template.

#### Examples

We provide several examples to help you get started:

1. [projects/](examples/projects/) - Project-specific rule examples
    - [custom_project_rules.py](examples/projects/custom_project_rules.py) - General custom rules example
    - [myproject_rules.py](examples/projects/myproject_rules.py) - Template for creating your own project rules
    - [web_project_rules.py](examples/projects/web_project_rules.py) - Example web project rules
2. [tasks/](examples/tasks/) - Task-specific rule examples
    - [code_review_task.py](examples/tasks/code_review_task.py) - Code review task rules

For built-in default rules, please check:

1. [forgeflow/core/cli_types/](forgeflow/core/cli_types/) - Default rules for different CLI types
    - [gemini_rules.py](forgeflow/core/cli_types/gemini_rules.py) - Default rules for Gemini CLI
    - [codex_rules.py](forgeflow/core/cli_types/codex_rules.py) - Default rules for Codex CLI
    - [claude_code_rules.py](forgeflow/core/cli_types/claude_code_rules.py) - Default rules for Claude Code CLI
2. [forgeflow/tasks/configs/](forgeflow/tasks/configs/) - Default task configurations
    - [improve_coverage_config.json](forgeflow/tasks/configs/improve_coverage_config.json) - Improve coverage task config
    - [task_planner_config.json](forgeflow/tasks/configs/task_planner_config.json) - Task planner config

#### Using Custom Rules

Use the `--project` parameter to automatically load your custom rules:

1. Create a rule file named `{project_name}_rules.py` (e.g., `myproject_rules.py`) or `{project_name}.py`
2. Place it in your project directory or in the `user_custom_rules/` directory
3. Run ForgeFlow with `--project myproject` parameter

The system will automatically search for your rule file in the following order:

1. `{project_name}_rules.py` in the current working directory
2. `{project_name}.py` in the current working directory
3. `{project_name}_rules.py` in the `user_custom_rules/` directory
4. `{project_name}.py` in the `user_custom_rules/` directory
5. `{project_name}_rules.py` in the `default_rules/` directory (built-in default rules)
6. `{project_name}.py` in the `default_rules/` directory (built-in default rules)
7. `{project_name}_rules.py` in the `examples/` directory (for backward compatibility)
8. `{project_name}.py` in the `examples/` directory (for backward compatibility)

It will then look for a rule-building function. The recommended function name is `build_rules`, which provides
consistency across all projects.

### Task Mode

ForgeFlow also supports task mode, which allows you to define reusable rules for specific types of tasks. Task mode can
be used in conjunction with project mode to provide finer control over specific tasks.

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

ForgeFlow comes with several built-in task types:

- `fix_tests`: Automatically fix failing test cases
- `improve_coverage`: Improve test coverage to a target percentage
- `task_planner`: Follow a TODO list to complete tasks in order

Additionally, you can create custom task types by implementing a Python module with a `build_rules` function. Default
task configurations can be found in the [default_rules/](default_rules/) directory.
See [Task Mode Documentation](docs/task_mode.md) for more details on creating custom tasks.

### CLI Adapter Pattern

ForgeFlow uses an adapter pattern to support different AI CLI tools. Each CLI tool has its own adapter that implements
the `CLIAdapter` interface, which defines methods for detecting input prompts, task processing states, and CLI
existence.

Currently supported adapters:

- **Gemini**: The default and currently only fully implemented adapter for Google's Qwen/Gemini CLI
- **Claude Code**: Placeholder adapter for Anthropic's Claude Code CLI (contains TODOs for implementation)

To add support for a new CLI tool:

1. Create a new adapter class that extends `CLIAdapter`
2. Implement all abstract methods according to your CLI's behavior
3. Register your adapter in the factory function in `forgeflow/core/cli_adapters/factory.py`
4. Use the `--cli-type` parameter to select your adapter

### Exiting

* Normal exit: Automatically exits when final verification is detected.
* Force stop: `Ctrl-C` (the script will exit gracefully without closing your `tmux` session).

## License

[MIT](./LICENSE)