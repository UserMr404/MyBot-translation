"""Read trained troops from army overview.

Translated from:
- getArmyTroops/getArmyTroops.au3 — detect troop types
- getArmyTroops/getArmyTroopCapacity.au3 — read camp capacity
- getArmyTroops/getArmyTroopTime.au3 — read training time

Source: COCBot/functions/CreateArmy/getArmyTroops/
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.constants import MID_OFFSET_Y, TROOP_SHORT_NAMES
from mybot.enums import Troop
from mybot.log import set_debug_log
from mybot.vision.ocr import read_number, read_text


def get_army_troops(
    image: np.ndarray,
    template_dir: Path | None = None,
) -> list[int]:
    """Read current troop quantities from army overview.

    Translated from getArmyTroops() — detects troop types via template
    matching and reads their quantities.

    Args:
        image: BGR screenshot with army overview open.
        template_dir: Template directory for troop detection.

    Returns:
        List of troop counts indexed by Troop enum.
    """
    counts = [0] * Troop.COUNT

    if template_dir is None:
        template_dir = resolve_img_dir("imgxml/ArmyOverview/Troops")

    if not template_dir.is_dir():
        return counts

    from mybot.vision.matcher import find_multiple

    # Search for troop icons in the troop row area
    result = find_multiple(
        image, template_dir,
        search_area=(0, 180 + MID_OFFSET_Y, 860, 80),
        confidence=0.80,
    )

    for match in result.matches:
        # Map template name to troop index
        troop_idx = _name_to_troop_index(match.name)
        if troop_idx >= 0:
            # Read quantity next to the troop icon
            qty = _read_troop_quantity(image, match.x, match.y)
            counts[troop_idx] = max(qty, 1)
            set_debug_log(f"Troop {match.name}: {counts[troop_idx]}")

    return counts


def get_army_troop_capacity(image: np.ndarray) -> tuple[int, int]:
    """Read troop camp capacity (current/total).

    Translated from getArmyTroopCapacity().

    Returns:
        (current_space, total_space).
    """
    text = read_text(image, 330, 200, 130, 22, whitelist="0123456789/")
    if "/" in text:
        parts = text.split("/")
        try:
            return int(parts[0].strip()), int(parts[1].strip())
        except (ValueError, IndexError):
            pass
    return 0, 0


def get_army_troop_time(image: np.ndarray) -> str:
    """Read remaining troop training time.

    Translated from getArmyTroopTime().
    """
    return read_text(image, 162, 200, 120, 27, whitelist="0123456789:hms ")


def _name_to_troop_index(name: str) -> int:
    """Map a template name to Troop enum index."""
    name_lower = name.lower()
    for i, short_name in enumerate(TROOP_SHORT_NAMES):
        if short_name.lower() == name_lower or short_name.lower() in name_lower:
            return i
    return -1


def _read_troop_quantity(image: np.ndarray, x: int, y: int) -> int:
    """Read the quantity number displayed below a troop icon."""
    return read_number(image, x - 15, y + 25, 30, 16, default=1)
