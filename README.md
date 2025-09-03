# ForgeFlow

[![Build Status](https://github.com/Kingson4Wu/ForgeFlow/workflows/CI/badge.svg)](https://github.com/Kingson4Wu/ForgeFlow/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Automatically drives AI CLI to continuously complete programming tasks within a `tmux` session.

## Features

- **Robust Session Management**: Automatically creates/reuses `tmux` sessions, separating text from enter when pasting
  commands.
- **Configurable Rule System**: Rules are evaluated in order, with priority matching taking effect, and custom rules are
  supported.
- **Reliable Input Detection**: Regular expressions detect "input prompts" and "existing text in input box".
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
  --session claude_session \
  --workdir "/absolute/path/to/your/project" \
  --ai-cmd "claude" \
  --cli-type claude_code \
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

For backward compatibility, the loader will also look for project-specific function names in this order:
1. `build_{project_name}_rules` (e.g., `build_web_project_rules`)
2. `build_{project_name}` (e.g., `build_web_project`)
3. `build_custom_rules`
4. `{project_name}_rules` (e.g., `web_project_rules`)
5. `rules`

See [myproject_rules.py](examples/myproject_rules.py) for a complete template.

#### Examples

We provide several examples to help you get started:

1. [custom_rules_example.py](examples/custom_rules_example.py) - General custom rules example (
   function: `build_rules`)
2. [web_project_rules.py](examples/web_project_rules.py) - Web project specific rules example (
   function: `build_rules`)
3. [myproject_rules.py](examples/myproject_rules.py) - Template for creating your own project rules (
   function: `build_rules`)

#### Using Custom Rules

Use the `--project` parameter to automatically load your custom rules:

1. Create a rule file named `{project_name}_rules.py` (e.g., `myproject_rules.py`) or `{project_name}.py`
2. Place it in your project directory or in the `examples/` directory
3. Run ForgeFlow with `--project myproject` parameter

The system will automatically search for your rule file in the following order:

1. `{project_name}_rules.py` in the current working directory
2. `{project_name}.py` in the current working directory
3. `{project_name}_rules.py` in the `examples/` directory
4. `{project_name}.py` in the `examples/` directory

It will then look for a rule-building function with one of these names (in order):

- `build_{project_name}_rules`
- `build_{project_name}`
- `build_custom_rules`
- `build_rules`
- `{project_name}_rules`
- `rules`

### Exiting

* Normal exit: Automatically exits when final verification is detected.
* Force stop: `Ctrl-C` (the script will exit gracefully without closing your `tmux` session).

## License

[MIT](./LICENSE)