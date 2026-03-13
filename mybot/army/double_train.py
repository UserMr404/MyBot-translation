"""Double Train mode translated from CreateArmy/DoubleTrain.au3.

Trains a second army while the first is fighting, so a fresh army
is ready immediately after battle.

Source: COCBot/functions/CreateArmy/DoubleTrain.au3
"""

from __future__ import annotations

import time
from typing import Callable

import numpy as np

from mybot.army.quick_train import quick_train
from mybot.log import set_debug_log, set_log


def double_train(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    army_slot: int = 0,
    use_quick_train: bool = True,
) -> bool:
    """Train a second army for when the first deploys.

    Translated from DoubleTrain() in DoubleTrain.au3.
    After first army is queued, trains a second copy so it's
    ready immediately when the first army returns from battle.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        army_slot: Quick train army slot to use.
        use_quick_train: Whether to use Quick Train.

    Returns:
        True if second army was queued.
    """
    set_debug_log("DoubleTrain: queuing second army")

    if use_quick_train:
        success = quick_train(capture_func, click_func, army_slot)
    else:
        # Custom training would go here
        success = False
        set_debug_log("DoubleTrain: custom train not yet implemented")

    if success:
        set_log("DoubleTrain: second army queued")
    else:
        set_debug_log("DoubleTrain: failed to queue second army")

    return success
