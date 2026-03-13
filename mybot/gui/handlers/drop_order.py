"""Drop order event handlers translated from MBR GUI Control Tab DropOrder.au3.

Handles troop deployment order customization.

Source: COCBot/GUI/MBR GUI Control Tab DropOrder.au3 (233 lines, 9 functions)
"""

from __future__ import annotations

from mybot.constants import TROOP_NAMES


def get_default_drop_order() -> list[int]:
    """Get the default troop drop order (tanks first, then damage, cleanup).

    Returns list of troop indices in deployment order.
    """
    from mybot.attack.drop_order import DEFAULT_DROP_ORDER
    return list(DEFAULT_DROP_ORDER)


def validate_drop_order(order: list[int]) -> bool:
    """Validate a custom drop order — must contain valid indices."""
    seen = set()
    for idx in order:
        if idx < 0 or idx in seen:
            return False
        seen.add(idx)
    return True


def move_troop_up(order: list[int], position: int) -> list[int]:
    """Move a troop earlier in the drop order."""
    if position <= 0 or position >= len(order):
        return order
    new_order = list(order)
    new_order[position], new_order[position - 1] = new_order[position - 1], new_order[position]
    return new_order


def move_troop_down(order: list[int], position: int) -> list[int]:
    """Move a troop later in the drop order."""
    if position < 0 or position >= len(order) - 1:
        return order
    new_order = list(order)
    new_order[position], new_order[position + 1] = new_order[position + 1], new_order[position]
    return new_order
