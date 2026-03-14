"""Village status report translated from Village/VillageReport.au3.

Reads and displays the current village status including resources,
builders, shield status, and more.

Source: COCBot/functions/Village/VillageReport.au3
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mybot.config.image_dirs import GOB_BUILDER, resolve as resolve_img_dir
from mybot.log import set_debug_log, set_log
from mybot.vision.matcher import find_multiple
from mybot.vision.ocr import (
    get_builder_count,
    get_dark_elixir_main,
    get_elixir_main,
    get_gem_count,
    get_gold_main,
    get_trophy_main,
)


# Goblin Builder UI offset for Lab window (in pixels).
# When the goblin builder is active, the lab research window shifts right by
# this amount. Used by laboratory checks to read timers/costs correctly.
GOB_BUILDER_OFFSET = 355


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
    gob_builder_present: bool = False


def detect_goblin_builder(image: np.ndarray) -> bool:
    """Detect whether the Goblin Builder icon is visible on the main screen.

    Translated from getBuilderCount.au3 line 31:
        FindImageInPlace2("GobBuilder", $g_sImgGobBuilder, 360, 0, 450, 60)

    The goblin builder icon appears near the builder count when available.
    It costs gems to use, so it should be excluded from the "real" builder
    count (free and total are each decremented by 1).

    Args:
        image: BGR screenshot of the main village screen.

    Returns:
        True if goblin builder icon is detected.
    """
    gob_dir = resolve_img_dir(GOB_BUILDER)
    if not gob_dir.is_dir():
        set_debug_log(f"GobBuilder template dir not found: {gob_dir}")
        return False

    # Search region from AutoIt: (360, 0, 450, 60) — near builder count area
    result = find_multiple(
        image,
        gob_dir,
        search_area=(360, 0, 450, 60),
        confidence=0.80,
        max_results=1,
    )

    if result.found:
        set_debug_log("Goblin Builder detected on main screen")
        return True
    return False


def read_village_report(image: np.ndarray) -> VillageReport:
    """Read the current village status from the main screen.

    Translated from VillageReport() in VillageReport.au3.
    Uses OCR to read resource amounts, gem count, trophy count,
    and builder availability from their fixed screen positions.

    Also detects the Goblin Builder and adjusts builder counts accordingly,
    matching getBuilderCount.au3 lines 31-48.

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

    # Read raw builder count (includes goblin builder if present)
    raw_free, raw_total = get_builder_count(image)

    # Detect goblin builder and adjust counts
    # From getBuilderCount.au3:
    #   $g_iFreeBuilderCount = Int($aGetBuilders[0] - $ExtraBuilderCount)
    #   If $ExtraBuilderCount = 1 And Number($aGetBuilders[0]) = 0 Then $g_iFreeBuilderCount = 0
    #   $g_iTotalBuilderCount = Int($aGetBuilders[1] - $ExtraBuilderCount)
    report.gob_builder_present = detect_goblin_builder(image)

    if report.gob_builder_present:
        report.free_builders = max(0, raw_free - 1)
        report.total_builders = raw_total - 1
        set_debug_log(
            f"Builders (adjusted for Goblin Builder): "
            f"{report.free_builders}/{report.total_builders} "
            f"(raw: {raw_free}/{raw_total})"
        )
    else:
        report.free_builders = raw_free
        report.total_builders = raw_total

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
    state.village.gob_builder_present = report.gob_builder_present
    state.village.gob_builder_offset = GOB_BUILDER_OFFSET if report.gob_builder_present else 0
