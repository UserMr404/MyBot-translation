"""Troop selection in attack bar translated from Troops/SelectDropTroop.au3.

Selects a specific troop type in the attack bar for deployment.

Source: COCBot/functions/Attack/Troops/SelectDropTroop.au3
"""

from __future__ import annotations

import time
from typing import Callable

from mybot.attack.attack_bar import AttackBar
from mybot.log import set_debug_log


def select_troop(
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
    troop_name: str | None = None,
    army_index: int | None = None,
) -> bool:
    """Select a troop in the attack bar for deployment.

    Translated from SelectDropTroop() in SelectDropTroop.au3.

    Args:
        click_func: Click function.
        attack_bar: Current attack bar.
        troop_name: Short name of troop (e.g., "Barb").
        army_index: ArmyIndex value (alternative to name).

    Returns:
        True if troop was found and selected.
    """
    slot = None
    if troop_name:
        slot = attack_bar.get_slot_by_name(troop_name)
    elif army_index is not None:
        slot = attack_bar.get_slot(army_index)

    if slot is None:
        set_debug_log(f"SelectTroop: not found (name={troop_name}, idx={army_index})")
        return False

    click_func(slot.x, slot.y)
    time.sleep(0.1)
    set_debug_log(f"SelectTroop: selected {slot.name} at ({slot.x},{slot.y})")
    return True
