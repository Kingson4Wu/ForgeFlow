from __future__ import annotations

import importlib.util
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

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


def _get_cli_types_rules_dir() -> str | None:
    """Get the CLI types rules directory path robustly.

    Returns:
        Path to CLI types rules directory, or None if not found
    """
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        cli_types_rules_dir = (pkg_dir / "core" / "cli_types").resolve()
        return str(cli_types_rules_dir)
    except Exception:
        # Best effort; if not available, skip
        return None


# These functions are no longer needed as we've reorganized the directory structure
# Keeping them for backward compatibility but they will return None
def _get_tasks_rules_dir() -> str | None:
    """Get the tasks rules directory path robustly.

    Returns:
        Path to tasks rules directory, or None if not found
    """
    return None


def _get_projects_rules_dir() -> str | None:
    """Get the projects rules directory path robustly.

    Returns:
        Path to projects rules directory, or None if not found
    """
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


def _find_build_function(module: object, possible_names: list[str]) -> Callable[..., Any] | None:
    """Find a build function in a module.

    Args:
        module: Module to search in
        possible_names: List of possible function names to look for

    Returns:
        Found function, or None if not found
    """
    for func_name in possible_names:
        if hasattr(module, func_name):
            return getattr(module, func_name)  # type: ignore
    return None


def load_custom_rules(project_name: str, workdir: str) -> list[Rule] | None:
    """
    Load custom rules from a Python file based on the project name.

    The function will look for a file in this order:
    1. `{project_name}_rules.py` in the current working directory
    2. `{project_name}.py` in the current working directory
    3. `user_custom_rules/projects/{project_name}_rules.py` in the user custom rules directory
    4. `user_custom_rules/projects/{project_name}.py` in the user custom rules directory
    5. `examples/projects/{project_name}_rules.py` in the examples directory (for backward compatibility)
    6. `examples/projects/{project_name}.py` in the examples directory (for backward compatibility)

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

    # Add user custom rules projects directory if available
    user_custom_rules_dir = _get_user_custom_rules_dir()
    if user_custom_rules_dir:
        possible_dirs.append(os.path.join(user_custom_rules_dir, "projects"))

    # Add repo examples projects directory if available (for backward compatibility)
    examples_dir = _get_examples_dir()
    if examples_dir:
        possible_dirs.append(os.path.join(examples_dir, "projects"))

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
        rules = build_func()  # type: ignore
        logger.info(f"Successfully loaded {len(rules)} custom rules")
        return rules  # type: ignore
    except Exception as e:
        logger.error(f"Error calling build function in {rule_file_path}: {e}")
        return None


def get_task_rules(task_name: str, workdir: str) -> list[Rule] | None:
    """
    Get predefined rules for a specific task type.

    This function loads CLI type rules as the base, then adds task-specific rules.

    Args:
        task_name: Name of the task type (e.g., 'fix_tests', 'improve_coverage')
        workdir: Working directory where the project is running

    Returns:
        List of Rule objects if found, None otherwise
    """
    # Load CLI type rules as the base (highest priority)
    # Note: We'll get the CLI type from the config when this function is called from get_rules
    # For now, we'll load task rules and let get_rules combine them with CLI type rules

    # First, try to load custom task rules
    custom_rules_builder = load_custom_task_rules(task_name, workdir)
    if custom_rules_builder:
        try:
            # Load task-specific configuration
            from .task_rules import load_task_config

            config = load_task_config(task_name, workdir)

            rules = custom_rules_builder(config)  # type: ignore
            logger.info(f"Successfully loaded {len(rules)} custom task rules for {task_name}")
            return rules  # type: ignore
        except Exception as e:
            logger.error(f"Error building custom task rules for {task_name}: {e}")

    # If no custom rules, try built-in rules
    rules_builder = get_task_rules_builder(task_name)
    if rules_builder:
        try:
            # Load task-specific configuration
            from .task_rules import load_task_config

            config = load_task_config(task_name, workdir)

            rules = rules_builder(config)  # type: ignore
            logger.info(f"Successfully loaded {len(rules)} built-in task rules for {task_name}")
            return rules  # type: ignore
        except Exception as e:
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
        task_rules = get_task_rules(config.task, config.workdir)
        if task_rules:
            logger.info(f"Using task rules for: {config.task}")
            # Combine CLI type rules with task rules
            # CLI type rules come first, then task rules
            return cli_type_rules + task_rules
        else:
            logger.warning(f"Failed to load task rules for '{config.task}'")

    # If project specified, try to load custom rules and combine with CLI type rules
    if config.project:
        custom_rules = load_custom_rules(config.project, config.workdir)
        if custom_rules:
            # Combine CLI type rules with custom rules
            # CLI type rules come first, then custom rules
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
