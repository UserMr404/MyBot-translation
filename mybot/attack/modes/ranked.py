"""Ranked battle mode translated from MOD/RankedBattle.au3.

Executes ranked/trophy push attacks.

Source: COCBot/functions/MOD/RankedBattle.au3
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from mybot.attack.cycle import AttackCycleConfig, attack_cycle
from mybot.attack.return_home import BattleEndResult
from mybot.attack.stats import AttackStats
from mybot.enums import MatchMode
from mybot.log import set_log


def ranked_battle(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    stats: AttackStats | None = None,
) -> BattleEndResult:
    """Execute a ranked/trophy push battle.

    Translated from RankedBattle() — uses live base mode.
    """
    set_log("Ranked Battle: starting")
    config = AttackCycleConfig(match_mode=MatchMode.LIVE_BASE)
    return attack_cycle(capture_func, click_func, config, stats)
