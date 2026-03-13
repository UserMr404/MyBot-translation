"""Read trained spells from army overview.

Translated from:
- getArmySpells/getArmySpells.au3 — detect spell types
- getArmySpells/getArmySpellCapacity.au3 — read spell capacity
- getArmySpells/getArmySpellCount.au3 — count spells
- getArmySpells/getArmySpellTime.au3 — read brew time

Source: COCBot/functions/CreateArmy/getArmySpells/
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mybot.constants import MID_OFFSET_Y, SPELL_SHORT_NAMES
from mybot.enums import Spell
from mybot.log import set_debug_log
from mybot.vision.ocr import read_number, read_text


def get_army_spells(
    image: np.ndarray,
    template_dir: Path | None = None,
) -> list[int]:
    """Read current spell quantities from army overview.

    Translated from getArmySpells() — detects spells via template matching.

    Args:
        image: BGR screenshot with army overview open.
        template_dir: Template directory for spell detection.

    Returns:
        List of spell counts indexed by Spell enum.
    """
    counts = [0] * Spell.COUNT

    if template_dir is None:
        template_dir = Path("imgxml/ArmyOverview/Spells")

    if not template_dir.is_dir():
        return counts

    from mybot.vision.matcher import find_multiple

    result = find_multiple(
        image, template_dir,
        search_area=(0, 290 + MID_OFFSET_Y, 860, 80),
        confidence=0.80,
    )

    for match in result.matches:
        spell_idx = _name_to_spell_index(match.name)
        if spell_idx >= 0:
            qty = read_number(image, match.x - 15, match.y + 25, 30, 16, default=1)
            counts[spell_idx] = max(qty, 1)
            set_debug_log(f"Spell {match.name}: {counts[spell_idx]}")

    return counts


def get_army_spell_capacity(image: np.ndarray) -> tuple[int, int]:
    """Read spell capacity (current/total).

    Translated from getArmySpellCapacity().
    """
    text = read_text(image, 330, 309, 100, 22, whitelist="0123456789/")
    if "/" in text:
        parts = text.split("/")
        try:
            return int(parts[0].strip()), int(parts[1].strip())
        except (ValueError, IndexError):
            pass
    return 0, 0


def get_army_spell_time(image: np.ndarray) -> str:
    """Read remaining spell brewing time.

    Translated from getArmySpellTime().
    """
    return read_text(image, 162, 309, 120, 27, whitelist="0123456789:hms ")


def _name_to_spell_index(name: str) -> int:
    """Map template name to Spell enum index."""
    name_lower = name.lower()
    for i, short_name in enumerate(SPELL_SHORT_NAMES):
        if short_name.lower() == name_lower or short_name.lower() in name_lower:
            return i
    return -1
