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
forgeflow.cli → automation/loop.run_automation()
                           ↓
                    tmux/ctl.TmuxCtl (send/receive)
                           ↓
              cli_adapter.is_input_prompt()   ← detects prompt
              cli_adapter.is_task_processing()  ← detects idle/processing
                           ↓
              rules/loader.get_rules() → [Rule, ...]
                           ↓
              RuleEngine.resolve() → send command to tmux
```

### Rule System

`get_rules(config)` returns `[cli_type_rules] + [task_or_custom_rules]`:

- `cli_type_rules` — from `rules/builtin/{gemini,codex,claude_code}_rules.py`
- `task_rules` — from `~/.forgeflow/user_custom_rules/tasks/{task}_task.py` or built-in `tasks/{task}_task.py`
- `custom_rules` — from `~/.forgeflow/user_custom_rules/projects/{project}_rules.py`

User config lives in `~/.forgeflow/user_custom_rules/`, never in the user's project directory.

### CLI Adapter Pattern

Each AI CLI has its own adapter in `adapters/`:

| Method | Purpose |
|--------|---------|
| `is_input_prompt(output)` | Detect prompt waiting for input |
| `is_input_prompt_with_text(output)` | Detect prompt with pre-filled text |
| `is_task_processing(history)` | Detect task running vs idle (frame comparison) |
| `is_ai_cli_exist(output)` | Detect CLI startup completion |

Adapters self-register via `adapters/registry.py`:
```python
from forgeflow.adapters.registry import register
register("gemini", GeminiCLIAdapter)
```

### Monitor Mode

`run_monitor_mode()` watches tmux output, tracks `was_processing → not processing` transitions, sends desktop notification when task stops. Uses `NO_PROCESSING_THRESHOLD=3` consecutive idle checks before notification.

## Source Layout

```
src/forgeflow/
├── cli.py                      # CLI entry, argument parsing
├── config.py                   # Unified Config (Pydantic) + constants
├── state.py                    # UnchangedTracker — idle detection
├── ansi.py                     # ANSI escape code parsing
├── notifier.py                 # Desktop notification
├── utils.py                    # Path/module loading helpers
├── automation/                 # Automation core
│   ├── loop.py                 # run_automation(), RuleEngine integration
│   ├── monitor.py              # run_monitor_mode()
│   └── recovery.py             # Timeout recovery (ESC/backspace/continue)
├── adapters/                   # One per AI CLI type
│   ├── base.py                 # CLIAdapter abstract base
│   ├── registry.py             # AdapterRegistry — register/get_adapter()
│   ├── gemini.py
│   ├── claude_code.py
│   └── codex.py
├── rules/                      # Rule system
│   ├── base.py                 # Rule, Command, RuleEngine, build_default_rules()
│   ├── loader.py               # get_rules(), load_custom_rules(), task loading
│   └── builtin/                # CLI-specific rule sets
│       ├── gemini_rules.py
│       ├── claude_code_rules.py
│       └── codex_rules.py
├── tmux/                       # tmux session management
│   ├── ctl.py                  # TmuxCtl — send keys, capture pane
│   └── window.py               # WindowManager — Codex window sizing
└── tasks/                      # Built-in task implementations
    ├── task_planner_task.py
    ├── fix_tests_task.py
    ├── improve_coverage_task.py
    └── configs/                # Task JSON configs
```

## Test Layout

Tests mirror `src/` structure:

```
tests/
├── automation/    # test_loop.py, test_monitor_mode.py, test_recovery.py
├── adapters/      # test_*.py for registry and adapters
├── rules/         # test_*.py for base, loader, builtin rules
├── tmux/          # test_ctl.py, test_window.py
├── test_config.py
├── test_state.py
├── test_notifier.py
└── ...
```
