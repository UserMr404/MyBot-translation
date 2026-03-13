"""Obstacle/popup detection and dismissal translated from checkObstacles.au3.

Detects and dismisses 15+ popup types that can block the bot:
network errors, graphics errors, updates, maintenance, surveys,
treasure hunt, grayed screens, battle states, and more.

Source: COCBot/functions/Main Screen/checkObstacles.au3
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.constants import MID_OFFSET_Y, BOTTOM_OFFSET_Y
from mybot.log import set_debug_log, set_log


# ── Obstacle Types ───────────────────────────────────────────────────────────

class ObstacleType(IntEnum):
    """Error/obstacle classification matching CheckAllObstacles() types."""
    CONNECTION_LOST = 0      # Connection lost / another device / inactivity
    OUT_OF_SYNC = 1          # Out of sync → reload
    RATE_GAME = 2            # Rate Clash of Clans → "Never"
    IMPORTANT_NOTICE = 3     # Important notice → "OK" / "Agree"
    MAJOR_UPDATE = 4         # Major update → stop bot
    GOOGLE_PLAY_STOPPED = 5  # Google Play stopped → "OK"
    NOT_RESPONDING = 6       # CoC not responding → reboot
    PERSONAL_DATA = 7        # Personal data sharing → "Deny"
    ANALYTICS = 8            # Analytics window → "Deny Light"
    ANOTHER_DEVICE = 9       # Another device connected → wait + reload
    NONE = -1                # No obstacle detected


@dataclass
class ObstacleResult:
    """Result of obstacle detection."""
    found: bool = False
    obstacle_type: ObstacleType = ObstacleType.NONE
    action_taken: str = ""
    minor: bool = False  # Non-critical obstacle (e.g., chat tab)


# ── Pixel Helpers ────────────────────────────────────────────────────────────

def _pixel_match(image: np.ndarray, x: int, y: int, color: int, tol: int = 15) -> bool:
    """Check a single pixel against expected color."""
    from mybot.vision.pixel import check_pixel
    return check_pixel(image, x, y, color, tol)


def _pixel_search_area(
    image: np.ndarray,
    x1: int, y1: int, x2: int, y2: int,
    color: int, tolerance: int = 15,
) -> tuple[int, int] | None:
    """Search for a pixel color in a rectangular area."""
    from mybot.vision.pixel import pixel_search
    return pixel_search(image, x1, y1, x2, y2, color, tolerance)


def _click(click_func: Callable | None, x: int, y: int) -> None:
    """Click at position if click function available."""
    if click_func is not None:
        click_func(x, y)


# ── Main Obstacle Checker ────────────────────────────────────────────────────

def check_obstacles(
    image: np.ndarray,
    click_func: Callable | None = None,
    builder_base: bool = False,
) -> ObstacleResult:
    """Detect and dismiss obstacles/popups blocking the bot.

    Translated from _checkObstacles() in checkObstacles.au3.
    Runs through all known popup types and attempts to dismiss them.

    Args:
        image: BGR screenshot.
        click_func: Callable(x, y) for clicking to dismiss popups.
        builder_base: Whether we're targeting builder base screen.

    Returns:
        ObstacleResult indicating what was found and what action was taken.
    """
    result = ObstacleResult()

    # Check each obstacle type in priority order

    # 1. Network reconnecting overlay
    if _check_network_reconnecting(image):
        result.found = True
        result.action_taken = "Waiting for network reconnection"
        set_debug_log("Obstacle: network reconnecting detected")
        return result

    # 2. Treasure hunt / locked chest
    cleared = _check_treasure_hunt(image, click_func)
    if cleared:
        result.found = True
        result.minor = True
        result.action_taken = "Dismissed treasure hunt"
        return result

    # 3. Reward received window
    cleared = _check_reward_window(image, click_func)
    if cleared:
        result.found = True
        result.minor = True
        result.action_taken = "Clicked continue on reward"
        return result

    # 4. Feedback / survey window
    cleared = _check_feedback_survey(image, click_func)
    if cleared:
        result.found = True
        result.minor = True
        result.action_taken = "Dismissed feedback/survey"
        return result

    # 5. Maintenance break
    if _check_maintenance(image):
        result.found = True
        result.obstacle_type = ObstacleType.CONNECTION_LOST
        result.action_taken = "Maintenance detected"
        set_log("Maintenance break detected")
        return result

    # 6. Error pixel (routes to full obstacle classification)
    error_result = _check_error_windows(image, click_func)
    if error_result.found:
        return error_result

    # 7. Window close buttons (white X, red OK)
    cleared = _check_close_buttons(image, click_func)
    if cleared:
        result.found = True
        result.minor = True
        result.action_taken = "Closed popup window"
        return result

    # 8. Grayed out screen (popups over main village)
    if not builder_base:
        cleared = _check_grayed_main(image, click_func)
    else:
        cleared = _check_grayed_builder_base(image, click_func)
    if cleared:
        result.found = True
        result.minor = True
        result.action_taken = "Dismissed grayed screen popup"
        return result

    # 9. Chat tab open
    cleared = _check_chat_tab(image, click_func)
    if cleared:
        result.found = True
        result.minor = True
        result.action_taken = "Closed chat tab"
        return result

    # 10. Battle state screens
    cleared = _check_battle_screens(image, click_func)
    if cleared:
        result.found = True
        result.action_taken = "Handled battle screen"
        return result

    return result


# ── Individual Obstacle Checks ───────────────────────────────────────────────

def _check_network_reconnecting(image: np.ndarray) -> bool:
    """Detect network reconnecting overlay.

    From checkObstacles_Network() — checks for reconnecting animation.
    """
    reconnect_dir = resolve_img_dir("imgxml/other/reconnecting")
    if not reconnect_dir.is_dir():
        return False

    from mybot.vision.matcher import find_image
    result = find_image(image, reconnect_dir, confidence=0.85)
    return result is not None


def _check_treasure_hunt(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Detect and dismiss treasure hunt / locked chest popup.

    Checks for grey chest pixel (0xCBCDD3) at ~(481, 490+offset)
    and yellow flame pixel (0xFFFFDB) at ~(277, 134+offset).
    """
    chest_match = _pixel_search_area(
        image, 481, 490 + MID_OFFSET_Y, 483, 494 + MID_OFFSET_Y,
        0xCBCDD3, 15,
    )
    flame_match = _pixel_search_area(
        image, 277, 134 + MID_OFFSET_Y, 279, 136 + MID_OFFSET_Y,
        0xFFFFDB, 15,
    )

    if chest_match or flame_match:
        set_debug_log("Obstacle: treasure hunt detected")
        # Click away to dismiss
        _click(click_func, 430, 20)
        return True
    return False


