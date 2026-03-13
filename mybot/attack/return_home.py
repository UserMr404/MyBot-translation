"""Return home after battle translated from Attack/ReturnHome.au3.

Handles end-of-battle sequence: clicking end battle, collecting stars,
and returning to the main village screen.

Source: COCBot/functions/Attack/ReturnHome.au3
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np

from mybot.config.coordinates import (
    END_FIGHT_SCENE_BTN,
    RETURN_HOME_BUTTON,
    REWARD_BUTTON,
    SURRENDER_BUTTON,
)
from mybot.log import set_debug_log, set_log
from mybot.vision.pixel import check_pixel


@dataclass
class BattleEndResult:
    """Result of ending a battle."""
    returned_home: bool = False
    stars: int = 0
    gold_looted: int = 0
    elixir_looted: int = 0
    dark_looted: int = 0
    trophies_change: int = 0


def return_home(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    max_wait: float = 120.0,
) -> BattleEndResult:
    """End battle and return to main village.

    Translated from ReturnHome() in ReturnHome.au3.

    Flow:
    1. Wait for battle to end (or click surrender)
    2. Click through end battle screens
    3. Click "Return Home" button
    4. Wait for main screen

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        max_wait: Max seconds to wait for battle end.

    Returns:
        BattleEndResult with loot summary.
    """
    result = BattleEndResult()
    start = time.time()

    while time.time() - start < max_wait:
        image = capture_func()
        if image is None:
            time.sleep(1.0)
            continue

        # Check for end fight scene button
        if check_pixel(image, *END_FIGHT_SCENE_BTN):
            set_debug_log("ReturnHome: end fight scene detected")
            click_func(END_FIGHT_SCENE_BTN[0], END_FIGHT_SCENE_BTN[1])
            time.sleep(1.0)
            continue

        # Check for return home button
        if check_pixel(image, *RETURN_HOME_BUTTON):
            set_debug_log("ReturnHome: return home button found")
            # Read battle results before clicking
            result = _read_battle_results(image, result)
            click_func(RETURN_HOME_BUTTON[0], RETURN_HOME_BUTTON[1])
            time.sleep(2.0)
            result.returned_home = True
            set_log(
                f"Battle ended: {result.stars}★ "
                f"G={result.gold_looted:,} E={result.elixir_looted:,} "
                f"DE={result.dark_looted:,} T={result.trophies_change:+d}"
            )
            return result

        # Check for reward button
        if check_pixel(image, *REWARD_BUTTON):
            click_func(REWARD_BUTTON[0], REWARD_BUTTON[1])
            time.sleep(1.0)
            continue

        # Still in battle
        time.sleep(2.0)

    set_log("ReturnHome: timed out waiting for battle end")
    return result


def surrender(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
) -> bool:
    """Surrender the current battle.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.

    Returns:
        True if surrender was clicked.
    """
    image = capture_func()
    if image is None:
        return False

    if check_pixel(image, *SURRENDER_BUTTON):
        click_func(SURRENDER_BUTTON[0], SURRENDER_BUTTON[1])
        set_log("Battle surrendered")
        return True

    return False


def _read_battle_results(
    image: np.ndarray,
    result: BattleEndResult,
) -> BattleEndResult:
    """Read loot/stars from the end battle screen."""
    from mybot.vision.ocr import read_number

    # Star count — check for star images in the results area
    # Loot amounts at standard positions on the results screen
    result.gold_looted = read_number(image, 135, 305, 120, 20)
    result.elixir_looted = read_number(image, 135, 340, 120, 20)
    result.dark_looted = read_number(image, 135, 375, 120, 20)
    result.trophies_change = read_number(image, 135, 410, 80, 20)

    return result
