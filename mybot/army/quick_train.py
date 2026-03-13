"""Quick Train mode translated from CreateArmy/QuickTrain.au3.

Uses the game's Quick Train feature to train pre-saved army compositions.

Source: COCBot/functions/CreateArmy/QuickTrain.au3
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.constants import MID_OFFSET_Y
from mybot.log import set_debug_log, set_log


# Quick Train army slot button positions (from QuickTrain.au3)
QUICK_TRAIN_SLOTS = [
    (195, 360 + MID_OFFSET_Y),   # Army 1
    (430, 360 + MID_OFFSET_Y),   # Army 2
    (660, 360 + MID_OFFSET_Y),   # Army 3
]

QUICK_TRAIN_BUTTON = (430, 485 + MID_OFFSET_Y)  # "Train Army" button


def quick_train(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    army_slot: int = 0,
) -> bool:
    """Execute Quick Train for a specific army slot.

    Translated from QuickTrain() in QuickTrain.au3.
    Opens quick train tab, selects the army slot, and clicks Train.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        army_slot: Quick train army slot (0, 1, or 2).

    Returns:
        True if training was initiated.
    """
    if army_slot < 0 or army_slot >= len(QUICK_TRAIN_SLOTS):
        set_log(f"QuickTrain: invalid slot {army_slot}")
        return False

    # Click Quick Train tab
    click_func(710, 14 + MID_OFFSET_Y)
    time.sleep(0.5)

    # Select army slot
    slot_x, slot_y = QUICK_TRAIN_SLOTS[army_slot]
    click_func(slot_x, slot_y)
    time.sleep(0.3)

    # Verify quick train page is visible
    image = capture_func()
    if image is None:
        return False

    # Check if the slot checkbox is selected (green check)
    quick_train_dir = resolve_img_dir("imgxml/Train/QuickTrain")
    if quick_train_dir.is_dir():
        from mybot.vision.matcher import find_image
        result = find_image(image, quick_train_dir, confidence=0.80)
        if result is None:
            set_debug_log("QuickTrain: slot selection not confirmed")

    # Click "Train Army" button
    click_func(QUICK_TRAIN_BUTTON[0], QUICK_TRAIN_BUTTON[1])
    time.sleep(0.5)

    set_log(f"QuickTrain: initiated training for Army {army_slot + 1}")
    return True


def check_quick_train_troop(
    image: np.ndarray,
    army_slot: int = 0,
) -> bool:
    """Check if a quick train army slot has troops configured.

    Translated from CheckQuickTrainTroop() in QuickTrain.au3.
    """
    if army_slot < 0 or army_slot >= len(QUICK_TRAIN_SLOTS):
        return False

    # Check for troop icons in the slot area
    troop_dir = resolve_img_dir("imgxml/Train/QuickTrainTroops")
    if not troop_dir.is_dir():
        return True  # Assume configured if we can't check

    from mybot.vision.matcher import find_image
    sx, sy = QUICK_TRAIN_SLOTS[army_slot]
    result = find_image(
        image, troop_dir,
        search_area=(sx - 90, sy - 60, 180, 120),
        confidence=0.75,
    )
    return result is not None
