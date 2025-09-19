import json
import os
import tempfile
from typing import Any
from unittest.mock import patch

from forgeflow.core.rules import Rule
from forgeflow.core.task_rules import (
    _find_build_function,
    _find_rule_file,
    _get_examples_dir,
    _load_module_from_file,
    get_task_rules_builder,
    load_task_config,
)

# Import the functions from the new separate files
from forgeflow.tasks.fix_tests_task import (
    check_all_tests_passed,
    check_test_failures,
)
from forgeflow.tasks.improve_coverage_task import (
    check_coverage_below_threshold,
    check_coverage_target_reached,
)
from forgeflow.tasks.task_planner_task import (
    check_all_tasks_done,
    check_task_completed,
)


# We need to define the builder functions for testing
def build_fix_tests_rules(config: dict[str, Any]) -> list[Rule]:
    from forgeflow.tasks.fix_tests_task import build_rules

    return build_rules(config)


def build_improve_coverage_rules(config: dict[str, Any]) -> list[Rule]:
    from forgeflow.tasks.improve_coverage_task import build_rules

    return build_rules(config)


def build_task_planner_rules(config: dict[str, Any]) -> list[Rule]:
    from forgeflow.tasks.task_planner_task import build_rules

    return build_rules(config)


def test_check_test_failures() -> None:
    # Test cases with test failures
    assert check_test_failures("1 failed test:")
    assert check_test_failures("TEST FAILED")
    assert check_test_failures("AssertionError in test_function")
    assert check_test_failures("pytest failed with exit code 1")

    # Test cases without test failures
    assert not check_test_failures("All tests passed")
    assert not check_test_failures("Running tests...")

    # Test that task completion message doesn't trigger test failure detection
    assert not check_test_failures("Task completed")


def test_check_all_tests_passed() -> None:
    # Test cases where all tests passed
    assert check_all_tests_passed("All tests passed")
    assert check_all_tests_passed("Ran 5 tests, all passed")
    assert check_all_tests_passed("OK 20 tests")

    # Test cases where not all tests passed
    assert not check_all_tests_passed("1 test failed")
    assert not check_all_tests_passed("Running tests...")


def test_check_coverage_below_threshold() -> None:
    # Test cases with coverage below threshold
    assert check_coverage_below_threshold("coverage: 75%", 80)

    # Test cases with coverage meeting or exceeding threshold
    assert not check_coverage_below_threshold("coverage: 85%", 80)
    assert not check_coverage_below_threshold("coverage: 80%", 80)


def test_check_coverage_target_reached() -> None:
    # Test cases with coverage meeting or exceeding target
    assert check_coverage_target_reached("coverage: 85%", 80)
    assert check_coverage_target_reached("coverage: 80%", 80)
    assert check_coverage_target_reached("Coverage target reached", 90)

    # Test cases with coverage below target
    assert not check_coverage_target_reached("coverage: 75%", 80)


def test_check_task_completed() -> None:
    # Test with default indicators
    config: dict[str, Any] = {}
    assert check_task_completed("Task completed", config)

    # Test with custom indicators
    config = {"task_completion_indicators": ["work done", "finished"]}
    assert check_task_completed("work done", config)
    assert not check_task_completed("task completed", config)  # Not in custom indicators

    # Test that instruction text doesn't trigger false positive
    assert not check_task_completed(
        'If you\'ve completed the current task, respond with "Task completed"', config
    )
    assert not check_task_completed("Please say 'task completed' when done", config)


def test_check_all_tasks_done() -> None:
    # Test that all tasks done is detected
    assert check_all_tasks_done("All tasks have been completed.")

    # Test that it's not triggered by partial matches
    assert not check_all_tasks_done("All tasks")
    assert not check_all_tasks_done("completed")

    # Test that instruction text doesn't trigger false positive
    assert not check_all_tasks_done('return the message: "All tasks have been completed."')
    assert not check_all_tasks_done('respond with "All tasks have been completed."')


