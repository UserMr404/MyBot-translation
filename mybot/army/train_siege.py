"""Siege machine training translated from CreateArmy/TrainSiege.au3.

Handles training of siege machines (Wall Wrecker, Battle Blimp, etc.).

Source: COCBot/functions/CreateArmy/TrainSiege.au3
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.army.army_overview import ArmyTab, switch_army_tab
from mybot.army.train_it import train_it
from mybot.constants import SIEGE_SHORT_NAMES
from mybot.enums import Siege
from mybot.log import set_debug_log, set_log


def train_siege(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    siege_config: list[int] | None = None,
) -> bool:
    """Train siege machines.

    Translated from TrainSiege() in TrainSiege.au3.
    Switches to the siege tab and trains each configured siege machine.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        siege_config: List of quantities per siege type (indexed by Siege enum).

    Returns:
        True if training was performed.
    """
    if siege_config is None:
        return False

    any_needed = any(q > 0 for q in siege_config)
    if not any_needed:
        return False

    # Switch to siege tab
    switch_army_tab(ArmyTab.SIEGE, click_func)
    time.sleep(0.5)

    trained = False
    for siege_idx in range(min(len(siege_config), Siege.COUNT)):
        count = siege_config[siege_idx]
        if count <= 0:
            continue

        name = SIEGE_SHORT_NAMES[siege_idx] if siege_idx < len(SIEGE_SHORT_NAMES) else f"Siege{siege_idx}"
        success = train_it(capture_func, click_func, name, count)
        if success:
            trained = True
            set_log(f"Trained {count}x {name}")

    return trained
