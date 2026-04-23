"""Shared utilities for rule loading. Used by both automation.py and task_rules.py."""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .defaults import DIR_CONFIGS, DIR_DEFAULT_RULES, DIR_EXAMPLES, DIR_TASKS, DIR_USER_CUSTOM_RULES

logger = logging.getLogger("forgeflow")


# ---------- Path helpers ----------

_repo_root: Path | None = None
_pkg_dir: Path | None = None


def _get_repo_root() -> Path | None:
    """Get the repo root (parent of the forgeflow package directory)."""
    global _repo_root
    if _repo_root is None:
        try:
            import forgeflow as _forgeflow

            _repo_root = Path(_forgeflow.__file__).resolve().parent.parent
        except Exception:
            return None
    return _repo_root


def _get_pkg_dir() -> Path | None:
    """Get the forgeflow package directory."""
    global _pkg_dir
    if _pkg_dir is None:
        try:
            import forgeflow as _forgeflow

            _pkg_dir = Path(_forgeflow.__file__).resolve().parent
        except Exception:
            return None
    return _pkg_dir


def _get_subdir(base: Path | None, *segments: str) -> str | None:
    """Resolve a subdirectory path, returning None if base is None."""
    if base is None:
        return None
    return str((base.joinpath(*segments)).resolve())


def _get_examples_dir() -> str | None:
    root = _get_repo_root()
    return _get_subdir(root, DIR_EXAMPLES)


def _get_user_custom_rules_dir() -> str | None:
    root = _get_repo_root()
    return _get_subdir(root, DIR_USER_CUSTOM_RULES)


def _get_examples_tasks_dir() -> str | None:
    return _get_subdir(Path(_get_examples_dir()), "tasks") if _get_examples_dir() else None


def _get_user_custom_rules_tasks_dir() -> str | None:
    return (
        _get_subdir(Path(_get_user_custom_rules_dir()), "tasks")
        if _get_user_custom_rules_dir()
        else None
    )


def _get_default_rules_dir() -> str | None:
    root = _get_repo_root()
    return _get_subdir(root, DIR_DEFAULT_RULES)


def _get_cli_types_rules_dir() -> str | None:
    pkg = _get_pkg_dir()
    return _get_subdir(pkg, "core", "cli_types") if pkg else None


_DIR_MAP = {
    DIR_USER_CUSTOM_RULES: lambda root, pkg: str(
        (root / DIR_USER_CUSTOM_RULES / DIR_TASKS).resolve()
    ),
    DIR_DEFAULT_RULES: lambda root, pkg: str((pkg / DIR_TASKS / DIR_CONFIGS).resolve()),
    DIR_EXAMPLES: lambda root, pkg: str((root / DIR_EXAMPLES / DIR_TASKS).resolve()),
}


def _get_config_directory(dir_type: str) -> str | None:
    """Get configuration directory path for the specified type."""
    pkg = _get_pkg_dir()
    root = _get_repo_root()
    if pkg is None or root is None:
        return None
    mapper = _DIR_MAP.get(dir_type)
    return mapper(root, pkg) if mapper else None


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
