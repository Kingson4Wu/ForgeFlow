from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable
from typing import Any

from forgeflow.rules.base import Rule, build_default_rules
from forgeflow.utils import (
    _find_build_function,
    _find_rule_file,
    _get_pkg_task_configs_dir,
    _get_user_custom_rules_projects_dir,
    _get_user_custom_rules_tasks_dir,
    _load_module_from_file,
    build_function_names,
)

logger = logging.getLogger("forgeflow")


def load_custom_rules(project_name: str) -> list[Rule] | None:
    """
    Load custom rules from a Python file based on the project name.

    Looks in:
    1. ~/.forgeflow/user_custom_rules/projects/{project_name}_rules.py
    2. ~/.forgeflow/user_custom_rules/projects/{project_name}.py

    Args:
        project_name: Name of the project (used to find the rule file)

    Returns:
        List of Rule objects if found, None otherwise
    """
    possible_files = [f"{project_name}_rules.py", f"{project_name}.py"]
    possible_dirs = []

    if ucr_projects := _get_user_custom_rules_projects_dir():
        possible_dirs.append(ucr_projects)

    rule_file_path = _find_rule_file(possible_files, possible_dirs)
    if not rule_file_path:
        logger.warning(f"Rule file not found for project: {project_name}")
        return None

    logger.info(f"Loading custom rules from: {rule_file_path}")

    module = _load_module_from_file(rule_file_path, f"{project_name}_rules")
    if module is None:
        return None

    possible_names = build_function_names(project_name)

    build_func = _find_build_function(module, possible_names)
    if build_func is None:
        logger.error(f"No build function found in {rule_file_path}")
        return None

    try:
        rules = build_func()  # type: ignore
        logger.info(f"Successfully loaded {len(rules)} custom rules")
        return rules  # type: ignore
    except (TypeError, ValueError, RuntimeError) as e:
        logger.error(f"Error calling build function in {rule_file_path}: {e}")
        return None


def load_task_config(task_name: str) -> dict[str, Any]:
    """Load task configuration from a JSON file.

    The function will look for a file named `{task_name}_config.json` in this order:
    1. ~/.forgeflow/user_custom_rules/tasks/ (user custom)
    2. src/forgeflow/tasks/configs/ (built-in)

    Args:
        task_name: Name of the task

    Returns:
        Dictionary containing task configuration
    """
    candidates = []

    if ucr := _get_user_custom_rules_tasks_dir():
        candidates.append(os.path.join(ucr, f"{task_name}_config.json"))
    if pkg := _get_pkg_task_configs_dir():
        candidates.append(os.path.join(pkg, f"{task_name}_config.json"))

    for path in candidates:
        try:
            with open(path) as f:
                return json.load(f)  # type: ignore[no-any-return]
        except FileNotFoundError:
            continue
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in task config: {path}")
            return {}

    return {}


def load_custom_task_rules(task_name: str) -> Callable[[dict[str, Any]], list[Rule]] | None:
    """Load custom task rules from a Python file.

    Looks in:
    1. ~/.forgeflow/user_custom_rules/tasks/{task_name}_task.py
    2. ~/.forgeflow/user_custom_rules/tasks/{task_name}.py

    Args:
        task_name: Name of the task (used to find the rule file)

    Returns:
        Function that builds rules if found, None otherwise
    """
    possible_files = [f"{task_name}_task.py", f"{task_name}.py"]
    possible_dirs = []

    if ucr_tasks := _get_user_custom_rules_tasks_dir():
        possible_dirs.append(ucr_tasks)

    rule_file_path = _find_rule_file(possible_files, possible_dirs)
    if not rule_file_path:
        logger.warning(f"Task rule file not found for task: {task_name}")
        return None

    logger.info(f"Loading custom task rules from: {rule_file_path}")

    module = _load_module_from_file(rule_file_path, f"{task_name}_task")
    if module is None:
        return None

    possible_names = build_function_names(task_name)

    build_func = _find_build_function(module, possible_names)
    if build_func is None:
        logger.error(f"No build function found in {rule_file_path}")
        return None

    return build_func


def get_task_rules_builder(task_name: str) -> Callable[[dict[str, Any]], list[Rule]] | None:
    """Get task rules builder function for a specific task type."""
    if task_name not in ("fix_tests", "improve_coverage", "task_planner"):
        return None

    try:
        from forgeflow.utils import _get_pkg_dir

        pkg_dir = _get_pkg_dir()
        if pkg_dir is None:
            return None
        task_file_path = str(pkg_dir / "tasks" / f"{task_name}_task.py")
    except (ImportError, OSError):
        return None

    module = _load_module_from_file(task_file_path, f"{task_name}_task")
    if module is not None and hasattr(module, "build_rules"):
        return module.build_rules  # type: ignore[no-any-return]
    return None


def get_task_rules(task_name: str) -> list[Rule] | None:
    """
    Get predefined rules for a specific task type.

    This function loads CLI type rules as the base, then adds task-specific rules.

    Args:
        task_name: Name of the task type (e.g., 'fix_tests', 'improve_coverage')

    Returns:
        List of Rule objects if found, None otherwise
    """
    # First, try to load custom task rules
    custom_rules_builder = load_custom_task_rules(task_name)
    if custom_rules_builder:
        try:
            config = load_task_config(task_name)

            rules = custom_rules_builder(config)  # type: ignore
            logger.info(f"Successfully loaded {len(rules)} custom task rules for {task_name}")
            return rules  # type: ignore
        except (TypeError, ValueError, RuntimeError) as e:
            logger.error(f"Error building custom task rules for {task_name}: {e}")

    # If no custom rules, try built-in rules
    rules_builder = get_task_rules_builder(task_name)
    if rules_builder:
        try:
            config = load_task_config(task_name)

            rules = rules_builder(config)  # type: ignore
            logger.info(f"Successfully loaded {len(rules)} built-in task rules for {task_name}")
            return rules  # type: ignore
        except (TypeError, ValueError, RuntimeError) as e:
            logger.error(f"Error building built-in task rules for {task_name}: {e}")
            return None

    logger.warning(f"Task rules not found for task: {task_name}")
    return None


def get_rules(config: Any) -> list[Rule]:
    """
    Get rules based on the configuration.

    The function loads rules in this priority order:
    1. CLI type rules from @forgeflow/core/cli_types/ (highest priority)
    2. Task-specific rules (if task specified)
    3. Project-specific custom rules (if project specified)
    4. Default rules (fallback)

    Args:
        config: Configuration object containing project name, task type and other settings

    Returns:
        List of Rule objects
    """
    # Start with CLI type rules as the base (highest priority)
    cli_type_rules = build_default_rules(config.cli_type)
    logger.info(f"Loaded CLI type rules for: {config.cli_type}")

    # If task specified, try to load task rules and combine with CLI type rules
    if config.task:
        task_rules = get_task_rules(config.task)
        if task_rules:
            logger.info(f"Using task rules for: {config.task}")
            return cli_type_rules + task_rules
        else:
            logger.warning(f"Failed to load task rules for '{config.task}'")

    # If project specified, try to load custom rules and combine with CLI type rules
    if config.project:
        custom_rules = load_custom_rules(config.project)
        if custom_rules:
            combined_rules = cli_type_rules + custom_rules
            logger.info(f"Using combined CLI type and custom rules for project: {config.project}")
            return combined_rules
        else:
            logger.warning(
                f"Failed to load custom rules for project '{config.project}', using CLI type rules only"
            )

    # If no project or task specified, just use CLI type rules
    logger.info("Using CLI type rules only")
    return cli_type_rules
