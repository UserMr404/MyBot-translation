"""All-troops attack algorithm translated from algorithm_AllTroops.au3.

Deploys all troops along one or multiple sides of the base,
following the configured drop order.

Source: COCBot/functions/Attack/Attack Algorithms/algorithm_AllTroops.au3
"""

from __future__ import annotations

import time
from typing import Callable

from mybot.attack.attack_bar import AttackBar
from mybot.attack.deploy import drop_on_edge, drop_troop
from mybot.attack.drop_order import DEFAULT_DROP_ORDER, reorder_attack_bar
from mybot.attack.heroes import HeroBattleState, deploy_hero
from mybot.attack.timing import get_deploy_delay, get_wave_delay
from mybot.enums import ArmyIndex, Hero
from mybot.log import set_debug_log, set_log
from mybot.vision.red_area import RedArea


def algorithm_all_troops(
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
    red_area: RedArea | None = None,
    sides: str = "all",
    drop_order: list[int] | None = None,
    hero_state: HeroBattleState | None = None,
) -> HeroBattleState:
    """Deploy all troops using the AllTroops algorithm.

    Translated from algorithm_AllTroops() in algorithm_AllTroops.au3.
    Deploys troops in order along the redline/edges.

    Args:
        click_func: Click function.
        attack_bar: Current attack bar.
        red_area: Detected red deployment zone.
        sides: Which sides to deploy on ("all", "top", "bottom", etc.).
        drop_order: Custom drop order (None for default).
        hero_state: Hero tracking state.

    Returns:
        Updated HeroBattleState.
    """
    if hero_state is None:
        hero_state = HeroBattleState()

    # Get deployment points
    deploy_points = _get_deploy_points(red_area, sides)
    if not deploy_points:
        set_log("AllTroops: no deployment points available")
        return hero_state

    set_log(f"AllTroops: deploying on {len(deploy_points)} points, {sides} side(s)")

    # Reorder slots by drop order
    ordered_slots = reorder_attack_bar(attack_bar.slots, drop_order)

    for slot in ordered_slots:
        if slot.quantity <= 0:
            continue

        # Handle heroes separately
        if slot.is_hero:
            hero_idx = _army_index_to_hero(slot.index)
            if hero_idx >= 0 and deploy_points:
                px, py = deploy_points[len(deploy_points) // 2]  # Deploy hero in center
                deploy_hero(click_func, hero_idx, px, py, attack_bar, hero_state)
                time.sleep(get_wave_delay())
            continue

        # Deploy regular troops along the edge
        if slot.is_spell or slot.is_siege:
            # Deploy spells/siege in center of deployment zone
            if deploy_points:
                px, py = deploy_points[len(deploy_points) // 2]
                # Select troop
                click_func(slot.x, slot.y)
                time.sleep(0.1)
                drop_troop(click_func, px, py, slot.quantity, get_deploy_delay())
        else:
            # Select troop
            click_func(slot.x, slot.y)
            time.sleep(0.1)
            # Deploy along edge
            drop_on_edge(click_func, deploy_points, slot.quantity, delay=get_deploy_delay())

        time.sleep(get_wave_delay())

    set_log("AllTroops: deployment complete")
    return hero_state


def _get_deploy_points(
    red_area: RedArea | None,
    sides: str,
) -> list[tuple[int, int]]:
    """Get deployment points for the specified sides."""
    if red_area is None or not red_area.is_valid:
        # Fallback: screen edge points
        from mybot.vision.red_area import get_external_edge
        return get_external_edge()

    all_points = []
    sides_lower = sides.lower()

    if sides_lower in ("all", "top", "top_left"):
        all_points.extend(red_area.top_left)
    if sides_lower in ("all", "top", "top_right"):
        all_points.extend(red_area.top_right)
    if sides_lower in ("all", "bottom", "bottom_left"):
        all_points.extend(red_area.bottom_left)
    if sides_lower in ("all", "bottom", "bottom_right"):
        all_points.extend(red_area.bottom_right)

    return all_points


def _army_index_to_hero(army_index: int) -> int:
    """Map ArmyIndex to Hero enum index."""
    mapping = {
        ArmyIndex.KING: Hero.BARBARIAN_KING,
        ArmyIndex.QUEEN: Hero.ARCHER_QUEEN,
        ArmyIndex.PRINCE: Hero.MINION_PRINCE,
        ArmyIndex.WARDEN: Hero.GRAND_WARDEN,
        ArmyIndex.CHAMPION: Hero.ROYAL_CHAMPION,
        ArmyIndex.DRAGON_DUKE: Hero.DRAGON_DUKE,
    }
    return mapping.get(army_index, -1)
