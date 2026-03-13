"""Attack timing and delays translated from Troops/SetSleep.au3.

Manages deployment delays between waves and troops.

Source: COCBot/functions/Attack/Troops/SetSleep.au3
"""

from __future__ import annotations

import random

# Default delay constants (from DelayTimes.au3)
DELAY_DROP_TROOP_MIN = 30    # ms
DELAY_DROP_TROOP_MAX = 60    # ms
DELAY_BETWEEN_WAVES = 200    # ms
DELAY_HERO_ACTIVATE = 1000   # ms


def get_deploy_delay(
    min_ms: int = DELAY_DROP_TROOP_MIN,
    max_ms: int = DELAY_DROP_TROOP_MAX,
) -> float:
    """Get a randomized delay between troop deployments.

    Translated from SetSleep() in SetSleep.au3.
    Returns a random delay to appear more human-like.

    Args:
        min_ms: Minimum delay in milliseconds.
        max_ms: Maximum delay in milliseconds.

    Returns:
        Delay in seconds.
    """
    return random.randint(min_ms, max_ms) / 1000.0


def get_wave_delay(
    base_ms: int = DELAY_BETWEEN_WAVES,
    variance: float = 0.3,
) -> float:
    """Get delay between deployment waves.

    Args:
        base_ms: Base delay in milliseconds.
        variance: Random variance (0.0 to 1.0).

    Returns:
        Delay in seconds.
    """
    jitter = random.uniform(1 - variance, 1 + variance)
    return (base_ms * jitter) / 1000.0
