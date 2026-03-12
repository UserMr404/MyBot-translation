"""Tests for the sleep/control flow system."""

import threading
import time

from mybot.utils.sleep import bot_sleep, sleep_ms


def test_bot_sleep_normal(stop_event: threading.Event):
    """Normal sleep completes and returns False."""
    start = time.perf_counter()
    result = bot_sleep(100, stop_event)
    elapsed = (time.perf_counter() - start) * 1000
    assert result is False
    assert elapsed >= 80  # Allow some tolerance


def test_bot_sleep_interrupted(stop_event: threading.Event):
    """Sleep returns True when stop event is set."""
    # Set stop event after 50ms
    def set_stop():
        time.sleep(0.05)
        stop_event.set()

    threading.Thread(target=set_stop, daemon=True).start()

    start = time.perf_counter()
    result = bot_sleep(5000, stop_event)  # Request 5s sleep
    elapsed = (time.perf_counter() - start) * 1000

    assert result is True
    assert elapsed < 500  # Should return much faster than 5s


def test_bot_sleep_zero(stop_event: threading.Event):
    """Zero delay returns immediately."""
    result = bot_sleep(0, stop_event)
    assert result is False


def test_bot_sleep_already_stopped():
    """Returns True immediately if stop event already set."""
    stop_event = threading.Event()
    stop_event.set()
    result = bot_sleep(1000, stop_event)
    assert result is True


def test_sleep_ms():
    """Simple millisecond sleep works."""
    start = time.perf_counter()
    sleep_ms(50)
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed >= 40
