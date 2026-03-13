"""Training click execution translated from CreateArmy/TrainClick.au3.

Low-level click functions for training troops/spells with quantity.

Source: COCBot/functions/CreateArmy/TrainClick.au3
"""

from __future__ import annotations

import time
from typing import Callable

from mybot.log import set_debug_log


def train_click(
    x: int,
    y: int,
    count: int,
    click_func: Callable[[int, int], None],
    delay: float = 0.1,
) -> int:
    """Click a training button multiple times.

    Translated from TrainClick() in TrainClick.au3.
    Clicks the specified position `count` times to queue troops.

    Args:
        x: Button X position.
        y: Button Y position.
        count: Number of clicks (troops to queue).
        click_func: Click function.
        delay: Delay between clicks in seconds.

    Returns:
        Number of clicks performed.
    """
    if count <= 0:
        return 0

    for i in range(count):
        click_func(x, y)
        if delay > 0 and i < count - 1:
            time.sleep(delay)

    set_debug_log(f"TrainClick: {count}x at ({x},{y})")
    return count
