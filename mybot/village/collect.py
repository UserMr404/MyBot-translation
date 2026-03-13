"""Resource collection translated from Village/Collect.au3.

Collects resources from mines, collectors, and drills by detecting
them via template matching and clicking on each one.

Source: COCBot/functions/Village/Collect.au3
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.log import set_debug_log, set_log
from mybot.vision.pixel import is_inside_diamond


@dataclass
class CollectResult:
    """Result of resource collection run."""
    gold_collected: int = 0
    elixir_collected: int = 0
    dark_collected: int = 0
    total_clicks: int = 0


def collect_resources(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
    collector_dirs: list[Path] | None = None,
    delay: float = 0.3,
) -> CollectResult:
    """Collect resources from all mines, collectors, and drills.

    Translated from Collect() in Collect.au3.
    Uses template matching to find collector buildings with ready
    resources, then clicks each one to collect.

    The original uses returnMultipleMatchesOwnVillage() to find
    collectors, filters by storage fullness, and clicks each.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking on collectors.
        collector_dirs: Template directories for collector detection.
                       Defaults to standard imgxml paths.
        delay: Seconds between collection clicks.

    Returns:
        CollectResult with collection statistics.
    """
    if collector_dirs is None:
        collector_dirs = [
            resolve_img_dir("imgxml/Resources/GoldMine"),
            resolve_img_dir("imgxml/Resources/ElixirCollector"),
            resolve_img_dir("imgxml/Resources/DarkElixirDrill"),
        ]

    result = CollectResult()

    image = capture_func()
    if image is None:
        return result

    from mybot.vision.matcher import find_multiple

    for collector_dir in collector_dirs:
        if not collector_dir.is_dir():
            set_debug_log(f"Collect: template dir not found: {collector_dir}")
            continue

        search_result = find_multiple(
            image,
            collector_dir,
            max_results=20,
            confidence=0.80,
        )

        if not search_result.found:
            continue

        dir_name = collector_dir.name
        set_debug_log(f"Collect: found {search_result.total_objects} {dir_name}")

        for match in search_result.matches:
            # Verify the collector is inside the village diamond
            if not is_inside_diamond(match.x, match.y):
                set_debug_log(
                    f"Collect: skipping ({match.x},{match.y}) — outside diamond"
                )
                continue

            if click_func:
                click_func(match.x, match.y)
                result.total_clicks += 1

            import time
            time.sleep(delay)

    if result.total_clicks > 0:
        set_log(f"Collected from {result.total_clicks} buildings")
    else:
        set_debug_log("Collect: no collectors found")

    return result


def is_storage_full(
    image: np.ndarray,
    resource_type: str = "gold",
) -> bool:
    """Check if a resource storage is full.

    Translated from resource fullness checks in Collect.au3.
    Checks specific pixel colors that indicate full storages.

    Pixel positions (from AutoIt):
    - Gold: (657, 2+MidY, 0xE7C00D)
    - Elixir: (657, 52+MidY, 0xC027C0)
    - Dark Elixir: (707, 102+MidY, 0x270D33)

    Args:
        image: BGR screenshot.
        resource_type: "gold", "elixir", or "dark_elixir".

    Returns:
        True if the storage appears full.
    """
    from mybot.constants import MID_OFFSET_Y
    from mybot.vision.pixel import check_pixel

    checks = {
        "gold": (657, 2 + MID_OFFSET_Y, 0xE7C00D, 15),
        "elixir": (657, 52 + MID_OFFSET_Y, 0xC027C0, 15),
        "dark_elixir": (707, 102 + MID_OFFSET_Y, 0x270D33, 15),
    }

    pixel = checks.get(resource_type)
    if pixel is None:
        return False

    return check_pixel(image, *pixel)
