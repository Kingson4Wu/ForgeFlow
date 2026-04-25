from __future__ import annotations

import logging
import subprocess

from forgeflow.config import CODEX_MIN_HEIGHT, CODEX_MIN_WIDTH

logger = logging.getLogger("forgeflow")


class WindowManager:
    """Manages tmux window dimensions, especially for Codex CLI requirements."""

    def __init__(self, session: str) -> None:
        self.session = session

    def should_resize_for_codex(self) -> bool:
        """Check if terminal width is below Codex minimum."""
        try:
            result = subprocess.run(
                ["tput", "cols"], capture_output=True, text=True, check=False  # nosec B603
            )
            if result.returncode == 0:
                current_width = int(result.stdout.strip())
                return current_width < CODEX_MIN_WIDTH
            else:
                logger.warning(
                    "Failed to determine terminal width (tput returned %d)", result.returncode
                )
        except (ValueError, subprocess.SubprocessError) as e:
            logger.warning("Failed to determine terminal width: %s", e)

        logger.debug("Defaulting to resize: terminal width could not be determined")
        return True

    def get_window_width(self) -> int | None:
        """Get current tmux window width. Returns None on failure."""
        try:
            result = subprocess.run(
                [
                    "tmux",
                    "display-message",
                    "-p",
                    "-t",
                    self.session,
                    "#{window_width}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )  # nosec B603

            if result.returncode == 0:
                return int(result.stdout.strip())
            else:
                logger.warning(
                    "Failed to get window width for session %s (returned %d)",
                    self.session,
                    result.returncode,
                )
        except (ValueError, subprocess.SubprocessError) as e:
            logger.warning("Failed to get window width for session %s: %s", self.session, e)

        return None

    def resize_window(self, width: int, height: int | None = None) -> bool:
        """Resize tmux window to specified dimensions."""
        try:
            result = subprocess.run(
                ["tmux", "resize-window", "-t", self.session, "-x", str(width)],
                check=False,
            )  # nosec B603
            success = result.returncode == 0
            if success:
                logger.info("Resized window width for session %s to %s", self.session, width)
            else:
                logger.warning(
                    "Failed to resize window width for session %s to %s (returned %d)",
                    self.session,
                    width,
                    result.returncode,
                )

            if success and height is not None:
                try:
                    subprocess.run(
                        [
                            "tmux",
                            "resize-window",
                            "-t",
                            self.session,
                            "-y",
                            str(height),
                        ],
                        check=False,
                    )  # nosec B603
                    logger.info("Resized window height for session %s to %s", self.session, height)
                except (OSError, subprocess.SubprocessError) as e:
                    logger.warning(
                        "Failed to set window height for session %s to %s: %s",
                        self.session,
                        height,
                        e,
                    )

            return success
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning(
                "Failed to resize window width for session %s to %s: %s",
                self.session,
                width,
                e,
            )
            return False

    def ensure_codex_width(self) -> None:
        """Ensure window width meets Codex minimum (120x40)."""
        current_width = self.get_window_width()
        if current_width is None or current_width < CODEX_MIN_WIDTH:
            logger.info(
                "Window width %s < %s, resizing for codex session %s",
                current_width,
                CODEX_MIN_WIDTH,
                self.session,
            )
            success = self.resize_window(CODEX_MIN_WIDTH, CODEX_MIN_HEIGHT)
            if not success:
                logger.warning("Failed to resize window for codex session %s", self.session)
        else:
            logger.debug("Window width %s already >= %s", current_width, CODEX_MIN_WIDTH)
