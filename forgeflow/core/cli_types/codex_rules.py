import re

from forgeflow.core.rules import Rule


def build_rules() -> list[Rule]:
    """Build rules specific to Codex CLI."""
    return [
        Rule(
            check=lambda out: bool(
                re.search(
                    r"■ stream disconnected before completion: Your input exceeds the context window of this model.*",
                    out,
                    re.DOTALL,
                )
            ),
            command="/compact",
        ),
        Rule(
            check=lambda out: "stream error: stream disconnected before completion: "
            "Your input exceeds the context window of this model" in out,
            command="/compact",
        ),
    ]
