import os
import sys
from pathlib import Path

from forgeflow.core.rule_loader import _load_module_from_file

# Add the project root to the path so we can import forgeflow
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_gemini_rules_file():
    """Test that the gemini rules file can be loaded and has a build_rules function."""
    gemini_rules_path = os.path.join(
        project_root, "forgeflow", "core", "cli_types", "gemini_rules.py"
    )
    assert os.path.exists(gemini_rules_path)

    module = _load_module_from_file(gemini_rules_path, "gemini_rules")
    assert module is not None
    assert hasattr(module, "build_rules")

    # Test that build_rules returns a list
    rules = module.build_rules()
    assert isinstance(rules, list)


def test_codex_rules_file():
    """Test that the codex rules file can be loaded and has a build_rules function."""
    codex_rules_path = os.path.join(
        project_root, "forgeflow", "core", "cli_types", "codex_rules.py"
    )
    assert os.path.exists(codex_rules_path)

    module = _load_module_from_file(codex_rules_path, "codex_rules")
    assert module is not None
    assert hasattr(module, "build_rules")

    # Test that build_rules returns a list
    rules = module.build_rules()
    assert isinstance(rules, list)


def test_claude_code_rules_file():
    """Test that the claude code rules file can be loaded and has a build_rules function."""
    claude_code_rules_path = os.path.join(
        project_root, "forgeflow", "core", "cli_types", "claude_code_rules.py"
    )
    assert os.path.exists(claude_code_rules_path)

    module = _load_module_from_file(claude_code_rules_path, "claude_code_rules")
    assert module is not None
    assert hasattr(module, "build_rules")

    # Test that build_rules returns a list
    rules = module.build_rules()
    assert isinstance(rules, list)
