"""Shared utilities for rule loading. Used by both automation.py and task_rules.py."""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger("forgeflow")


# ---------- Path helpers ----------


def _get_repo_root() -> Path | None:
    """Get the repo root (parent of the forgeflow package directory)."""
    try:
        import forgeflow as _forgeflow

        return Path(_forgeflow.__file__).resolve().parent.parent
    except Exception:
        return None


def _get_pkg_dir() -> Path | None:
    """Get the forgeflow package directory."""
    try:
        import forgeflow as _forgeflow

        return Path(_forgeflow.__file__).resolve().parent
    except Exception:
        return None


def _get_examples_dir() -> str | None:
    root = _get_repo_root()
    if root is None:
        return None
    return str((root / "examples").resolve())


def _get_user_custom_rules_dir() -> str | None:
    root = _get_repo_root()
    if root is None:
        return None
    return str((root / "user_custom_rules").resolve())


def _get_examples_tasks_dir() -> str | None:
    examples = _get_examples_dir()
    if examples is None:
        return None
    return str((Path(examples) / "tasks").resolve())


def _get_user_custom_rules_tasks_dir() -> str | None:
    ucr = _get_user_custom_rules_dir()
    if ucr is None:
        return None
    return str((Path(ucr) / "tasks").resolve())


def _get_default_rules_dir() -> str | None:
    root = _get_repo_root()
    if root is None:
        return None
    return str((root / "default_rules").resolve())


def _get_cli_types_rules_dir() -> str | None:
    pkg = _get_pkg_dir()
    if pkg is None:
        return None
    return str((pkg / "core" / "cli_types").resolve())


def _get_config_directory(dir_type: str) -> str | None:
    """Get configuration directory path for the specified type."""
    pkg = _get_pkg_dir()
    root = _get_repo_root()
    if pkg is None or root is None:
        return None

    if dir_type == "user_custom_rules":
        return str((root / "user_custom_rules" / "tasks").resolve())
    elif dir_type == "default_rules":
        return str((pkg / "tasks" / "configs").resolve())
    elif dir_type == "examples":
        return str((root / "examples" / "tasks").resolve())
    return None


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


def _load_module_from_file(file_path: str, module_name: str) -> object | None:
    """Load a Python module from a file path."""
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
    """Find a build function in a module."""
    for func_name in possible_names:
        if hasattr(module, func_name):
            return getattr(module, func_name)  # type: ignore[no-any-return]
    return None
