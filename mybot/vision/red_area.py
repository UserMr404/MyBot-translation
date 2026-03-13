"""Red deployment zone detection translated from _GetRedArea.au3.

Detects the red deployment boundary around enemy villages during attacks.
The red area defines where troops can be deployed. The original used
DllCallMyBot("getRedArea", ...) and DllCallMyBot("SearchRedLines", ...).
This module replaces those with OpenCV color detection and contour analysis.

Source files:
- Attack/RedArea/_GetRedArea.au3 (main red area detection)
- Image Search/imglocAuxiliary.au3 (SearchRedLinesMultipleTimes)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from mybot.constants import GAME_HEIGHT, GAME_WIDTH
from mybot.log import set_debug_log
from mybot.vision.geometry import (
    get_deployable_points,
    offset_polyline,
    partition_points_by_side,
    sort_by_distance,
)


@dataclass
class RedArea:
    """Detected red deployment zone.

    Replaces the global arrays $g_aiPixelTopLeft, $g_aiPixelBottomLeft,
    $g_aiPixelTopRight, $g_aiPixelBottomRight, and their "Further" variants.
    """
    # Red line points partitioned by side
    top_left: list[tuple[int, int]] = field(default_factory=list)
    bottom_left: list[tuple[int, int]] = field(default_factory=list)
    bottom_right: list[tuple[int, int]] = field(default_factory=list)
    top_right: list[tuple[int, int]] = field(default_factory=list)

    # Offset points for ranged troop deployment (15px further out)
    top_left_further: list[tuple[int, int]] = field(default_factory=list)
    bottom_left_further: list[tuple[int, int]] = field(default_factory=list)
    bottom_right_further: list[tuple[int, int]] = field(default_factory=list)
    top_right_further: list[tuple[int, int]] = field(default_factory=list)

    @property
    def all_points(self) -> list[tuple[int, int]]:
        """All red line points combined."""
        return self.top_left + self.bottom_left + self.bottom_right + self.top_right

    @property
    def all_further_points(self) -> list[tuple[int, int]]:
        """All offset points combined."""
        return (self.top_left_further + self.bottom_left_further +
                self.bottom_right_further + self.top_right_further)

    @property
    def is_valid(self) -> bool:
        """Check if red area detection produced usable results."""
        return len(self.all_points) >= 20

    def get_side(self, side: str) -> list[tuple[int, int]]:
        """Get points for a specific side."""
        return getattr(self, side, [])

    def get_side_further(self, side: str) -> list[tuple[int, int]]:
        """Get further points for a specific side."""
        return getattr(self, f"{side}_further", [])


# ── Red Line Color Detection ────────────────────────────────────────────────

# Red line color range in HSV (the game's deployment boundary is bright red)
_RED_HSV_LOWER1 = np.array([0, 100, 100])
_RED_HSV_UPPER1 = np.array([10, 255, 255])
_RED_HSV_LOWER2 = np.array([160, 100, 100])
_RED_HSV_UPPER2 = np.array([180, 255, 255])


def detect_red_lines(
    screenshot: np.ndarray,
    min_area: int = 50,
) -> list[tuple[int, int]]:
    """Detect red deployment boundary lines in a screenshot.

    Replaces DllCallMyBot("SearchRedLines", ...) and
    SearchRedLinesMultipleTimes() from imglocAuxiliary.au3.

    Uses HSV color filtering to find the bright red deployment boundary
    that appears around enemy villages during attack preparation.

    Args:
        screenshot: BGR screenshot of attack screen.
        min_area: Minimum contour area to include (filters noise).

    Returns:
        List of (x, y) points along the red boundary.
    """
    if screenshot.size == 0:
        return []

    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

    # Red wraps around 0 in HSV, so we need two ranges
    mask1 = cv2.inRange(hsv, _RED_HSV_LOWER1, _RED_HSV_UPPER1)
    mask2 = cv2.inRange(hsv, _RED_HSV_LOWER2, _RED_HSV_UPPER2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    points = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        # Sample points along the contour
        for pt in contour:
            x, y = int(pt[0][0]), int(pt[0][1])
            points.append((x, y))

    return points


def detect_red_area(
    screenshot: np.ndarray,
    further_distance: float = 15.0,
    min_side_points: int = 10,
) -> RedArea:
    """Detect and partition the full red deployment zone.

    Replaces _GetRedArea() from _GetRedArea.au3.
    Detects the red boundary, partitions it into 4 sides, sorts points
    along each side, and generates offset points for ranged troops.

    Args:
        screenshot: BGR screenshot during attack preparation.
        further_distance: Pixel distance for ranged troop offset.
        min_side_points: Minimum points per side to consider valid.

    Returns:
        RedArea with all side data populated.
    """
    # Detect raw red line points
    raw_points = detect_red_lines(screenshot)
    if len(raw_points) < 20:
        set_debug_log(f"Red area: insufficient points ({len(raw_points)})")
        return RedArea()

    # Partition into sides
    sides = partition_points_by_side(raw_points)

    result = RedArea()

    # Sort each side's points and generate further points
    for side_name in ("top_left", "bottom_left", "bottom_right", "top_right"):
        side_points = sides[side_name]
        if len(side_points) < min_side_points:
            set_debug_log(f"Red area: {side_name} has too few points ({len(side_points)})")
            continue

        # Sort by nearest-neighbor chaining
        sorted_points = sort_by_distance(side_points)
        setattr(result, side_name, sorted_points)

        # Generate offset points for ranged troops
        further = offset_polyline(sorted_points, further_distance, outward=True)
        setattr(result, f"{side_name}_further", further)

    return result


def detect_red_area_near_building(
    screenshot: np.ndarray,
    building_type: str,
    building_pos: tuple[int, int] | None = None,
) -> list[tuple[int, int]]:
    """Detect red area points near a specific building.

    Replaces DllCallMyBot("getRedAreaSideBuilding", ...) from _GetRedArea.au3.
    Used for targeted attacks (e.g., attack from the Dark Elixir Storage side
    or Town Hall side).

    Args:
        screenshot: BGR screenshot.
        building_type: Building to target ("TH", "DES", etc.).
        building_pos: Known building position. If None, auto-detects.

    Returns:
        Red line points on the side nearest to the building.
    """
    red_area = detect_red_area(screenshot)
    if not red_area.is_valid:
        return []

    if building_pos is None:
        return red_area.all_points

    bx, by = building_pos

    # Find which side is closest to the building
    best_side = ""
    best_dist = float("inf")

    for side_name in ("top_left", "bottom_left", "bottom_right", "top_right"):
        side_points = red_area.get_side(side_name)
        if not side_points:
            continue
        # Average distance from side points to building
        avg_dist = sum(
            ((px - bx) ** 2 + (py - by) ** 2) ** 0.5
            for px, py in side_points
        ) / len(side_points)
        if avg_dist < best_dist:
            best_dist = avg_dist
            best_side = side_name

    return red_area.get_side(best_side) if best_side else []


# ── External Green Zone (Fallback) ───────────────────────────────────────────

# Fixed external boundary corners from _GetRedArea.au3
# Used as fallback when red line detection fails
EXTERNAL_CORNERS = {
    "top": (430, 2),
    "right": (848, 340),
    "bottom": (430, 672),
    "left": (2, 340),
}


def get_external_edge(
    side: str,
    point_count: int = 20,
) -> list[tuple[int, int]]:
    """Generate deployment points along the external edge of the game screen.

    Used as fallback when red line detection fails.
    From _GetVectorOutZone() in _GetRedArea.au3.

    Args:
        side: "top_left", "bottom_left", "bottom_right", or "top_right".
        point_count: Number of points to generate.

    Returns:
        List of (x, y) points along the outer edge.
    """
    corners = EXTERNAL_CORNERS

    if side == "top_left":
        start, end = corners["top"], corners["left"]
    elif side == "bottom_left":
        start, end = corners["left"], corners["bottom"]
    elif side == "bottom_right":
        start, end = corners["bottom"], corners["right"]
    elif side == "top_right":
        start, end = corners["right"], corners["top"]
    else:
        return []

    points = []
    for i in range(point_count):
        t = i / max(1, point_count - 1)
        x = int(start[0] + (end[0] - start[0]) * t)
        y = int(start[1] + (end[1] - start[1]) * t)
        points.append((x, y))

    return points
