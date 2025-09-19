import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from .rules import Rule

logger = logging.getLogger("forgeflow")


# ---------- Task Configuration ----------
def load_task_config(task_name: str, workdir: str) -> dict[str, Any]:
    """Load task configuration from a JSON file.

    The function will look for a file named `{task_name}_config.json` in this order:
    1. Current working directory
    2. user_custom_rules directory
    3. default_rules/tasks directory
    4. default_rules directory (for backward compatibility)
    5. forgeflow/examples directory (for backward compatibility)

    Args:
        task_name: Name of the task
        workdir: Working directory where the project is running

    Returns:
        Dictionary containing task configuration
    """
    config_file = os.path.join(workdir, f"{task_name}_config.json")

    # If not found in workdir, try user custom rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            user_custom_rules_dir = (repo_root / "user_custom_rules").resolve()
            config_file = os.path.join(user_custom_rules_dir, f"{task_name}_config.json")
        except Exception:
            pass

    # If not found in user custom rules directory, try tasks rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            tasks_rules_dir = (repo_root / "default_rules" / "tasks").resolve()
            config_file = os.path.join(tasks_rules_dir, f"{task_name}_config.json")
        except Exception:
            pass

    # If not found in tasks rules directory, try default rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            default_rules_dir = (repo_root / "default_rules").resolve()
            config_file = os.path.join(default_rules_dir, f"{task_name}_config.json")
        except Exception:
            pass

    # If not found in default rules directory, try examples directory (for backward compatibility)
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            examples_dir = (repo_root / "examples").resolve()
            config_file = os.path.join(examples_dir, f"{task_name}_config.json")
        except Exception:
            pass

    if not os.path.exists(config_file):
        return {}

    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception:
        # If there's an error reading the config file, return empty dict
        return {}


# ---------- Dynamic Task Rule Loading ----------
def _find_rule_file(file_names: list[str], directories: list[str]) -> Optional[str]:
    """Find a rule file in the given directories.

    Args:
        file_names: List of possible file names to look for
        directories: List of directories to search in

    Returns:
        Path to the found file, or None if not found
    """
    for directory in directories:
        for filename in file_names:
            path = os.path.abspath(os.path.join(directory, filename))
            if os.path.isfile(path):
                return path
    return None


def _get_examples_dir() -> Optional[str]:
    """Get the examples directory path robustly.

    Returns:
        Path to examples directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent  # root that contains 'forgeflow' dir
        examples_dir = (repo_root / "examples").resolve()
        return str(examples_dir)
    except Exception:
        # Best effort; if not available (e.g., installed package without examples), skip
        return None


def _get_default_rules_dir() -> Optional[str]:
    """Get the default rules directory path robustly.

    Returns:
        Path to default rules directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent  # root that contains 'forgeflow' dir
        default_rules_dir = (repo_root / "default_rules").resolve()
        return str(default_rules_dir)
    except Exception:
        # Best effort; if not available, skip
        return None


def _get_tasks_rules_dir() -> Optional[str]:
    """Get the tasks rules directory path robustly.

    Returns:
        Path to tasks rules directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent  # root that contains 'forgeflow' dir
        tasks_rules_dir = (repo_root / "default_rules" / "tasks").resolve()
        return str(tasks_rules_dir)
    except Exception:
        # Best effort; if not available, skip
        return None


def _get_user_custom_rules_dir() -> Optional[str]:
    """Get the user custom rules directory path robustly.

    Returns:
        Path to user custom rules directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent  # root that contains 'forgeflow' dir
        user_custom_rules_dir = (repo_root / "user_custom_rules").resolve()
        return str(user_custom_rules_dir)
    except Exception:
        # Best effort; if not available, skip
        return None


