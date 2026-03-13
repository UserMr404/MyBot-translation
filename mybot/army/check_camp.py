"""Army camp verification translated from CreateArmy/checkArmyCamp.au3.

Reads current army camp contents to verify trained troops match
the desired composition.

Source: COCBot/functions/CreateArmy/checkArmyCamp.au3
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mybot.log import set_debug_log
from mybot.vision.ocr import read_number, read_text


@dataclass
class ArmyCampStatus:
    """Current army camp capacity and contents."""
    current_space: int = 0
    total_space: int = 0
    spell_current: int = 0
    spell_total: int = 0
    cc_current: int = 0
    cc_total: int = 0

    @property
    def is_full(self) -> bool:
        return self.total_space > 0 and self.current_space >= self.total_space

    @property
    def fill_percent(self) -> float:
        return (self.current_space / self.total_space * 100) if self.total_space > 0 else 0


def check_army_camp(image: np.ndarray) -> ArmyCampStatus:
    """Read army camp capacity from the army overview.

    Translated from checkArmyCamp() in checkArmyCamp.au3.
    Reads the "X/Y" capacity strings for troops, spells, and CC.

    Args:
        image: BGR screenshot with army overview open.

    Returns:
        ArmyCampStatus with current capacities.
    """
    status = ArmyCampStatus()

    # Troop camp capacity (e.g., "200/200")
    camp_text = read_text(image, 330, 200, 130, 22, whitelist="0123456789/")
    current, total = _parse_capacity(camp_text)
    status.current_space = current
    status.total_space = total

    # Spell capacity (e.g., "11/11")
    spell_text = read_text(image, 330, 309, 100, 22, whitelist="0123456789/")
    status.spell_current, status.spell_total = _parse_capacity(spell_text)

    # CC capacity (e.g., "40/40")
    cc_text = read_text(image, 330, 418, 100, 22, whitelist="0123456789/")
    status.cc_current, status.cc_total = _parse_capacity(cc_text)

    set_debug_log(
        f"Army camp: {status.current_space}/{status.total_space} "
        f"Spells: {status.spell_current}/{status.spell_total} "
        f"CC: {status.cc_current}/{status.cc_total}"
    )

    return status


def _parse_capacity(text: str) -> tuple[int, int]:
    """Parse a capacity string like '200/200' into (current, total)."""
    if "/" not in text:
        return 0, 0
    parts = text.split("/")
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except (ValueError, IndexError):
        return 0, 0
