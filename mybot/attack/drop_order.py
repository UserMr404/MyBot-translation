"""Custom troop drop order translated from Troops/DropOrderTroops.au3.

Determines the order in which troops should be deployed during attacks.

Source: COCBot/functions/Attack/Troops/DropOrderTroops.au3
"""

from __future__ import annotations

from mybot.constants import TROOP_SHORT_NAMES
from mybot.enums import DropOrder


# Default drop order (tanks first, then damage, then cleanup)
DEFAULT_DROP_ORDER: list[int] = [
    DropOrder.GOLEM,
    DropOrder.GIANT,
    DropOrder.SUPER_GIANT,
    DropOrder.ICE_GOLEM,
    DropOrder.LAVA_HOUND,
    DropOrder.WALL_BREAKER,
    DropOrder.SUPER_WALL_BREAKER,
    DropOrder.HEALER,
    DropOrder.WITCH,
    DropOrder.BOWLER,
    DropOrder.WIZARD,
    DropOrder.VALKYRIE,
    DropOrder.PEKKA,
    DropOrder.DRAGON,
    DropOrder.ELECTRO_DRAGON,
    DropOrder.BABY_DRAGON,
    DropOrder.BALLOON,
    DropOrder.MINER,
    DropOrder.HOG_RIDER,
    DropOrder.BARBARIAN,
    DropOrder.ARCHER,
    DropOrder.GOBLIN,
    DropOrder.MINION,
    DropOrder.HEROES,
    DropOrder.CLAN_CASTLE,
]


def get_drop_order(custom_order: list[int] | None = None) -> list[int]:
    """Get the troop deployment order.

    Translated from DropOrderTroops() in DropOrderTroops.au3.
    Returns either custom or default ordering.

    Args:
        custom_order: Custom drop order list (DropOrder enum values).

    Returns:
        Ordered list of DropOrder values.
    """
    if custom_order:
        return custom_order
    return list(DEFAULT_DROP_ORDER)


def reorder_attack_bar(
    slots: list,
    drop_order: list[int] | None = None,
) -> list:
    """Reorder attack bar slots according to drop order.

    Args:
        slots: AttackBarSlot list from attack bar.
        drop_order: Custom order (None for default).

    Returns:
        Reordered slot list.
    """
    order = get_drop_order(drop_order)

    ordered = []
    remaining = list(slots)

    for idx in order:
        for slot in remaining[:]:
            if slot.index == idx:
                ordered.append(slot)
                remaining.remove(slot)
                break

    # Add any unordered slots at the end
    ordered.extend(remaining)
    return ordered
