---
sidebar_position: 2
title: CLI Adapters
description: CLI adapter implementations for Gemini, Claude Code, Codex in ForgeFlow.
---

# CLI Adapters

CLI adapters implement the adapter pattern to normalize ForgeFlow's interaction with different AI CLI tools.

## Interface

```python
class CLIAdapter(ABC):
    def is_input_prompt(self, output: str) -> bool:
        """Detect if AI CLI is waiting for input."""

    def is_input_prompt_with_text(self, output: str) -> bool:
        """Detect if input prompt has text already entered."""

    def is_task_processing(self, history: list[str]) -> bool:
        """Detect if task is being processed (uses output history for change detection)."""

    def is_ai_cli_exist(self, output: str) -> bool:
        """Detect if AI CLI is running."""

    def wants_ansi(self) -> bool:
        """Whether to capture ANSI escape sequences (default False)."""
```

## Built-in Adapters

| CLI Type | File | Notes |
|----------|------|-------|
| `claude_code` | `core/cli_adapters/claude_code.py` | Default |
| `gemini` | `core/cli_adapters/gemini.py` | Full implementation |
| `codex` | `core/cli_adapters/codex.py` | Full implementation |

## Rule Files

Each CLI type has corresponding rules in `core/cli_types/`:

- `core/cli_types/gemini_rules.py`
- `core/cli_types/claude_code_rules.py`
- `core/cli_types/codex_rules.py`

Rules are loaded via `forgeflow.rules.loader.get_rules()`, which combines CLI-type rules from `rules/builtin/` with task rules and custom user rules.