def _load_module_from_file(file_path: str, module_name: str) -> Optional[object]:
    """Load a Python module from a file path.

    Args:
        file_path: Path to the Python file
        module_name: Name to give the module

    Returns:
        Loaded module, or None if failed
    """
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to load spec for {file_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error loading module from {file_path}: {e}")
        return None


def _find_build_function(module: object, possible_names: list[str]) -> Optional[Callable]:
    """Find a build function in a module.

    Args:
        module: Module to search in
        possible_names: List of possible function names to look for

    Returns:
        Found function, or None if not found
    """
    for func_name in possible_names:
        if hasattr(module, func_name):
            return getattr(module, func_name)
    return None


def load_custom_task_rules(
    task_name: str, workdir: str
) -> Optional[Callable[[dict[str, Any]], list[Rule]]]:
    """Load custom task rules from a Python file.

    The function will look for a file in this order:
    1. `{task_name}_task.py` in the current working directory
    2. `{task_name}.py` in the current working directory
    3. `{task_name}_task.py` in the user_custom_rules directory
    4. `{task_name}.py` in the user_custom_rules directory
    5. `{task_name}_task.py` in the default_rules/tasks directory (for built-in task rules)
    6. `{task_name}.py` in the default_rules/tasks directory (for built-in task rules)
    7. `{task_name}_task.py` in the default_rules directory (for backward compatibility)
    8. `{task_name}.py` in the default_rules directory (for backward compatibility)
    9. `{task_name}_task.py` in the forgeflow/examples directory (for backward compatibility)
    10. `{task_name}.py` in the forgeflow/examples directory (for backward compatibility)

    Args:
        task_name: Name of the task (used to find the rule file)
        workdir: Working directory where the project is running

    Returns:
        Function that builds rules if found, None otherwise
    """
    # Possible file names to look for
    possible_files = [f"{task_name}_task.py", f"{task_name}.py"]

    # Possible directories to look in
    possible_dirs = [workdir]

    # Add user custom rules directory if available
    user_custom_rules_dir = _get_user_custom_rules_dir()
    if user_custom_rules_dir:
        possible_dirs.append(user_custom_rules_dir)

    # Add tasks rules directory if available
    tasks_rules_dir = _get_tasks_rules_dir()
    if tasks_rules_dir:
        possible_dirs.append(tasks_rules_dir)

    # Add default rules directory if available
    default_rules_dir = _get_default_rules_dir()
    if default_rules_dir:
        possible_dirs.append(default_rules_dir)

    # Add repo examples directory if available (for backward compatibility)
    examples_dir = _get_examples_dir()
    if examples_dir:
        possible_dirs.append(examples_dir)

    # Try to find the rule file
    rule_file_path = _find_rule_file(possible_files, possible_dirs)

    # Check if the file exists
    if not rule_file_path:
        logger.warning(f"Task rule file not found for task: {task_name}")
        return None

    logger.info(f"Loading custom task rules from: {rule_file_path}")

    # Load the module dynamically
    module = _load_module_from_file(rule_file_path, f"{task_name}_task")
    if module is None:
        return None

    # Look for a function that builds rules
    # Try function names in order of preference
    # Prioritize build_rules as the standard function name
    possible_names = [
        "build_rules",  # Standard function name for all tasks
        f"build_{task_name}_rules",  # e.g., build_my_task_rules
        f"build_{task_name}",  # e.g., build_my_task
        "build_custom_rules",
        f"{task_name}_rules",  # e.g., my_task_rules
        "rules",
    ]

    build_func = _find_build_function(module, possible_names)
    if build_func is None:
        logger.error(f"No build function found in {rule_file_path}")
        return None

    return build_func


def get_task_rules_builder(task_name: str) -> Optional[Callable[[dict[str, Any]], list[Rule]]]:
    """Get task rules builder function for a specific task type.

    This function first looks for custom task rules, then falls back to built-in rules.

    Args:
        task_name: Name of the task type

    Returns:
        Function that builds rules if found, None otherwise
    """
    # List of built-in task names
    BUILT_IN_TASKS = ["fix_tests", "improve_coverage", "task_planner"]

    # First, try to load custom task rules
    # We'll implement this in the rule loader where we have access to workdir
    # For now, just return built-in rules if available
    if task_name in BUILT_IN_TASKS:
        # Try to load the built-in task rules dynamically
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            # Update path to reflect new directory structure
            # Tasks are now in forgeflow/tasks, not forgeflow/core/tasks
            task_file_path = os.path.join(pkg_dir, "tasks", f"{task_name}_task.py")

            if os.path.exists(task_file_path):
                # Load the module dynamically
                spec = importlib.util.spec_from_file_location(f"{task_name}_task", task_file_path)
                if spec is None or spec.loader is None:
                    logger.error(f"Failed to load spec for {task_file_path}")
                    return None

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "build_rules"):
                    return module.build_rules
        except Exception as e:
            logger.error(f"Error loading module from {task_file_path}: {e}")
            pass

    return None

    # If no built-in rules, return None
    # The rule loader will try to load custom rules
    return None
