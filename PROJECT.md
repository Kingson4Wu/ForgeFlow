# ForgeFlow Project Context for AI Programming

This document provides technical context for AI programming assistance in the ForgeFlow project. Unlike README.md which is intended for end users, this file contains detailed information about the project's architecture, design patterns, and implementation details to help AI better understand and contribute to the codebase.

## Project Overview

ForgeFlow is a Python application that automatically drives AI CLI tools to continuously complete programming tasks within a `tmux` session. It provides robust session management, configurable rule systems, multi-CLI support, reliable input detection, and timeout recovery strategies.

## Architecture and Design Patterns

### Core Components

1. **TmuxCtl (`forgeflow/core/tmux_ctl.py`)**:
   - Manages tmux sessions for interacting with AI CLI tools
   - Provides methods for sending text, enter, escape, and backspace commands
   - Handles session creation and output capture

2. **Automation Engine (`forgeflow/core/automation.py`)**:
   - Core automation loop that drives the interaction with AI CLI tools
   - Implements timeout recovery strategies
   - Manages task processing states

3. **Rule System (`forgeflow/core/rules.py`, `forgeflow/core/task_rules.py`)**:
   - Configurable rule evaluation system
   - Supports both general rules and task-specific rules
   - Rules are evaluated in order with priority matching

4. **Rule Loader (`forgeflow/core/rule_loader.py`)**:
   - Loads custom rules from various sources
   - Resolves rule files from different directories
   - Supports different types of rule definitions

5. **CLI Adapters (`forgeflow/core/cli_adapters/`)**:
   - Adapter pattern implementation for supporting different AI CLI tools
   - Includes implementations for Gemini, Codex, and Claude Code
   - Provides interface for detecting input prompts and task processing states

### Task System

The project implements a task-based system with the following components:

1. **Task Planner (`forgeflow/tasks/task_planner_task.py`)**:
   - Follows a TODO list to complete tasks in order
   - Configurable through JSON configuration files

2. **Fix Tests Task (`forgeflow/tasks/fix_tests_task.py`)**:
   - Automatically fixes failing test cases
   - Monitors test output and generates fix commands

3. **Improve Coverage Task (`forgeflow/tasks/improve_coverage_task.py`)**:
   - Improves test coverage to a target percentage
   - Monitors coverage reports and generates test cases

### Key Design Patterns

1. **Adapter Pattern**:
   - Used for supporting different AI CLI tools
   - Defined in `forgeflow/core/cli_adapters/base.py`
   - Implementations in `forgeflow/core/cli_adapters/`

2. **Factory Pattern**:
   - Used for creating CLI adapters
   - Implemented in `forgeflow/core/cli_adapters/factory.py`

3. **Rule-Based System**:
   - Configurable rules that are evaluated in order
   - Priority matching with early exit on first match
   - Support for custom rules at project and task levels

## Code Structure

```
forgeflow/
├── cli.py                 # Command-line interface
├── core/
│   ├── tmux_ctl.py        # Tmux session management
│   ├── automation.py       # Core automation engine
│   ├── rules.py           # General rule definitions
│   ├── task_rules.py      # Task-specific rule handling
│   ├── rule_loader.py     # Rule loading and resolution
│   ├── ansi.py            # ANSI escape code parsing
│   ├── cli_adapters/      # CLI adapter implementations
│   └── cli_types/         # Default rules for CLI types
└── tasks/
    ├── task_planner_task.py      # Task planner implementation
    ├── fix_tests_task.py         # Test fixing task
    ├── improve_coverage_task.py  # Coverage improvement task
    └── configs/                  # Default task configurations
```

## Key Classes and Interfaces

### CLIAdapter (Base Class)
Abstract base class for CLI adapters:
- `is_input_prompt(output: str) -> bool`: Detects input prompts
- `is_input_prompt_with_text(output: str) -> tuple[bool, str]`: Detects prompts with existing text
- `is_task_processing(output: str) -> bool`: Detects task processing states
- `is_ai_cli_exist() -> bool`: Checks if CLI tool is available
- `wants_ansi() -> bool`: Indicates if CLI wants ANSI output

