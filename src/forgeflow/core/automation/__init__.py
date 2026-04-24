"""Core automation loop and configuration."""

from .defaults import UNCHANGED_OUTPUT_THRESHOLD as UNCHANGED_OUTPUT_THRESHOLD
from .loop import (
    Config as Config,
)
from .loop import (
    is_task_processing as is_task_processing,
)
from .loop import (
    reset_unchanged_output_tracking as reset_unchanged_output_tracking,
)
from .loop import (
    run_automation as run_automation,
)
from .loop import (
    run_monitor_mode as run_monitor_mode,
)
from .loop import (
    setup_logger as setup_logger,
)

__all__ = [
    "Config",
    "is_task_processing",
    "reset_unchanged_output_tracking",
    "run_automation",
    "run_monitor_mode",
    "setup_logger",
    "UNCHANGED_OUTPUT_THRESHOLD",
]
