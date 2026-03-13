"""Town Hall detection translated from Image Search/imglocTHSearch.au3.

Locates and identifies the Town Hall building on enemy villages.
Returns the TH position, level, and nearby deployment points.

Source: COCBot/functions/Image Search/imglocTHSearch.au3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from mybot.log import set_debug_log, set_log
from mybot.vision.geometry import get_deployable_points
from mybot.vision.matcher import MatchResult, find_multiple


@dataclass
class TownHallResult:
    """Town Hall detection result.

    Replaces the global variables $g_iTHx, $g_iTHy, $g_iImglocTHLevel,
    $IMGLOCTHLOCATION, $IMGLOCTHNEAR, $IMGLOCTHFAR.
    """
    found: bool = False
    x: int = 0
    y: int = 0
    level: int = 0
    confidence: float = 0.0
    near_points: list[tuple[int, int]] = field(default_factory=list)
    far_points: list[tuple[int, int]] = field(default_factory=list)


def find_town_hall(
    screenshot: np.ndarray,
    th_dirs: list[Path],
    search_area: tuple[int, int, int, int] | None = None,
    redline: list[tuple[int, int]] | None = None,
    max_retries: int = 4,
    confidence: float = 0.80,
) -> TownHallResult:
    """Locate the Town Hall on an enemy village.

    Translated from imglocTHSearch() in imglocTHSearch.au3.
    Searches multiple template directories (normal TH, snow TH, TH2 variants)
    and returns the best match.

    Args:
        screenshot: BGR screenshot of enemy village.
        th_dirs: List of template directories to search
                 (e.g., [imgxml/Buildings/Townhall/, imgxml/Buildings/Townhall2/]).
        search_area: Optional (x, y, w, h) to restrict search.
        redline: Red line points for calculating near/far deployment points.
        max_retries: Number of search retries if not found.
        confidence: Minimum match confidence.

    Returns:
        TownHallResult with position, level, and deployment points.
    """
    result = TownHallResult()

    best_match: MatchResult | None = None

    for attempt in range(max_retries):
        for th_dir in th_dirs:
            if not th_dir.is_dir():
                continue

            search_result = find_multiple(
                screenshot,
                th_dir,
                search_area=search_area,
                max_results=5,
                confidence=confidence,
            )

            if not search_result.found:
                continue

            # Select the highest level match (or highest confidence if same level)
            for match in search_result.matches:
                if best_match is None:
                    best_match = match
                elif match.level > best_match.level:
                    best_match = match
                elif match.level == best_match.level and match.confidence > best_match.confidence:
                    best_match = match

        if best_match is not None:
            break

        set_debug_log(f"TH search attempt {attempt + 1}/{max_retries}: not found, retrying")

    if best_match is None:
        set_debug_log("Town Hall not found after all retries")
        return result

    result.found = True
    result.x = best_match.x
    result.y = best_match.y
    result.level = best_match.level
    result.confidence = best_match.confidence

    # Calculate deployment points near TH
    if redline:
        result.near_points = get_deployable_points(redline, count=5, distance=5.0)
        result.far_points = get_deployable_points(redline, count=5, distance=25.0)

    set_debug_log(f"Town Hall found: level={result.level} at ({result.x},{result.y}) conf={result.confidence:.2f}")
    return result


def reset_th_search() -> TownHallResult:
    """Return a reset/empty TH result.

    Translated from ResetTHsearch() in imglocTHSearch.au3.
    """
    return TownHallResult()
