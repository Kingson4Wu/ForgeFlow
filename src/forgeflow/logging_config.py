from __future__ import annotations

import logging
import sys


def setup_logger(path: str, to_console: bool = True, level: str = "INFO") -> logging.Logger:
    """Configure the forgeflow logger with file and optional console output."""
    logger = logging.getLogger("forgeflow")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
    logger.addHandler(fh)

    if to_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
        logger.addHandler(ch)

    return logger
