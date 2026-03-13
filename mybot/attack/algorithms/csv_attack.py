"""CSV-scripted attack algorithm translated from AttackFromCSV.au3.

Loads and executes CSV attack scripts that define precise deployment
sequences using vectors and commands.

Source: COCBot/functions/Attack/Attack Algorithms/AttackFromCSV.au3
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from mybot.attack.attack_bar import AttackBar
from mybot.attack.csv.execute import execute_csv_attack
from mybot.attack.csv.parser import CSVAttackScript
from mybot.attack.csv.validate import validate_script
from mybot.attack.heroes import HeroBattleState
from mybot.log import set_debug_log, set_log
from mybot.vision.red_area import RedArea


def algorithm_csv(
    click_func: Callable[[int, int], None],
    attack_bar: AttackBar,
    script_path: Path,
    red_area: RedArea | None = None,
    hero_state: HeroBattleState | None = None,
) -> HeroBattleState:
    """Execute a CSV-scripted attack.

    Translated from Algorithm_AttackCSV() in AttackFromCSV.au3.

    Args:
        click_func: Click function.
        attack_bar: Current attack bar.
        script_path: Path to the CSV attack script.
        red_area: Red deployment zone.
        hero_state: Hero tracking state.

    Returns:
        Updated HeroBattleState.
    """
    if hero_state is None:
        hero_state = HeroBattleState()

    # Parse the script
    script = CSVAttackScript(script_path)

    if not script.commands:
        set_log(f"CSV Attack: failed to parse '{script_path}'")
        return hero_state

    # Validate
    validation = validate_script(script)
    if not validation.valid:
        for error in validation.errors:
            set_log(f"CSV validation error: {error}")
        return hero_state

    for warning in validation.warnings:
        set_debug_log(f"CSV validation warning: {warning}")

    # Execute
    return execute_csv_attack(script, click_func, attack_bar, red_area, hero_state)
