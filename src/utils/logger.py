from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.utils.constants import APP_NAME, DEFAULT_CONFIG_PATH


def setup_logger(
    name: str = APP_NAME,
    log_dir: Path | None = None,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Configure and return the application logger.

    Args:
        name: Logger name.
        log_dir: Directory for log files. Defaults to config directory.
        level: Minimum logging level.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    log_path = (log_dir or DEFAULT_CONFIG_PATH) / "app.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Module-level logger instance
logger = setup_logger()
