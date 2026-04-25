from __future__ import annotations


class UnchangedTracker:
    """Tracks consecutive unchanged outputs to detect idle state."""

    __slots__ = ("_previous_output", "_count", "_threshold")

    def __init__(self, threshold: int = 5) -> None:
        self._threshold = threshold
        self._previous_output = ""
        self._count = 0

    def reset(self) -> None:
        self._previous_output = ""
        self._count = 0

    def is_unchanged_too_long(self, output: str) -> bool:
        if output != self._previous_output:
            self._previous_output = output
            self._count = 0
            return False
        self._count += 1
        return self._count >= self._threshold
