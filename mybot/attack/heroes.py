"""Hero management during battle translated from Troops/CheckHeroesHealth.au3.

Monitors hero health during battle and activates abilities when low.
Also handles hero deployment.

Source files:
- Troops/CheckHeroesHealth.au3 — health monitoring
- Troops/dropHeroes.au3 — hero deployment functions
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np

from mybot.attack.attack_bar import AttackBar, AttackBarSlot
from mybot.attack.deploy import drop_troop
from mybot.config.coordinates import (
    CHAMPION_HEALTH,
    KING_HEALTH,
    PRINCE_HEALTH,
    QUEEN_HEALTH,
    WARDEN_HEALTH,
)
from mybot.constants import HERO_SHORT_NAMES
from mybot.enums import ArmyIndex, Hero
from mybot.log import set_debug_log, set_log
from mybot.vision.pixel import check_pixel


# Hero ArmyIndex mapping
_HERO_ARMY_INDICES = [
    ArmyIndex.KING,
    ArmyIndex.QUEEN,
    ArmyIndex.PRINCE,
    ArmyIndex.WARDEN,
    ArmyIndex.CHAMPION,
    ArmyIndex.DRAGON_DUKE,
]

# Health check coordinates (x, y, color, tolerance, offset)
_HERO_HEALTH_CHECKS = [
    KING_HEALTH,
    QUEEN_HEALTH,
    PRINCE_HEALTH,
    WARDEN_HEALTH,
    CHAMPION_HEALTH,
]


@dataclass
class HeroBattleState:
    """Hero state during battle."""
    deployed: list[bool]
    ability_used: list[bool]
    health_ok: list[bool]

    def __init__(self) -> None:
        self.deployed = [False] * Hero.COUNT
        self.ability_used = [False] * Hero.COUNT
        self.health_ok = [True] * Hero.COUNT


def check_heroes_health(
    image: np.ndarray,
    attack_bar: AttackBar,
    state: HeroBattleState,
    click_func: Callable[[int, int], None] | None = None,
    auto_ability: bool = True,
) -> HeroBattleState:
    """Monitor hero health and activate abilities when needed.

    Translated from CheckHeroesHealth() in CheckHeroesHealth.au3.
    Checks each deployed hero's health bar pixel. If health is low
    (pixel no longer matches green), activates the hero's ability.

    Args:
        image: BGR screenshot during battle.
        attack_bar: Current attack bar state.
        state: Current hero battle state.
        click_func: For clicking hero ability button.
        auto_ability: Whether to auto-activate abilities.

    Returns:
        Updated HeroBattleState.
    """
    for hero_idx in range(min(Hero.COUNT, len(_HERO_HEALTH_CHECKS))):
        if not state.deployed[hero_idx]:
            continue
        if state.ability_used[hero_idx]:
            continue

        health_check = _HERO_HEALTH_CHECKS[hero_idx]
        # health_check format: (x, y, color, tolerance, offset)
        # x=-1 means position is dynamic (from attack bar slot)
        hx, hy, hcolor, htol, hoffset = health_check

        if hx == -1:
            # Get X from attack bar slot
            slot = attack_bar.get_slot(_HERO_ARMY_INDICES[hero_idx])
            if slot is None:
                continue
            hx = slot.x

        health_ok = check_pixel(image, hx, hy, hcolor, htol)
        state.health_ok[hero_idx] = health_ok

        if not health_ok and auto_ability and click_func:
            # Activate hero ability by clicking the hero slot
            slot = attack_bar.get_slot(_HERO_ARMY_INDICES[hero_idx])
            if slot:
                click_func(slot.x, slot.y)
                state.ability_used[hero_idx] = True
                set_log(f"Hero ability activated: {HERO_SHORT_NAMES[hero_idx]}")

    return state


def deploy_hero(
    click_func: Callable[[int, int], None],
    hero_index: int,
    x: int,
    y: int,
    attack_bar: AttackBar,
    state: HeroBattleState,
) -> bool:
    """Deploy a hero on the battlefield.

    Translated from dropKing(), dropQueen(), etc. in dropHeroes.au3.

    Args:
        click_func: Click function.
        hero_index: Hero enum index.
        x: Deploy X coordinate.
        y: Deploy Y coordinate.
        attack_bar: Current attack bar.
        state: Hero battle state to update.

    Returns:
        True if deployed.
    """
    if hero_index >= Hero.COUNT:
        return False

    army_idx = _HERO_ARMY_INDICES[hero_index]
    slot = attack_bar.get_slot(army_idx)

    if slot is None:
        set_debug_log(f"Deploy hero: {HERO_SHORT_NAMES[hero_index]} not in attack bar")
        return False

    # Select the hero in attack bar
    click_func(slot.x, slot.y)
    time.sleep(0.1)

    # Deploy at target position
    deployed = drop_troop(click_func, x, y, count=1)
    if deployed > 0:
        state.deployed[hero_index] = True
        set_log(f"Deployed {HERO_SHORT_NAMES[hero_index]} at ({x},{y})")
        return True

    return False
