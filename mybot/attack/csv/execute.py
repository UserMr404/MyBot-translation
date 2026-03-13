"""CSV attack script execution engine.

Translated from AttackCSV/ParseAttackCSV.au3 (execution phase) and
AttackCSV/DropTroopFromINI.au3.

Executes parsed CSV commands against the live game state.

Source files:
- AttackCSV/ParseAttackCSV.au3 — execution flow
- AttackCSV/DropTroopFromINI.au3 — DROP command execution
"""

from __future__ import annotations

import time
from typing import Callable

from mybot.attack.attack_bar import AttackBar
from mybot.attack.csv.drop_points import make_drop_points
from mybot.attack.csv.parser import (
    CSVAttackScript,
    DropCommand,
    MakeCommand,
    WaitCommand,
)
from mybot.attack.deploy import drop_troop
from mybot.attack.heroes import HeroBattleState
from mybot.log import set_debug_log, set_log
from mybot.vision.red_area import RedArea


def execute_csv_attack(
    script: CSVAttackScript,
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
    red_area: RedArea | None = None,
    hero_state: HeroBattleState | None = None,
) -> HeroBattleState:
    """Execute a parsed CSV attack script.

    Translated from Algorithm_AttackCSV() in AttackFromCSV.au3.

    Flow:
    1. Process MAKE commands to build deployment vectors
    2. Execute DROP commands to deploy troops
    3. Process WAIT commands for timing

    Args:
        script: Parsed CSV attack script.
        click_func: Click function.
        attack_bar: Current attack bar state.
        red_area: Red deployment zone.
        hero_state: Hero tracking state.

    Returns:
        Updated HeroBattleState.
    """
    if hero_state is None:
        hero_state = HeroBattleState()

    if not script.commands:
        set_log("CSV Attack: no commands to execute")
        return hero_state

    set_log(f"CSV Attack: executing '{script.name}' ({len(script.commands)} commands)")

    # Step 1: Build all vectors (populate drop points)
    for vector in script.vectors.values():
        vector.points = make_drop_points(vector, red_area)

    # Step 2: Execute commands in order
    for cmd in script.commands:
        if isinstance(cmd, MakeCommand):
            # Already processed above
            continue

        elif isinstance(cmd, DropCommand):
            _execute_drop(cmd, script, click_func, attack_bar)

        elif isinstance(cmd, WaitCommand):
            if cmd.delay_ms > 0:
                set_debug_log(f"CSV WAIT: {cmd.delay_ms}ms")
                time.sleep(cmd.delay_ms / 1000.0)

    set_log("CSV Attack: execution complete")
    return hero_state


def _execute_drop(
    cmd: DropCommand,
    script: CSVAttackScript,
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
) -> None:
    """Execute a DROP command.

    Translated from DropTroopFromINI() in DropTroopFromINI.au3.
    """
    # Get the deployment vector
    vector = script.vectors.get(cmd.vector)
    if vector is None:
        set_debug_log(f"CSV DROP: vector '{cmd.vector}' not found")
        return

    if not vector.points:
        set_debug_log(f"CSV DROP: vector '{cmd.vector}' has no points")
        return

    # Find the troop in the attack bar
    slot = attack_bar.get_slot_by_name(cmd.troop_name)
    if slot is None:
        set_debug_log(f"CSV DROP: troop '{cmd.troop_name}' not in attack bar")
        return

    if slot.quantity <= 0:
        set_debug_log(f"CSV DROP: troop '{cmd.troop_name}' has 0 quantity")
        return

    # Select the troop in attack bar
    click_func(slot.x, slot.y)
    time.sleep(0.1)

    # Determine point range
    start = max(0, cmd.start_index)
    end = cmd.end_index if cmd.end_index >= 0 else len(vector.points)
    end = min(end, len(vector.points))

    if start >= end:
        return

    points = vector.points[start:end]
    quantity = cmd.quantity if cmd.quantity > 0 else slot.quantity

    # Distribute troops across points
    per_point = max(1, quantity // len(points)) if points else quantity
    remaining = quantity
    delay = cmd.delay_ms / 1000.0 if cmd.delay_ms > 0 else 0.05

    for px, py in points:
        if remaining <= 0:
            break
        to_drop = min(per_point, remaining)
        dropped = drop_troop(click_func, px, py, to_drop, delay)
        remaining -= dropped

    slot.quantity = max(0, slot.quantity - (quantity - remaining))

    set_debug_log(
        f"CSV DROP: {cmd.troop_name} x{quantity - remaining} "
        f"on vector '{cmd.vector}' [{start}:{end}]"
    )

    # Sleep after drop if specified
    if cmd.sleep_after > 0:
        time.sleep(cmd.sleep_after / 1000.0)
