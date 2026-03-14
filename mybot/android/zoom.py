"""Zoom control translated from ZoomOut.au3 and Android.au3.

Handles zooming out the game view to ensure consistent screenshot coordinates.
The bot requires max zoom-out for correct image template matching.

AutoIt's ZoomOut strategy:
1. BlueStacks5: sends DOWN arrow key (KEYCODE_DPAD_DOWN = 20)
2. MEmu: sends F3 key
3. Nox: sends Ctrl+MouseWheel
4. All: fallback to AndroidZoomOut() which uses minitouch multi-touch pinch scripts
5. Verification: GetVillageSize() finds stone+tree templates and measures village size

Timing from AutoIt:
- DELAYZOOMOUT1 = 1500ms — initial delay before zooming
- DELAYZOOMOUT2 = 200ms  — delay between zoom key presses
- DELAYZOOMOUT3 = 1000ms — extra delay after 20+ retries
- 1000ms sleep between SearchZoomOut verification retries
- Up to 80 total attempts before giving up
"""

from __future__ import annotations

import random
import time

from mybot.android.adb import AdbClient, AdbError
from mybot.constants import COLOR_ERROR, COLOR_INFO, GAME_HEIGHT, GAME_WIDTH
from mybot.log import set_debug_log, set_log

# ADB keycodes
KEYCODE_DPAD_DOWN = 20

# Timing constants matching AutoIt's DelayTimes.au3
_DELAY_INITIAL = 1.5       # DELAYZOOMOUT1: before first zoom
_DELAY_BETWEEN = 0.2       # DELAYZOOMOUT2: between key presses
_DELAY_SLOW = 1.0          # DELAYZOOMOUT3: after 20+ retries
_DELAY_VERIFY = 1.0        # between verification captures
_SLOW_THRESHOLD = 20       # switch to slower delays after this many attempts
_MAX_ATTEMPTS = 80         # give up after this many


def _is_zoomed_out(adb: AdbClient) -> bool | None:
    """Verify the game is fully zoomed out using template matching.

    Checks for ZoomOut indicator templates. If the indicator is NOT found,
    we're zoomed out enough. If found, need to zoom more.

    Returns:
        True if confirmed zoomed out, False if not zoomed out,
        None if verification is not possible (no templates/capture failure).
    """
    try:
        from mybot.android.capture import ScreenCapture
        from mybot.config.image_dirs import resolve as resolve_img_dir
        from mybot.vision.matcher import find_multiple

        capture = ScreenCapture(adb=adb)
        image = capture.capture_full()
        if image is None:
            return None  # Can't verify

        zoom_dir = resolve_img_dir("imgxml/zoomout")
        if not zoom_dir.is_dir():
            set_debug_log(f"ZoomOut: template dir not found: {zoom_dir}")
            return None  # No templates, can't verify

        result = find_multiple(image, zoom_dir, confidence=0.80, max_results=1)
        # Templates detect "not zoomed out" state. If found → need more zoom.
        # If NOT found → we're zoomed out enough.
        if result.found:
            set_debug_log("ZoomOut: zoom indicator still visible, need more zoom")
            return False
        return True
    except Exception as e:
        set_debug_log(f"ZoomOut: verification error: {e}")
        return None  # Can't verify on error


