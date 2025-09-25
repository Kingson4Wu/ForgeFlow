import os
import tempfile
from unittest.mock import patch

from forgeflow.core.rule_loader import (
    _find_rule_file,
    _get_examples_dir,
    _get_user_custom_rules_dir,
    _load_module_from_file,
    load_custom_rules,
)


def test_find_rule_file() -> None:
    """Test _find_rule_file function."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        file1_path = os.path.join(temp_dir, "test_rules.py")
        file2_path = os.path.join(temp_dir, "test.py")

        with open(file1_path, "w") as f:
            f.write("# Test file 1")

        with open(file2_path, "w") as f:
            f.write("# Test file 2")

        # Test finding first file
        result = _find_rule_file(["test_rules.py", "test.py"], [temp_dir])
        assert result == file1_path

        # Test finding second file
        os.remove(file1_path)
        result = _find_rule_file(["test_rules.py", "test.py"], [temp_dir])
        assert result == file2_path

        # Test file not found
        os.remove(file2_path)
        result = _find_rule_file(["test_rules.py", "test.py"], [temp_dir])
        assert result is None


def test_get_examples_dir() -> None:
    """Test _get_examples_dir function."""
    # This test will pass if the function returns a string or None
    result = _get_examples_dir()
    assert result is None or isinstance(result, str)


def test_get_user_custom_rules_dir() -> None:
    """Test _get_user_custom_rules_dir function."""
    # This test will pass if the function returns a string or None
    result = _get_user_custom_rules_dir()
    assert result is None or isinstance(result, str)


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


# Mock functions for testing load_custom_rules
def mock_get_user_custom_rules_dir() -> None:
    return None


def mock_get_default_rules_dir() -> None:
    return None


def mock_get_examples_dir() -> None:
    return None


def mock_get_cli_types_rules_dir() -> str:
    # Return the actual path to the CLI types directory for testing
    import os

    return os.path.join(os.path.dirname(__file__), "..", "forgeflow", "core", "cli_types")


@patch("forgeflow.core.rule_loader._get_user_custom_rules_dir", mock_get_user_custom_rules_dir)
@patch("forgeflow.core.rule_loader._get_default_rules_dir", mock_get_default_rules_dir)
@patch("forgeflow.core.rule_loader._get_examples_dir", mock_get_examples_dir)
def test_load_custom_rules_not_found() -> None:
    """Test load_custom_rules when no rule file is found."""
    result = load_custom_rules("nonexistent_project", "/tmp")
    assert result is None


def test_get_rules_priority() -> None:
    """Test that CLI type rules take priority over project/task custom rules."""
    from forgeflow.core.rule_loader import get_rules
    from forgeflow.core.rules import build_default_rules

    # Create a mock config object
    class MockConfig:
        def __init__(self, cli_type="gemini", project=None, task=None, workdir="/tmp"):
            self.cli_type = cli_type
            self.project = project
            self.task = task
            self.workdir = workdir

    # Test 1: Only CLI type rules should be loaded
    config1 = MockConfig(cli_type="gemini")
    rules1 = get_rules(config1)
    default_rules = build_default_rules("gemini")

    # The rules should be the same as the default rules since no project or task is specified
    assert len(rules1) == len(default_rules)

    # Test 2: CLI type rules should be loaded first when project is specified
    config2 = MockConfig(cli_type="gemini", project="test_project")
    rules2 = get_rules(config2)

    # The rules should include CLI type rules (at the beginning)
    # Since no custom rules file exists for "test_project", it should fall back to CLI type rules only
    assert len(rules2) == len(default_rules)
