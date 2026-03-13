"""Army training and reading module.

Phase 5: Army composition management — training, reading, verification.
"""

from mybot.army.check_camp import ArmyCampStatus, check_army_camp
from mybot.army.check_full import check_full_army
from mybot.army.read_cc import CCContents, get_cc_troops
from mybot.army.read_heroes import HeroStatus, get_army_heroes
from mybot.army.read_siege import get_army_siege
from mybot.army.read_spells import get_army_spells
from mybot.army.read_troops import get_army_troops
from mybot.army.smart_wait import parse_train_time, smart_wait_for_train
from mybot.army.train import TrainConfig, TrainResult, train_system

__all__ = [
    "ArmyCampStatus",
    "CCContents",
    "HeroStatus",
    "TrainConfig",
    "TrainResult",
    "check_army_camp",
    "check_full_army",
    "get_army_heroes",
    "get_army_siege",
    "get_army_spells",
    "get_army_troops",
    "get_cc_troops",
    "parse_train_time",
    "smart_wait_for_train",
    "train_system",
]
