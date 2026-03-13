"""Attack system module.

Phase 5: Attack preparation, execution, algorithms, and deployment.
"""

from mybot.attack.attack_bar import AttackBar, AttackBarSlot, get_attack_bar
from mybot.attack.cycle import AttackCycleConfig, attack_cycle
from mybot.attack.deploy import drop_cc, drop_on_edge, drop_on_edges, drop_troop
from mybot.attack.drop_order import DEFAULT_DROP_ORDER, get_drop_order
from mybot.attack.heroes import HeroBattleState, check_heroes_health, deploy_hero
from mybot.attack.launch import launch_troop
from mybot.attack.prepare import AttackPlan, prepare_attack
from mybot.attack.report import attack_report
from mybot.attack.return_home import BattleEndResult, return_home, surrender
from mybot.attack.smart_zap import SmartZapResult, smart_zap
from mybot.attack.stats import AttackStats
from mybot.attack.timing import get_deploy_delay, get_wave_delay

__all__ = [
    "AttackBar",
    "AttackBarSlot",
    "AttackCycleConfig",
    "AttackPlan",
    "AttackStats",
    "BattleEndResult",
    "DEFAULT_DROP_ORDER",
    "HeroBattleState",
    "SmartZapResult",
    "attack_cycle",
    "attack_report",
    "check_heroes_health",
    "deploy_hero",
    "drop_cc",
    "drop_on_edge",
    "drop_on_edges",
    "drop_troop",
    "get_attack_bar",
    "get_deploy_delay",
    "get_drop_order",
    "get_wave_delay",
    "launch_troop",
    "prepare_attack",
    "return_home",
    "smart_zap",
    "surrender",
]
