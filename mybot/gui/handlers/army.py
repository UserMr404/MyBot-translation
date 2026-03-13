"""Army tab event handlers translated from MBR GUI Control Child Army.au3.

Handles troop composition changes, training mode switches, slot updates.

Source: COCBot/GUI/MBR GUI Control Child Army.au3 (1,608 lines, 81 functions)
"""

from __future__ import annotations

from mybot.constants import TROOP_SPACE, SPELL_SPACE
from mybot.enums import Troop, Spell, Siege
from mybot.log import set_log
from mybot.state import BotState


def apply_army_config(state: BotState, troops: dict[int, int],
                      spells: dict[int, int], sieges: dict[int, int]) -> None:
    """Apply army composition from GUI to state.

    Args:
        state: Bot state to update.
        troops: Dict of {troop_index: quantity}.
        spells: Dict of {spell_index: quantity}.
        sieges: Dict of {siege_index: quantity}.
    """
    for idx, qty in troops.items():
        if 0 <= idx < Troop.COUNT:
            state.army.custom_troops[idx] = qty

    for idx, qty in spells.items():
        if 0 <= idx < Spell.COUNT:
            state.army.custom_spells[idx] = qty

    for idx, qty in sieges.items():
        if 0 <= idx < Siege.COUNT:
            state.army.custom_sieges[idx] = qty


def calculate_total_space(troops: dict[int, int]) -> int:
    """Calculate total troop space for a composition."""
    total = 0
    for idx, qty in troops.items():
        if 0 <= idx < len(TROOP_SPACE):
            total += qty * TROOP_SPACE[idx]
    return total


def calculate_spell_space(spells: dict[int, int]) -> int:
    """Calculate total spell space for a composition."""
    total = 0
    for idx, qty in spells.items():
        if 0 <= idx < len(SPELL_SPACE):
            total += qty * SPELL_SPACE[idx]
    return total


def validate_army_composition(troops: dict[int, int], max_space: int) -> list[str]:
    """Validate that army composition fits within camp capacity.

    Returns list of error messages (empty if valid).
    """
    errors: list[str] = []
    total = calculate_total_space(troops)
    if total > max_space:
        errors.append(f"Army uses {total} space but camp capacity is {max_space}")
    if total == 0:
        errors.append("No troops selected")
    return errors
