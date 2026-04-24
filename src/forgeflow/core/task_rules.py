from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable
from typing import Any

from .rules.base import Rule
from .utils import (
    _find_build_function,
    _find_rule_file,
    _get_pkg_task_configs_dir,
    _get_user_custom_rules_tasks_dir,
    _load_module_from_file,
    build_function_names,
)

logger = logging.getLogger("forgeflow")


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
                return json.load(f)
        except FileNotFoundError:
            continue
        except Exception:
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
        from .utils import _get_pkg_dir

        pkg_dir = _get_pkg_dir()
        if pkg_dir is None:
            return None
        task_file_path = str(pkg_dir / "tasks" / f"{task_name}_task.py")
    except Exception:
        return None

    module = _load_module_from_file(task_file_path, f"{task_name}_task")
    if module is not None and hasattr(module, "build_rules"):
        return module.build_rules
    return None
