# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Dev Commands

```bash
uv sync                           # Install dependencies
uv run forgeflow --session ...   # Run
pytest tests/ -v                 # Run all tests
pytest tests/rules/test_loader.py # Run single test file
ruff check src/                  # Lint
ruff format src/                 # Format
```

Python >= 3.13 required. Uses `uv` for dependency management.

## Architecture

### Core Flow

```
forgeflow.cli → core/automation/loop.run_automation()
                           ↓
                    tmux/ctl.TmuxCtl (send/receive)
                           ↓
              cli_adapter.is_input_prompt()   ← detects prompt
              cli_adapter.is_task_processing()  ← detects idle/processing
                           ↓
              rules/loader.get_rules() → [Rule, ...]
                           ↓
              next_command() → send command to tmux
```

### Rule System

`get_rules(config)` returns `[cli_type_rules] + [task_or_custom_rules]`:

- `cli_type_rules` — from `core/cli_types/{gemini,codex,claude_code}_rules.py`
- `task_rules` — from `~/.forgeflow/user_custom_rules/tasks/{task}_task.py` or built-in `tasks/{task}_task.py`
- `custom_rules` — from `~/.forgeflow/user_custom_rules/projects/{project}_rules.py`

User config lives in `~/.forgeflow/user_custom_rules/`, never in the user's project directory.

### CLI Adapter Pattern

Each AI CLI has its own adapter in `core/cli_adapters/`:

| Method | Purpose |
|--------|---------|
| `is_input_prompt(output)` | Detect prompt waiting for input |
| `is_input_prompt_with_text(output)` | Detect prompt with pre-filled text |
| `is_task_processing(history)` | Detect task running vs idle (frame comparison) |
| `is_ai_cli_exist(output)` | Detect CLI startup completion |

### Monitor Mode

`run_monitor_mode()` watches tmux output, tracks `was_processing → not processing` transitions, sends desktop notification when task stops. Uses `NO_PROCESSING_THRESHOLD=3` consecutive idle checks before notification.

## Source Layout

```
src/forgeflow/
├── cli.py                      # CLI entry, argument parsing
└── core/
    ├── automation/
    │   ├── loop.py             # run_automation(), run_monitor_mode()
    │   └── defaults.py         # All magic numbers/constants
    ├── cli_adapters/           # One per AI CLI type
    │   ├── base.py             # CLIAdapter abstract base
    │   ├── factory.py          # get_cli_adapter()
    │   ├── gemini.py
    │   ├── claude_code.py
    │   └── codex.py
    ├── cli_types/              # CLI-specific rule sets
    │   ├── gemini_rules.py
    │   ├── claude_code_rules.py
    │   └── codex_rules.py
    ├── rules/
    │   ├── base.py             # Rule dataclass, build_default_rules(), next_command()
    │   └── loader.py          # get_rules(), get_task_rules()
    ├── tmux/
    │   ├── ctl.py             # TmuxCtl — send keys, capture pane
    │   └── notifier.py       # Desktop notification
    ├── task_rules.py          # load_task_config(), get_task_rules_builder()
    ├── utils.py              # Path helpers
    └── ansi.py               # ANSI escape code parsing
tasks/                         # Built-in task implementations
    ├── task_planner_task.py
    ├── fix_tests_task.py
    ├── improve_coverage_task.py
    └── configs/              # Task JSON configs
```

## Test Layout

Tests mirror `src/` structure:

```
tests/
├── automation/    # test_loop.py, test_monitor_mode.py
├── cli_adapters/  # test_*.py
├── rules/         # test_*.py
└── tmux/          # test_ctl.py
```
