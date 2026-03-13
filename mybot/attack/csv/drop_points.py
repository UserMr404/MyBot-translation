"""Drop point calculation for CSV attacks.

Translated from AttackCSV/MakeDropPoints.au3.
Calculates deployment coordinates from MAKE vector definitions
using the red area deployment zone.

Source: COCBot/functions/Attack/AttackCSV/MakeDropPoints.au3
"""

from __future__ import annotations

from mybot.attack.csv.parser import AttackVector
from mybot.log import set_debug_log
from mybot.vision.red_area import RedArea


def make_drop_points(
    vector: AttackVector,
    red_area: RedArea | None,
) -> list[tuple[int, int]]:
    """Calculate drop points for a deployment vector.

    Translated from MakeDropPoints() in MakeDropPoints.au3.
    Uses the red area sides and vector configuration to generate
    evenly-spaced deployment coordinates.

    Args:
        vector: Vector definition from MAKE command.
        red_area: Detected red deployment zone.

    Returns:
        List of (x, y) deployment coordinates.
    """
    # Get base points from the appropriate red area side
    side_points = _get_side_points(vector.side, red_area)

    if not side_points:
        set_debug_log(f"MakeDropPoints: no points for side '{vector.side}'")
        return []

    # Generate evenly-spaced subset
    num = max(1, vector.num_points)
    if len(side_points) <= num:
        points = list(side_points)
    else:
        step = len(side_points) / num
        points = [side_points[int(i * step)] for i in range(num)]

    # Apply offset (move points further from base)
    if vector.offset != 0:
        from mybot.vision.geometry import offset_polyline
        points = offset_polyline(points, vector.offset)

    # Reverse if needed
    if vector.direction == "reverse":
        points.reverse()

    set_debug_log(f"MakeDropPoints: vector '{vector.name}' = {len(points)} points")
    return points


def _get_side_points(
    side: str,
    red_area: RedArea | None,
) -> list[tuple[int, int]]:
    """Get deployment points for a named side."""
    if red_area is None or not red_area.is_valid:
        from mybot.vision.red_area import get_external_edge
        return get_external_edge()

    side_lower = side.lower().strip()

    mapping = {
        "top-left": red_area.top_left,
        "top_left": red_area.top_left,
        "tl": red_area.top_left,
        "top-right": red_area.top_right,
        "top_right": red_area.top_right,
        "tr": red_area.top_right,
        "bottom-left": red_area.bottom_left,
        "bottom_left": red_area.bottom_left,
        "bl": red_area.bottom_left,
        "bottom-right": red_area.bottom_right,
        "bottom_right": red_area.bottom_right,
        "br": red_area.bottom_right,
        "top": red_area.top_left + red_area.top_right,
        "bottom": red_area.bottom_left + red_area.bottom_right,
        "left": red_area.top_left + red_area.bottom_left,
        "right": red_area.top_right + red_area.bottom_right,
    }

    points = mapping.get(side_lower)
    if points is not None:
        return points

    # Default: all sides
    return (
        red_area.top_left + red_area.top_right +
        red_area.bottom_right + red_area.bottom_left
    )
