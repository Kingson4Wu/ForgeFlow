import pytest

from forgeflow.adapters.base import CLIAdapter
from forgeflow.adapters.registry import get_adapter, list_adapters, register


class DummyAdapter(CLIAdapter):
    def is_input_prompt(self, output: str) -> bool:
        return False

    def is_input_prompt_with_text(self, output: str) -> bool:
        return False

    def is_task_processing(self, history: list[str]) -> bool:
        return False

    def is_ai_cli_exist(self, output: str) -> bool:
        return False


class TestRegistry:
    def test_register_and_get(self):
        register("dummy", DummyAdapter)
        adapter = get_adapter("dummy")
        assert isinstance(adapter, DummyAdapter)

    def test_get_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown CLI type"):
            get_adapter("nonexistent")

    def test_list_adapters_includes_registered(self):
        current = list_adapters()
        assert "dummy" in current

    def test_case_insensitive_lookup(self):
        adapter = get_adapter("DUMMY")
        assert isinstance(adapter, DummyAdapter)

    def test_built_in_adapters_registered(self):
        # Importing the modules should trigger registration
        from forgeflow.adapters import (  # noqa: F401
            claude_code,
            codex,
            gemini,
        )

        names = list_adapters()
        assert "gemini" in names
        assert "claude_code" in names
        assert "codex" in names

    def test_get_built_in_adapters(self):
        from forgeflow.adapters.claude_code import ClaudeCodeCLIAdapter
        from forgeflow.adapters.codex import CodexCLIAdapter
        from forgeflow.adapters.gemini import GeminiCLIAdapter

        assert isinstance(get_adapter("gemini"), GeminiCLIAdapter)
        assert isinstance(get_adapter("claude_code"), ClaudeCodeCLIAdapter)
        assert isinstance(get_adapter("codex"), CodexCLIAdapter)
