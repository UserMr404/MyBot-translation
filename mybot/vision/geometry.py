"""Geometry utilities for village coordinates and deployment zones.

Translated from:
- MBRFunc.au3 — ConvertVillagePos, ConvertToVillagePos, ConvertFromVillagePos
- imglocAuxiliary.au3 — GetDeployableNextTo, GetOffSetRedline
- _GetRedArea.au3 — GetPixelDistance, GetPixelSection, SortByDistance

These functions handle coordinate transformations between screen space and
village space, and geometry calculations for troop deployment zones.
"""

from __future__ import annotations

import math

import numpy as np

from mybot.constants import GAME_HEIGHT, GAME_WIDTH


# ── Coordinate Transformations ───────────────────────────────────────────────
# The game uses a diamond-shaped isometric view. Village coordinates differ
# from screen pixel coordinates based on zoom level and scroll offset.

def screen_to_village(
    x: int,
    y: int,
    offset: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> tuple[float, float]:
    """Convert screen coordinates to village coordinates.

    Replaces ConvertToVillagePos() from MBRFunc.au3.
    Adjusts for the current village scroll offset and zoom level.

    Args:
        x: Screen X coordinate.
        y: Screen Y coordinate.
        offset: Village offset (offset_x, offset_y, zoom_factor).

    Returns:
        (village_x, village_y) in village coordinate space.
    """
    ox, oy, zoom = offset
    if zoom == 0:
        zoom = 1.0

    # Center of game screen
    cx = GAME_WIDTH / 2
    cy = GAME_HEIGHT / 2

    vx = (x - cx) / zoom + cx - ox
    vy = (y - cy) / zoom + cy - oy
    return vx, vy


def village_to_screen(
    vx: float,
    vy: float,
    offset: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> tuple[int, int]:
    """Convert village coordinates to screen coordinates.

    Replaces ConvertFromVillagePos() from MBRFunc.au3.

    Args:
        vx: Village X coordinate.
        vy: Village Y coordinate.
        offset: Village offset (offset_x, offset_y, zoom_factor).

    Returns:
        (screen_x, screen_y) in screen pixel coordinates.
    """
    ox, oy, zoom = offset
    if zoom == 0:
        zoom = 1.0

    cx = GAME_WIDTH / 2
    cy = GAME_HEIGHT / 2

    sx = int((vx + ox - cx) * zoom + cx)
    sy = int((vy + oy - cy) * zoom + cy)
    return sx, sy


# ── Pixel Section / Quadrant ─────────────────────────────────────────────────

def get_pixel_section(x: int, y: int) -> int:
    """Determine which quadrant a point belongs to.

    Translated from GetPixelSection() in _GetRedArea.au3.
    Divides the game screen into 4 quadrants for red line partitioning:
    1 = Top-Left, 2 = Bottom-Left, 3 = Bottom-Right, 4 = Top-Right

    The division follows the village diamond axes, not simple screen halves.

    Args:
        x: Screen X coordinate.
        y: Screen Y coordinate.

    Returns:
        Quadrant number (1-4).
    """
    # Diamond center
    cx = GAME_WIDTH / 2  # 430
    cy = GAME_HEIGHT / 2  # 366

    # Relative position
    dx = x - cx
    dy = y - cy

    # Diamond axes: the isometric grid rotates 45 degrees
    # The dividing lines go through the center at ~26.5 degree angles
    # matching the 2:1 aspect ratio of the isometric diamond
    if dy < -abs(dx) * (cy / cx):
        return 1 if dx <= 0 else 4  # Top half
    elif dx <= 0:
        return 2  # Bottom-left
    else:
        return 3  # Bottom-right


# ── Distance and Sorting ─────────────────────────────────────────────────────

def pixel_distance(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    """Euclidean distance between two points.

    Translated from GetPixelDistance() in _GetRedArea.au3.
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def polyline_length(points: list[tuple[int, int]]) -> float:
    """Total length of a polyline through the given points.

    Translated from GetPixelListDistance() in _GetRedArea.au3.
    """
    if len(points) < 2:
        return 0.0
    total = 0.0
    for i in range(len(points) - 1):
        total += pixel_distance(points[i], points[i + 1])
    return total


def sort_by_distance(
    points: list[tuple[int, int]],
    start: tuple[int, int] | None = None,
    max_jump_factor: float = 10.0,
) -> list[tuple[int, int]]:
    """Sort points by chaining nearest neighbors.

    Translated from SortByDistance() in _GetRedArea.au3.
    Starting from a point, picks the closest unvisited point as next.
    Removes outlier points that jump too far (> max_jump_factor * average).

    Args:
        points: Unordered list of (x, y) points.
        start: Starting point. None = use first point.
        max_jump_factor: Skip points that jump more than this * average distance.

    Returns:
        Ordered list of points along the path.
    """
    if len(points) <= 1:
        return list(points)

    remaining = list(points)
    current = start if start else remaining[0]
    if current in remaining:
        remaining.remove(current)

    ordered = [current]
    distances: list[float] = []

    while remaining:
        # Find closest point
        min_dist = float("inf")
        closest_idx = 0
        for i, pt in enumerate(remaining):
            d = pixel_distance(current, pt)
            if d < min_dist:
                min_dist = d
                closest_idx = i

        distances.append(min_dist)
        current = remaining.pop(closest_idx)
        ordered.append(current)

    # Remove outlier jumps
    if len(distances) > 2:
        avg_dist = sum(distances) / len(distances)
        if avg_dist > 0:
            filtered = [ordered[0]]
            for i, (pt, d) in enumerate(zip(ordered[1:], distances)):
                if d <= avg_dist * max_jump_factor:
                    filtered.append(pt)
            return filtered

    return ordered


# ── Deployment Zone Geometry ─────────────────────────────────────────────────

def offset_polyline(
    points: list[tuple[int, int]],
    distance: float,
    outward: bool = True,
) -> list[tuple[int, int]]:
    """Offset a polyline by a fixed distance outward or inward.

    Translated from GetOffSetRedline() / _GetOffsetTroopFurther() in _GetRedArea.au3.
    Creates a parallel line for ranged troop deployment (e.g., archers
    deploy further back from the red line than melee troops).

    Args:
        points: Ordered list of polyline points.
        distance: Offset distance in pixels.
        outward: True for outward (away from village center), False for inward.

    Returns:
        Offset polyline points.
    """
    if len(points) < 2:
        return list(points)

    # Village center for determining "outward" direction
    cx = GAME_WIDTH / 2
    cy = GAME_HEIGHT / 2

    result = []
    for i, (px, py) in enumerate(points):
        # Normal direction: perpendicular to the line segment
        if i == 0:
            dx = points[1][0] - px
            dy = points[1][1] - py
        elif i == len(points) - 1:
            dx = px - points[-2][0]
            dy = py - points[-2][1]
        else:
            dx = points[i + 1][0] - points[i - 1][0]
            dy = points[i + 1][1] - points[i - 1][1]

        # Perpendicular direction
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            result.append((px, py))
            continue

        # Normal vector (perpendicular)
        nx = -dy / length
        ny = dx / length

        # Determine if normal points outward (away from center)
        to_center_x = cx - px
        to_center_y = cy - py
        dot = nx * to_center_x + ny * to_center_y

        if outward:
            # Normal should point away from center (negative dot)
            if dot > 0:
                nx, ny = -nx, -ny
        else:
            # Normal should point toward center (positive dot)
            if dot < 0:
                nx, ny = -nx, -ny

        ox = int(px + nx * distance)
        oy = int(py + ny * distance)
        result.append((ox, oy))

    return result


def get_deployable_points(
    redline: list[tuple[int, int]],
    count: int = 5,
    distance: float = 5.0,
) -> list[tuple[int, int]]:
    """Get evenly spaced deployable points near the red line.

    Translated from GetDeployableNextTo() in imglocAuxiliary.au3.
    Returns points along the red line offset outward by `distance`.

    Args:
        redline: Red line points.
        count: Number of points to return.
        distance: Offset distance from red line.

    Returns:
        List of (x, y) deployment points.
    """
    if not redline:
        return []

    # Offset the redline outward
    offset_line = offset_polyline(redline, distance, outward=True)
    if not offset_line:
        return []

    if len(offset_line) <= count:
        return offset_line

    # Sample evenly spaced points
    step = len(offset_line) / count
    return [offset_line[int(i * step)] for i in range(count)]


# ── Side Partitioning ────────────────────────────────────────────────────────

def partition_points_by_side(
    points: list[tuple[int, int]],
) -> dict[str, list[tuple[int, int]]]:
    """Partition red line points into 4 sides.

    Translated from the red line partitioning in _GetRedArea.au3.
    Assigns each point to one of: top_left, bottom_left, bottom_right, top_right
    based on its quadrant relative to the village center.

    Args:
        points: Red line points.

    Returns:
        Dict with keys "top_left", "bottom_left", "bottom_right", "top_right".
    """
    sides: dict[str, list[tuple[int, int]]] = {
        "top_left": [],
        "bottom_left": [],
        "bottom_right": [],
        "top_right": [],
    }

    section_map = {
        1: "top_left",
        2: "bottom_left",
        3: "bottom_right",
        4: "top_right",
    }

    for pt in points:
        section = get_pixel_section(pt[0], pt[1])
        side_name = section_map.get(section, "top_left")
        sides[side_name].append(pt)

    return sides
