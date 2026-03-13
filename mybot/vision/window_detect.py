"""Game window and dialog detection translated from Image Search/IsWindowOpen.au3.

Detects whether specific game UI windows, dialogs, or popups are currently
open by searching for their characteristic template images (close buttons,
header images, etc.).

Source: COCBot/functions/Image Search/IsWindowOpen.au3
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mybot.constants import GAME_HEIGHT, GAME_WIDTH
from mybot.log import set_debug_log
from mybot.vision.matcher import MatchResult, find_image, find_multiple


def is_window_open(
    screenshot: np.ndarray,
    template_path: Path,
    search_area: tuple[int, int, int, int] | None = None,
    max_attempts: int = 1,
    confidence: float = 0.85,
) -> tuple[bool, int, int]:
    """Check if a game window/dialog is open.

    Translated from IsWindowOpen() in IsWindowOpen.au3.
    Searches for a template image (typically a close button or header)
    to determine if a specific window is currently displayed.

    Default search area is the center 50% of the game screen (where
    most dialogs appear).

    Args:
        screenshot: BGR screenshot.
        template_path: Path to template image or directory.
        search_area: Optional (x, y, w, h) search region.
                     None uses center 50% of screen.
        max_attempts: Number of detection attempts.
        confidence: Minimum match confidence.

    Returns:
        (is_open, x, y) — whether window was found and its coordinates.
    """
    # Default search area: center 50% of screen
    if search_area is None:
        margin_x = GAME_WIDTH // 4
        margin_y = 0
        search_area = (margin_x, margin_y, GAME_WIDTH // 2, GAME_HEIGHT // 2)

    for attempt in range(max_attempts):
        if template_path.is_dir():
            result = find_multiple(
                screenshot,
                template_path,
                search_area=search_area,
                max_results=1,
                confidence=confidence,
            )
            if result.found and result.first:
                return True, result.first.x, result.first.y
        else:
            match = find_image(
                screenshot,
                template_path,
                search_area=search_area,
                confidence=confidence,
            )
            if match:
                return True, match.x, match.y

    return False, 0, 0


def find_close_button(
    screenshot: np.ndarray,
    close_button_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.85,
) -> tuple[bool, int, int]:
    """Find the close button (X) on an open window.

    Translated from CloseWindow() in IsWindowOpen.au3.
    The close button is typically a red/white X in the top-right
    corner of game dialogs.

    Args:
        screenshot: BGR screenshot.
        close_button_dir: Directory of close button templates.
        search_area: Optional search region. None = right half of screen.
        confidence: Minimum match confidence.

    Returns:
        (found, x, y) — button location.
    """
    if search_area is None:
        # Close buttons are typically in the right half, upper area
        search_area = (GAME_WIDTH // 2, 0, GAME_WIDTH // 2, GAME_HEIGHT // 2)

    result = find_multiple(
        screenshot,
        close_button_dir,
        search_area=search_area,
        max_results=1,
        confidence=confidence,
    )

    if result.found and result.first:
        return True, result.first.x, result.first.y
    return False, 0, 0
