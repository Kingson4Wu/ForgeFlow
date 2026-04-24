"""Rule system: base classes, loader, task rules, CLI adapters, and CLI type rules."""

from .base import (
    CommandPostProcessor as CommandPostProcessor,
)
from .base import (
    Rule as Rule,
)
from .base import (
    build_default_rules as build_default_rules,
)
from .base import (
    get_command_post_processor as get_command_post_processor,
)
from .base import (
    is_all_task_finished as is_all_task_finished,
)
from .base import (
    is_final_verification_finished as is_final_verification_finished,
)
from .base import (
    next_command as next_command,
)
from .loader import (
    get_rules as get_rules,
)
from .loader import (
    get_task_rules as get_task_rules,
)
from .loader import (
    load_custom_rules as load_custom_rules,
)

__all__ = [
    "CommandPostProcessor",
    "Rule",
    "build_default_rules",
    "get_command_post_processor",
    "is_all_task_finished",
    "is_final_verification_finished",
    "next_command",
    "get_rules",
    "get_task_rules",
    "load_custom_rules",
]
