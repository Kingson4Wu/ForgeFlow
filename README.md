# ForgeFlow

[![Build Status](https://github.com/Kingson4Wu/ForgeFlow/workflows/CI/badge.svg)](https://github.com/Kingson4Wu/ForgeFlow/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Automatically drives AI CLI to continuously complete programming tasks within a `tmux` session.

## Features

- **Robust Session Management**: Automatically creates/reuses `tmux` sessions, separating text from enter when pasting commands.
- **Configurable Rule System**: Rules are evaluated in order, with priority matching taking effect, and custom rules are supported.
- **Multi-CLI Support**: Supports different AI CLI tools through an adapter pattern (currently supports Gemini as the default, with a placeholder for Claude Code).
- **Reliable Input Detection**: Regular expressions detect "input prompts" and "existing text in input box" specific to each CLI tool.
- **Timeout Recovery Strategy**: Long periods without input prompt → send `ESC` → backspace clear → `continue`.
- **Logging and Debugging**: Dual channel file + console logging with timestamps.
- **Task Monitoring**: Monitors task processing status and sends desktop notifications when tasks stop processing (macOS notifications supported).

## Quick Start

### Clone and Set Up the Project

To clone and set up the project, follow these steps:

1. Clone the repository locally:
   ```bash
   git clone https://github.com/Kingson4Wu/ForgeFlow
   cd ForgeFlow
   ```

### Quick Start for Mac Users

For Mac users, see our [Quick Start Guide for Mac Users](docs/quick_start_mac.md) which provides detailed step-by-step instructions for setting up and using ForgeFlow on macOS.

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
   conda create -n forgeflow python=3.13
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

### Monitor-Only Mode

ForgeFlow also supports a monitor-only mode that watches an existing tmux session and sends desktop notifications when tasks stop processing, without sending any commands to the AI CLI. This is useful for monitoring tasks while you work on other things.

To run in monitor-only mode:

```bash
forgeflow \\
  --session qwen_session \\
  --monitor-only \\
  --poll 10 \\
  --log-file forgeflow.log
```

Note: In monitor-only mode, the `--ai-cmd` and `--workdir` parameters are not required since ForgeFlow will not be starting or controlling the AI CLI, only monitoring its status.

By default, ForgeFlow uses the Gemini CLI adapter to monitor task processing status. If you're monitoring a session that's using a different AI CLI tool, you should specify the appropriate `--cli-type` parameter:

```bash
forgeflow \\
  --session claude_session \\
  --monitor-only \\
  --cli-type claude_code \\
  --poll 10 \\
  --log-file forgeflow.log
```

### Running the Script Directly (without installation)

If you want to run the script directly without installing the package, you can use the following command:

```bash
python -m forgeflow.cli \\
  --session qwen_session \\
  --workdir "/absolute/path/to/your/project" \\
  --ai-cmd "qwen --proxy http://localhost:7890 --yolo" \\
  --poll 10 \\
  --timeout 2000 \\
  --log-file forgeflow.log
```

Note: When using this method, make sure you're running the command in the project's root directory.

### Running in Monitor-Only Mode (Direct Script)

To run the monitor-only mode directly without installation:

```bash
python -m forgeflow.cli 
  --session qwen_session 
  --monitor-only 
  --poll 10 
  --log-file forgeflow.log
```

Note: When using monitor-only mode, if you're monitoring a session that's using a different AI CLI tool than the default Gemini, you should specify the appropriate `--cli-type` parameter:

```bash
python -m forgeflow.cli 
  --session claude_session 
  --monitor-only 
  --cli-type claude_code 
  --poll 10 
  --log-file forgeflow.log
```

### Exiting

* Normal exit: Automatically exits when final verification is detected.
* Force stop: `Ctrl-C` (the script will exit gracefully without closing your `tmux` session).

## License

[MIT](./LICENSE)