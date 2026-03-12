"""Logging system translated from SetLog.au3.

Replaces SetLog/SetDebugLog/SetAtkLog with Python stdlib logging.
Supports colored console output and file logging with rotation.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from mybot.constants import (
    COLOR_ACTION,
    COLOR_ACTION1,
    COLOR_DEBUG,
    COLOR_DEBUG1,
    COLOR_DEBUG2,
    COLOR_DEBUGS,
    COLOR_ERROR,
    COLOR_INFO,
    COLOR_SUCCESS,
    COLOR_SUCCESS1,
    COLOR_WARNING,
)

# Custom log levels matching AutoIt's color-based system
LOG_ACTION = 25  # Between INFO and WARNING

logging.addLevelName(LOG_ACTION, "ACTION")

# Map AutoIt colors to log levels
_COLOR_TO_LEVEL: dict[int, int] = {
    COLOR_ERROR: logging.ERROR,
    COLOR_WARNING: logging.WARNING,
    COLOR_INFO: logging.INFO,
    COLOR_SUCCESS: logging.INFO,
    COLOR_SUCCESS1: logging.INFO,
    COLOR_DEBUG: logging.DEBUG,
    COLOR_DEBUG1: logging.DEBUG,
    COLOR_DEBUG2: logging.DEBUG,
    COLOR_DEBUGS: logging.DEBUG,
    COLOR_ACTION: LOG_ACTION,
    COLOR_ACTION1: LOG_ACTION,
}

# Map AutoIt colors to level name strings (matches GetLogLevel in SetLog.au3)
_COLOR_TO_LABEL: dict[int, str] = {
    COLOR_ERROR: "ERROR",
    COLOR_WARNING: "WARN",
    COLOR_SUCCESS: "SUCCESS",
    COLOR_SUCCESS1: "SUCCESS1",
    COLOR_INFO: "INFO",
    COLOR_DEBUG: "DEBUG",
    COLOR_DEBUG1: "DEBUG1",
    COLOR_DEBUG2: "DEBUG2",
    COLOR_DEBUGS: "DEBUGS",
    COLOR_ACTION: "ACTION",
    COLOR_ACTION1: "ACTION1",
}


class BotFormatter(logging.Formatter):
    """Formatter matching AutoIt's log format: [HH:MM:SS AM/PM] LEVEL message."""

    def format(self, record: logging.LogRecord) -> str:
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        level = record.levelname[:8].ljust(8)
        return f"[{time_str}] {level} {record.getMessage()}"


class ColorConsoleHandler(logging.StreamHandler):  # type: ignore[type-arg]
    """Console handler with ANSI color output."""

    # ANSI color codes
    _LEVEL_COLORS: dict[int, str] = {
        logging.ERROR: "\033[91m",     # Red
        logging.WARNING: "\033[93m",   # Yellow
        logging.INFO: "\033[94m",      # Blue
        LOG_ACTION: "\033[33m",        # Orange
        logging.DEBUG: "\033[35m",     # Purple
    }
    _RESET = "\033[0m"

    def emit(self, record: logging.LogRecord) -> None:
        color = self._LEVEL_COLORS.get(record.levelno, "")
        record.msg = f"{color}{record.msg}{self._RESET}" if color else record.msg
        super().emit(record)


# Module-level logger
_logger: logging.Logger | None = None
_gui_callback: object | None = None


def setup_logging(
    log_dir: Path | None = None,
    debug: bool = False,
    console: bool = True,
) -> logging.Logger:
    """Initialize the bot logging system.

    Args:
        log_dir: Directory for log files. None for console-only.
        debug: Enable debug level logging.
        console: Enable console output.

    Returns:
        Configured logger instance.
    """
    global _logger

    logger = logging.getLogger("mybot")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()

    formatter = BotFormatter()

    if console:
        console_handler = ColorConsoleHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        logger.addHandler(console_handler)

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"mybot_{datetime.now():%Y-%m-%d}.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Get the bot logger, initializing with defaults if needed."""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


# ── Convenience functions matching AutoIt SetLog/SetDebugLog ─────────────────

def set_log(message: str, color: int = 0x000000) -> None:
    """Log a message (translates AutoIt SetLog calls).

    Args:
        message: Log message text.
        color: AutoIt color constant determining log level.
    """
    logger = get_logger()
    level = _COLOR_TO_LEVEL.get(color, logging.INFO)
    logger.log(level, message)


def set_debug_log(message: str, color: int = COLOR_DEBUG) -> None:
    """Log a debug message (translates AutoIt SetDebugLog calls).

    Only outputs when debug logging is enabled.
    """
    get_logger().debug(message)
