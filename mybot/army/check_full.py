"""Army fullness check translated from CreateArmy/CheckFullArmy.au3.

Determines whether the army is fully trained and ready for battle.

Source: COCBot/functions/CreateArmy/CheckFullArmy.au3
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mybot.log import set_debug_log, set_log


def check_full_army(
    image: np.ndarray,
    army_overview_open: bool = False,
) -> bool:
    """Check if the army is fully trained.

    Translated from CheckFullArmy() in CheckFullArmy.au3.
    Detects the "army is full" indicator in the army overview
    or on the main screen army camp button.

    Args:
        image: BGR screenshot.
        army_overview_open: Whether army overview is currently open.

    Returns:
        True if army is full and ready for battle.
    """
    full_dir = Path("imgxml/ArmyOverview/ArmyFull")

    if full_dir.is_dir():
        from mybot.vision.matcher import find_image
        result = find_image(image, full_dir, confidence=0.85)
        if result is not None:
            set_debug_log("Army is FULL (template match)")
            return True

    # Fallback: read army camp capacity via OCR
    if army_overview_open:
        from mybot.vision.ocr import read_text
        # Camp capacity text region (e.g., "200/200")
        text = read_text(image, 330, 200, 130, 22, whitelist="0123456789/")
        if "/" in text:
            parts = text.split("/")
            try:
                current = int(parts[0].strip())
                total = int(parts[1].strip())
                if current >= total > 0:
                    set_debug_log(f"Army is FULL ({current}/{total})")
                    return True
                else:
                    set_debug_log(f"Army {current}/{total} — not full")
            except ValueError:
                pass

    return False
