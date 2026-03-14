"""Main screen detection translated from Main Screen/checkMainScreen.au3.

Verifies the bot is on the game's main village screen and provides
recovery logic when the game drifts to other screens.

Source files:
- Main Screen/checkMainScreen.au3 — checkMainScreen(), _checkMainScreenImage()
- Main Screen/waitMainScreen.au3 — waitMainScreen(), waitMainScreenMini()
- Main Screen/isOnBuilderBase.au3 — isOnBuilderBase(), isOnMainVillage()
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import numpy as np

from mybot.config.coordinates import (
    IS_MAIN,
    IS_ON_BUILDER_BASE,
)
from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.constants import COLOR_WARNING, MID_OFFSET_Y
from mybot.log import set_debug_log, set_log


# ── Pixel Check Helpers ──────────────────────────────────────────────────────

def _check_pixel_tuple(
    image: np.ndarray,
    pixel: tuple[int, int, int, int],
) -> bool:
    """Check a single pixel against expected color with tolerance.

    Args:
        image: BGR screenshot.
        pixel: (x, y, expected_color_0xRRGGBB, tolerance).

    Returns:
        True if the pixel matches within tolerance.
    """
    from mybot.vision.pixel import check_pixel
    x, y, color, tol = pixel
    return check_pixel(image, x, y, color, tol)


# ── Main Screen Detection ────────────────────────────────────────────────────

def is_main_screen(
    image: np.ndarray,
    builder_base: bool = False,
) -> bool:
    """Check if the game is on the main village (or builder base) screen.

    Translated from _checkMainScreenImage() in checkMainScreen.au3.
    Combines pixel check with chat tab verification and network error absence.

    Args:
        image: BGR screenshot.
        builder_base: If True, check for builder base instead of main village.

    Returns:
        True if on the expected main screen.
    """
    pixel = IS_ON_BUILDER_BASE if builder_base else IS_MAIN

    if not _check_pixel_tuple(image, pixel):
        # Log the actual pixel color for debugging when the check fails
        from mybot.vision.pixel import get_pixel_color
        x, y, expected, tol = pixel
        actual = get_pixel_color(image, x, y)
        set_debug_log(
            f"Main screen pixel mismatch at ({x},{y}): "
            f"expected 0x{expected:06X} (tol={tol}), got 0x{actual:06X}"
        )
        return False

    # Additional verification: check for network reconnecting overlay
    if check_network_error(image):
        return False

    return True


def check_network_error(image: np.ndarray) -> bool:
    """Detect the 'Reconnecting' network error overlay.

    Translated from checkObstacles_Network() in checkObstacles.au3.
    The reconnecting animation shows a loading spinner.

    Args:
        image: BGR screenshot.

    Returns:
        True if a network error/reconnecting overlay is detected.
    """
    from mybot.vision.matcher import find_image
    # Check for reconnecting image template
    reconnect_dir = resolve_img_dir("imgxml/other/reconnecting")
    if not reconnect_dir.is_dir():
        return False

    result = find_image(image, reconnect_dir, confidence=0.85)
    return result is not None


def check_main_screen(
    capture_func,
    click_func=None,
    builder_base: bool = False,
    max_retries: int = 24,
    android_restart_threshold: int = 20,
    delay: float = 2.0,
    stop_event: threading.Event | None = None,
) -> bool:
    """Verify we're on the main screen, retrying with obstacle checks.

    Translated from checkMainScreen() in checkMainScreen.au3.
    Loops up to max_retries times, checking for obstacles each iteration.

    Args:
        capture_func: Callable returning BGR screenshot (np.ndarray).
        click_func: Optional callable for clicking away obstacles.
        builder_base: Check for builder base screen.
        max_retries: Maximum retry attempts (default 24).
        android_restart_threshold: After this many failures, restart Android.
        delay: Seconds between retry attempts.
        stop_event: Optional threading event to interrupt waiting (for stop button).

    Returns:
        True if main screen confirmed, False if recovery failed or stopped.
    """
    from mybot.game.obstacles import check_obstacles

    for attempt in range(max_retries):
        if stop_event and stop_event.is_set():
            set_log("Main screen check interrupted by stop")
            return False

        image = capture_func()
        if image is None:
            if stop_event:
                stop_event.wait(timeout=delay)
            else:
                time.sleep(delay)
            continue

        if is_main_screen(image, builder_base=builder_base):
            if attempt > 0:
                set_log(f"Main screen confirmed after {attempt + 1} attempts")
            return True

        # Try to clear obstacles
        obstacle_cleared = check_obstacles(image, click_func, builder_base=builder_base)

        if attempt >= android_restart_threshold:
            set_log(f"Main screen not found after {attempt + 1} attempts, Android restart needed")
            return False

        if not obstacle_cleared:
            set_debug_log(f"Main screen check {attempt + 1}/{max_retries}: not found")

        if stop_event:
            stop_event.wait(timeout=delay)
        else:
            time.sleep(delay)

    set_log("Main screen not found after all retries, restart required")
    return False


def wait_main_screen(
    capture_func,
    click_func=None,
    builder_base: bool = False,
    max_wait: float = 210.0,
    check_interval: float = 2.0,
    stop_event: threading.Event | None = None,
) -> bool:
    """Wait for the main screen to load.

    Translated from waitMainScreen() in waitMainScreen.au3.
    Waits up to ~3.5 minutes (105 iterations × 2s) for the main screen.

    Args:
        capture_func: Callable returning BGR screenshot.
        click_func: Optional callable for clicking.
        builder_base: Wait for builder base screen.
        max_wait: Maximum total wait time in seconds.
        check_interval: Seconds between checks.
        stop_event: Optional threading event to interrupt waiting (for stop button).

    Returns:
        True if main screen appeared within timeout.
    """
    from mybot.game.obstacles import check_obstacles

    start = time.time()
    attempts = 0
    last_progress_log = 0.0

    while time.time() - start < max_wait:
        if stop_event and stop_event.is_set():
            set_log("Main screen wait interrupted by stop")
            return False

        attempts += 1
        image = capture_func()

        if image is not None and is_main_screen(image, builder_base=builder_base):
            elapsed = time.time() - start
            set_debug_log(f"Main screen loaded in {elapsed:.1f}s ({attempts} checks)")
            return True

        # Periodically check obstacles
        if image is not None and attempts % 5 == 0:
            check_obstacles(image, click_func, builder_base=builder_base)

        # Log progress every 30 seconds so it doesn't appear stuck
        elapsed = time.time() - start
        if elapsed - last_progress_log >= 30.0:
            set_log(
                f"Still waiting for main screen... "
                f"({elapsed:.0f}s / {max_wait:.0f}s, {attempts} checks)",
                COLOR_WARNING,
            )
            last_progress_log = elapsed

        if stop_event:
            stop_event.wait(timeout=check_interval)
        else:
            time.sleep(check_interval)

    elapsed = time.time() - start
    set_log(f"Main screen not found after {elapsed:.1f}s ({attempts} checks)")
    return False


# ── Builder Base Detection ────────────────────────────────────────────────────

def is_on_builder_base(
    image: np.ndarray,
    bb_template_dir: Path | None = None,
) -> bool:
    """Check if currently on the Builder Base.

    Translated from isOnBuilderBase() in isOnBuilderBase.au3.
    Uses image template search in the top area of the screen.

    Args:
        image: BGR screenshot.
        bb_template_dir: Path to builder base indicator templates.

    Returns:
        True if on Builder Base.
    """
    if bb_template_dir is None:
        bb_template_dir = resolve_img_dir("imgxml/other/IsOnBB")

    if not bb_template_dir.is_dir():
        # Fallback to pixel check
        return _check_pixel_tuple(image, IS_ON_BUILDER_BASE)

    from mybot.vision.matcher import find_image
    # Search in top portion of screen (445, 0) to (500, 54)
    result = find_image(
        image,
        bb_template_dir,
        search_area=(445, 0, 55, 54),
        confidence=0.85,
    )
    return result is not None


def is_on_main_village(
    image: np.ndarray,
    mv_template_dir: Path | None = None,
) -> bool:
    """Check if currently on the Main Village.

    Translated from isOnMainVillage() in isOnBuilderBase.au3.

    Args:
        image: BGR screenshot.
        mv_template_dir: Path to main village indicator templates.

    Returns:
        True if on Main Village.
    """
    if mv_template_dir is None:
        mv_template_dir = resolve_img_dir("imgxml/other/IsOnMainVillage")

    if not mv_template_dir.is_dir():
        return _check_pixel_tuple(image, IS_MAIN)

    from mybot.vision.matcher import find_image
    # Search in top portion of screen (360, 0) to (450, 60)
    result = find_image(
        image,
        mv_template_dir,
        search_area=(360, 0, 90, 60),
        confidence=0.85,
    )
    return result is not None


# ── Screen State Queries ─────────────────────────────────────────────────────

def is_main_grayed(image: np.ndarray) -> bool:
    """Detect if the main village screen is grayed out (popup overlay).

    Translated from IsMainGrayed() in checkObstacles.au3.
    Checks pixel colors at the top bar to detect a gray overlay.

    Args:
        image: BGR screenshot.

    Returns:
        True if main screen appears grayed out.
    """
    from mybot.vision.pixel import get_pixel_color, color_check

    # Three pixel positions to check for gray overlay
    # Original: positions at (370-390, 7-9) checking for desaturated colors
    gray_checks = [
        (378, 7),
        (380, 8),
        (390, 9),
    ]

    for x, y in gray_checks:
        color = get_pixel_color(image, x, y)
        if color is None:
            continue
        # Gray means R, G, B are close together and darkened
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        # Check if desaturated (channels within 30 of each other) and dim
        spread = max(r, g, b) - min(r, g, b)
        avg = (r + g + b) // 3
        if spread < 30 and 40 < avg < 160:
            return True

    return False


def is_builder_base_grayed(image: np.ndarray) -> bool:
    """Detect if the builder base screen is grayed out.

    Translated from IsBuilderBaseGrayed() in checkObstacles.au3.

    Args:
        image: BGR screenshot.

    Returns:
        True if builder base appears grayed out.
    """
    from mybot.vision.pixel import get_pixel_color

    gray_checks = [
        (440, 7),
        (450, 8),
        (465, 9),
    ]

    for x, y in gray_checks:
        color = get_pixel_color(image, x, y)
        if color is None:
            continue
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        spread = max(r, g, b) - min(r, g, b)
        avg = (r + g + b) // 3
        if spread < 30 and 40 < avg < 160:
            return True

    return False
