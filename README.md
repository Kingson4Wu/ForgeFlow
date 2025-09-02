# ForgeFlow

Automatically drives AI CLI to continuously complete programming tasks within a `tmux` session.

## Features

- **Robust Session Management**: Automatically creates/reuses `tmux` sessions, separating text from enter when pasting commands.
- **Configurable Rule System**: Rules are evaluated in order, with priority matching taking effect, and custom rules are supported.
- **Reliable Input Detection**: Regular expressions detect \"input prompts\" and \"existing text in input box\".
- **Timeout Recovery Strategy**: Long periods without input prompt → send `ESC` → backspace clear → `continue`.
- **Logging and Debugging**: Dual channel file + console logging with timestamps.
- **CI and Testing**: `ruff` + `black` compliance, `pytest` unit tests covering core logic.

## Quick Start

### Clone and Set Up the Project

To clone and set up the project, follow these steps:

1. Clone the repository locally:
   ```bash
   git clone <repository-url>
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
forgeflow \\
  --session qwen_session \\
  --workdir \"/absolute/path/to/your/project\" \\
  --ai-cmd \"qwen --proxy http://localhost:7890 --yolo\" \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

### Running the Script Directly (without installation)

If you want to run the script directly without installing the package, you can use the following command:

```bash
python -m forgeflow.cli \\
  --session qwen_session \\
  --workdir \"/absolute/path/to/your/project\" \\
  --ai-cmd \"qwen --proxy http://localhost:7890 --yolo\" \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

Note: When using this method, make sure you're running the command in the project's root directory.

## Development Guide

### Running Test Cases

First, ensure you have installed the development dependencies:

```bash
pip install -e \".[dev]\"
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

ForgeFlow's core design philosophy is to allow users to customize rules according to different project requirements. In most cases, you only need to modify the `rules.py` file without changing other parts.

#### Creating Custom Rule Files

To create custom rules, you need to implement the following components:

1. **Check Functions**: Receive AI output string and return a boolean value
2. **Command Strings**: Instructions to send to the AI when the check function returns True
3. **Rule List**: A list of Rule objects combining check functions and command strings

#### Examples

We provide several examples to help you get started:

1. [custom_rules_example.py](examples/custom_rules_example.py) - General custom rules example
2. [web_project_rules.py](examples/web_project_rules.py) - Web project specific rules example

#### Using Custom Rules

To use your custom rules file, you need to:

1. Place your custom rules file in the project
2. Modify the `automation.py` file to import and use your custom rule building function
3. Rerun ForgeFlow

### Exiting

* Normal exit: Automatically exits when final verification is detected.
* Force stop: `Ctrl-C` (the script will exit gracefully without closing your `tmux` session).

## License

[MIT](./LICENSE)
