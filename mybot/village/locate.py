"""Building location detection translated from various Village/ files.

Detects building positions in the village using template matching
and OCR-based verification. Supports auto-locate for key buildings
like Laboratory, Clan Castle, and Heroes.

Source files:
- Village/Laboratory.au3 — LocateLab()
- Village/ClanCastle.au3 — LocateClanCastle()
- Village/UpgradeHeroes.au3 — LocateHeroAltar()
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.log import set_debug_log, set_log
from mybot.vision.ocr import get_building_info
from mybot.vision.pixel import is_inside_diamond


@dataclass
class BuildingLocation:
    """Located building position and identity."""
    found: bool = False
    name: str = ""
    level: int = 0
    x: int = 0
    y: int = 0


def locate_building(
    image: np.ndarray,
    template_dir: Path,
    expected_name: str = "",
    search_area: tuple[int, int, int, int] | None = None,
) -> BuildingLocation:
    """Locate a building by template matching.

    Uses image templates to find the building, then validates
    the position is inside the village diamond.

    Args:
        image: BGR screenshot of the village.
        template_dir: Path to building template images.
        expected_name: Expected building name for OCR verification.
        search_area: Optional (x, y, w, h) to restrict search.

    Returns:
        BuildingLocation with position and identity.
    """
    result = BuildingLocation()

    if not template_dir.is_dir():
        set_debug_log(f"Locate: template dir not found: {template_dir}")
        return result

    from mybot.vision.matcher import find_multiple

    search = find_multiple(
        image,
        template_dir,
        search_area=search_area,
        max_results=3,
        confidence=0.80,
    )

    if not search.found:
        return result

    # Find the best match that's inside the village diamond
    for match in search.matches:
        if not is_inside_diamond(match.x, match.y):
            continue

        result.found = True
        result.x = match.x
        result.y = match.y
        result.name = match.name or expected_name
        result.level = match.level

        set_debug_log(
            f"Located {result.name} at ({result.x},{result.y}) "
            f"level={result.level}"
        )
        return result

    return result


def locate_building_with_verify(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
    template_dir: Path = Path(),
    expected_name: str = "",
) -> BuildingLocation:
    """Locate a building and verify via OCR.

    Clicks the found building to open its info popup, then reads
    the building name/level via OCR for verification.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking on buildings.
        template_dir: Building template images.
        expected_name: Expected name (e.g., "Laboratory", "Clan Castle").

    Returns:
        BuildingLocation with verified position.
    """
    image = capture_func()
    if image is None:
        return BuildingLocation()

    loc = locate_building(image, template_dir, expected_name)
    if not loc.found:
        return loc

    # Click building to open info popup
    if click_func:
        click_func(loc.x, loc.y)

    import time
    time.sleep(0.5)

    # Read building info from popup
    verify_image = capture_func()
    if verify_image is None:
        return loc

    info = get_building_info(verify_image)

    # Verify name matches (fuzzy — AutoIt uses partial matching)
    if expected_name and info.name:
        if expected_name.lower() not in info.name.lower():
            set_debug_log(
                f"Locate verify failed: expected '{expected_name}', "
                f"got '{info.name}'"
            )
            loc.found = False
            return loc

    loc.name = info.name or expected_name
    loc.level = info.level or loc.level

    set_log(f"Verified {loc.name} L{loc.level} at ({loc.x},{loc.y})")
    return loc


# ── Convenience Locators ─────────────────────────────────────────────────────

def locate_lab(
    image: np.ndarray,
    lab_dir: Path | None = None,
) -> BuildingLocation:
    """Locate the Laboratory building.

    Translated from LocateLab() in Laboratory.au3.
    """
    if lab_dir is None:
        lab_dir = Path("imgxml/Buildings/Laboratory")
    return locate_building(image, lab_dir, expected_name="Laboratory")


def locate_clan_castle(
    image: np.ndarray,
    cc_dir: Path | None = None,
) -> BuildingLocation:
    """Locate the Clan Castle building.

    Translated from LocateClanCastle().
    """
    if cc_dir is None:
        cc_dir = Path("imgxml/Buildings/ClanCastle")
    return locate_building(image, cc_dir, expected_name="Clan Castle")


def locate_spell_factory(
    image: np.ndarray,
    sf_dir: Path | None = None,
) -> BuildingLocation:
    """Locate the Spell Factory building."""
    if sf_dir is None:
        sf_dir = Path("imgxml/Buildings/SpellFactory")
    return locate_building(image, sf_dir, expected_name="Spell Factory")


def locate_hero_altar(
    image: np.ndarray,
    hero_index: int,
    altar_dirs: dict[int, Path] | None = None,
) -> BuildingLocation:
    """Locate a hero altar.

    Translated from LocateHeroAltar() logic.

    Args:
        image: BGR screenshot.
        hero_index: Hero index (0=King, 1=Queen, etc.).
        altar_dirs: Mapping of hero index to template directory.

    Returns:
        BuildingLocation for the hero altar.
    """
    hero_names = {
        0: "Barbarian King",
        1: "Archer Queen",
        2: "Minion Prince",
        3: "Grand Warden",
        4: "Royal Champion",
        5: "Dragon Duke",
    }

    if altar_dirs and hero_index in altar_dirs:
        altar_dir = altar_dirs[hero_index]
    else:
        altar_dir = Path(f"imgxml/Buildings/HeroAltar/{hero_index}")

    name = hero_names.get(hero_index, f"Hero {hero_index}")
    return locate_building(image, altar_dir, expected_name=name)
