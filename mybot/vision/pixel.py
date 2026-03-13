"""Pixel operations translated from COCBot/functions/Pixels/.

Source files:
- _GetPixelColor.au3 — get_pixel_color()
- _CheckPixel.au3 — check_pixel()
- _ColorCheck.au3 — color_check()
- _PixelSearch.au3 — pixel_search()
- _MultiPixelSearch.au3 — multi_pixel_search()
- isInsideDiamond.au3 — is_inside_diamond()
- GetListPixel.au3 — parse_pixel_list()

Note: get_pixel_color, check_pixel, pixel_search, multi_pixel_search are
already implemented in android/capture.py from Phase 2. This module adds
the remaining pixel functions and re-exports for convenience.
"""

from __future__ import annotations

import numpy as np

# Re-export Phase 2 pixel functions for convenience
from mybot.android.capture import (
    check_pixel,
    get_pixel_color,
    multi_pixel_search,
    pixel_search,
)

__all__ = [
    "check_pixel",
    "color_check",
    "get_pixel_color",
    "is_inside_diamond",
    "multi_pixel_search",
    "parse_pixel_list",
    "pixel_search",
]


def color_check(
    color1: int | str,
    color2: int | str,
    tolerance: int = 5,
    ignore: str = "",
) -> bool:
    """Compare two colors with per-channel tolerance.

    Translated from _ColorCheck() in _ColorCheck.au3.
    Supports optional channel masking via the `ignore` parameter.

    The AutoIt version uses hex strings ("RRBBGG" — note: non-standard order
    where bytes are R, B, G from left to right in the hex string).
    This function accepts both hex strings and 0xBBGGRR integers.

    Args:
        color1: First color (hex string "RRBBGG" or 0xBBGGRR int).
        color2: Second color (hex string "RRBBGG" or 0xBBGGRR int).
        tolerance: Maximum difference per channel (default 5).
        ignore: Channel mask — "" for all channels, "Red" to skip red,
                "Heroes" to skip blue, "Red+Blue" to skip both.

    Returns:
        True if colors match within tolerance on compared channels.
    """
    r1, g1, b1 = _parse_color(color1)
    r2, g2, b2 = _parse_color(color2)

    ignore_lower = ignore.lower()

    # Check red channel (unless ignored)
    if "red" not in ignore_lower:
        if abs(r1 - r2) > tolerance:
            return False

    # Check green channel (always checked)
    if abs(g1 - g2) > tolerance:
        return False

    # Check blue channel (unless ignored via "heroes" or "blue")
    if "heroes" not in ignore_lower and "blue" not in ignore_lower:
        if abs(b1 - b2) > tolerance:
            return False

    return True


def _parse_color(color: int | str) -> tuple[int, int, int]:
    """Parse a color into (R, G, B) components.

    Handles:
    - Integer 0xBBGGRR format (AutoIt COLORREF)
    - Hex string "RRBBGG" format (AutoIt _GetPixelColor return)
    - Hex string "RRGGBB" format (standard)
    """
    if isinstance(color, str):
        color = color.lstrip("#").lstrip("0x")
        if len(color) == 6:
            # AutoIt _ColorCheck uses Dec(StringMid(hex, 1, 2)) for "Red"
            # Dec(StringMid(hex, 3, 2)) for "Blue", Dec(StringMid(hex, 5, 2)) for "Green"
            # So the hex string format is RRBBGG
            r = int(color[0:2], 16)
            b = int(color[2:4], 16)
            g = int(color[4:6], 16)
            return r, g, b
        return 0, 0, 0

    # Integer 0xBBGGRR format
    r = color & 0xFF
    g = (color >> 8) & 0xFF
    b = (color >> 16) & 0xFF
    return r, g, b


def is_inside_diamond(
    x: int,
    y: int,
    diamond: tuple[int, int, int, int] | None = None,
    check_ui_zones: bool = True,
    bottom_offset_y: int = 0,
) -> bool:
    """Check if a point is inside the village diamond boundary.

    Translated from isInsideDiamond() in isInsideDiamond.au3.
    The village playable area is a diamond shape on the 860x732 game screen.
    Points inside the diamond but within protected UI zones (buttons, chat)
    are considered outside for click safety.

    Args:
        x: X coordinate.
        y: Y coordinate.
        diamond: (left, top, right, bottom) diamond bounds.
                 None uses default village diamond.
        check_ui_zones: If True, exclude protected UI button areas.
        bottom_offset_y: Y offset for bottom UI elements ($g_iBottomOffsetY).

    Returns:
        True if point is inside the deployable diamond area.
    """
    # Default village diamond bounds (from ScreenCoordinates.au3)
    if diamond is None:
        diamond = (18, 18, 840, 596)

    left, top, right, bottom = diamond

    # Diamond center
    mid_x = (left + right) / 2
    mid_y = (top + bottom) / 2

    # Half-widths
    half_w = (right - left) / 2
    half_h = (bottom - top) / 2

    if half_w <= 0 or half_h <= 0:
        return False

    # Standard diamond containment: |dx/half_w| + |dy/half_h| <= 1
    dx = abs(x - mid_x)
    dy = abs(y - mid_y)

    if dx / half_w + dy / half_h > 1:
        return False

    # Check protected UI zones (from isInsideDiamond.au3 lines 81-93)
    if check_ui_zones:
        # War button zone: bottom-left
        if x < 82 and y > 427 + bottom_offset_y:
            return False

        # Chat tab: left side
        if x < 72 and 270 + bottom_offset_y <= y <= 345 + bottom_offset_y:
            return False

        # Builder/Shield buttons: top area
        if y < 63:
            return False

        # Gems button: right side
        if x > 692 and 126 + bottom_offset_y <= y <= 180 + bottom_offset_y:
            return False

    return True


def parse_pixel_list(
    pixel_string: str,
    coord_delim: str = "-",
    pair_delim: str = "|",
) -> list[tuple[int, int]]:
    """Parse a pipe-delimited list of pixel coordinates.

    Translated from GetListPixel() in GetListPixel.au3.
    The AutoIt version parses strings like "123-456|789-012" into
    arrays of [x, y] coordinate pairs.

    Args:
        pixel_string: Coordinate string (e.g., "123-456|789-012").
        coord_delim: Delimiter between x and y (default "-").
        pair_delim: Delimiter between pairs (default "|").

    Returns:
        List of (x, y) coordinate tuples.
    """
    if not pixel_string:
        return []

    result = []
    for pair in pixel_string.split(pair_delim):
        pair = pair.strip()
        if not pair:
            continue
        parts = pair.split(coord_delim)
        if len(parts) >= 2:
            try:
                x = int(parts[0].strip())
                y = int(parts[1].strip())
                result.append((x, y))
            except ValueError:
                continue
    return result


def check_pixel_list(
    image: np.ndarray,
    pixels: list[tuple[int, int, int, int]],
) -> bool:
    """Check multiple pixel positions against expected colors.

    Each entry in pixels is (x, y, expected_color, tolerance).
    Returns True only if ALL pixels match.

    Args:
        image: BGR numpy array.
        pixels: List of (x, y, color, tolerance) tuples.

    Returns:
        True if all pixels match within tolerance.
    """
    for x, y, expected, tol in pixels:
        if not check_pixel(image, x, y, expected, tol):
            return False
    return True
