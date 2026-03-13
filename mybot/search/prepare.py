"""Search preparation translated from Search/PrepareSearch.au3.

Sets up the search state, opens the attack screen, and handles
pre-search configuration like zoom level and army verification.

Source: COCBot/functions/Search/PrepareSearch.au3
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from mybot.config.coordinates import ATTACK_BUTTON, FIND_MATCH_BUTTON, IS_ATTACK_SHIELD
from mybot.log import set_debug_log, set_log
from mybot.vision.pixel import check_pixel


@dataclass
class PrepareResult:
    """Result of search preparation."""
    ready: bool = False
    error: str = ""


def prepare_search(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
) -> PrepareResult:
    """Prepare for village searching.

    Translated from PrepareSearch() in PrepareSearch.au3.
    Navigates from main screen to attack search screen.

    Steps:
    1. Click the Attack button on main screen
    2. Wait for attack shield/confirmation screen
    3. Click "Find a Match" button
    4. Wait for search to begin (clouds)

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking UI elements.

    Returns:
        PrepareResult indicating readiness.
    """
    result = PrepareResult()

    # Step 1: Click Attack button
    if click_func:
        set_debug_log("PrepareSearch: clicking Attack button")
        click_func(ATTACK_BUTTON[0], ATTACK_BUTTON[1])

    # Step 2: Verify attack shield screen appeared
    import time
    for _ in range(10):
        time.sleep(1.0)
        image = capture_func()
        if image is None:
            continue
        if check_pixel(image, *IS_ATTACK_SHIELD):
            set_debug_log("PrepareSearch: attack shield screen confirmed")
            break
    else:
        result.error = "Attack shield screen not found"
        set_log(result.error)
        return result

    # Step 3: Click "Find a Match"
    if click_func:
        set_debug_log("PrepareSearch: clicking Find a Match")
        click_func(FIND_MATCH_BUTTON[0], FIND_MATCH_BUTTON[1])

    result.ready = True
    return result


def is_search_active(image: np.ndarray) -> bool:
    """Check if village search is currently active (in clouds).

    The search screen has a distinct layout with resource display
    and Next/Attack buttons.

    Args:
        image: BGR screenshot.

    Returns:
        True if currently in search mode.
    """
    # During search, the "Next" button area has a characteristic pattern
    # Check for the resource display area at top-left (search loot panel)
    from mybot.vision.pixel import pixel_search
    # Gold icon area during search at approximately (10, 70) to (45, 90)
    gold_icon = pixel_search(image, 10, 70, 45, 90, 0xFFD700, 30)
    return gold_icon is not None
