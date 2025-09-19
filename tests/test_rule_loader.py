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


def test_find_rule_file():
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


# Mock functions for testing load_custom_rules
def mock_get_user_custom_rules_dir():
    return None


def mock_get_default_rules_dir():
    return None


def mock_get_examples_dir():
    return None


@patch("forgeflow.core.rule_loader._get_user_custom_rules_dir", mock_get_user_custom_rules_dir)
@patch("forgeflow.core.rule_loader._get_default_rules_dir", mock_get_default_rules_dir)
@patch("forgeflow.core.rule_loader._get_examples_dir", mock_get_examples_dir)
def test_load_custom_rules_not_found():
    """Test load_custom_rules when no rule file is found."""
    result = load_custom_rules("nonexistent_project", "/tmp")
    assert result is None
