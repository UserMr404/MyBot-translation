"""Resource reading and comparison during village search.

Translated from:
- Search/GetResources.au3 — OCR resource reading during search
- Search/CompareResources.au3 — loot threshold comparison

Source: COCBot/functions/Search/
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mybot.enums import LootType, MatchMode
from mybot.log import set_debug_log, set_log
from mybot.vision.ocr import read_number


# ── Resource Reading ─────────────────────────────────────────────────────────

@dataclass
class SearchLoot:
    """Resources detected on an enemy village during search.

    Replaces the array returned by GetResources() in GetResources.au3.
    """
    gold: int = 0
    elixir: int = 0
    dark_elixir: int = 0
    trophies: int = 0

    def __getitem__(self, loot_type: int) -> int:
        """Access by LootType index."""
        if loot_type == LootType.GOLD:
            return self.gold
        elif loot_type == LootType.ELIXIR:
            return self.elixir
        elif loot_type == LootType.DARK_ELIXIR:
            return self.dark_elixir
        elif loot_type == LootType.TROPHY:
            return self.trophies
        return 0

    @property
    def total_loot(self) -> int:
        """Total gold + elixir."""
        return self.gold + self.elixir


def get_resources(image: np.ndarray) -> SearchLoot:
    """Read resource amounts from the village search screen via OCR.

    Translated from GetResources() in GetResources.au3.
    Reads gold, elixir, dark elixir, and trophy values from their
    fixed positions on the search screen.

    OCR coordinates (from AutoIt):
    - Gold: X=48, Y=76, W=100, H=18
    - Elixir: X=48, Y=105, W=100, H=18
    - Dark Elixir: X=48, Y=133, W=100, H=18
    - Trophies: X=48, Y=175, W=80, H=18

    Args:
        image: BGR screenshot of the search screen.

    Returns:
        SearchLoot with all resource values.
    """
    loot = SearchLoot()

    loot.gold = read_number(image, 48, 76, 100, 18)
    loot.elixir = read_number(image, 48, 105, 100, 18)
    loot.dark_elixir = read_number(image, 48, 133, 100, 18)
    loot.trophies = read_number(image, 48, 175, 80, 18)

    set_debug_log(
        f"Search resources: G={loot.gold:,} E={loot.elixir:,} "
        f"DE={loot.dark_elixir:,} T={loot.trophies}"
    )
    return loot


# ── Resource Comparison ──────────────────────────────────────────────────────

@dataclass
class SearchFilter:
    """Loot thresholds for village search filtering.

    Replaces the arrays $g_aiFilterMeetGE[], $g_aiSearchGold[], etc.
    from CompareResources.au3.
    """
    min_gold: int = 0
    min_elixir: int = 0
    min_dark_elixir: int = 0
    min_trophies: int = -99
    max_th_level: int = 99
    meet_condition: str = "and"  # "and", "or", "g+e"

    # Search count reduction: after N searches, reduce thresholds
    reduce_count: int = 0
    reduce_gold: int = 0
    reduce_elixir: int = 0
    reduce_dark_elixir: int = 0


def compare_resources(
    loot: SearchLoot,
    filters: SearchFilter,
    th_level: int = 0,
    search_count: int = 0,
) -> bool:
    """Compare found resources against search filters.

    Translated from CompareResources() in CompareResources.au3.
    Supports AND/OR/G+E meet conditions and search count reduction.

    Args:
        loot: Detected resources from search screen.
        filters: Minimum resource thresholds.
        th_level: Detected Town Hall level (0 if unknown).
        search_count: Current search attempt count (for threshold reduction).

    Returns:
        True if the base meets the search criteria.
    """
    # Calculate effective thresholds (reduce after many searches)
    min_g = filters.min_gold
    min_e = filters.min_elixir
    min_de = filters.min_dark_elixir

    if filters.reduce_count > 0 and search_count >= filters.reduce_count:
        reductions = search_count // filters.reduce_count
        min_g = max(0, min_g - filters.reduce_gold * reductions)
        min_e = max(0, min_e - filters.reduce_elixir * reductions)
        min_de = max(0, min_de - filters.reduce_dark_elixir * reductions)
        if reductions > 0:
            set_debug_log(
                f"Reduced thresholds ({reductions}x): G≥{min_g:,} E≥{min_e:,} DE≥{min_de:,}"
            )

    # TH level check
    if th_level > 0 and th_level > filters.max_th_level:
        set_debug_log(f"TH{th_level} exceeds max TH{filters.max_th_level}")
        return False

    # Trophy check (can be negative for trophy dropping)
    if loot.trophies < filters.min_trophies:
        set_debug_log(f"Trophies {loot.trophies} < {filters.min_trophies}")
        return False

    # Resource threshold comparison
    gold_ok = loot.gold >= min_g
    elixir_ok = loot.elixir >= min_e
    de_ok = loot.dark_elixir >= min_de

    condition = filters.meet_condition.lower()

    if condition == "and":
        meets = gold_ok and elixir_ok and de_ok
    elif condition == "or":
        meets = gold_ok or elixir_ok or de_ok
    elif condition == "g+e":
        # Gold + Elixir combined must meet individual thresholds
        meets = (loot.gold + loot.elixir >= min_g + min_e) and de_ok
    else:
        meets = gold_ok and elixir_ok and de_ok

    if meets:
        set_log(
            f"Base meets criteria: G={loot.gold:,} E={loot.elixir:,} "
            f"DE={loot.dark_elixir:,} T={loot.trophies}"
        )
    else:
        set_debug_log(
            f"Base rejected ({condition}): "
            f"G={loot.gold:,}/{min_g:,} E={loot.elixir:,}/{min_e:,} "
            f"DE={loot.dark_elixir:,}/{min_de:,}"
        )

    return meets
