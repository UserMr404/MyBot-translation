"""Troop launching translated from Troops/LaunchTroop.au3.

Selects a troop from the attack bar and deploys it at target coordinates.

Source: COCBot/functions/Attack/Troops/LaunchTroop.au3
"""

from __future__ import annotations

import time
from typing import Callable

from mybot.attack.attack_bar import AttackBar
from mybot.attack.deploy import drop_troop
from mybot.log import set_debug_log


def launch_troop(
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
    troop_name: str,
    x: int,
    y: int,
    count: int = 1,
    delay: float = 0.05,
) -> int:
    """Select and deploy a troop from the attack bar.

    Translated from LaunchTroop() in LaunchTroop.au3.

    Args:
        click_func: Click function.
        attack_bar: Current attack bar state.
        troop_name: Short name of the troop.
        x: Deployment X.
        y: Deployment Y.
        count: Number to deploy.
        delay: Delay between deployments.

    Returns:
        Number of troops deployed.
    """
    slot = attack_bar.get_slot_by_name(troop_name)
    if slot is None:
        set_debug_log(f"LaunchTroop: '{troop_name}' not in attack bar")
        return 0

    if slot.quantity <= 0:
        set_debug_log(f"LaunchTroop: '{troop_name}' has 0 quantity")
        return 0

    # Select the troop in attack bar
    click_func(slot.x, slot.y)
    time.sleep(0.1)

    # Deploy at target
    to_deploy = min(count, slot.quantity)
    deployed = drop_troop(click_func, x, y, to_deploy, delay)

    if deployed > 0:
        slot.quantity -= deployed
        set_debug_log(f"LaunchTroop: {deployed}x {troop_name} at ({x},{y})")

    return deployed
