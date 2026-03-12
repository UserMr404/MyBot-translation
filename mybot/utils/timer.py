"""Timer utilities translated from StopWatch.au3 and Time.au3.

Provides high-resolution timing and function call profiling.
"""

from __future__ import annotations

import time
from datetime import datetime


def now_time() -> str:
    """Return formatted time string: [HH:MM:SS AM/PM].

    Replaces AutoIt Time() function.
    """
    return datetime.now().strftime("[%I:%M:%S %p] ")


def now_time_debug() -> str:
    """Return detailed time string: [YYYY-MM-DD HH:MM:SS.ms].

    Replaces AutoIt TimeDebug() function.
    """
    now = datetime.now()
    return now.strftime("[%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}] "


def timer_init() -> float:
    """Start a timer. Returns current time in seconds.

    Replaces AutoIt __TimerInit() which used GetTickCount.
    Uses time.perf_counter() for high-resolution timing.
    """
    return time.perf_counter()


def timer_diff(start_time: float) -> float:
    """Return elapsed milliseconds since timer_init().

    Replaces AutoIt __TimerDiff().
    """
    return (time.perf_counter() - start_time) * 1000.0


class StopWatch:
    """Execution timing utility translated from StopWatch.au3.

    Usage:
        sw = StopWatch()
        sw.start("MyOperation")
        # ... do work ...
        elapsed = sw.stop("MyOperation")
    """

    def __init__(self) -> None:
        self._timers: dict[str, float] = {}
        self._stack: list[str] = []

    def start(self, tag: str) -> None:
        """Start timing a named operation."""
        self._timers[tag] = time.perf_counter()
        self._stack.append(tag)

    def stop(self, tag: str | None = None) -> float:
        """Stop timing and return elapsed milliseconds.

        Args:
            tag: Timer tag. None to stop the most recent.

        Returns:
            Elapsed time in milliseconds.
        """
        if tag is None and self._stack:
            tag = self._stack.pop()
        elif tag and tag in self._stack:
            self._stack.remove(tag)

        if tag and tag in self._timers:
            elapsed = (time.perf_counter() - self._timers.pop(tag)) * 1000.0
            return elapsed
        return 0.0

    @property
    def level(self) -> int:
        """Current nesting level."""
        return len(self._stack)
