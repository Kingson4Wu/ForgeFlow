from __future__ import annotations

import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Callable

from .rules import Rule, build_default_rules


def load_custom_rules(project_name: str, workdir: str) -> list[Rule] | None:
    """
    Load custom rules from a Python file based on the project name.

    The function will look for a file in this order:
    1. `{project_name}_rules.py` in the current working directory
    2. `{project_name}.py` in the current working directory
    3. `{project_name}_rules.py` in the forgeflow/examples directory
    4. `{project_name}.py` in the forgeflow/examples directory

    Args:
        project_name: Name of the project (used to find the rule file)
        workdir: Working directory where the project is running

    Returns:
        List of Rule objects if found, None otherwise
    """
    logger = logging.getLogger("forgeflow")

    # Possible file names to look for
    possible_files = [f"{project_name}_rules.py", f"{project_name}.py"]

    # Possible directories to look in
    possible_dirs = [workdir]

    # Add repo examples directory robustly (works in source checkout)
    try:
        import forgeflow as _forgeflow

        pkg_dir = Path(_forgeflow.__file__).resolve().parent
        repo_root = pkg_dir.parent  # root that contains 'forgeflow' dir
        examples_dir = (repo_root / "examples").resolve()
        possible_dirs.append(str(examples_dir))
    except Exception:
        # Best effort; if not available (e.g., installed package without examples), skip
        pass

    # Try to find the rule file
    rule_file_path = None
    for directory in possible_dirs:
        for filename in possible_files:
            path = os.path.abspath(os.path.join(directory, filename))
            if os.path.isfile(path):
                rule_file_path = path
                break
        if rule_file_path:
            break

    # Check if the file exists
    if not rule_file_path:
        logger.warning(f"Rule file not found for project: {project_name}")
        return None

    logger.info(f"Loading custom rules from: {rule_file_path}")

    try:
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(f"{project_name}_rules", rule_file_path)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to load spec for {rule_file_path}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{project_name}_rules"] = module
        spec.loader.exec_module(module)

        # Look for a function that builds rules
        build_func: Callable[[], list[Rule]] | None = None

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

        for func_name in possible_names:
            if hasattr(module, func_name):
                build_func = getattr(module, func_name)
                break

        if build_func is None:
            logger.error(f"No build function found in {rule_file_path}")
            return None

        # Call the build function to get the rules
        rules = build_func()
        logger.info(f"Successfully loaded {len(rules)} custom rules")
        return rules

    except Exception as e:
        logger.error(f"Error loading custom rules from {rule_file_path}: {e}")
        return None


def get_rules(config) -> list[Rule]:
    """
    Get rules based on the configuration.

    If a project name is specified, try to load custom rules.
    Otherwise, use the default rules.

    Args:
        config: Configuration object containing project name and other settings

    Returns:
        List of Rule objects
    """
    logger = logging.getLogger("forgeflow")

    # If no project specified, use default rules
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
