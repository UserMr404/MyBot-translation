"""Village management module.

Phase 4: Resource collection, reporting, donations, upgrades,
building location, and multi-account switching.

- collect: Resource collection from mines/collectors/drills
- report: Village status reading and reporting
- donate: Clan Castle donation processing
- switch_account: Multi-account Supercell ID switching
- upgrade: Building upgrade detection and execution
- locate: Building location via template matching
"""

from mybot.village.collect import CollectResult, collect_resources, is_storage_full
from mybot.village.donate import DonateConfig, DonateResult, donate_cc
from mybot.village.locate import (
    BuildingLocation,
    locate_building,
    locate_clan_castle,
    locate_hero_altar,
    locate_lab,
    locate_spell_factory,
)
from mybot.village.report import VillageReport, read_village_report, update_bot_state
from mybot.village.switch_account import (
    AccountConfig,
    SwitchAccountConfig,
    SwitchResult,
    select_next_account,
    should_switch,
    switch_account,
)
from mybot.village.upgrade import (
    UpgradeResult,
    UpgradeSlot,
    auto_upgrade,
    check_upgrade_available,
    start_upgrade,
)

__all__ = [
    # collect
    "CollectResult",
    "collect_resources",
    "is_storage_full",
    # report
    "VillageReport",
    "read_village_report",
    "update_bot_state",
    # donate
    "DonateConfig",
    "DonateResult",
    "donate_cc",
    # switch_account
    "AccountConfig",
    "SwitchAccountConfig",
    "SwitchResult",
    "select_next_account",
    "should_switch",
    "switch_account",
    # upgrade
    "UpgradeResult",
    "UpgradeSlot",
    "auto_upgrade",
    "check_upgrade_available",
    "start_upgrade",
    # locate
    "BuildingLocation",
    "locate_building",
    "locate_clan_castle",
    "locate_hero_altar",
    "locate_lab",
    "locate_spell_factory",
]
