"""Shared utilities for task rule modules."""

from __future__ import annotations

from collections.abc import Callable

from forgeflow.rules.base import Command, Rule


def instruction_phrases(indicator: str) -> list[str]:
    """Return the standard instruction phrases for a given indicator."""
    return [
        f'respond with "{indicator}"',
        f"respond with '{indicator}'",
    ]


def is_instruction_text(output_lower: str, phrases: list[str]) -> bool:
    """Check if the output contains instruction text that should be ignored."""
    return any(phrase.lower() in output_lower for phrase in phrases)


def build_standard_rules(
    stop_check: Callable[[str], bool],
    condition_check: Callable[[str], bool],
    default_prompt: str,
    condition_prompt: str,
    stop_desc: str,
    condition_desc: str,
    default_desc: str,
) -> list[Rule]:
    """Build the standard three-rule template used by all task modules."""
    return [
        Rule(check=stop_check, command=Command(None), description=stop_desc),
        Rule(
            check=condition_check,
            command=Command(condition_prompt),
            description=condition_desc,
        ),
        Rule(
            check=lambda out: True,
            command=Command(default_prompt),
            description=default_desc,
        ),
    ]
