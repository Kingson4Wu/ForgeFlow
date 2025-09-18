from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Callable, TypeVar

from .rules import Rule, build_default_rules
from .task_rules import get_task_rules_builder, load_custom_task_rules

logger = logging.getLogger("forgeflow")

T = TypeVar("T")


def _find_rule_file(file_names: list[str], directories: list[str]) -> str | None:
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


def _get_examples_dir() -> str | None:
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


def _get_default_rules_dir() -> str | None:
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


def _get_user_custom_rules_dir() -> str | None:
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


def _load_module_from_file(file_path: str, module_name: str) -> object | None:
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


def _find_build_function(module: object, possible_names: list[str]) -> Callable | None:
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


def load_custom_rules(project_name: str, workdir: str) -> list[Rule] | None:
    """
    Load custom rules from a Python file based on the project name.

    The function will look for a file in this order:
    1. `{project_name}_rules.py` in the current working directory
    2. `{project_name}.py` in the current working directory
    3. `{project_name}_rules.py` in the user_custom_rules directory
    4. `{project_name}.py` in the user_custom_rules directory
    5. `{project_name}_rules.py` in the default_rules directory (for built-in default rules)
    6. `{project_name}.py` in the default_rules directory (for built-in default rules)
    7. `{project_name}_rules.py` in the forgeflow/examples directory (for backward compatibility)
    8. `{project_name}.py` in the forgeflow/examples directory (for backward compatibility)

    Args:
        project_name: Name of the project (used to find the rule file)
        workdir: Working directory where the project is running

    Returns:
        List of Rule objects if found, None otherwise
    """
    # Possible file names to look for
    possible_files = [f"{project_name}_rules.py", f"{project_name}.py"]

    # Possible directories to look in
    possible_dirs = [workdir]

    # Add user custom rules directory if available
    user_custom_rules_dir = _get_user_custom_rules_dir()
    if user_custom_rules_dir:
        possible_dirs.append(user_custom_rules_dir)

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
        logger.warning(f"Rule file not found for project: {project_name}")
        return None

    logger.info(f"Loading custom rules from: {rule_file_path}")

    # Load the module dynamically
    module = _load_module_from_file(rule_file_path, f"{project_name}_rules")
    if module is None:
        return None

    # Look for a function that builds rules
    # Try function names in order of preference
    # Prioritize build_rules as the standard function name
    possible_names = [
        "build_rules",  # Standard function name for all projects
        f"build_{project_name}_rules",  # e.g., build_web_project_rules
        f"build_{project_name}",  # e.g., build_web_project
        "build_custom_rules",
        f"{project_name}_rules",  # e.g., web_project_rules
        "rules",
    ]

    build_func = _find_build_function(module, possible_names)
    if build_func is None:
        logger.error(f"No build function found in {rule_file_path}")
        return None

    # Call the build function to get the rules
    try:
        rules = build_func()
        logger.info(f"Successfully loaded {len(rules)} custom rules")
        return rules
    except Exception as e:
        logger.error(f"Error calling build function in {rule_file_path}: {e}")
        return None


def get_task_rules(task_name: str, workdir: str) -> list[Rule] | None:
    """
    Get predefined rules for a specific task type.

    This function first looks for custom task rules, then falls back to built-in rules.

    Args:
        task_name: Name of the task type (e.g., 'fix_tests', 'improve_coverage')
        workdir: Working directory where the project is running

    Returns:
        List of Rule objects if found, None otherwise
    """
    # First, try to load custom task rules
    custom_rules_builder = load_custom_task_rules(task_name, workdir)
    if custom_rules_builder:
        try:
            # Load task-specific configuration
            from .task_rules import load_task_config

            config = load_task_config(task_name, workdir)

            rules = custom_rules_builder(config)
            logger.info(f"Successfully loaded {len(rules)} custom task rules for {task_name}")
            return rules
        except Exception as e:
            logger.error(f"Error building custom task rules for {task_name}: {e}")

    # If no custom rules, try built-in rules
    rules_builder = get_task_rules_builder(task_name)
    if rules_builder:
        try:
            # Load task-specific configuration
            from .task_rules import load_task_config

            config = load_task_config(task_name, workdir)

            rules = rules_builder(config)
            logger.info(f"Successfully loaded {len(rules)} built-in task rules for {task_name}")
            return rules
        except Exception as e:
            logger.error(f"Error building built-in task rules for {task_name}: {e}")
            return None

    logger.warning(f"Task rules not found for task: {task_name}")
    return None


def get_rules(config) -> list[Rule]:
    """
    Get rules based on the configuration.

    If a task type is specified, use task-specific rules.
    If a project name is specified, try to load custom rules.
    Otherwise, use the default rules.

    Args:
        config: Configuration object containing project name, task type and other settings

    Returns:
        List of Rule objects
    """
    # If task specified, try to load task rules first
    if config.task:
        task_rules = get_task_rules(config.task, config.workdir)
        if task_rules:
            logger.info(f"Using task rules for: {config.task}")
            return task_rules
        else:
            logger.warning(f"Failed to load task rules for '{config.task}'")

    # If no project specified and no valid task rules, use default rules
    if not config.project:
        logger.info("Using default rules")
        return build_default_rules()

    # Try to load custom rules
    custom_rules = load_custom_rules(config.project, config.workdir)
    if custom_rules:
        return custom_rules

    # Fallback to default rules if custom rules failed to load
    logger.warning(
        f"Failed to load custom rules for project '{config.project}', using default rules"
    )
    return build_default_rules()
