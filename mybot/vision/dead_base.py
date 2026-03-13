"""Dead base detection translated from Image Search/checkDeadBase.au3.

Identifies abandoned (dead) villages by detecting full resource collectors.
Dead bases have collectors that appear visually "full" because no one has
raided them recently, making them attractive targets.

Source: COCBot/functions/Image Search/checkDeadBase.au3
"""

from __future__ import annotations

from pathlib import Path

from mybot.log import set_debug_log, set_log
from mybot.vision.matcher import MatchResult, find_multiple

import numpy as np


def check_dead_base(
    screenshot: np.ndarray,
    collector_fill_dir: Path,
    collector_level_dir: Path,
    min_collector_matches: int = 3,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.80,
) -> bool:
    """Check if an enemy village is a dead (abandoned) base.

    Translated from checkDeadBaseQuick() in checkDeadBase.au3.
    Searches for filled elixir collectors and verifies their levels.
    A base is considered dead if enough filled collectors are found.

    Algorithm:
    1. Search for filled elixir collector images in the screenshot
    2. For each filled collector found, search for collector level near it
    3. Count verified collector matches
    4. Return True if count >= min_collector_matches

    Args:
        screenshot: BGR screenshot of enemy village.
        collector_fill_dir: Path to filled collector template directory
                           (imgxml/deadbase/ or similar).
        collector_level_dir: Path to collector level template directory.
        min_collector_matches: Minimum filled collectors to confirm dead base.
        search_area: Optional search area restriction.
        confidence: Template matching confidence threshold.

    Returns:
        True if the base appears to be dead/abandoned.
    """
    # Step 1: Search for filled collectors
    fill_result = find_multiple(
        screenshot,
        collector_fill_dir,
        search_area=search_area,
        confidence=confidence,
    )

    if not fill_result.found:
        set_debug_log("Dead base check: no filled collectors found")
        return False

    set_debug_log(f"Dead base check: found {fill_result.total_objects} filled collectors")

    # Step 2: Verify collector levels near each filled collector
    verified_count = 0

    for match in fill_result.matches:
        # Search for collector level templates near this collector
        # Use a small search area around the filled collector
        level_area = (
            max(0, match.x - 30),
            max(0, match.y - 30),
            60,  # width
            60,  # height
        )

        level_result = find_multiple(
            screenshot,
            collector_level_dir,
            search_area=level_area,
            max_results=1,
            confidence=confidence,
        )

        if level_result.found:
            verified_count += 1
            set_debug_log(
                f"Dead base: verified collector at ({match.x},{match.y}) "
                f"level={level_result.first.level if level_result.first else '?'}"
            )

    # If no level templates available, use fill count alone
    if verified_count == 0 and fill_result.total_objects >= min_collector_matches:
        set_debug_log("Dead base: using fill count without level verification")
        return True

    is_dead = verified_count >= min_collector_matches
    set_debug_log(f"Dead base check: {verified_count}/{min_collector_matches} verified → {'DEAD' if is_dead else 'LIVE'}")
    return is_dead


def check_dead_eagle(
    screenshot: np.ndarray,
    eagle_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.80,
) -> bool:
    """Check for a Dead Eagle Artillery (alternative dead base indicator).

    Translated from CheckForDeadEagle() in checkDeadBase.au3.
    TH13+ bases can be identified as dead by checking if the Eagle
    Artillery appears inactive/dead.

    Args:
        screenshot: BGR screenshot.
        eagle_dir: Path to Dead Eagle template directory.
        search_area: Optional search area.
        confidence: Matching confidence.

    Returns:
        True if dead eagle is detected.
    """
    result = find_multiple(
        screenshot,
        eagle_dir,
        search_area=search_area,
        max_results=1,
        confidence=confidence,
    )
    if result.found:
        set_debug_log(f"Dead Eagle found at ({result.first.x},{result.first.y})")
    return result.found


def has_elixir_storage(
    screenshot: np.ndarray,
    storage_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.80,
) -> bool:
    """Check if the base has an elixir storage building.

    Translated from hasElixirStorage() in checkDeadBase.au3.
    Used in conjunction with collector detection.

    Args:
        screenshot: BGR screenshot.
        storage_dir: Path to elixir storage template directory.
        search_area: Optional search area.
        confidence: Matching confidence.

    Returns:
        True if elixir storage is detected.
    """
    result = find_multiple(
        screenshot,
        storage_dir,
        search_area=search_area,
        max_results=1,
        confidence=confidence,
    )
    return result.found