def test_build_fix_tests_rules() -> None:
    # Test that fix_tests rules are created correctly
    rules = build_fix_tests_rules({})

    # Should have 3 rules
    assert len(rules) == 3

    # Check rule types
    assert isinstance(rules[0], Rule)
    assert isinstance(rules[1], Rule)
    assert isinstance(rules[2], Rule)

    # Check that first rule stops when tests pass
    assert rules[0].check("All tests passed")
    assert rules[0].command is None


def test_build_improve_coverage_rules() -> None:
    # Test that improve_coverage rules are created correctly
    config = {"target_coverage": 90}
    rules = build_improve_coverage_rules(config)

    # Should have 3 rules
    assert len(rules) == 3

    # Check rule types
    assert isinstance(rules[0], Rule)
    assert isinstance(rules[1], Rule)
    assert isinstance(rules[2], Rule)

    # Check that first rule stops when target coverage is reached
    assert rules[0].check("coverage: 90%")
    assert rules[0].command is None


def test_build_task_planner_rules() -> None:
    # Test that task_planner rules are created correctly
    config: dict[str, Any] = {}
    rules = build_task_planner_rules(config)

    # Should have 3 rules
    assert len(rules) == 3

    # Check rule types
    assert isinstance(rules[0], Rule)
    assert isinstance(rules[1], Rule)
    assert isinstance(rules[2], Rule)

    # Check that first rule stops when all tasks are done
    assert rules[0].check("All tasks have been completed.")
    assert rules[0].command is None

    # Check that second rule handles task completion
    assert rules[1].check("Task completed")


def test_get_task_rules_builder() -> None:
    # Test that built-in task rules builders are returned
    assert get_task_rules_builder("fix_tests") is not None
    assert get_task_rules_builder("improve_coverage") is not None
    assert get_task_rules_builder("task_planner") is not None

    # Test that None is returned for non-existent task types
    assert get_task_rules_builder("non_existent_task") is None


def test_task_rules_with_config() -> None:
    # Create a temporary config file
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "improve_coverage_config.json")
        config_data: dict[str, Any] = {"target_coverage": 95}

        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # Test loading config
        with patch("forgeflow.core.task_rules.load_task_config") as mock_load:
            mock_load.return_value = config_data
            rules = build_improve_coverage_rules(config_data)

            # Check that the target coverage is used in the rules
            # We can't easily test the lambda functions directly, but we can verify the structure
            assert len(rules) == 3


def test_find_rule_file() -> None:
    """Test the _find_rule_file helper function."""
    # Test with existing file
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_file.py")
        with open(test_file, "w") as f:
            f.write("# test file")

        result = _find_rule_file(["test_file.py"], [tmpdir])
        assert result == test_file

    # Test with non-existing file
    result = _find_rule_file(["non_existent.py"], ["/tmp"])
    assert result is None


def test_get_examples_dir() -> None:
    """Test the _get_examples_dir helper function."""
    # Test that it returns a path (we can't easily test the exact path)
    result = _get_examples_dir()
    # Should be either a string or None
    assert isinstance(result, (str, type(None)))


def test_load_module_from_file() -> None:
    """Test the _load_module_from_file helper function."""
    # Test with non-existent file
    result = _load_module_from_file("/non/existent/file.py", "test_module")
    assert result is None


def test_find_build_function() -> None:
    """Test the _find_build_function helper function."""

    # Create a mock module with a function
    class MockModule:
        def __init__(self) -> None:
            self.test_func = lambda: "test"

    mock_module = MockModule()

    # Test finding existing function
    result = _find_build_function(mock_module, ["test_func"])
    assert result is not None
    assert result() == "test"  # type: ignore

    # Test not finding function
    result = _find_build_function(mock_module, ["non_existent_func"])
    assert result is None


def test_load_task_config() -> None:
    """Test the load_task_config function."""
    # Test with non-existent config file
    config = load_task_config("test_task", "/non/existent/dir")
    assert config == {}

    # Test with existing config file
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "test_task_config.json")
        config_data = {"test_key": "test_value"}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Patch os.path.exists to return True for our config file
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: path == config_file or os.path.exists(path)

            config = load_task_config("test_task", tmpdir)
            assert config == config_data
