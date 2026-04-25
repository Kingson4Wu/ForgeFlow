from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

logger = logging.getLogger("forgeflow")


@dataclass(frozen=True)
class Command:
    """A command to send to the AI CLI. text=None means stop automation."""

    text: str | None


@dataclass(frozen=True)
class Rule:
    check: Callable[[str], bool]
    command: Command
    description: str = ""


class CommandPostProcessor:
    """Base class for command post-processing."""

    def post_process_command(self, output: str, initial_command: str | None) -> str | None:
        return None


class RuleEngine:
    """Evaluates rules against AI CLI output to determine the next command."""

    def __init__(
        self,
        rules: list[Rule],
        post_processors: dict[str, CommandPostProcessor] | None = None,
    ) -> None:
        self._rules = rules
        self._post_processors = post_processors or {}

    def resolve(self, output: str, cli_type: str) -> str | None:
        initial = self._match(output)
        return self._post_process(output, cli_type, initial)

    def _match(self, output: str) -> str | None:
        for rule in self._rules:
            try:
                if rule.check(output):
                    if rule.description:
                        logger.info(f"Rule matched: {rule.description}")
                    return rule.command.text
            except Exception:
                logger.warning(
                    f"Rule '{rule.description or '<unnamed>'}' check failed", exc_info=True
                )
                continue
        return "continue"

    def _post_process(self, output: str, cli_type: str, initial: str | None) -> str | None:
        processor = self._post_processors.get(cli_type.strip().lower())
        if processor is None:
            return initial
        result = processor.post_process_command(output, initial)
        if result is not None and result != initial:
            logger.info(f"Post-processed command '{initial}' to '{result}'")
            return result
        return initial


def build_default_rules(cli_type: str = "gemini") -> list[Rule]:
    key = cli_type.strip().lower()
    if key == "gemini":
        return _build_gemini_rules()
    elif key == "codex":
        return _build_codex_rules()
    elif key == "claude_code":
        return _build_claude_code_rules()
    return []


def _build_gemini_rules() -> list[Rule]:
    from forgeflow.rules.builtin.gemini import build_rules

    return build_rules()


def _build_codex_rules() -> list[Rule]:
    from forgeflow.rules.builtin.codex import build_rules

    return build_rules()


def _build_claude_code_rules() -> list[Rule]:
    from forgeflow.rules.builtin.claude_code import build_rules

    return build_rules()
