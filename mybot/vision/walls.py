"""Wall level detection translated from Image Search/imglocCheckWall.au3.

Detects wall segments at specific upgrade levels for the wall upgrade
automation feature. Uses a two-phase search: first near the last known
wall position, then expanding to the full screen.

Source: COCBot/functions/Image Search/imglocCheckWall.au3
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from mybot.log import set_debug_log
from mybot.vision.matcher import find_multiple
from mybot.vision.ocr import get_building_info


@dataclass
class WallSearchResult:
    """Result of wall detection."""
    found: bool = False
    x: int = 0
    y: int = 0
    level: int = 0


def find_wall(
    screenshot: np.ndarray,
    wall_template_dir: Path,
    target_level: int,
    last_known_pos: tuple[int, int] | None = None,
    confidence: float = 0.80,
) -> WallSearchResult:
    """Find a wall segment at a specific upgrade level.

    Translated from imglocCheckWall() in imglocCheckWall.au3.
    Uses two-phase search: local (near last position) then global.

    Args:
        screenshot: BGR screenshot of own village.
        wall_template_dir: Directory with wall level templates.
        target_level: Wall level to find.
        last_known_pos: Last known good wall position for local search.
        confidence: Template matching confidence.

    Returns:
        WallSearchResult with position and level.
    """
    # Phase 1: Local search near last known position
    if last_known_pos is not None:
        lx, ly = last_known_pos
        local_area = (
            max(0, lx - 16),
            max(0, ly - 14),
            32,
            28,
        )

        local_result = find_multiple(
            screenshot,
            wall_template_dir,
            search_area=local_area,
            min_level=target_level,
            max_level=target_level,
            max_results=4,
            confidence=confidence,
        )

        if local_result.found and local_result.first:
            m = local_result.first
            set_debug_log(f"Wall found locally at ({m.x},{m.y}) level={m.level}")
            return WallSearchResult(found=True, x=m.x, y=m.y, level=m.level)

    # Phase 2: Global search
    global_result = find_multiple(
        screenshot,
        wall_template_dir,
        min_level=target_level,
        max_level=target_level,
        max_results=10,
        confidence=confidence,
    )

    if global_result.found and global_result.first:
        m = global_result.first
        set_debug_log(f"Wall found globally at ({m.x},{m.y}) level={m.level}")
        return WallSearchResult(found=True, x=m.x, y=m.y, level=m.level)

    set_debug_log(f"No wall found at level {target_level}")
    return WallSearchResult()
