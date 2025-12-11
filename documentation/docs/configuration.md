---
sidebar_position: 3
title: ForgeFlow Configuration Guide - AI CLI Automation
description: Complete guide to configuring ForgeFlow for AI CLI tools like Qwen, Gemini, Claude. Learn about parameters, rules, and tmux session setup.
---

# Configuration

Learn how to configure ForgeFlow for different use cases and environments.

## Basic Configuration

ForgeFlow is configured primarily through command-line arguments. Here are the main options:

### Essential Parameters

```bash
forgeflow \\
  --session my_session \\
  --workdir "/path/to/your/project" \\
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

- `--session`: Name of the tmux session to create or reuse
- `--workdir`: Directory where the AI CLI will operate
- `--ai-cmd`: Command to start your AI CLI tool
- `--poll`: Polling interval in seconds to check the session status
- `--timeout`: Maximum time to wait before considering the task stalled (in seconds)
- `--log-file`: File to write logs to

### CLI Adapter Configuration

```bash
forgeflow \\
  --session my_session \\
  --workdir "/path/to/your/project" \\
  --ai-cmd "claude" \\
  --cli-type claude_code \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

- `--cli-type`: Specify the CLI adapter type (default: gemini)

### Project-Specific Rules

```bash
forgeflow \\
  --session my_session \\
  --workdir "/path/to/your/project" \\
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \\
  --project myproject \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

- `--project`: Name of the project to load custom rules for

### Task-Specific Configuration

```bash
forgeflow \\
  --session my_session \\
  --workdir "/path/to/your/project" \\
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \\
  --task fix_tests \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

- `--task`: Name of a predefined task (e.g., fix_tests, improve_coverage)

## Monitor-Only Mode

Run ForgeFlow in monitor-only mode to watch an existing session:

```bash
forgeflow \\
  --session my_session \\
  --monitor-only \\
  --poll 10 \\
  --log-file forgeflow.log
```

This mode monitors task processing status and sends notifications when tasks stop processing, without sending any commands to the AI CLI.

## Advanced Settings

### Performance Tuning

Adjust polling and timeout values based on your needs:

```bash
forgeflow \\
  --session my_session \\
  --workdir "/path/to/your/project" \\
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \\
  --poll 5 \\        # Check more frequently (every 5 seconds)
  --timeout 3600 \\  # Wait longer before considering task stalled
  --log-file forgeflow.log
```

### Logging Configuration

ForgeFlow provides comprehensive logging:

- Dual channel logging: file + console
- Timestamps for all log entries
- Different log levels for various types of information

## Default Values

ForgeFlow comes with sensible defaults:

- Session name: "forgeflow" (if not specified)
- Polling interval: 10 seconds
- Timeout: 2000 seconds
- CLI type: "gemini"
- Log file: No log file (console only)

## Configuration Sources

ForgeFlow supports configuration from multiple sources:

1. Command-line arguments (highest precedence)
2. Environment variables
3. Default values (lowest precedence)

## Next Steps

Explore advanced topics like [Rule System](./custom-nodes.md) and [Task Types](./advanced-patterns.md).