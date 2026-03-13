"""Village status report translated from Village/VillageReport.au3.

Reads and displays the current village status including resources,
builders, shield status, and more.

Source: COCBot/functions/Village/VillageReport.au3
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mybot.log import set_debug_log, set_log
from mybot.vision.ocr import (
    get_builder_count,
    get_dark_elixir_main,
    get_elixir_main,
    get_gem_count,
    get_gold_main,
    get_trophy_main,
)


@dataclass
class VillageReport:
    """Village status snapshot.

    Replaces the globals updated by VillageReport() in VillageReport.au3.
    """
    gold: int = 0
    elixir: int = 0
    dark_elixir: int = 0
    gems: int = 0
    trophies: int = 0
    free_builders: int = 0
    total_builders: int = 0


def read_village_report(image: np.ndarray) -> VillageReport:
    """Read the current village status from the main screen.

    Translated from VillageReport() in VillageReport.au3.
    Uses OCR to read resource amounts, gem count, trophy count,
    and builder availability from their fixed screen positions.

    Args:
        image: BGR screenshot of the main village screen.

    Returns:
        VillageReport with all status values.
    """
    report = VillageReport()

    report.gold = get_gold_main(image)
    report.elixir = get_elixir_main(image)
    report.dark_elixir = get_dark_elixir_main(image)
    report.gems = get_gem_count(image)
    report.trophies = get_trophy_main(image)
    report.free_builders, report.total_builders = get_builder_count(image)

    set_log(
        f"Village: G={report.gold:,} E={report.elixir:,} "
        f"DE={report.dark_elixir:,} Gems={report.gems} "
        f"Trophies={report.trophies} "
        f"Builders={report.free_builders}/{report.total_builders}"
    )

    return report


def update_bot_state(report: VillageReport, state) -> None:
    """Update BotState.village with report values.

    Args:
        report: Fresh village report.
        state: BotState instance to update.
    """
    from mybot.enums import LootType

    state.village.current_loot[LootType.GOLD] = report.gold
    state.village.current_loot[LootType.ELIXIR] = report.elixir
    state.village.current_loot[LootType.DARK_ELIXIR] = report.dark_elixir
    state.village.current_loot[LootType.TROPHY] = report.trophies
    state.village.gems = report.gems
    state.village.free_builder_count = report.free_builders
    state.village.total_builder_count = report.total_builders
