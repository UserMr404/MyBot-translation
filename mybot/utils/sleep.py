"""Sleep/control flow system translated from _Sleep.au3.

The original _Sleep() is called 1,801 times across the codebase. It's the
cooperative multitasking mechanism that checks for pause/restart/stop between
every operation.

This Python version uses threading.Event for efficient waiting instead of
busy-polling with ZwYieldExecution.
"""

from __future__ import annotations

import threading
import time

from mybot.config.delays import DELAY_SLEEP


def bot_sleep(
    delay_ms: int,
    stop_event: threading.Event,
    pause_event: threading.Event | None = None,
) -> bool:
    """Sleep for the specified duration, checking for stop/pause signals.

    This is the core replacement for AutoIt's _Sleep() function.
    Called throughout the bot to yield execution while checking for
    stop/restart conditions.

    Args:
        delay_ms: Milliseconds to sleep.
        stop_event: Event that signals the bot should stop.
            When set, this function returns True immediately.
        pause_event: Optional event that signals the bot is paused.
            When set, this function blocks until it's cleared or stop is signaled.

    Returns:
        True if interrupted (stop requested), False if sleep completed normally.
    """
    if delay_ms <= 0:
        return stop_event.is_set()

    # Check for pause first
    if pause_event is not None and pause_event.is_set():
        # Block until unpaused or stopped
        while pause_event.is_set():
            if stop_event.wait(timeout=0.1):
                return True

    # Sleep in chunks of DELAY_SLEEP ms, checking stop_event between chunks
    remaining_ms = delay_ms
    chunk_ms = min(DELAY_SLEEP, delay_ms)

    while remaining_ms > 0:
        wait_ms = min(chunk_ms, remaining_ms)
        # Event.wait returns True if the event was set (stop requested)
        if stop_event.wait(timeout=wait_ms / 1000.0):
            return True
        remaining_ms -= wait_ms

    return False


def sleep_ms(ms: int) -> None:
    """Simple millisecond sleep without stop checking.

    Replaces AutoIt's _SleepMilli().
    """
    if ms > 0:
        time.sleep(ms / 1000.0)


def sleep_micro(us: int) -> None:
    """Microsecond sleep (best-effort, OS scheduler limited).

    Replaces AutoIt's _SleepMicro() which used ZwDelayExecution.
    Python's time.sleep has ~1ms resolution on Windows.
    """
    if us > 0:
        time.sleep(us / 1_000_000.0)
