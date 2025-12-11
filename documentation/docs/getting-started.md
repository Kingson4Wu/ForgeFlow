---
sidebar_position: 2
title: Getting Started with ForgeFlow - AI CLI Automation
description: Learn how to install and configure ForgeFlow for AI CLI automation in tmux sessions. Step-by-step guide to automate Qwen, Gemini, Claude for programming tasks.
---

# Getting Started

This guide will walk you through the process of installing and setting up ForgeFlow for your project.

## Prerequisites

Before installing ForgeFlow, ensure you have the following prerequisites:

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)
- tmux (terminal multiplexer)
- An AI CLI tool (e.g., Qwen, Gemini, Claude)

## Installation

### Using pip

To install ForgeFlow directly from the repository:

```bash
pip install -e .
```

### Using Conda Environment

If you prefer to use a Conda environment:

```bash
conda create -n forgeflow python=3.13
conda activate forgeflow
pip install -e .
```

## Quick Start

Here's how to run ForgeFlow with a basic configuration:

```bash
forgeflow \\
  --session my_session \\
  --workdir "/path/to/your/project" \\
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

## Understanding the Basics

### Core Components

ForgeFlow consists of several core components that work together:

- **TmuxCtl**: Manages tmux sessions for interacting with AI CLI tools
- **Automation Engine**: Core loop that drives interaction with AI CLI tools
- **Rule System**: Configurable rules that determine appropriate responses
- **CLI Adapters**: Interface implementations for different AI CLI tools

### Basic Parameters

- `--session`: Name of the tmux session to create or reuse
- `--workdir`: Directory where the AI CLI will operate
- `--ai-cmd`: Command to start your AI CLI tool
- `--poll`: Polling interval in seconds to check the session status
- `--timeout`: Maximum time to wait before considering the task stalled
- `--log-file`: File to write logs to

### CLI Adapter Types

ForgeFlow supports different AI CLI tools through adapters:

- `gemini` (default): For Google's Gemini CLI
- `claude_code`: For Anthropic's Claude Code CLI
- Custom adapters can be created for other tools

## Monitor-Only Mode

ForgeFlow also supports a monitor-only mode that watches an existing tmux session and sends notifications when tasks stop processing:

```bash
forgeflow \\
  --session my_session \\
  --monitor-only \\
  --poll 10 \\
  --log-file forgeflow.log
```

## Next Steps

After completing this quick start guide, explore the following topics:

- [Configuration](./configuration.md)
- [Rule System](./custom-nodes.md)
- [Task Types](./advanced-patterns.md)