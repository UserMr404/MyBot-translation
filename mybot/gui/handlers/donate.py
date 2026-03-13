"""Donate event handlers translated from MBR GUI Control Donate.au3.

Handles donation slot configuration changes.

Source: COCBot/GUI/MBR GUI Control Donate.au3 (292 lines, 20 functions)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DonateSlotConfig:
    """Configuration for a single donation slot."""
    enabled: bool = False
    troop_index: int = 0
    quantity: int = 1
    keywords: list[str] = field(default_factory=list)


@dataclass
class DonateConfig:
    """Complete donation configuration from the GUI."""
    enabled: bool = True
    donate_all: bool = False
    check_delay: int = 5
    troop_slots: list[DonateSlotConfig] = field(default_factory=lambda: [DonateSlotConfig() for _ in range(3)])
    spell_slots: list[DonateSlotConfig] = field(default_factory=lambda: [DonateSlotConfig() for _ in range(2)])
    siege_slot: DonateSlotConfig = field(default_factory=DonateSlotConfig)
    blacklist_keywords: list[str] = field(default_factory=list)
