from __future__ import annotations

import datetime
import logging
import platform
import subprocess

logger = logging.getLogger("forgeflow")


def send_notification(title: str, message: str) -> None:
    """
    Send a desktop notification based on the operating system.

    Args:
        title: The title of the notification
        message: The message content of the notification
    """
    system = platform.system()

    try:
        if system == "Darwin":  # macOS
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            subprocess.run(
                [
                    "terminal-notifier",
                    "-title",
                    title,
                    "-message",
                    f"{message} ({timestamp})",
                    "-sender",
                    "com.forge_flow.app",
                ]
            )
        elif system == "Windows":
            # Windows notification (requires plyer or win10toast library)
            # This is a placeholder implementation
            logger.warning("Windows notifications not yet implemented")
        elif system == "Linux":
            # Linux notification (requires notify-send)
            # This is a placeholder implementation
            logger.warning("Linux notifications not yet implemented")
        else:
            logger.warning(f"Notifications not supported for system: {system}")
    except (subprocess.SubprocessError, OSError) as e:
        logger.error("Failed to send notification: %s", e)