### TmuxCtl
Manages tmux sessions for AI CLI interaction:
- `create_session()`: Creates or reuses tmux session
- `send_text_then_enter(text: str)`: Sends text followed by enter
- `send_enter()`: Sends enter key
- `send_escape()`: Sends escape key
- `send_backspace(count: int = 1)`: Sends backspace key
- `capture_output() -> str`: Captures session output

### Rule
Represents a rule with a check function and command:
- `check: Callable[[str], bool]`: Function to check condition
- `command: str`: Command to execute when condition is met

## Configuration and Customization

### Project Structure for Custom Rules

Custom rules can be defined at different levels:
1. Project-level rules: `{project_name}_rules.py` or `{project_name}.py`
2. Task-level rules: Defined in task-specific modules
3. CLI-type rules: Default rules for specific CLI tools

### Rule File Resolution Order

The system searches for rule files in the following order:
1. `{project_name}_rules.py` in the current working directory
2. `{project_name}.py` in the current working directory
3. `{project_name}_rules.py` in the `user_custom_rules/` directory
4. `{project_name}.py` in the `user_custom_rules/` directory
5. Built-in default rules in the codebase

### Task Configuration

Tasks can be configured through JSON files located in `forgeflow/tasks/configs/`:
- `task_planner_config.json`: Configuration for task planner
- `improve_coverage_config.json`: Configuration for coverage improvement

## Development Guidelines

### Code Quality Tools

The project uses several tools to ensure code quality:
1. **Ruff**: For linting and code formatting
2. **Black**: For code formatting
3. **MyPy**: For type checking
4. **Bandit**: For security checking
5. **Radon**: For complexity analysis
6. **Flake8**: For additional code quality checks

Run all checks with:
```bash
./scripts/check-health.sh
```

### Testing

The project uses pytest for testing with:
- Unit tests for core functionality
- Integration tests for rule evaluation
- CLI adapter tests for different AI tools

Run tests with:
```bash
python -m pytest tests/ -v
```

### Type Checking

The project uses MyPy for type checking. Currently, there are type errors that need to be addressed:
- Functions missing return type annotations
- Issues with Any types being returned from typed functions
- Duplicate function definitions

### Security Considerations

The project uses subprocess to interact with tmux and AI CLI tools. Security considerations include:
- Validating inputs before sending to subprocess
- Avoiding shell=True in subprocess calls
- Properly handling exceptions in subprocess calls

## Common Patterns and Conventions

### Rule Definition

Rules are typically defined as:
```python
Rule(
    check=lambda output: "some condition" in output,
    command="command to send when condition is met"
)
```

### Task Configuration

Task configurations are JSON files with:
- `name`: Task name
- `description`: Task description
- `rules`: List of rule definitions or references

### ANSI Parsing

The project includes ANSI escape code parsing in `forgeflow/core/ansi.py` for:
- Stripping ANSI codes from output
- Parsing ANSI segments for styling
- Handling color and formatting information

## Known Issues and Technical Debt

1. **Type Checking**: MyPy reports 130+ type errors that need to be addressed
2. **Security Warnings**: Bandit reports several low-severity security issues
3. **Code Complexity**: Some functions have high cyclomatic complexity (up to 30)
4. **Exception Handling**: Several try-except-pass patterns that should be reviewed
5. **Duplicate Code**: Some duplicate function definitions need to be resolved

These issues should be addressed gradually while maintaining functionality.

## Future Improvements

1. **Enhanced CLI Support**: Complete implementation for Claude Code adapter
2. **Improved Rule System**: More sophisticated rule matching and evaluation
3. **Better Error Handling**: More robust error recovery mechanisms
4. **Extended Task Types**: Additional built-in task types for common programming tasks
5. **Performance Optimization**: Optimizing the automation loop for faster response times