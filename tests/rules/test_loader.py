import os
import tempfile
from unittest.mock import patch

from forgeflow.core.rules.loader import load_custom_rules
from forgeflow.core.utils import (
    _find_rule_file,
    _load_module_from_file,
)


def test_find_rule_file() -> None:
    """Test _find_rule_file function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file1_path = os.path.join(temp_dir, "test_rules.py")
        file2_path = os.path.join(temp_dir, "test.py")

        with open(file1_path, "w") as f:
            f.write("# Test file 1")

        with open(file2_path, "w") as f:
            f.write("# Test file 2")

        result = _find_rule_file(["test_rules.py", "test.py"], [temp_dir])
        assert result == file1_path

        os.remove(file1_path)
        result = _find_rule_file(["test_rules.py", "test.py"], [temp_dir])
        assert result == file2_path

        os.remove(file2_path)
        result = _find_rule_file(["test_rules.py", "test.py"], [temp_dir])
        assert result is None


def test_load_module_from_file_not_found() -> None:
    """Test _load_module_from_file with non-existent file."""
    result = _load_module_from_file("/non/existent/file.py", "test_module")
    assert result is None


def test_load_module_from_file_invalid_syntax() -> None:
    """Test _load_module_from_file with invalid Python file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("invalid python syntax +++")
        temp_path = f.name

    try:
        result = _load_module_from_file(temp_path, "test_module")
        assert result is None
    finally:
        os.unlink(temp_path)


def mock_get_user_custom_rules_projects_dir() -> None:
    return None


@patch(
    "forgeflow.core.rules.loader._get_user_custom_rules_projects_dir",
    mock_get_user_custom_rules_projects_dir,
)
def test_load_custom_rules_not_found() -> None:
    """Test load_custom_rules when no rule file is found."""
    result = load_custom_rules("nonexistent_project")
    assert result is None


def test_get_rules_priority() -> None:
    """Test that CLI type rules take priority over project/task custom rules."""
    from forgeflow.core.rules import get_rules
    from forgeflow.core.rules.base import build_default_rules

    class MockConfig:
        def __init__(self, cli_type="gemini", project=None, task=None):
            self.cli_type = cli_type
            self.project = project
            self.task = task

    config1 = MockConfig(cli_type="gemini")
    rules1 = get_rules(config1)
    default_rules = build_default_rules("gemini")
    assert len(rules1) == len(default_rules)

    config2 = MockConfig(cli_type="gemini", project="test_project")
    rules2 = get_rules(config2)
    assert len(rules2) == len(default_rules)
