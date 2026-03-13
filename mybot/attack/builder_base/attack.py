"""Builder Base attack translated from BuilderBase/AttackBB.au3.

Handles Builder Base specific attack mechanics including troop
deployment and ability timing.

Source: COCBot/functions/Attack/BuilderBase/AttackBB.au3
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.attack.attack_bar import AttackBar, get_attack_bar
from mybot.attack.deploy import drop_on_edge
from mybot.attack.timing import get_deploy_delay
from mybot.log import set_debug_log, set_log
from mybot.vision.red_area import RedArea, detect_red_area


@dataclass
class BBAttackResult:
    """Result of a Builder Base attack."""
    stars: int = 0
    destruction: float = 0.0
    success: bool = False


def attack_builder_base(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
) -> BBAttackResult:
    """Execute a Builder Base attack.

    Translated from AttackBB() in AttackBB.au3.
    Builder Base attacks are simpler — troops regenerate and
    abilities trigger automatically.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.

    Returns:
        BBAttackResult with attack outcome.
    """
    result = BBAttackResult()

    image = capture_func()
    if image is None:
        return result

    # Read attack bar
    bar = get_attack_bar(image)
    if not bar.slots:
        set_log("BB Attack: no troops in attack bar")
        return result

    # Detect red area
    red_area = detect_red_area(image)

    # Get deployment points
    if red_area and red_area.is_valid:
        points = (
            red_area.top_left + red_area.top_right +
            red_area.bottom_left + red_area.bottom_right
        )
    else:
        from mybot.vision.red_area import get_external_edge
        points = get_external_edge()

    # Deploy all troops
    for slot in bar.slots:
        if slot.quantity <= 0:
            continue

        click_func(slot.x, slot.y)
        time.sleep(0.1)

        drop_on_edge(click_func, points, slot.quantity, delay=get_deploy_delay())
        time.sleep(0.5)

    result.success = True
    set_log("BB Attack: deployment complete")
    return result
