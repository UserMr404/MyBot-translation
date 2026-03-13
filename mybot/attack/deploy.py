"""Troop deployment translated from RedArea/DropTroop.au3 and related.

Handles deploying troops at specific coordinates during battle.

Source files:
- RedArea/DropTroop.au3 — main deployment
- RedArea/DropOnPixel.au3 — pixel-precise deployment
- Troops/DropOnEdge.au3 — edge deployment
- Troops/DropOnEdges.au3 — multi-edge deployment
- Troops/dropCC.au3 — Clan Castle deployment
"""

from __future__ import annotations

import time
from typing import Callable

from mybot.log import set_debug_log
from mybot.vision.pixel import is_inside_diamond


def drop_troop(
    click_func: Callable[[int, int], None],
    x: int,
    y: int,
    count: int = 1,
    delay: float = 0.05,
) -> int:
    """Deploy troops at a specific coordinate.

    Translated from DropTroop() in DropTroop.au3.
    Clicks at the specified position to deploy troops, with
    diamond boundary validation.

    Args:
        click_func: Click function.
        x: Deployment X coordinate.
        y: Deployment Y coordinate.
        count: Number of troops to deploy.
        delay: Delay between deployments.

    Returns:
        Number of troops actually deployed.
    """
    if not is_inside_diamond(x, y, check_ui_zones=False):
        set_debug_log(f"DropTroop: ({x},{y}) outside diamond, skipping")
        return 0

    deployed = 0
    for i in range(count):
        click_func(x, y)
        deployed += 1
        if delay > 0 and i < count - 1:
            time.sleep(delay)

    return deployed


def drop_on_edge(
    click_func: Callable[[int, int], None],
    points: list[tuple[int, int]],
    count: int = 1,
    troops_per_point: int = 1,
    delay: float = 0.05,
) -> int:
    """Deploy troops evenly along an edge (list of points).

    Translated from DropOnEdge() in DropOnEdge.au3.
    Distributes troops across the deployment points.

    Args:
        click_func: Click function.
        points: Deployment coordinates.
        count: Total troops to deploy.
        troops_per_point: Troops per point.
        delay: Delay between deployments.

    Returns:
        Total troops deployed.
    """
    if not points:
        return 0

    deployed = 0
    remaining = count

    for px, py in points:
        if remaining <= 0:
            break

        to_drop = min(troops_per_point, remaining)
        dropped = drop_troop(click_func, px, py, to_drop, delay)
        deployed += dropped
        remaining -= dropped

    return deployed


def drop_on_edges(
    click_func: Callable[[int, int], None],
    sides: dict[str, list[tuple[int, int]]],
    count: int = 1,
    delay: float = 0.05,
) -> int:
    """Deploy troops across multiple edges/sides.

    Translated from DropOnEdges() in DropOnEdges.au3.
    Distributes troops evenly across all provided sides.

    Args:
        click_func: Click function.
        sides: Dict of side_name → list of deployment points.
        count: Total troops to deploy.
        delay: Delay between deployments.

    Returns:
        Total troops deployed.
    """
    if not sides:
        return 0

    all_points = []
    for side_points in sides.values():
        all_points.extend(side_points)

    if not all_points:
        return 0

    return drop_on_edge(click_func, all_points, count, troops_per_point=1, delay=delay)


def drop_cc(
    click_func: Callable[[int, int], None],
    x: int,
    y: int,
) -> bool:
    """Deploy Clan Castle troops.

    Translated from dropCC() in dropCC.au3.
    Single click to deploy CC troops at the target position.

    Args:
        click_func: Click function.
        x: Target X.
        y: Target Y.

    Returns:
        True if deployed.
    """
    if not is_inside_diamond(x, y, check_ui_zones=False):
        set_debug_log(f"dropCC: ({x},{y}) outside diamond")
        return False

    click_func(x, y)
    set_debug_log(f"dropCC: deployed at ({x},{y})")
    return True
