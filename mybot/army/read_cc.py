"""Read Clan Castle contents from army overview.

Translated from:
- getArmyCCTroops/getArmyCCTroops.au3 — CC troop detection
- getArmyCCTroops/getArmyCCStatus.au3 — CC fill status
- getArmyCCSpells/getArmyCCSpell.au3 — CC spell detection
- getArmyCCSpells/getArmyCCSpellCapacity.au3 — CC spell capacity
- getArmyCCSiegeMachines/getArmyCCSiegeMachines.au3 — CC siege detection

Source: COCBot/functions/CreateArmy/getArmyCC*/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.constants import MID_OFFSET_Y
from mybot.enums import Siege, Spell, Troop
from mybot.log import set_debug_log
from mybot.vision.ocr import read_number, read_text


# CC capacity by level (from DonateCC.au3)
CC_CAPACITY = {
    1: (10, 0), 2: (15, 0), 3: (20, 0), 4: (25, 1), 5: (30, 1),
    6: (35, 1), 7: (35, 2), 8: (40, 2), 9: (40, 2), 10: (45, 3),
    11: (45, 3), 12: (50, 3), 13: (50, 4), 14: (55, 4),
}


@dataclass
class CCContents:
    """Clan Castle contents summary."""
    troops: list[int] = field(default_factory=lambda: [0] * Troop.COUNT)
    spells: list[int] = field(default_factory=lambda: [0] * Spell.COUNT)
    siege: list[int] = field(default_factory=lambda: [0] * Siege.COUNT)
    troop_space: int = 0
    troop_capacity: int = 0
    spell_space: int = 0
    spell_capacity: int = 0

    @property
    def is_full(self) -> bool:
        return self.troop_capacity > 0 and self.troop_space >= self.troop_capacity


def get_cc_troops(
    image: np.ndarray,
    template_dir: Path | None = None,
) -> CCContents:
    """Read Clan Castle contents from army overview.

    Translated from getArmyCCTroops() and related functions.

    Args:
        image: BGR screenshot with CC section visible.
        template_dir: Base template dir for CC detection.

    Returns:
        CCContents with current CC state.
    """
    contents = CCContents()

    # Read CC capacity text
    cap_text = read_text(image, 330, 418, 100, 22, whitelist="0123456789/")
    if "/" in cap_text:
        parts = cap_text.split("/")
        try:
            contents.troop_space = int(parts[0].strip())
            contents.troop_capacity = int(parts[1].strip())
        except (ValueError, IndexError):
            pass

    # Detect CC troop types
    if template_dir is None:
        template_dir = resolve_img_dir("imgxml/ArmyOverview/CCTroops")

    if template_dir.is_dir():
        from mybot.vision.matcher import find_multiple
        result = find_multiple(
            image, template_dir,
            search_area=(0, 400 + MID_OFFSET_Y, 860, 80),
            confidence=0.80,
        )
        for match in result.matches:
            set_debug_log(f"CC troop: {match.name} L{match.level}")

    return contents


def get_cc_spell_capacity(image: np.ndarray) -> tuple[int, int]:
    """Read CC spell capacity.

    Translated from getArmyCCSpellCapacity().

    Returns:
        (current, total) spell space.
    """
    text = read_text(image, 445, 418, 80, 22, whitelist="0123456789/")
    if "/" in text:
        parts = text.split("/")
        try:
            return int(parts[0].strip()), int(parts[1].strip())
        except (ValueError, IndexError):
            pass
    return 0, 0


def get_cc_status(image: np.ndarray) -> str:
    """Read CC fill status text.

    Translated from getArmyCCStatus().
    Returns text like "Full", "Not Full", "Empty".
    """
    return read_text(image, 400, 450 + MID_OFFSET_Y, 100, 20)
