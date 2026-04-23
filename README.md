# ForgeFlow

[![Build Status](https://github.com/Kingson4Wu/ForgeFlow/workflows/CI/badge.svg)](https://github.com/Kingson4Wu/ForgeFlow/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Automatically drives AI CLI tools to continuously complete programming tasks within a `tmux` session.

## Features

- **Robust Session Management**: Automatically creates/reuses `tmux` sessions
- **Multi-CLI Support**: Gemini, Claude Code, Codex — through adapter pattern
- **Configurable Rule System**: Rules evaluated in order with priority matching; custom rules supported
- **Timeout Recovery**: Input prompt timeout → `ESC` → backspace clear → `continue`
- **Logging**: Dual channel file + console with timestamps
- **Task Monitoring**: Desktop notifications when task processing stalls (macOS supported)
- **Monitor-Only Mode**: Watch existing sessions without sending commands

## Prerequisites

- Python >= 3.13
- [tmux](https://github.com/tmux/tmux) installed and on PATH
- An AI CLI tool: [claude](https://docs.anthropic.com/en/docs/claude-code/overview), [gemini-cli](https://ai.google.dev/gemini-api/docs/cli), or similar

## Installation

```bash
git clone https://github.com/Kingson4Wu/ForgeFlow
cd ForgeFlow
uv sync
```

## Running

Execute with `uv run` from the project directory (no activation needed):

```bash
uv run forgeflow --session my_session --workdir "/path/to/project" --ai-cmd "claude --dangerously-skip-permissions" --cli-type claude_code
```

Or activate the environment first:

```bash
source .venv/bin/activate
forgeflow --session my_session --workdir "/path/to/project" --ai-cmd "claude --dangerously-skip-permissions" --cli-type claude_code
```

### CLI Types

| CLI Type | Example `--ai-cmd` |
|---------|-------------------|
| `claude_code` (default) | `claude --dangerously-skip-permissions` |
| `gemini` | `gemini --yolo` |
| `codex` | `codex --yolo` |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--session` | (required) | tmux session name |
| `--workdir` | (required in normal mode) | Working directory |
| `--ai-cmd` | (required in normal mode) | AI CLI command to start |
| `--cli-type` | `claude_code` | AI CLI adapter type |
| `--poll` | `10` | Poll interval (seconds) |
| `--timeout` | `1000` | Input prompt timeout (seconds) |
| `--log-file` | `forgeflow.log` | Log file path |
| `--log-level` | `INFO` | Logging level |
| `--project` | — | Project name for custom rules |
| `--task` | — | Task type (`fix_tests`, `task_planner`, `improve_coverage`) |
| `--monitor-only` | — | Monitor mode (no commands sent) |

### Custom Rules

Place `{project_name}_rules.py` or `{project_name}.py` in your project directory or `user_custom_rules/`:

```bash
uv run forgeflow --project myproject ...
```

### Task Modes

```bash
uv run forgeflow --task fix_tests ...
uv run forgeflow --task task_planner ...
uv run forgeflow --task improve_coverage ...
```

### Monitor-Only Mode

Watch an existing session without sending commands:

```bash
uv run forgeflow --session my_session --monitor-only --cli-type claude_code --poll 10
```

## Exiting

- **Normal exit**: Automatically exits when final verification is detected
- **Force stop**: `Ctrl-C` (exits gracefully, tmux session preserved)

## Project Structure

```
ForgeFlow/
├── src/forgeflow/       # Main Python package
│   ├── cli.py           # CLI entry point
│   └── core/
│       ├── automation.py     # Core automation loop
│       ├── tmux_ctl.py       # tmux session management
│       ├── rules.py          # Rule system
│       ├── rule_loader.py    # Custom rule loading
│       ├── task_rules.py     # Task-specific rules
│       ├── defaults.py       # Default configuration values
│       ├── notifier.py       # Desktop notifications
│       ├── cli_adapters/     # CLI adapter implementations
│       │   ├── base.py       # CLIAdapter base class
│       │   ├── claude_code.py
│       │   ├── gemini.py
│       │   └── codex.py
│       └── cli_types/        # CLI-specific rules
│           ├── claude_code_rules.py
│           ├── gemini_rules.py
│           └── codex_rules.py
├── tests/               # Test suite
├── documentation/       # Docusaurus docs site
├── docs/                # Additional documentation
└── scripts/            # Utility scripts
```

## Documentation

- **[Docusaurus Site](documentation/)** — Run with `cd documentation && npm run start`
- **[docs/](docs/)** — Quick start, task mode config, tech stack

## License

[MIT](./LICENSE)
