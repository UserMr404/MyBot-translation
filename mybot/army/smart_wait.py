"""Smart wait for training translated from CreateArmy/SmartWait4Train.au3.

Calculates optimal wait time based on remaining training duration.

Source: COCBot/functions/CreateArmy/SmartWait4Train.au3
"""

from __future__ import annotations

import re
import time

from mybot.log import set_debug_log, set_log


def parse_train_time(time_str: str) -> float:
    """Parse a training time string like '5m 30s' or '1h 20m' into seconds.

    Args:
        time_str: Time string from OCR.

    Returns:
        Time in seconds.
    """
    total = 0.0
    hours = re.search(r"(\d+)\s*h", time_str)
    mins = re.search(r"(\d+)\s*m", time_str)
    secs = re.search(r"(\d+)\s*s", time_str)

    if hours:
        total += int(hours.group(1)) * 3600
    if mins:
        total += int(mins.group(1)) * 60
    if secs:
        total += int(secs.group(1))

    return total


def smart_wait_for_train(
    remaining_time: str,
    min_wait: float = 30.0,
    max_wait: float = 300.0,
) -> float:
    """Calculate smart wait time for training to complete.

    Translated from SmartWait4Train() in SmartWait4Train.au3.
    Returns a wait time that balances efficiency (not checking too early)
    with responsiveness (not waiting too long).

    Args:
        remaining_time: Training time string from OCR (e.g., "5m 30s").
        min_wait: Minimum wait time in seconds.
        max_wait: Maximum wait time in seconds.

    Returns:
        Recommended wait time in seconds.
    """
    seconds = parse_train_time(remaining_time)

    if seconds <= 0:
        return 0.0

    # Wait for 80% of remaining time, clamped to bounds
    wait = seconds * 0.8
    wait = max(min_wait, min(wait, max_wait))

    set_debug_log(f"SmartWait: remaining={remaining_time} ({seconds:.0f}s), waiting {wait:.0f}s")
    return wait
