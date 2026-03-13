"""Building upgrade management translated from Village/UpgradeBuilding.au3.

Handles building upgrade detection, cost reading, and upgrade execution.

Source files:
- Village/UpgradeBuilding.au3 — main upgrade logic
- Village/UpgradeWall.au3 — wall upgrades
- Village/Auto Upgrade.au3 — automatic upgrade selection
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.constants import MID_OFFSET_Y, UPGRADE_SLOTS
from mybot.log import set_debug_log, set_log
from mybot.vision.ocr import get_building_info, get_upgrade_cost, get_upgrade_time


@dataclass
class UpgradeSlot:
    """A tracked building upgrade slot.

    Replaces $g_avBuildingUpgrades[] from MBR Global Variables.au3.
    """
    enabled: bool = False
    name: str = ""
    level: int = 0
    x: int = 0
    y: int = 0
    cost: int = 0
    time: str = ""
    resource_type: str = ""  # "gold", "elixir", "dark_elixir"
    in_progress: bool = False


@dataclass
class UpgradeResult:
    """Result of an upgrade attempt."""
    success: bool = False
    building_name: str = ""
    level: int = 0
    cost: int = 0
    error: str = ""


def check_upgrade_available(
    image: np.ndarray,
    x: int,
    y: int,
) -> UpgradeSlot | None:
    """Check if a building at (x, y) has an available upgrade.

    Reads the building info popup to determine name, level, and cost.

    Args:
        image: BGR screenshot with building info popup visible.
        x: Building X position.
        y: Building Y position.

    Returns:
        UpgradeSlot with details, or None if no upgrade available.
    """
    from mybot.game.obstacles import is_gem_window, is_no_upgrade_loot

    # Read building info from popup
    info = get_building_info(image)
    if not info.name:
        return None

    slot = UpgradeSlot(
        name=info.name,
        level=info.level,
        x=x,
        y=y,
    )

    # Read upgrade cost
    slot.cost = get_upgrade_cost(image)
    slot.time = get_upgrade_time(image)

    # Check if we can afford the upgrade
    if is_gem_window(image):
        set_debug_log(f"Upgrade {info.name}: gem window detected (insufficient resources)")
        return None

    if is_no_upgrade_loot(image):
        set_debug_log(f"Upgrade {info.name}: insufficient loot")
        return None

    slot.enabled = True
    return slot


def start_upgrade(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
    slot: UpgradeSlot | None = None,
) -> UpgradeResult:
    """Execute a building upgrade.

    Translated from UpgradeBuilding() in UpgradeBuilding.au3.

    Flow:
    1. Click on the building
    2. Find and click the upgrade button
    3. Confirm the upgrade
    4. Verify upgrade started

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking UI elements.
        slot: Upgrade slot with building position.

    Returns:
        UpgradeResult indicating success/failure.
    """
    result = UpgradeResult()

    if slot is None:
        result.error = "No upgrade slot provided"
        return result

    result.building_name = slot.name
    result.level = slot.level
    result.cost = slot.cost

    # Click on the building
    if click_func:
        click_func(slot.x, slot.y)

    import time
    time.sleep(0.5)

    # Find upgrade button in the building menu
    upgrade_btn_dir = resolve_img_dir("imgxml/imglocbuttons/UpgradeButton")
    if not upgrade_btn_dir.is_dir():
        result.error = "Upgrade button templates not found"
        return result

    image = capture_func()
    if image is None:
        result.error = "Failed to capture screenshot"
        return result

    from mybot.vision.matcher import find_image
    btn = find_image(image, upgrade_btn_dir, confidence=0.80)

    if btn is None:
        result.error = "Upgrade button not found"
        set_debug_log(f"Upgrade {slot.name}: button not found")
        return result

    # Click upgrade button
    if click_func:
        click_func(btn.x, btn.y)

    time.sleep(0.5)

    # Verify upgrade started (check for gem window = insufficient funds)
    image = capture_func()
    if image is not None:
        from mybot.game.obstacles import is_gem_window
        if is_gem_window(image):
            result.error = "Insufficient resources (gem window appeared)"
            set_log(f"Upgrade {slot.name}: insufficient resources")
            # Close gem window
            if click_func:
                click_func(430, 20)  # Click away
            return result

    result.success = True
    set_log(
        f"Upgrade started: {slot.name} L{slot.level} → L{slot.level + 1} "
        f"(cost: {slot.cost:,})"
    )
    return result


def auto_upgrade(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
    upgrade_slots: list[UpgradeSlot] | None = None,
) -> list[UpgradeResult]:
    """Automatically upgrade buildings from tracked slots.

    Translated from Auto Upgrade logic in Auto Upgrade.au3.
    Iterates through enabled upgrade slots and attempts each.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking UI elements.
        upgrade_slots: List of tracked upgrade slots.

    Returns:
        List of upgrade results for each attempted slot.
    """
    if not upgrade_slots:
        return []

    results = []

    for slot in upgrade_slots:
        if not slot.enabled or slot.in_progress:
            continue

        result = start_upgrade(capture_func, click_func, slot)
        results.append(result)

        if result.success:
            slot.in_progress = True

    return results
