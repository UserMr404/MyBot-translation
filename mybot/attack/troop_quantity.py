"""Troop quantity reading translated from Troops/ReadTroopQuantity.au3.

Reads troop counts from the attack bar during battle.

Source: COCBot/functions/Attack/Troops/ReadTroopQuantity.au3
"""

from __future__ import annotations

import numpy as np

from mybot.vision.ocr import read_number


def read_troop_quantity(
    image: np.ndarray,
    slot_x: int,
    slot_y: int,
) -> int:
    """Read troop quantity from an attack bar slot.

    Translated from ReadTroopQuantity() in ReadTroopQuantity.au3.
    Reads the small number displayed on each troop slot.

    Args:
        image: BGR screenshot.
        slot_x: Center X of the troop slot.
        slot_y: Center Y of the troop slot.

    Returns:
        Quantity (default 1 if unreadable).
    """
    return read_number(image, slot_x - 12, slot_y + 22, 24, 14, default=1)
