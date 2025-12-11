---
sidebar_position: 4
title: ForgeFlow Rule System - Custom AI CLI Rules
description: Learn how to create custom rules for ForgeFlow automation. Configure behavior for Qwen, Gemini, Claude AI CLIs based on output conditions.
---

# Rule System

ForgeFlow's rule system allows you to customize the behavior of the automation engine by defining specific conditions and responses. Rules determine what commands to send based on the output from AI CLI tools.

## Understanding Rules

Rules in ForgeFlow are simple conditional statements that follow the pattern: "If condition is met, then execute command". The system evaluates rules in order, and the first matching rule is executed.

Each rule consists of:
- **Check condition**: A function that takes the session output as input and returns a boolean
- **Command**: The text to send to the AI CLI when the condition is met

## Default Rules

ForgeFlow comes with a comprehensive set of default rules for common AI CLI tools:

- **Input Detection**: Detect when the AI CLI is waiting for input
- **Task Processing Detection**: Detect when the AI is actively processing a task
- **Response Handling**: Handle various response patterns from the AI
- **Timeout Recovery**: Implement recovery strategies when the AI stops responding

## Project-Specific Rules

To create project-specific rules, create a file named `{project_name}_rules.py` or `{project_name}.py` in your project directory. For example:

```
myproject_rules.py
```

The system will automatically load these rules when you run ForgeFlow with the `--project myproject` flag.

### Rule File Resolution Order

ForgeFlow searches for rule files in the following order:

1. `{project_name}_rules.py` in the current working directory
2. `{project_name}.py` in the current working directory
3. `{project_name}_rules.py` in the `user_custom_rules/` directory
4. `{project_name}.py` in the `user_custom_rules/` directory
5. Built-in default rules in the codebase

## Rule Structure

A basic rule definition looks like this:

```python
from forgeflow.core.rules import Rule

Rule(
    check=lambda output: "some condition" in output,
    command="command to send when condition is met"
)
```

## Creating Custom Rules

To create custom rules, define them in your project-specific rules file:

```python
# In your myproject_rules.py file
from forgeflow.core.rules import Rule

# Rule to detect when AI asks for more information
Rule(
    check=lambda output: "How can I help you" in output or "What would you like me to do" in output,
    command="Please implement the next task in the TODO list."
)

# Rule to handle error responses
Rule(
    check=lambda output: "error" in output.lower() or "failed" in output.lower(),
    command="Please review the error and suggest a fix."
)

# Rule to continue when AI finishes a task
Rule(
    check=lambda output: "completed" in output.lower() or "done" in output.lower(),
    command="Please move on to the next task in the list."
)
```

## Rule Evaluation Order

Rules are evaluated in the order they are defined. The system uses priority matching, meaning the first rule whose condition is met will execute its command. This allows you to define more specific rules first and more general rules later.

## Advanced Rule Concepts

### Input Prompt Detection

Different AI CLI tools have different input prompt patterns. The rule system uses regular expressions to detect when the AI is ready for input:

```python
Rule(
    check=lambda output: "gemini" in output.split('\n')[-1] if output.split('\n') else False,  # Simplified example
    command="Next task from the list: "
)
```

### Recovery Strategies

Rules can implement timeout recovery strategies:

```python
Rule(
    check=lambda output: "no response" in output.lower(),  # This would be triggered by a timeout mechanism
    command="ESC + backspace to clear and continue"
)
```

## Best Practices

- Place more specific rules before general ones
- Test rules thoroughly to avoid unexpected behavior
- Use descriptive names and comments for complex conditions
- Consider edge cases in AI responses
- Leverage regex for pattern matching when appropriate

## Built-in Rule Categories

ForgeFlow includes several categories of built-in rules:

- **Prompt Detection Rules**: Identify when the AI CLI is ready for input
- **Task Status Rules**: Monitor task processing status
- **Error Handling Rules**: Respond to error conditions
- **Timeout Recovery Rules**: Handle stalled conversations
- **Task Completion Rules**: Detect when tasks are completed

The rule system provides flexibility to customize ForgeFlow's behavior for your specific project needs and AI CLI tools.