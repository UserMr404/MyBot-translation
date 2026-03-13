"""Search tab event handlers translated from MBR GUI Control Tab Search.au3.

Handles search filter changes, threshold updates, condition toggles.

Source: COCBot/GUI/MBR GUI Control Tab Search.au3 (402 lines, 38 functions)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SearchSettings:
    """Search filter settings from the GUI."""
    enabled: bool = True
    min_gold: int = 80_000
    min_elixir: int = 80_000
    min_dark: int = 0
    min_trophies: int = -100
    max_th_level: int = 17
    meet_gold_elixir: bool = False  # AND vs OR for gold/elixir
    army_camp_percent: int = 100


def validate_search_settings(settings: SearchSettings) -> list[str]:
    """Validate search settings for consistency.

    Returns list of warning messages.
    """
    warnings: list[str] = []
    if settings.min_gold > 1_000_000:
        warnings.append("Gold threshold very high — may skip many bases")
    if settings.min_elixir > 1_000_000:
        warnings.append("Elixir threshold very high — may skip many bases")
    if settings.max_th_level < 5:
        warnings.append("Low max TH level — very few matching bases")
    return warnings
