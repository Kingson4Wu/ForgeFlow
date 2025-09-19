import os
import tempfile
from unittest.mock import patch

from forgeflow.core.task_rules import (
    _find_build_function,
    _find_rule_file,
    _get_examples_dir,
    _get_user_custom_rules_dir,
    _load_module_from_file,
    load_custom_task_rules,
    load_task_config,
)


def test_find_rule_file():
    """Test _find_rule_file function."""
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        file1_path = os.path.join(temp_dir, "test_task.py")
        file2_path = os.path.join(temp_dir, "test.py")

        with open(file1_path, "w") as f:
            f.write("# Test file 1")

        with open(file2_path, "w") as f:
            f.write("# Test file 2")

        # Test finding first file
        result = _find_rule_file(["test_task.py", "test.py"], [temp_dir])
        assert result == file1_path

        # Test finding second file
        os.remove(file1_path)
        result = _find_rule_file(["test_task.py", "test.py"], [temp_dir])
        assert result == file2_path

        # Test file not found
        os.remove(file2_path)
        result = _find_rule_file(["test_task.py", "test.py"], [temp_dir])
        assert result is None


def test_get_examples_dir():
    """Test _get_examples_dir function."""
    # This test will pass if the function returns a string or None
    result = _get_examples_dir()
    assert result is None or isinstance(result, str)


def test_get_user_custom_rules_dir():
    """Test _get_user_custom_rules_dir function."""
    # This test will pass if the function returns a string or None
    result = _get_user_custom_rules_dir()
    assert result is None or isinstance(result, str)


def test_load_module_from_file_not_found():
    """Test _load_module_from_file with non-existent file."""
    result = _load_module_from_file("/non/existent/file.py", "test_module")
    assert result is None


def test_load_module_from_file_invalid_syntax():
    """Test _load_module_from_file with invalid Python file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("invalid python syntax +++")
        temp_path = f.name

    try:
        result = _load_module_from_file(temp_path, "test_module")
        assert result is None
    finally:
        os.unlink(temp_path)


def test_find_build_function():
    """Test _find_build_function function."""

    class MockModule:
        def build_rules(self):
            return []

        def build_test_task_rules(self):
            return []

        def build_test_task(self):
            return []

    mock_module = MockModule()

    # Test finding build_rules function
    result = _find_build_function(mock_module, ["build_rules"])
    assert result == mock_module.build_rules

    # Test finding specific function
    result = _find_build_function(mock_module, ["build_test_task_rules", "build_rules"])
    assert result == mock_module.build_test_task_rules

    # Test function not found
    result = _find_build_function(mock_module, ["nonexistent_function"])
    assert result is None


def test_load_task_config_not_found():
    """Test load_task_config when no config file is found."""
    result = load_task_config("nonexistent_task", "/tmp")
    assert result == {}


# Mock functions for testing load_custom_task_rules
def mock_get_user_custom_rules_dir():
    return None


def mock_get_default_rules_dir():
    return None


def mock_get_examples_dir():
    return None


@patch("forgeflow.core.task_rules._get_user_custom_rules_dir", mock_get_user_custom_rules_dir)
@patch("forgeflow.core.task_rules._get_default_rules_dir", mock_get_default_rules_dir)
@patch("forgeflow.core.task_rules._get_examples_dir", mock_get_examples_dir)
def test_load_custom_task_rules_not_found():
    """Test load_custom_task_rules when no rule file is found."""
    result = load_custom_task_rules("nonexistent_task", "/tmp")
    assert result is None
