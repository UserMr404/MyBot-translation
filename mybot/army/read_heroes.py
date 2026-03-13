"""Read hero status from army overview.

Translated from:
- getArmyHeroes/getArmyHeroCount.au3 — detect hero availability
- getArmyHeroes/getArmyHeroTime.au3 — read hero regen time

Source: COCBot/functions/CreateArmy/getArmyHeroes/
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from mybot.constants import HERO_NAMES, HERO_SHORT_NAMES, MID_OFFSET_Y
from mybot.enums import Hero
from mybot.log import set_debug_log
from mybot.vision.ocr import read_text


@dataclass
class HeroStatus:
    """Status of a single hero."""
    available: bool = False
    upgrading: bool = False
    regen_time: str = ""
    level: int = 0


def get_army_heroes(
    image: np.ndarray,
    template_dir: Path | None = None,
) -> list[HeroStatus]:
    """Read hero status from army overview.

    Translated from getArmyHeroCount() — detects hero availability,
    upgrading state, and regen time.

    Args:
        image: BGR screenshot with army overview on heroes tab.
        template_dir: Template directory for hero detection.

    Returns:
        List of HeroStatus indexed by Hero enum.
    """
    statuses = [HeroStatus() for _ in range(Hero.COUNT)]

    if template_dir is None:
        template_dir = Path("imgxml/ArmyOverview/Heroes")

    if not template_dir.is_dir():
        return statuses

    from mybot.vision.matcher import find_multiple

    # Search for hero icons
    result = find_multiple(
        image, template_dir,
        search_area=(0, 350 + MID_OFFSET_Y, 860, 100),
        confidence=0.80,
    )

    for match in result.matches:
        hero_idx = _name_to_hero_index(match.name)
        if hero_idx >= 0:
            statuses[hero_idx].available = True
            statuses[hero_idx].level = match.level
            set_debug_log(f"Hero {HERO_NAMES[hero_idx]}: available, L{match.level}")

    # Check for upgrading heroes (grayed out icons)
    upgrade_dir = template_dir / "Upgrading"
    if upgrade_dir.is_dir():
        upgrade_result = find_multiple(
            image, upgrade_dir,
            search_area=(0, 350 + MID_OFFSET_Y, 860, 100),
            confidence=0.80,
        )
        for match in upgrade_result.matches:
            hero_idx = _name_to_hero_index(match.name)
            if hero_idx >= 0:
                statuses[hero_idx].upgrading = True
                statuses[hero_idx].available = False
                set_debug_log(f"Hero {HERO_NAMES[hero_idx]}: upgrading")

    return statuses


def get_army_hero_time(image: np.ndarray, hero_index: int) -> str:
    """Read hero regeneration/upgrade time.

    Translated from getArmyHeroTime().

    Args:
        image: BGR screenshot.
        hero_index: Hero index (Hero enum).

    Returns:
        Time string like "5m 30s".
    """
    # Hero time positions vary by which hero slot
    x_offsets = [120, 230, 340, 450, 560, 670]
    if hero_index >= len(x_offsets):
        return ""
    x = x_offsets[hero_index]
    return read_text(image, x, 440 + MID_OFFSET_Y, 80, 20, whitelist="0123456789hms ")


def _name_to_hero_index(name: str) -> int:
    """Map template name to Hero enum index."""
    name_lower = name.lower()
    for i, short_name in enumerate(HERO_SHORT_NAMES):
        if short_name.lower() in name_lower:
            return i
    # Also try full names
    for i, full_name in enumerate(HERO_NAMES):
        if full_name.lower().replace(" ", "") in name_lower.replace(" ", ""):
            return i
    return -1
