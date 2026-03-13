"""Attack preparation translated from Attack/PrepareAttack.au3.

Sets up the attack: reads the troop bar, selects attack mode,
and prepares deployment data.

Source: COCBot/functions/Attack/PrepareAttack.au3
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from mybot.attack.attack_bar import AttackBar, get_attack_bar
from mybot.enums import MatchMode
from mybot.log import set_debug_log, set_log
from mybot.vision.red_area import RedArea, detect_red_area


@dataclass
class AttackPlan:
    """Prepared attack plan with troop bar and deployment zones."""
    attack_bar: AttackBar = field(default_factory=AttackBar)
    red_area: RedArea | None = None
    match_mode: MatchMode = MatchMode.DEAD_BASE
    ready: bool = False
    error: str = ""


def prepare_attack(
    capture_func: Callable[[], np.ndarray | None],
    match_mode: MatchMode = MatchMode.DEAD_BASE,
) -> AttackPlan:
    """Prepare for attack after a base is found.

    Translated from PrepareAttack() in PrepareAttack.au3.
    Reads the attack bar, detects the red deployment zone, and
    builds an attack plan.

    Args:
        capture_func: Returns BGR screenshot.
        match_mode: Attack mode (dead base, live base, etc.).

    Returns:
        AttackPlan with troop bar and deployment data.
    """
    plan = AttackPlan(match_mode=match_mode)

    image = capture_func()
    if image is None:
        plan.error = "Failed to capture screenshot"
        return plan

    # Step 1: Read the attack bar
    set_debug_log("PrepareAttack: reading attack bar")
    plan.attack_bar = get_attack_bar(image)

    if not plan.attack_bar.slots:
        plan.error = "No troops found in attack bar"
        set_log("PrepareAttack: no troops in attack bar")
        return plan

    set_log(f"Attack bar: {len(plan.attack_bar.slots)} troop types, "
            f"{plan.attack_bar.total_troops} total")

    # Step 2: Detect red deployment zone
    set_debug_log("PrepareAttack: detecting red area")
    plan.red_area = detect_red_area(image)

    if plan.red_area is None or not plan.red_area.is_valid:
        set_debug_log("PrepareAttack: red area detection failed, using fallback")

    plan.ready = True
    return plan
