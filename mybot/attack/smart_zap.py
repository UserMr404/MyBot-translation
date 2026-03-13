"""Smart Zap (DE stealing) translated from SmartZap/smartZap.au3.

Uses Lightning spells on Dark Elixir drills to steal resources.

Source files:
- SmartZap/smartZap.au3 — main zap logic
- SmartZap/drillSearch.au3 — drill detection
- SmartZap/easyPreySearch.au3 — easy target detection
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.attack.attack_bar import AttackBar
from mybot.attack.deploy import drop_troop
from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.enums import ArmyIndex
from mybot.log import set_debug_log, set_log


@dataclass
class DrillTarget:
    """A detected Dark Elixir drill."""
    x: int
    y: int
    level: int = 0
    estimated_de: int = 0


@dataclass
class SmartZapResult:
    """Result of smart zap operation."""
    drills_found: int = 0
    spells_used: int = 0
    estimated_de: int = 0


def smart_zap(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
    min_de: int = 1000,
    max_spells: int = 4,
) -> SmartZapResult:
    """Execute Smart Zap on DE drills.

    Translated from smartZap() in smartZap.au3.
    Detects DE drills, estimates their value, and drops Lightning
    spells on the most valuable ones.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        attack_bar: Current attack bar.
        min_de: Minimum DE value to zap a drill.
        max_spells: Maximum lightning spells to use.

    Returns:
        SmartZapResult with zap statistics.
    """
    result = SmartZapResult()

    # Check if we have lightning spells
    spell_slot = attack_bar.get_slot(ArmyIndex.L_SPELL)
    if spell_slot is None or spell_slot.quantity <= 0:
        set_debug_log("SmartZap: no lightning spells available")
        return result

    image = capture_func()
    if image is None:
        return result

    # Find DE drills
    drills = _find_drills(image)
    result.drills_found = len(drills)

    if not drills:
        set_debug_log("SmartZap: no DE drills found")
        return result

    # Sort by estimated DE (highest first)
    drills.sort(key=lambda d: d.estimated_de, reverse=True)

    # Zap each drill
    spells_remaining = min(max_spells, spell_slot.quantity)

    for drill in drills:
        if spells_remaining <= 0:
            break

        if drill.estimated_de < min_de:
            set_debug_log(f"SmartZap: drill at ({drill.x},{drill.y}) DE too low ({drill.estimated_de})")
            continue

        # Select lightning spell
        click_func(spell_slot.x, spell_slot.y)
        time.sleep(0.2)

        # Drop on drill
        dropped = drop_troop(click_func, drill.x, drill.y, count=1)
        if dropped > 0:
            result.spells_used += 1
            result.estimated_de += drill.estimated_de
            spells_remaining -= 1
            spell_slot.quantity -= 1
            set_log(f"SmartZap: zapped drill at ({drill.x},{drill.y}), ~{drill.estimated_de} DE")
            time.sleep(1.0)  # Wait for spell animation

    return result


def _find_drills(
    image: np.ndarray,
    template_dir: Path | None = None,
) -> list[DrillTarget]:
    """Detect Dark Elixir drills on the enemy base.

    Translated from drillSearch() in drillSearch.au3.
    """
    if template_dir is None:
        template_dir = resolve_img_dir("imgxml/deadbase/Storages/Dark")

    if not template_dir.is_dir():
        return []

    from mybot.vision.matcher import find_multiple

    result = find_multiple(image, template_dir, confidence=0.75, max_results=10)

    drills = []
    for match in result.matches:
        # Estimate DE based on drill level
        level = match.level
        de_estimates = {
            1: 160, 2: 300, 3: 540, 4: 840, 5: 1200,
            6: 1600, 7: 2000, 8: 2400, 9: 2800,
        }
        estimated_de = de_estimates.get(level, 500)

        drills.append(DrillTarget(
            x=match.x, y=match.y,
            level=level,
            estimated_de=estimated_de,
        ))

    return drills
