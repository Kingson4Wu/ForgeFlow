---
slug: forgeflow-engineering-grade-automation
title: 'FORGEFLOW: Engineering-Grade Automation for AI CLIs Inside Tmux'
authors: [kingsonwu]
tags: [ai, automation, tmux, cli, forgeflow, development]
description: Comprehensive guide to ForgeFlow - an engineering-grade automation tool that drives AI CLI tools (Qwen, Gemini, Claude) inside tmux sessions with configurable rules.
---

ForgeFlow automates interactive AI CLIs (e.g., Qwen, Gemini, Claude) inside a tmux session using a clean "adapter + rules" architecture. It detects prompts and processing states, sends the right commands, and keeps going until tasks converge — with logs, extensibility, and sensible recovery behavior.

<!-- truncate -->

## This guide covers:

- How to install and use ForgeFlow (focus)
- Architecture overview, key interfaces, and ANSI support
- Extending with custom rules and adapters
- A simple flow diagram in Markdown

## Who It's For

- Developers who live in the terminal and use AI CLIs
- Teams that want a repeatable driver for long-running, iterative tasks
- Anyone who needs logging and simple extensibility without reinventing the loop

## Requirements

- macOS/Linux
- Python 3.9+
- tmux installed and on PATH

## Install And Run

- Dev install (pinned tooling):
  - `pip install -e .[dev] -c constraints-dev.txt`
- Runtime install:
  - `pip install -e .`
- Makefile helpers:
  - `make dev-install` — install dev deps with constraints
  - `make lint` / `make fmt` / `make test`
  - `make setup-hooks` — optional Git hooks
- Typical run:

```bash
forgeflow \
--session qwen_session \
--workdir "/abs/path/to/your/project" \
--ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
--cli-type qwen \
--poll 10 \
--timeout 2000 \
--log-level INFO \
--log-file forgeflow.log
```

- Switch adapters:
  - `--cli-type qwen` or `--cli-type gemini` (claude_code is a placeholder)
- Use project-specific rules:
  - Add `{project}_rules.py` or `{project}.py` in your project root or in examples/
  - Run with `--project myproject`

```bash
forgeflow \
--session qwen_session \
--workdir "/abs/path/to/your/project" \
--ai-cmd "qwen --proxy http://localhost:7890 --yolo" \
--project myproject \
--cli-type qwen
```

- Logging:
  - `--log-file forgeflow.log` writes file logs
  - `--no-console` disables console logging
  - `--log-level` supports DEBUG/INFO/WARNING/ERROR

## Python API

```python
from forgeflow.core.automation import Config, run_automation

cfg = Config(
    session="qwen_session",
    workdir="/abs/path/to/your/project",
    ai_cmd="qwen --proxy http://localhost:7890 --yolo",
    cli_type="qwen",
    poll_interval=10,
    input_prompt_timeout=2000,
    log_file="forgeflow.log",
    log_to_console=True,
    project="myproject",   # optional
    log_level="INFO",
)
run_automation(cfg)
```

## Rules: Project-Level Customization

- File naming:
  - `{project}_rules.py` or `{project}.py`
- Function name (recommended):
  - `build_rules()` -> `list[Rule]`
- Minimal example:

```python
# examples/myproject_rules.py

from forgeflow.core.rules import Rule

def build_rules() -> list[Rule]:
    def done(output: str) -> bool:
        return "All tasks have been completed." in output

    return [
        Rule(check=done, command=None),  # stop
        Rule(check=lambda out: "API Error" in out, command="continue"),
        Rule(check=lambda out: True, command="continue"),
    ]
```

- Rule behavior:
  - Rules are evaluated in order, the first matching rule returns its command.
  - If command is None, automation stops.

## Architecture Overview

- Core loop (`forgeflow/core/automation.py`)
  - Creates/attaches tmux session
  - Determines adapter by `--cli-type`
  - Captures tmux output, checks "prompt vs. processing", evaluates rules
  - Timeout recovery: ESC → progressive Backspace until prompt → send continue
  - Logging level configurable; file and console outputs supported
- tmux I/O (`forgeflow/core/tmux_ctl.py`)
  - Encapsulates tmux operations: session creation, send keys, capture pane
  - `capture_output(include_ansi=False)` supports capturing raw ANSI when needed
- Adapters (`forgeflow/core/cli_adapters/*`)
  - Interface `CLIAdapter`:
    - `is_input_prompt(output)` -> `bool`
    - `is_input_prompt_with_text(output)` -> `bool`
    - `is_task_processing(output)` -> `bool`
    - `is_ai_cli_exist(output)` -> `bool`
    - `wants_ansi()` -> `bool` — ask automation to capture pane with ANSI codes
  - Implementations: `qwen.py`, `gemini.py` (claude_code placeholder present)
  - Adapter resolution via `get_cli_adapter(cli_type)`
- Rules (`forgeflow/core/rules.py`)
  - `Rule(check: Callable[[str], bool], command: str | None)`
  - Default rules and `next_command(output, rules)`
- Rule loader (`forgeflow/core/rule_loader.py`)
  - Dynamically loads `{project}_rules.py` or `{project}.py` from workdir or examples/

## ANSI Utilities For Smarter Detection

Some CLIs render distinct prompt colors or attributes. You can opt-in to capture ANSI and parse it in your adapter:

- Adapter opt-in:

```python
def wants_ansi(self) -> bool:
    return True
```

- Utilities (`forgeflow/core/ansi.py`):
  - `strip_ansi(text)` -> `str` — removes all ANSI escape sequences
  - `parse_ansi_segments(text)` -> `list[Segment]`
    - Splits text into styled segments (tracks SGR attributes)
    - Supports bold, dim, italic, underline, blink, inverse, strike
    - Supports FG/BG basic (30–37/90–97/40–47/100–107), 256-color, truecolor
  - `split_segments_lines(segments)` -> `list[list[Segment]]`
    - Split by newline while preserving styles
- Example usage in an adapter:

```python
from forgeflow.core.ansi import parse_ansi_segments

class MyAdapter(CLIAdapter):
    def wants_ansi(self) -> bool:
        return True

    def is_input_prompt(self, output: str) -> bool:
        # Example heuristic: find a red prompt marker at end of screen
        segments = parse_ansi_segments(output)
        text = ''.join(seg.text for seg in segments)
        return text.rstrip().endswith('>')  # combine with color checks if needed
```

This keeps default behavior unchanged while enabling color-aware rules when helpful.

## Simple Flow Diagram

```mermaid
flowchart TD
    A[Start forgeflow] --> B[Create/attach tmux session]
    B --> C[Ensure AI CLI running]
    C --> D{Capture output<br/>(ANSI optional)}
    D --> |prompt & idle| E[Evaluate rules -> command]
    E --> F[Send text + Enter]
    F --> G[Sleep 2s]
    G --> D
    D --> |prompt has text| H[Send Enter]
    H --> G
    D --> |processing| I[Wait poll interval]
    I --> D
    D --> |timeout| J[ESC + progressive backspace]
    J --> K[Send "continue"]
    K --> D
    E --> |None| L[Stop]
```

## Troubleshooting

- "tmux is required but not found"
  - Install tmux and ensure `tmux -V` succeeds
- CLI not detected as running
  - Check `--ai-cmd` and allow a few seconds post-launch
- No project rules
  - Defaults are used; add custom rules for better convergence

## Repository And License

- Repo: https://github.com/kingson4wu/ForgeFlow
- License: MIT