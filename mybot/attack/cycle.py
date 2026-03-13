"""Attack cycle coordinator translated from MOD/AttackCycle.au3.

Main attack routine that orchestrates the full attack flow:
donation, search, preparation, execution, and return home.

Source: COCBot/functions/MOD/AttackCycle.au3
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.attack.algorithms.all_troops import algorithm_all_troops
from mybot.attack.attack_bar import AttackBar
from mybot.attack.heroes import HeroBattleState
from mybot.attack.prepare import AttackPlan, prepare_attack
from mybot.attack.report import attack_report
from mybot.attack.return_home import BattleEndResult, return_home
from mybot.attack.stats import AttackStats
from mybot.enums import MatchMode
from mybot.log import set_debug_log, set_log
from mybot.search.search import SearchConfig, SearchResult, village_search


@dataclass
class AttackCycleConfig:
    """Configuration for the attack cycle."""
    match_mode: MatchMode = MatchMode.DEAD_BASE
    algorithm: str = "all_troops"  # "all_troops", "csv", "smart_farm"
    csv_script: Path | None = None
    search_config: SearchConfig | None = None
    drop_order: list[int] | None = None


def attack_cycle(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    config: AttackCycleConfig | None = None,
    stats: AttackStats | None = None,
) -> BattleEndResult:
    """Execute a complete attack cycle.

    Translated from AttackCycle() in AttackCycle.au3.

    Flow:
    1. Search for a suitable base
    2. Prepare attack (read bar, detect red area)
    3. Execute attack algorithm
    4. Monitor heroes during battle
    5. Return home and collect results

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        config: Attack cycle configuration.
        stats: Statistics tracker.

    Returns:
        BattleEndResult with attack outcome.
    """
    if config is None:
        config = AttackCycleConfig()
    if stats is None:
        stats = AttackStats()

    result = BattleEndResult()

    # Step 1: Search for base
    set_log("Attack cycle: searching for base...")
    search_config = config.search_config or SearchConfig(match_mode=config.match_mode)
    search = village_search(capture_func, click_func, search_config)

    if not search.found:
        set_log("Attack cycle: no suitable base found")
        stats.skipped_bases += search.search_count
        return result

    # Step 2: Prepare attack
    set_log("Attack cycle: preparing attack...")
    plan = prepare_attack(capture_func, config.match_mode)

    if not plan.ready:
        set_log(f"Attack cycle: preparation failed — {plan.error}")
        return result

    # Step 3: Execute attack algorithm
    set_log(f"Attack cycle: executing {config.algorithm} algorithm")
    hero_state = HeroBattleState()

    if config.algorithm == "smart_farm":
        from mybot.attack.algorithms.smart_farm import smart_farm
        hero_state = smart_farm(
            capture_func, click_func,
            plan.attack_bar, plan.red_area, hero_state,
        )
    elif config.algorithm == "csv" and config.csv_script:
        from mybot.attack.algorithms.csv_attack import algorithm_csv
        hero_state = algorithm_csv(
            click_func, plan.attack_bar,
            config.csv_script, plan.red_area, hero_state,
        )
    else:
        hero_state = algorithm_all_troops(
            click_func, plan.attack_bar,
            plan.red_area, drop_order=config.drop_order,
            hero_state=hero_state,
        )

    # Step 4: Wait for battle to end and return home
    set_log("Attack cycle: returning home...")
    result = return_home(capture_func, click_func)

    # Step 5: Record stats and report
    stats.record_attack(result, search.search_count)
    attack_report(result, search.search_count)

    return result