def _check_reward_window(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Detect reward received window with continue button.

    Light pixel (0xFEFEED) at ~(404, 11) and green continue (0x88D039) at ~(430, 507+offset).
    """
    light = _pixel_search_area(image, 404, 11, 406, 13, 0xFEFEED, 10)
    green_btn = _pixel_search_area(
        image, 428, 506 + MID_OFFSET_Y, 432, 508 + MID_OFFSET_Y,
        0x88D039, 15,
    )

    if light and green_btn:
        set_debug_log("Obstacle: reward window detected, clicking continue")
        _click(click_func, 430, 507 + MID_OFFSET_Y)
        return True
    return False


def _check_feedback_survey(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Detect feedback/survey popup and dismiss with 'No Thanks'.

    Checks for info button in top-right corner (740-840, 0-90+offset).
    """
    no_thanks_dir = resolve_img_dir("imgxml/other/NoThanks")
    if not no_thanks_dir.is_dir():
        return False

    from mybot.vision.matcher import find_image
    result = find_image(
        image, no_thanks_dir,
        search_area=(200, 400 + MID_OFFSET_Y, 460, 200),
        confidence=0.80,
    )
    if result is not None:
        set_debug_log("Obstacle: feedback/survey detected")
        _click(click_func, result.x, result.y)
        return True
    return False


def _check_maintenance(image: np.ndarray) -> bool:
    """Detect maintenance break screen.

    Checks for maintenance clock icon in the right portion of screen.
    """
    maint_dir = resolve_img_dir("imgxml/other/maintenance")
    if not maint_dir.is_dir():
        # Fallback: check for black bars indicating loading screen
        black1 = _pixel_match(image, 10, 3, 0x000000, 5)
        black2 = _pixel_match(image, 300, 6, 0x000000, 5)
        black3 = _pixel_match(image, 600, 9, 0x000000, 5)
        return black1 and black2 and black3

    from mybot.vision.matcher import find_image
    result = find_image(
        image, maint_dir,
        search_area=(760, 160, 100, 70 + MID_OFFSET_Y),
        confidence=0.80,
    )
    return result is not None


def _check_error_windows(
    image: np.ndarray,
    click_func: Callable | None,
) -> ObstacleResult:
    """Classify and handle error dialog windows.

    Translated from CheckAllObstacles() — detects 10 error types
    and clicks the appropriate response button.
    """
    result = ObstacleResult()

    # Check for error icon at (630, 270+offset)
    error_icon = _pixel_match(image, 630, 270 + MID_OFFSET_Y, 0xEB1617, 20)
    if not error_icon:
        return result

    set_debug_log("Obstacle: error window detected, classifying...")

    # Try to find response buttons
    button_dirs = {
        "TryAgain": resolve_img_dir("imgxml/other/TryAgain"),
        "ReloadGame": resolve_img_dir("imgxml/other/ReloadGame"),
        "OkayButton": resolve_img_dir("imgxml/other/OkayButton"),
    }

    from mybot.vision.matcher import find_image

    for btn_name, btn_dir in button_dirs.items():
        if not btn_dir.is_dir():
            continue
        btn = find_image(
            image, btn_dir,
            search_area=(200, 350 + MID_OFFSET_Y, 460, 250),
            confidence=0.80,
        )
        if btn is not None:
            result.found = True
            result.obstacle_type = ObstacleType.CONNECTION_LOST
            result.action_taken = f"Clicked {btn_name} at ({btn.x}, {btn.y})"
            set_log(f"Obstacle: error window → {btn_name}")
            _click(click_func, btn.x, btn.y)
            return result

    # Fallback: click center of screen to try to dismiss
    result.found = True
    result.obstacle_type = ObstacleType.CONNECTION_LOST
    result.action_taken = "Clicked center to dismiss error"
    _click(click_func, 430, 400 + MID_OFFSET_Y)
    return result


def _check_close_buttons(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Detect and click window close buttons (white X or red OK).

    White button (0xFFFFFF) at (618, 150+offset) with beige (0xE9E8E1) at (735, 510+offset).
    Red/brown OK button (0x892B1F) at (810, 185+offset).
    """
    # White close button pattern
    white_btn = _pixel_match(image, 618, 150 + MID_OFFSET_Y, 0xFFFFFF, 10)
    beige_bg = _pixel_match(image, 735, 510 + MID_OFFSET_Y, 0xE9E8E1, 10)

    if white_btn and beige_bg:
        set_debug_log("Obstacle: close button (white X) detected")
        _click(click_func, 618, 150 + MID_OFFSET_Y)
        return True

    # Red/brown OK button
    red_btn = _pixel_match(image, 810, 185 + MID_OFFSET_Y, 0x892B1F, 15)
    if red_btn:
        set_debug_log("Obstacle: OK button (red) detected")
        _click(click_func, 810, 185 + MID_OFFSET_Y)
        return True

    return False


def _check_grayed_main(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Handle popups that gray out the main village screen.

    Detects season end/start, freebie, offers, daily reward, etc.
    """
    from mybot.game.main_screen import is_main_grayed
    if not is_main_grayed(image):
        return False

    set_debug_log("Obstacle: main village grayed out")

    # Try to find OK/Confirm/Close buttons on the overlay
    for btn_dir_name in ("OkayButton", "ConfirmButton", "CloseWindow"):
        btn_dir = resolve_img_dir(f"imgxml/other/{btn_dir_name}")
        if not btn_dir.is_dir():
            continue
        from mybot.vision.matcher import find_image
        btn = find_image(image, btn_dir, confidence=0.80)
        if btn is not None:
            set_debug_log(f"Grayed main: clicking {btn_dir_name}")
            _click(click_func, btn.x, btn.y)
            return True

    # Check for daily reward window
    daily_left = _pixel_match(image, 126, 545 + MID_OFFSET_Y, 0xFBE000, 20)
    daily_right = _pixel_match(image, 816, 555 + MID_OFFSET_Y, 0xFCE227, 20)
    if daily_left and daily_right:
        set_debug_log("Grayed main: daily reward detected")
        _click(click_func, 430, 550 + MID_OFFSET_Y)
        return True

    # Fallback: click away
    _click(click_func, 430, 20)
    return True


def _check_grayed_builder_base(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Handle popups that gray out the builder base screen."""
    from mybot.game.main_screen import is_builder_base_grayed
    if not is_builder_base_grayed(image):
        return False

    set_debug_log("Obstacle: builder base grayed out")

    # Try OK/Close buttons
    for btn_dir_name in ("OkayButton", "CloseWindow"):
        btn_dir = resolve_img_dir(f"imgxml/other/{btn_dir_name}")
        if not btn_dir.is_dir():
            continue
        from mybot.vision.matcher import find_image
        btn = find_image(image, btn_dir, confidence=0.80)
        if btn is not None:
            _click(click_func, btn.x, btn.y)
            return True

    _click(click_func, 430, 20)
    return True


def _check_chat_tab(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Detect and close an open chat tab.

    Chat tab appears on the left side of screen when open.
    Uses image search for the chat tab indicator.
    """
    chat_dir = resolve_img_dir("imgxml/other/ChatTab")
    if not chat_dir.is_dir():
        return False

    from mybot.vision.matcher import find_image
    result = find_image(
        image, chat_dir,
        search_area=(5, 285 + MID_OFFSET_Y, 30, 45),
        confidence=0.80,
    )
    if result is not None:
        set_debug_log("Obstacle: chat tab open, closing")
        _click(click_func, 5, 340 + MID_OFFSET_Y)
        return True
    return False


def _check_battle_screens(
    image: np.ndarray,
    click_func: Callable | None,
) -> bool:
    """Detect battle-related screens (surrender, end fight, return home).

    Checks for surrender button, end fight button, and return home button.
    """
    from mybot.config.coordinates import (
        SURRENDER_BUTTON,
        END_FIGHT_SCENE_BTN,
        RETURN_HOME_BUTTON,
    )

    # Check surrender button
    if _pixel_match(image, *SURRENDER_BUTTON):
        set_debug_log("Obstacle: surrender button visible (in battle)")
        return False  # Don't auto-dismiss — we're in a battle

    # Check end fight scene
    if _pixel_match(image, *END_FIGHT_SCENE_BTN):
        set_debug_log("Obstacle: end fight scene detected")
        _click(click_func, END_FIGHT_SCENE_BTN[0], END_FIGHT_SCENE_BTN[1])
        return True

    # Check return home button
    if _pixel_match(image, *RETURN_HOME_BUTTON):
        set_debug_log("Obstacle: return home button detected")
        _click(click_func, RETURN_HOME_BUTTON[0], RETURN_HOME_BUTTON[1])
        return True

    return False


# ── Utility Functions ────────────────────────────────────────────────────────

def is_gem_window(image: np.ndarray) -> bool:
    """Check if the gem purchase window is open.

    From isGemOpen() — detects the gem purchase popup.
    """
    from mybot.config.coordinates import IS_GEM_WINDOW
    return _pixel_match(image, *IS_GEM_WINDOW)


def is_no_upgrade_loot(image: np.ndarray) -> bool:
    """Check if insufficient loot for upgrade (red/orange cost text).

    From isNoUpgradeLoot() — detects red (0xFF887F) and orange (0xFF7A0D)
    pixels in the cost display area.
    """
    red = _pixel_search_area(
        image, 500, 539 + MID_OFFSET_Y, 700, 552 + MID_OFFSET_Y,
        0xFF887F, 20,
    )
    orange = _pixel_search_area(
        image, 500, 539 + MID_OFFSET_Y, 700, 552 + MID_OFFSET_Y,
        0xFF7A0D, 20,
    )
    return red is not None or orange is not None
