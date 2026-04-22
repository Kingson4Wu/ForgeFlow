from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable
from typing import Any

from ._shared_utils import (
    _find_build_function,
    _find_rule_file,
    _get_config_directory,
    _get_examples_tasks_dir,
    _get_user_custom_rules_tasks_dir,
    _load_module_from_file,
)
from .rules import Rule

logger = logging.getLogger("forgeflow")


def load_task_config(task_name: str, workdir: str) -> dict[str, Any]:
    """Load task configuration from a JSON file.

    The function will look for a file named `{task_name}_config.json` in this order:
    1. Current working directory
    2. user_custom_rules/tasks directory
    3. forgeflow/default_rules directory (built-in configurations)
    4. examples/tasks directory (for backward compatibility)

    Args:
        task_name: Name of the task
        workdir: Working directory where the project is running

    Returns:
        Dictionary containing task configuration
    """
    candidates = [os.path.join(workdir, f"{task_name}_config.json")]

    for dir_type in ("user_custom_rules", "default_rules", "examples"):
        dir_path = _get_config_directory(dir_type)
        if dir_path:
            candidates.append(os.path.join(dir_path, f"{task_name}_config.json"))

    for path in candidates:
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            continue
        except Exception:
            return {}

    return {}


def load_custom_task_rules(
    task_name: str, workdir: str
) -> Callable[[dict[str, Any]], list[Rule]] | None:
    """Load custom task rules from a Python file.

    The function will look for a file in this order:
    1. `{task_name}_task.py` in the current working directory
    2. `{task_name}.py` in the current working directory
    3. `user_custom_rules/tasks/{task_name}_task.py` in the user custom rules directory
    4. `user_custom_rules/tasks/{task_name}.py` in the user custom rules directory
    5. `forgeflow/default_rules/{task_name}_config.json` (built-in configurations)
    6. `examples/tasks/{task_name}_task.py` in the examples directory (for backward compatibility)
    7. `examples/tasks/{task_name}.py` in the examples directory (for backward compatibility)

    Args:
        task_name: Name of the task (used to find the rule file)
        workdir: Working directory where the project is running

    Returns:
        Function that builds rules if found, None otherwise
    """
    possible_files = [f"{task_name}_task.py", f"{task_name}.py"]
    possible_dirs = [workdir]

    if ucr_tasks := _get_user_custom_rules_tasks_dir():
        possible_dirs.append(ucr_tasks)
    if examples_tasks := _get_examples_tasks_dir():
        possible_dirs.append(examples_tasks)

    rule_file_path = _find_rule_file(possible_files, possible_dirs)
    if not rule_file_path:
        logger.warning(f"Task rule file not found for task: {task_name}")
        return None

    logger.info(f"Loading custom task rules from: {rule_file_path}")

    module = _load_module_from_file(rule_file_path, f"{task_name}_task")
    if module is None:
        return None

    possible_names = [
        "build_rules",
        f"build_{task_name}_rules",
        f"build_{task_name}",
        "build_custom_rules",
        f"{task_name}_rules",
        "rules",
    ]

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
        from ._shared_utils import _get_pkg_dir

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
