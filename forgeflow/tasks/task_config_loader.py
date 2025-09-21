import json
import logging
import os
from pathlib import Path
from typing import Any

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
    config_file = os.path.join(workdir, f"{task_name}_config.json")

    # If not found in workdir, try user custom rules tasks directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            user_custom_rules_dir = (repo_root / "user_custom_rules" / "tasks").resolve()
            config_file = os.path.join(user_custom_rules_dir, f"{task_name}_config.json")
        except Exception:
            # Best effort; if not available, continue with next option
            pass

    # If not found in user custom rules tasks directory, try default rules directory
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            default_rules_dir = (pkg_dir / "tasks" / "configs").resolve()
            config_file = os.path.join(default_rules_dir, f"{task_name}_config.json")
        except Exception:
            # Best effort; if not available, continue with next option
            pass

    # If not found in default rules directory, try examples tasks directory (for backward compatibility)
    if not os.path.exists(config_file):
        try:
            import forgeflow as _forgeflow

            pkg_dir = Path(_forgeflow.__file__).resolve().parent
            repo_root = pkg_dir.parent
            examples_dir = (repo_root / "examples" / "tasks").resolve()
            config_file = os.path.join(examples_dir, f"{task_name}_config.json")
        except Exception:
            # Best effort; if not available, continue with next option
            pass

    if not os.path.exists(config_file):
        return {}  # type: ignore

    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception:
        # If there's an error reading the config file, return empty dict
        return {}  # type: ignore
