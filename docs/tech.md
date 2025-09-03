# Technology Stack

## Core Technologies

1. **Python**: The main programming language for the project, requiring Python 3.9 or higher.

2. **tmux**: Terminal multiplexer used to create and manage terminal sessions. The project controls the AI CLI through
   tmux.

3. **Regular Expressions (re module)**: Used to detect input prompts and output states of the AI CLI.

4. **Data Classes (dataclasses)**: Used to define data structures for configuration and rules.

5. **subprocess module**: Used to execute system commands and interact with tmux.

## Development Tools

1. **pytest**: Testing framework for writing and running unit tests.

2. **ruff**: Python code checking tool for code quality and style checks.

3. **black**: Python code formatting tool to ensure code style consistency.

4. **setuptools**: Python package building and distribution tool.

## Project Architecture Patterns

1. **Command-Line Interface (CLI)**: Provides a command-line interface through the `forgeflow.cli` module.

2. **Rule Engine**: Configurable rule system that allows users to customize AI interaction rules.

3. **Automation Control**: Precise control of tmux sessions implemented through the `tmux_ctl` module.

4. **State Detection**: Uses regular expressions to detect the output status and input prompts of the AI CLI.

5. **Exception Recovery**: Implements timeout recovery mechanisms to automatically recover when the AI CLI is
   unresponsive.

## Core Functional Modules

1. **automation.py**: Core automation logic that coordinates the entire process.
2. **tmux_ctl.py**: tmux session control module.
3. **rules.py**: Rule system and state detection.
4. **cli.py**: Command-line interface definition.

## Purpose

This project is primarily used to automatically drive AI CLI tools to complete programming tasks within tmux sessions.
It features a configurable rule system and powerful error recovery capabilities.