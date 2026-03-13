"""Individual troop training translated from CreateArmy/TrainIt.au3.

Finds a specific troop/spell in the training window and clicks it
the required number of times.

Source: COCBot/functions/CreateArmy/TrainIt.au3
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.army.train_click import train_click
from mybot.log import set_debug_log, set_log


def train_it(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    troop_name: str,
    count: int,
    template_dir: Path | None = None,
) -> bool:
    """Train a specific troop or spell.

    Translated from TrainIt() in TrainIt.au3.
    Finds the troop in the training window via template matching,
    then clicks it the required number of times.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        troop_name: Short name of the troop (e.g., "Barb", "Arch").
        count: Number of troops to train.
        template_dir: Base template directory for training icons.

    Returns:
        True if troop found and clicked.
    """
    if count <= 0:
        return True

    if template_dir is None:
        template_dir = Path("imgxml/Train")

    # Build specific template path for this troop
    troop_dir = template_dir / troop_name
    if not troop_dir.is_dir():
        # Try case-insensitive search
        for d in template_dir.iterdir():
            if d.is_dir() and d.name.lower() == troop_name.lower():
                troop_dir = d
                break
        else:
            set_debug_log(f"TrainIt: template dir not found for '{troop_name}'")
            return False

    image = capture_func()
    if image is None:
        return False

    from mybot.vision.matcher import find_image
    result = find_image(image, troop_dir, confidence=0.80)

    if result is None:
        set_debug_log(f"TrainIt: '{troop_name}' not found in training window")
        return False

    set_debug_log(f"TrainIt: training {count}x {troop_name} at ({result.x},{result.y})")
    train_click(result.x, result.y, count, click_func, delay=0.1)
    return True
