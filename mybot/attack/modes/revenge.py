"""Revenge battle mode translated from MOD/RevengeBattle.au3.

Handles revenge attacks on players who previously attacked you.

Source: COCBot/functions/MOD/RevengeBattle.au3
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from mybot.attack.algorithms.all_troops import algorithm_all_troops
from mybot.attack.heroes import HeroBattleState
from mybot.attack.prepare import prepare_attack
from mybot.attack.return_home import BattleEndResult, return_home
from mybot.enums import MatchMode
from mybot.log import set_log


def revenge_battle(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
) -> BattleEndResult:
    """Execute a revenge battle.

    Translated from RevengeBattle() — attacks a specific player.
    """
    set_log("Revenge Battle: preparing")
    plan = prepare_attack(capture_func, MatchMode.LIVE_BASE)

    if not plan.ready:
        set_log(f"Revenge Battle: preparation failed — {plan.error}")
        return BattleEndResult()

    hero_state = algorithm_all_troops(
        click_func, plan.attack_bar, plan.red_area,
        hero_state=HeroBattleState(),
    )

    return return_home(capture_func, click_func)
