"""Smart Farm attack algorithm translated from SmartFarm.au3.

Intelligent farming that targets resource collectors by deploying
troops near the highest concentration of loot buildings.

Source: COCBot/functions/Attack/Attack Algorithms/SmartFarm.au3
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.attack.attack_bar import AttackBar
from mybot.attack.deploy import drop_on_edge, drop_troop
from mybot.attack.heroes import HeroBattleState, deploy_hero
from mybot.attack.timing import get_deploy_delay, get_wave_delay
from mybot.enums import ArmyIndex, Hero
from mybot.log import set_debug_log, set_log
from mybot.vision.geometry import pixel_distance
from mybot.vision.red_area import RedArea


@dataclass
class CollectorTarget:
    """A detected resource collector and its value."""
    x: int
    y: int
    resource_type: str = ""  # "gold", "elixir", "dark"
    estimated_value: int = 0


@dataclass
class SmartFarmPlan:
    """Deployment plan for smart farming."""
    targets: list[CollectorTarget] = field(default_factory=list)
    deploy_side: str = ""
    deploy_points: list[tuple[int, int]] = field(default_factory=list)


def smart_farm(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
    red_area: RedArea | None = None,
    hero_state: HeroBattleState | None = None,
) -> HeroBattleState:
    """Execute Smart Farm attack algorithm.

    Translated from SmartFarm() in SmartFarm.au3.
    Detects collector positions, determines the best side for deployment,
    and deploys troops targeting resource buildings.

    Flow:
    1. Detect collector positions via template matching
    2. Group collectors by side
    3. Select the richest side
    4. Deploy tanks first (near defenses), then collectors troops
    5. Deploy heroes toward center

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        attack_bar: Current attack bar.
        red_area: Red deployment zone.
        hero_state: Hero tracking state.

    Returns:
        Updated HeroBattleState.
    """
    if hero_state is None:
        hero_state = HeroBattleState()

    image = capture_func()
    if image is None:
        set_log("SmartFarm: capture failed, falling back to AllTroops")
        from mybot.attack.algorithms.all_troops import algorithm_all_troops
        return algorithm_all_troops(click_func, attack_bar, red_area, hero_state=hero_state)

    # Step 1: Detect collectors
    targets = _detect_collectors(image)
    if not targets:
        set_log("SmartFarm: no collectors found, using AllTroops")
        from mybot.attack.algorithms.all_troops import algorithm_all_troops
        return algorithm_all_troops(click_func, attack_bar, red_area, hero_state=hero_state)

    set_log(f"SmartFarm: found {len(targets)} collectors")

    # Step 2: Determine best side
    plan = _plan_deployment(targets, red_area)

    if not plan.deploy_points:
        set_log("SmartFarm: no deployment points, using AllTroops")
        from mybot.attack.algorithms.all_troops import algorithm_all_troops
        return algorithm_all_troops(click_func, attack_bar, red_area, hero_state=hero_state)

    set_log(f"SmartFarm: deploying on {plan.deploy_side} side ({len(plan.deploy_points)} points)")

    # Step 3: Deploy troops
    for slot in attack_bar.slots:
        if slot.quantity <= 0:
            continue

        if slot.is_hero:
            hero_idx = _army_index_to_hero(slot.index)
            if hero_idx >= 0 and plan.deploy_points:
                mid = plan.deploy_points[len(plan.deploy_points) // 2]
                deploy_hero(click_func, hero_idx, mid[0], mid[1], attack_bar, hero_state)
                time.sleep(get_wave_delay())
            continue

        # Select and deploy
        click_func(slot.x, slot.y)
        time.sleep(0.1)

        if slot.is_spell or slot.is_siege:
            if plan.deploy_points:
                mid = plan.deploy_points[len(plan.deploy_points) // 2]
                drop_troop(click_func, mid[0], mid[1], slot.quantity, get_deploy_delay())
        else:
            drop_on_edge(click_func, plan.deploy_points, slot.quantity, delay=get_deploy_delay())

        time.sleep(get_wave_delay())

    set_log("SmartFarm: deployment complete")
    return hero_state


def _detect_collectors(
    image: np.ndarray,
) -> list[CollectorTarget]:
    """Detect resource collectors on the enemy base."""
    targets = []

    collector_dirs = {
        "gold": Path("imgxml/deadbase/Storages/Gold"),
        "elixir": Path("imgxml/deadbase/Storages/Elixir"),
        "dark": Path("imgxml/deadbase/Storages/Dark"),
    }

    from mybot.vision.matcher import find_multiple

    for resource_type, template_dir in collector_dirs.items():
        if not template_dir.is_dir():
            continue

        result = find_multiple(image, template_dir, confidence=0.75, max_results=15)
        for match in result.matches:
            targets.append(CollectorTarget(
                x=match.x, y=match.y,
                resource_type=resource_type,
            ))

    return targets


def _plan_deployment(
    targets: list[CollectorTarget],
    red_area: RedArea | None,
) -> SmartFarmPlan:
    """Plan deployment based on collector positions."""
    plan = SmartFarmPlan(targets=targets)

    if red_area is None or not red_area.is_valid:
        from mybot.vision.red_area import get_external_edge
        plan.deploy_points = get_external_edge()
        plan.deploy_side = "all"
        return plan

    # Count collectors near each side
    sides = {
        "top_left": red_area.top_left,
        "top_right": red_area.top_right,
        "bottom_left": red_area.bottom_left,
        "bottom_right": red_area.bottom_right,
    }

    best_side = "top_left"
    best_count = 0

    for side_name, side_points in sides.items():
        if not side_points:
            continue
        # Count collectors close to this side
        count = sum(
            1 for t in targets
            if any(pixel_distance(t.x, t.y, px, py) < 200 for px, py in side_points)
        )
        if count > best_count:
            best_count = count
            best_side = side_name

    plan.deploy_side = best_side
    plan.deploy_points = sides.get(best_side, [])
    return plan


def _army_index_to_hero(army_index: int) -> int:
    mapping = {
        ArmyIndex.KING: Hero.BARBARIAN_KING,
        ArmyIndex.QUEEN: Hero.ARCHER_QUEEN,
        ArmyIndex.PRINCE: Hero.MINION_PRINCE,
        ArmyIndex.WARDEN: Hero.GRAND_WARDEN,
        ArmyIndex.CHAMPION: Hero.ROYAL_CHAMPION,
        ArmyIndex.DRAGON_DUKE: Hero.DRAGON_DUKE,
    }
    return mapping.get(army_index, -1)
