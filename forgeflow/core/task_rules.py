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
def _get_config_directory(dir_type: str) -> Optional[str]:
    """Get configuration directory path for the specified type.

    Args:
        dir_type: Type of directory to get ('user_custom_rules', 'default_rules', or 'examples')

    Returns:
        Path to the directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent

        if dir_type == "user_custom_rules":
            user_custom_rules_dir = (repo_root / "user_custom_rules" / "tasks").resolve()
            return str(user_custom_rules_dir)
        elif dir_type == "default_rules":
            default_rules_dir = (pkg_dir / "tasks" / "configs").resolve()
            return str(default_rules_dir)
        elif dir_type == "examples":
            examples_dir = (repo_root / "examples" / "tasks").resolve()
            return str(examples_dir)
    except Exception:
        # Best effort; if not available, return None
        return None

    # If we get here, the dir_type was not recognized
    return None


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
    config_file = os.path.join(workdir, f"{task_name}_config.json")

    # If not found in workdir, try user custom rules tasks directory
    if not os.path.exists(config_file):
        user_custom_rules_dir = _get_config_directory("user_custom_rules")
        if user_custom_rules_dir:
            config_file = os.path.join(user_custom_rules_dir, f"{task_name}_config.json")

    # If not found in user custom rules tasks directory, try default rules directory
    if not os.path.exists(config_file):
        default_rules_dir = _get_config_directory("default_rules")
        if default_rules_dir:
            config_file = os.path.join(default_rules_dir, f"{task_name}_config.json")

    # If not found in default rules directory, try examples tasks directory (for backward compatibility)
    if not os.path.exists(config_file):
        examples_dir = _get_config_directory("examples")
        if examples_dir:
            config_file = os.path.join(examples_dir, f"{task_name}_config.json")

    if not os.path.exists(config_file):
        return {}  # type: ignore

    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception:
        # If there's an error reading the config file, return empty dict
        return {}  # type: ignore


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


def _get_examples_tasks_dir() -> Optional[str]:
    """Get the examples tasks directory path robustly.

    Returns:
        Path to examples tasks directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent  # root that contains 'forgeflow' dir
        examples_tasks_dir = (repo_root / "examples" / "tasks").resolve()
        return str(examples_tasks_dir)
    except Exception:
        # Best effort; if not available (e.g., installed package without examples), skip
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


def _get_user_custom_rules_tasks_dir() -> Optional[str]:
    """Get the user custom rules tasks directory path robustly.

    Returns:
        Path to user custom rules tasks directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent  # root that contains 'forgeflow' dir
        user_custom_rules_tasks_dir = (repo_root / "user_custom_rules" / "tasks").resolve()
        return str(user_custom_rules_tasks_dir)
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
    # Possible file names to look for
    possible_files = [f"{task_name}_task.py", f"{task_name}.py"]

    # Possible directories to look in
    possible_dirs = [workdir]

    # Add user custom rules tasks directory if available
    user_custom_rules_tasks_dir = _get_user_custom_rules_tasks_dir()
    if user_custom_rules_tasks_dir:
        possible_dirs.append(user_custom_rules_tasks_dir)

    # Add repo examples tasks directory if available (for backward compatibility)
    examples_tasks_dir = _get_examples_tasks_dir()
    if examples_tasks_dir:
        possible_dirs.append(examples_tasks_dir)

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

    # If no built-in rules, return None
    # The rule loader will try to load custom rules
    return None
