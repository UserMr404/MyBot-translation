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


def _is_zoomed_out(adb: AdbClient) -> bool:
    """Verify the game is fully zoomed out using template matching.

    Takes a screenshot and looks for ZoomOut indicator templates.
    If the template is NOT found, we're zoomed out enough.
    If it IS found, we need to zoom out more.

    Falls back to True (assume success) if capture or templates fail.
    """
    try:
        from mybot.android.capture import ScreenCapture
        from mybot.config.image_dirs import resolve as resolve_img_dir
        from mybot.vision.matcher import find_multiple

        capture = ScreenCapture(adb=adb)
        image = capture.capture_full()
        if image is None:
            return True  # Can't verify, assume OK

        zoom_dir = resolve_img_dir("imgxml/other/ZoomOut")
        if not zoom_dir.is_dir():
            return True  # No templates, assume OK

        result = find_multiple(image, zoom_dir, confidence=0.80, max_results=1)
        if result.found:
            set_debug_log("ZoomOut: zoom indicator still visible, need more zoom")
            return False
        return True
    except Exception as e:
        set_debug_log(f"ZoomOut verification error: {e}")
        return True  # Assume OK on error


def zoom_out(
    adb: AdbClient,
    attempts: int = 5,
    verify: bool = True,
) -> bool:
    """Zoom out the game view to maximum.

    Replaces ZoomOut() from Android.au3.
    Sends pinch-in gestures via ADB to zoom out and verifies
    using template matching to check if the zoom indicator is gone.

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
            _send_pinch_in(adb, cx, cy)
            time.sleep(1.0)

            if not verify:
                return True

            if _is_zoomed_out(adb):
                set_debug_log("ZoomOut: verified — fully zoomed out")
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
