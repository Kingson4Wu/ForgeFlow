"""Shared utilities for rule loading. Used by both automation.py and task_rules.py."""

from __future__ import annotations

import functools
import importlib.util
import logging
import os
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger("forgeflow")


# ---------- Path helpers ----------


@functools.cache
def _get_repo_root() -> Path | None:
    """Get the repo root (parent of the forgeflow package directory)."""
    try:
        import forgeflow as _forgeflow

        return Path(_forgeflow.__file__).resolve().parent.parent
    except (ImportError, OSError):
        return None


@functools.cache
def _get_pkg_dir() -> Path | None:
    """Get the forgeflow package directory."""
    try:
        import forgeflow as _forgeflow

        return Path(_forgeflow.__file__).resolve().parent
    except (ImportError, OSError):
        return None


@functools.cache
def _get_home_config_dir() -> Path | None:
    """Get the ~/.forgeflow/ directory for user-level configuration."""
    return Path.home() / ".forgeflow"


def _get_user_custom_rules_dir() -> str | None:
    """Get the ~/.forgeflow/user_custom_rules/ directory."""
    home = _get_home_config_dir()
    return str(home / "user_custom_rules") if home else None


def _get_user_custom_rules_tasks_dir() -> str | None:
    """Get the ~/.forgeflow/user_custom_rules/tasks/ directory."""
    ucr = _get_user_custom_rules_dir()
    return os.path.join(ucr, "tasks") if ucr else None


def _get_user_custom_rules_projects_dir() -> str | None:
    """Get the ~/.forgeflow/user_custom_rules/projects/ directory."""
    ucr = _get_user_custom_rules_dir()
    return os.path.join(ucr, "projects") if ucr else None


def _get_pkg_task_configs_dir() -> str | None:
    """Get the package-built-in task configs directory: forgeflow/tasks/configs/."""
    pkg = _get_pkg_dir()
    if pkg is None:
        return None
    return str((pkg / "tasks" / "configs").resolve())


# ---------- File finding ----------


def _find_rule_file(file_names: list[str], directories: list[str]) -> str | None:
    """Find a rule file in the given directories."""
    for directory in directories:
        for filename in file_names:
            path = os.path.abspath(os.path.join(directory, filename))
            if os.path.isfile(path):
                return path
    return None


# ---------- Module loading ----------


def _load_module_from_file(file_path: str, module_name: str) -> types.ModuleType | None:
    """Load a Python module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            logger.error("Failed to load spec for %s", file_path)
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except (ImportError, OSError, ValueError, SyntaxError) as e:
        logger.error("Error loading module from %s: %s", file_path, e)
        return None


def _find_build_function(
    module: types.ModuleType, possible_names: list[str]
) -> Callable[..., Any] | None:
    """Find a build function in a module."""
    for func_name in possible_names:
        if hasattr(module, func_name):
            return getattr(module, func_name)  # type: ignore[no-any-return]
    return None


def build_function_names(base_name: str) -> list[str]:
    """Build the standard list of possible build function names."""
    return [
        "build_rules",
        f"build_{base_name}_rules",
        f"build_{base_name}",
        "build_custom_rules",
        f"{base_name}_rules",
        "rules",
    ]
