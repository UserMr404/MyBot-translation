"""Attack bar reading translated from Attack/GetAttackBar.au3.

Reads the troop slots displayed in the bottom attack bar during battle,
identifying troop types, quantities, and positions.

Source: COCBot/functions/Attack/GetAttackBar.au3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from mybot.constants import BOTTOM_OFFSET_Y, MID_OFFSET_Y, TROOP_SHORT_NAMES
from mybot.enums import ArmyIndex
from mybot.log import set_debug_log
from mybot.vision.ocr import read_number


@dataclass
class AttackBarSlot:
    """A single troop slot in the attack bar."""
    index: int = 0          # ArmyIndex enum value
    name: str = ""
    quantity: int = 0
    x: int = 0              # Center X of the slot
    y: int = 0              # Center Y of the slot
    is_hero: bool = False
    is_spell: bool = False
    is_siege: bool = False


@dataclass
class AttackBar:
    """Complete attack bar state during battle."""
    slots: list[AttackBarSlot] = field(default_factory=list)

    def get_slot(self, army_index: int) -> AttackBarSlot | None:
        """Find a slot by ArmyIndex."""
        for slot in self.slots:
            if slot.index == army_index:
                return slot
        return None

    def get_slot_by_name(self, name: str) -> AttackBarSlot | None:
        """Find a slot by troop short name."""
        name_lower = name.lower()
        for slot in self.slots:
            if slot.name.lower() == name_lower:
                return slot
        return None

    @property
    def total_troops(self) -> int:
        return sum(s.quantity for s in self.slots if not s.is_hero and not s.is_spell and not s.is_siege)


# Attack bar Y position and slot spacing
ATTACK_BAR_Y = 595 + BOTTOM_OFFSET_Y
SLOT_WIDTH = 72
FIRST_SLOT_X = 30


def get_attack_bar(
    image: np.ndarray,
    template_dir: Path | None = None,
) -> AttackBar:
    """Read all troop slots from the attack bar.

    Translated from GetAttackBar() in GetAttackBar.au3.
    Scans the bottom bar during battle to identify each troop type
    and its remaining quantity.

    Args:
        image: BGR screenshot during battle.
        template_dir: Template directory for attack bar icons.

    Returns:
        AttackBar with all detected slots.
    """
    bar = AttackBar()

    if template_dir is None:
        template_dir = Path("imgxml/ArmyOverview/TroopBar")

    if not template_dir.is_dir():
        return bar

    from mybot.vision.matcher import find_multiple

    # Search the bottom bar area
    result = find_multiple(
        image, template_dir,
        search_area=(0, ATTACK_BAR_Y - 40, 860, 80),
        confidence=0.80,
    )

    for match in result.matches:
        slot = AttackBarSlot(
            name=match.name,
            x=match.x,
            y=match.y,
            index=_name_to_army_index(match.name),
        )

        # Read quantity below the troop icon
        slot.quantity = read_number(image, match.x - 12, match.y + 22, 24, 14, default=1)

        # Classify slot type
        idx = slot.index
        if ArmyIndex.KING <= idx <= ArmyIndex.DRAGON_DUKE:
            slot.is_hero = True
        elif ArmyIndex.L_SPELL <= idx <= ArmyIndex.IB_SPELL:
            slot.is_spell = True
        elif ArmyIndex.WALL_W <= idx <= ArmyIndex.TROOP_L:
            slot.is_siege = True

        bar.slots.append(slot)
        set_debug_log(f"AttackBar: {slot.name} x{slot.quantity} at ({slot.x},{slot.y})")

    # Sort slots by X position (left to right)
    bar.slots.sort(key=lambda s: s.x)
    return bar


def get_slot_from_x(x: int) -> int:
    """Map an X position to a slot index (0-based).

    Translated from GetSlotIndexFromXPos() in GetSlotIndexFromXPos.au3.
    """
    if x < FIRST_SLOT_X:
        return 0
    return (x - FIRST_SLOT_X) // SLOT_WIDTH


def _name_to_army_index(name: str) -> int:
    """Map a template name to ArmyIndex value."""
    name_lower = name.lower()
    for i, short_name in enumerate(TROOP_SHORT_NAMES):
        if short_name.lower() == name_lower or short_name.lower() in name_lower:
            return i
    return -1