def zoom_out(
    adb: AdbClient,
    emulator: str = "BlueStacks5",
    max_attempts: int = _MAX_ATTEMPTS,
    verify: bool = True,
) -> bool:
    """Zoom out the game view to maximum.

    Translated from ZoomOut() / DefaultZoomOut() / ZoomOutBlueStacks5() in
    ZoomOut.au3.

    Strategy:
    1. First try ADB-based zoom (AndroidZoomOut equivalent)
    2. Then send emulator-specific key presses with proper delays
    3. Verify with village size measurement between attempts

    Args:
        adb: ADB client.
        emulator: Emulator name ("BlueStacks5", "MEmu", "Nox").
        max_attempts: Maximum zoom attempts.
        verify: Whether to verify zoom level.

    Returns:
        True if zoom-out succeeded (or verification skipped).
    """
    set_log("Zooming Out", COLOR_INFO)

    # Initial delay before zooming (DELAYZOOMOUT1 = 1500ms)
    time.sleep(_DELAY_INITIAL)

    # First attempt: try ADB pinch zoom
    try:
        _android_zoom_out(adb)
        time.sleep(_DELAY_VERIFY)
        if verify:
            status = _is_zoomed_out(adb)
            if status is True:
                set_debug_log("ZoomOut: verified after initial ADB zoom")
                return True
            # status is None (can't verify) or False — continue with key presses
    except AdbError as e:
        set_debug_log(f"ZoomOut: ADB zoom failed: {e}, falling back to key method")

    # Minimum key presses before trusting unverified result
    min_presses = 15
    can_verify: bool | None = True  # None once we know templates are absent

    for attempt in range(max_attempts):
        try:
            _send_zoom_key(adb, emulator)
        except AdbError as e:
            set_debug_log(f"ZoomOut: key press failed: {e}")

        # Delay between attempts (matches AutoIt timing)
        if attempt >= _SLOW_THRESHOLD:
            time.sleep(_DELAY_SLOW)
        else:
            time.sleep(_DELAY_BETWEEN)

        # Verify after each press (like AutoIt's SearchZoomOut on every iteration)
        if verify and can_verify is not None:
            time.sleep(_DELAY_VERIFY)
            status = _is_zoomed_out(adb)
            if status is True:
                set_debug_log(
                    f"ZoomOut: verified after {attempt + 1} key presses"
                )
                return True
            if status is None:
                # Templates unavailable — stop trying to verify
                can_verify = None
                set_debug_log("ZoomOut: no templates, switching to unverified mode")

        # If we can't verify, fall back to minimum press count
        if (not verify or can_verify is None) and attempt >= min_presses:
            set_debug_log(
                f"ZoomOut: completed {attempt + 1} key presses (unverified)"
            )
            return True

    set_log("ZoomOut failed after all attempts", COLOR_ERROR)
    return False


def _send_zoom_key(adb: AdbClient, emulator: str) -> None:
    """Send the emulator-appropriate zoom-out key press.

    BlueStacks5: DOWN arrow key (KEYCODE_DPAD_DOWN = 20)
    MEmu: F3 key (not available via keyevent, use shell command)
    Nox: DOWN arrow key as fallback
    """
    # All emulators support DOWN arrow for zoom-out
    adb.key_event(KEYCODE_DPAD_DOWN)


def _android_zoom_out(adb: AdbClient) -> None:
    """Send ADB-based zoom-out gesture.

    Translated from AndroidZoomOut() in Android.au3.
    Uses 'input swipe' to simulate a pinch-in (zoom out) gesture.
    Sends two converging swipes from edges toward center.

    The AutoIt version uses minitouch scripts with pre-recorded
    multi-touch coordinates. This Python version uses the simpler
    'input swipe' approach which works on most emulators.
    """
    cx = GAME_WIDTH // 2   # 430
    cy = GAME_HEIGHT // 2  # 366
    offset = 200
    duration = 300  # ms

    # Randomize slightly like AutoIt's Normal0-6 scripts
    offset += random.randint(-20, 20)

    # Top-left to center
    adb.swipe(cx - offset, cy - offset, cx - 20, cy - 20, duration)
    time.sleep(0.05)
    # Bottom-right to center
    adb.swipe(cx + offset, cy + offset, cx + 20, cy + 20, duration)


def zoom_in(adb: AdbClient) -> None:
    """Zoom in the game view (rarely needed, for testing).

    Sends UP arrow key.
    """
    adb.key_event(19)  # KEYCODE_DPAD_UP
