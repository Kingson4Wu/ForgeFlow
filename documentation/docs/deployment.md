---
sidebar_position: 5
title: ForgeFlow Task Types - Automation Workflows
description: Explore built-in task types in ForgeFlow for AI CLI automation. Task Planner, test fixing, coverage improvement, and custom automation workflows.
---

# Task Types

ForgeFlow includes several built-in task types that provide specialized automation for common programming activities. These tasks come with predefined configurations and rules to optimize the AI CLI interaction for specific use cases.

## Task Planner

The Task Planner task follows a TODO list to complete tasks in order. It's the most basic task type that provides a sequential approach to completing programming tasks.

### Configuration

The task planner can be configured with a JSON configuration file that defines the sequence of tasks to complete. By default, it looks for `task_planner_config.json`.

### Usage

```bash
forgeflow \\
  --session my_session \\
  --workdir \"/path/to/your/project\" \\
  --ai-cmd \"qwen --proxy http://localhost:7890 --yolo\" \\
  --task task_planner \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

### Features

- Sequential task execution based on a predefined list
- Configurable through JSON configuration files
- Can be customized with project-specific rules

## Fix Tests Task

The Fix Tests task automatically fixes failing test cases by monitoring test output and generating appropriate fix commands. This task is particularly useful for maintaining code quality and resolving test failures efficiently.

### Usage

```bash
forgeflow \\
  --session my_session \\
  --workdir \"/path/to/your/project\" \\
  --ai-cmd \"qwen --proxy http://localhost:7890 --yolo\" \\
  --task fix_tests \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

### Features

- Automatically detects failing tests in output
- Analyzes error messages to understand the cause of failures
- Generates targeted fixes for specific test issues
- Monitors the test execution process continuously

### Configuration

The fix tests task can be configured to work with different testing frameworks and has default configurations for common test runners.

## Improve Coverage Task

The Improve Coverage task works to increase test coverage to a target percentage by monitoring coverage reports and generating additional test cases.

### Usage

```bash
forgeflow \\
  --session my_session \\
  --workdir \"/path/to/your/project\" \\
  --ai-cmd \"qwen --proxy http://localhost:7890 --yolo\" \\
  --task improve_coverage \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

### Features

- Monitors code coverage reports
- Identifies under-tested code sections
- Generates test cases to improve overall coverage
- Works towards a configurable coverage target

### Configuration

This task can be configured with a target coverage percentage and other parameters to customize its behavior for different projects.

## Creating Custom Tasks

While the built-in tasks cover common use cases, you can also create custom tasks by defining new task classes in the `forgeflow/tasks/` directory or by using the project-specific rule system.

### Custom Task Structure

Custom tasks typically include:

1. A task class that inherits from the base task class
2. Task-specific rule configurations
3. Custom logic for monitoring and responding to specific conditions
4. Configuration file support for customization

## Using Task Configurations

Task configurations are stored in the `forgeflow/tasks/configs/` directory with the following structure:

- `task_planner_config.json` - Configuration for the task planner
- `fix_tests_config.json` - Configuration for the test fixing task
- `improve_coverage_config.json` - Configuration for the coverage improvement task

### Configuration Options

Each task configuration file can include:

- Task-specific parameters
- Rule configurations
- Timeout settings
- Output processing rules
- Project-specific settings

## Combining Tasks with Projects

Tasks can be combined with project-specific rules for maximum customization:

```bash
forgeflow \\
  --session my_session \\
  --workdir \"/path/to/your/project\" \\
  --ai-cmd \"qwen --proxy http://localhost:7890 --yolo\" \\
  --task fix_tests \\
  --project myproject \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

This combination allows you to use a specialized task type with project-specific rules and configurations.

## Task Monitoring

All tasks provide detailed monitoring capabilities:

- Real-time status updates
- Progress tracking
- Error detection and recovery
- Performance metrics
- Notification when tasks complete or stall

The task system in ForgeFlow provides a powerful way to automate complex programming activities with minimal manual intervention.