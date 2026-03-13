"""Read siege machine status from army overview.

Translated from getArmySiegeMachines/getArmySiegeMachines.au3.

Source: COCBot/functions/CreateArmy/getArmySiegeMachines/
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mybot.constants import MID_OFFSET_Y, SIEGE_SHORT_NAMES
from mybot.enums import Siege
from mybot.log import set_debug_log
from mybot.vision.ocr import read_number


def get_army_siege(
    image: np.ndarray,
    template_dir: Path | None = None,
) -> list[int]:
    """Read current siege machine quantities from army overview.

    Translated from getArmySiegeMachines().

    Args:
        image: BGR screenshot with army overview open.
        template_dir: Template directory for siege detection.

    Returns:
        List of siege counts indexed by Siege enum.
    """
    counts = [0] * Siege.COUNT

    if template_dir is None:
        template_dir = Path("imgxml/ArmyOverview/SiegeMachines")

    if not template_dir.is_dir():
        return counts

    from mybot.vision.matcher import find_multiple

    result = find_multiple(
        image, template_dir,
        search_area=(0, 150 + MID_OFFSET_Y, 860, 80),
        confidence=0.80,
    )

    for match in result.matches:
        siege_idx = _name_to_siege_index(match.name)
        if siege_idx >= 0:
            qty = read_number(image, match.x - 15, match.y + 25, 30, 16, default=1)
            counts[siege_idx] = max(qty, 1)
            set_debug_log(f"Siege {match.name}: {counts[siege_idx]}")

    return counts


def _name_to_siege_index(name: str) -> int:
    """Map template name to Siege enum index."""
    name_lower = name.lower()
    for i, short_name in enumerate(SIEGE_SHORT_NAMES):
        if short_name.lower() == name_lower or short_name.lower() in name_lower:
            return i
    return -1
