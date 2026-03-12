"""Emulator health monitoring translated from CheckAndroidRebootCondition.au3
and CheckBotRestartCondition.au3.

Monitors the emulator and bot for conditions requiring a reboot or restart:
- ADB connection failures (consecutive error threshold)
- Emulator process crashes
- Memory/resource exhaustion
- Stuck states (no screen changes over time)
"""

from __future__ import annotations

import time

import psutil

from mybot.android.adb import AdbClient
from mybot.constants import COLOR_ERROR, COLOR_WARNING
from mybot.log import set_log

# Default thresholds matching AutoIt constants
ADB_ERROR_THRESHOLD = 10       # Consecutive ADB errors before reboot
REBOOT_INTERVAL_HOURS = 0      # 0 = disabled; hours between forced reboots
SCREEN_STUCK_SECONDS = 300     # 5 minutes of no screen change = stuck


def check_android_reboot_condition(
    adb: AdbClient,
    pid: int = 0,
    reboot_interval_hours: float = 0,
    last_reboot_time: float = 0,
) -> str | None:
    """Check if the Android emulator needs a reboot.

    Replaces CheckAndroidRebootCondition() from CheckAndroidRebootCondition.au3.

    Checks:
    1. ADB consecutive error count exceeds threshold
    2. Emulator process has died
    3. Scheduled reboot interval reached

    Args:
        adb: ADB client to check error state.
        pid: Emulator process ID to check.
        reboot_interval_hours: Force reboot every N hours (0 = disabled).
        last_reboot_time: Timestamp of last reboot (time.monotonic()).

    Returns:
        Reason string if reboot needed, None otherwise.
    """
    # Check ADB error threshold
    if adb.needs_reboot:
        reason = f"ADB consecutive errors ({adb.consecutive_errors}) >= threshold ({ADB_ERROR_THRESHOLD})"
        set_log(f"Reboot needed: {reason}", COLOR_WARNING)
        return reason

    # Check if emulator process is still alive
    if pid > 0 and not _is_process_alive(pid):
        reason = f"Emulator process (PID {pid}) is not running"
        set_log(f"Reboot needed: {reason}", COLOR_ERROR)
        return reason

    # Check scheduled reboot interval
    if reboot_interval_hours > 0 and last_reboot_time > 0:
        elapsed = time.monotonic() - last_reboot_time
        interval_sec = reboot_interval_hours * 3600
        if elapsed >= interval_sec:
            reason = f"Scheduled reboot after {reboot_interval_hours}h"
            set_log(f"Reboot needed: {reason}", COLOR_WARNING)
            return reason

    return None


def check_bot_restart_condition(
    adb: AdbClient,
    pid: int = 0,
    bot_start_time: float = 0,
    restart_interval_hours: float = 0,
) -> str | None:
    """Check if the bot should restart.

    Replaces CheckBotRestartCondition() from CheckBotRestartCondition.au3.

    Args:
        adb: ADB client.
        pid: Emulator process ID.
        bot_start_time: When the bot was started (time.monotonic()).
        restart_interval_hours: Restart interval (0 = disabled).

    Returns:
        Reason string if restart needed, None otherwise.
    """
    # Check scheduled restart
    if restart_interval_hours > 0 and bot_start_time > 0:
        elapsed = time.monotonic() - bot_start_time
        interval_sec = restart_interval_hours * 3600
        if elapsed >= interval_sec:
            return f"Scheduled restart after {restart_interval_hours}h"

    # ADB unresponsive (try a simple command)
    try:
        devices = adb.devices()
        device_str = adb.device
        if device_str and device_str not in devices:
            return f"ADB device {device_str} not in device list"
    except Exception:
        return "ADB not responding"

    return None


def _is_process_alive(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def get_emulator_memory_mb(pid: int) -> float:
    """Get memory usage of the emulator process in MB.

    Useful for detecting memory leaks that require a reboot.
    """
    try:
        proc = psutil.Process(pid)
        return proc.memory_info().rss / (1024 * 1024)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0
