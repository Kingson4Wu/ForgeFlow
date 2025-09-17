import json
import os
import tempfile
from unittest.mock import patch

from forgeflow.core.rules import Rule
from forgeflow.core.task_rules import (
    build_fix_tests_rules,
    build_improve_coverage_rules,
    build_task_planner_rules,
    check_all_tasks_done,
    check_all_tests_passed,
    check_coverage_below_threshold,
    check_coverage_target_reached,
    check_task_completed,
    check_test_failures,
    get_task_rules_builder,
)


def test_check_test_failures():
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


def test_check_all_tests_passed():
    # Test cases where all tests passed
    assert check_all_tests_passed("All tests passed")
    assert check_all_tests_passed("Ran 5 tests, all passed")
    assert check_all_tests_passed("OK 20 tests")

    # Test cases where not all tests passed
    assert not check_all_tests_passed("1 test failed")
    assert not check_all_tests_passed("Running tests...")


def test_check_coverage_below_threshold():
    # Test cases with coverage below threshold
    assert check_coverage_below_threshold("coverage: 75%", 80)

    # Test cases with coverage meeting or exceeding threshold
    assert not check_coverage_below_threshold("coverage: 85%", 80)
    assert not check_coverage_below_threshold("coverage: 80%", 80)


def test_check_coverage_target_reached():
    # Test cases with coverage meeting or exceeding target
    assert check_coverage_target_reached("coverage: 85%", 80)
    assert check_coverage_target_reached("coverage: 80%", 80)
    assert check_coverage_target_reached("Coverage target reached", 90)

    # Test cases with coverage below target
    assert not check_coverage_target_reached("coverage: 75%", 80)


def test_check_task_completed():
    # Test with default indicators
    config = {}
    assert check_task_completed("Task completed", config)

    # Test with custom indicators
    config = {"task_completion_indicators": ["work done", "finished"]}
    assert check_task_completed("work done", config)
    assert not check_task_completed("task completed", config)  # Not in custom indicators


def test_check_all_tasks_done():
    # Test that all tasks done is detected
    assert check_all_tasks_done("All tasks have been completed.")

    # Test that it's not triggered by partial matches
    assert not check_all_tasks_done("All tasks")
    assert not check_all_tasks_done("completed")


def test_build_fix_tests_rules():
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


def test_build_improve_coverage_rules():
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


def test_build_task_planner_rules():
    # Test that task_planner rules are created correctly
    config = {}
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


def test_get_task_rules_builder():
    # Test that built-in task rules builders are returned
    assert get_task_rules_builder("fix_tests") is not None
    assert get_task_rules_builder("improve_coverage") is not None
    assert get_task_rules_builder("task_planner") is not None

    # Test that None is returned for non-existent task types
    assert get_task_rules_builder("non_existent_task") is None


def test_task_rules_with_config():
    # Create a temporary config file
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "improve_coverage_config.json")
        config_data = {"target_coverage": 95}

        with open(config_path, "w") as f:
            json.dump(config_data, f)

        # Test loading config
        with patch("forgeflow.core.task_rules.load_task_config") as mock_load:
            mock_load.return_value = config_data
            rules = build_improve_coverage_rules(config_data)

            # Check that the target coverage is used in the rules
            # We can't easily test the lambda functions directly, but we can verify the structure
            assert len(rules) == 3
