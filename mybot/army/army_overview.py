"""Army overview navigation translated from CreateArmy/openArmyOverview.au3.

Opens the army overview tab and navigates between sub-tabs
(troops, spells, sieges, heroes, clan castle).

Source: COCBot/functions/CreateArmy/openArmyOverview.au3
"""

from __future__ import annotations

import time
from enum import IntEnum
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.config.coordinates import IS_TRAIN_PAGE
from mybot.constants import MID_OFFSET_Y
from mybot.log import set_debug_log, set_log
from mybot.vision.pixel import check_pixel


class ArmyTab(IntEnum):
    """Army overview sub-tabs."""
    TROOPS = 0
    SPELLS = 1
    SIEGE = 2
    HEROES = 3


# Tab button X positions (approximate, from openArmyOverview.au3)
_TAB_POSITIONS = {
    ArmyTab.TROOPS: (260, 14 + MID_OFFSET_Y),
    ArmyTab.SPELLS: (370, 14 + MID_OFFSET_Y),
    ArmyTab.SIEGE: (480, 14 + MID_OFFSET_Y),
    ArmyTab.HEROES: (590, 14 + MID_OFFSET_Y),
}


def open_army_overview(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
    max_retries: int = 10,
) -> bool:
    """Open the army overview window.

    Translated from OpenArmyOverview() in openArmyOverview.au3.
    Clicks the army button on main screen and waits for the
    army overview page to appear.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking UI elements.
        max_retries: Maximum attempts.

    Returns:
        True if army overview opened successfully.
    """
    # Click army camp button (bottom bar)
    if click_func:
        click_func(295, 592 + MID_OFFSET_Y)

    for attempt in range(max_retries):
        time.sleep(0.5)
        image = capture_func()
        if image is None:
            continue

        if is_army_overview_open(image):
            set_debug_log(f"Army overview opened (attempt {attempt + 1})")
            return True

    set_log("Failed to open army overview")
    return False


def is_army_overview_open(image: np.ndarray) -> bool:
    """Check if the army overview page is currently visible.

    Uses the IS_TRAIN_PAGE pixel check.
    """
    return check_pixel(image, *IS_TRAIN_PAGE)


def switch_army_tab(
    tab: ArmyTab,
    click_func: Callable[[int, int], None] | None = None,
) -> None:
    """Switch to a specific army overview sub-tab.

    Args:
        tab: Target tab.
        click_func: For clicking.
    """
    pos = _TAB_POSITIONS.get(tab)
    if pos and click_func:
        click_func(pos[0], pos[1])
        time.sleep(0.3)


def close_army_overview(
    click_func: Callable[[int, int], None] | None = None,
) -> None:
    """Close the army overview window.

    Clicks the close button (X) in the top-right.
    """
    if click_func:
        click_func(815, 146 + MID_OFFSET_Y)
