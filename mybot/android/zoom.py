"""Zoom control translated from ZoomOut functionality in Android.au3.

Handles zooming out the game view to ensure consistent screenshot coordinates.
The bot requires max zoom-out for correct image template matching.

AutoIt uses multiple zoom methods:
1. ADB pinch gesture (most reliable)
2. Keyboard Ctrl+Minus
3. Ctrl+Mouse wheel
Then verifies by checking for stone/tree templates at known positions.
"""

from __future__ import annotations

import time

from mybot.android.adb import AdbClient, AdbError
from mybot.constants import COLOR_ERROR, GAME_HEIGHT, GAME_WIDTH
from mybot.log import set_debug_log, set_log


def zoom_out(
    adb: AdbClient,
    attempts: int = 5,
    verify: bool = True,
) -> bool:
    """Zoom out the game view to maximum.

    Replaces ZoomOut() from Android.au3.
    Sends pinch-in gestures via ADB to zoom out.

    Args:
        adb: ADB client.
        attempts: Maximum number of zoom-out attempts.
        verify: Whether to verify zoom level after zooming.

    Returns:
        True if zoom-out succeeded (or verification skipped).
    """
    cx = GAME_WIDTH // 2   # 430
    cy = GAME_HEIGHT // 2  # 366

    for attempt in range(attempts):
        set_debug_log(f"ZoomOut attempt {attempt + 1}/{attempts}")

        try:
            # Send pinch-in gesture (two fingers moving toward center)
            # This zooms out in the game
            _send_pinch_in(adb, cx, cy)
            time.sleep(1.0)

            if not verify:
                return True

            # Verification would use image template matching (Phase 3)
            # For now, assume success after gesture
            set_debug_log("ZoomOut: verification deferred to vision system")
            return True

        except AdbError as e:
            set_debug_log(f"ZoomOut failed: {e}")

    set_log("ZoomOut failed after all attempts", COLOR_ERROR)
    return False


def _send_pinch_in(adb: AdbClient, cx: int, cy: int) -> None:
    """Send a pinch-in (zoom out) gesture via ADB.

    Simulates two fingers moving from edges toward center.
    Uses ADB shell input commands.
    """
    # Method 1: Two sequential swipes toward center (simulates pinch)
    offset = 200
    duration = 500

    # Top-left to center
    adb.swipe(cx - offset, cy - offset, cx - 20, cy - 20, duration)
    time.sleep(0.1)
    # Bottom-right to center
    adb.swipe(cx + offset, cy + offset, cx + 20, cy + 20, duration)


def zoom_in(adb: AdbClient) -> None:
    """Zoom in the game view (rarely needed, for testing).

    Sends pinch-out gesture.
    """
    cx = GAME_WIDTH // 2
    cy = GAME_HEIGHT // 2
    offset = 200
    duration = 500

    # Center to top-left
    adb.swipe(cx - 20, cy - 20, cx - offset, cy - offset, duration)
    time.sleep(0.1)
    # Center to bottom-right
    adb.swipe(cx + 20, cy + 20, cx + offset, cy + offset, duration)
