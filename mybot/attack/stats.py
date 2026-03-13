"""Attack statistics tracking translated from Attack/AttackStats.au3.

Maintains running totals of attack results across sessions.

Source: COCBot/functions/Attack/AttackStats.au3
"""

from __future__ import annotations

from dataclasses import dataclass

from mybot.attack.return_home import BattleEndResult


@dataclass
class AttackStats:
    """Cumulative attack statistics."""
    total_attacks: int = 0
    total_searches: int = 0
    total_gold: int = 0
    total_elixir: int = 0
    total_dark: int = 0
    total_trophies: int = 0
    total_stars: int = 0
    skipped_bases: int = 0

    # Per-session
    session_attacks: int = 0
    session_gold: int = 0
    session_elixir: int = 0
    session_dark: int = 0

    @property
    def avg_gold_per_attack(self) -> float:
        return self.total_gold / self.total_attacks if self.total_attacks > 0 else 0

    @property
    def avg_elixir_per_attack(self) -> float:
        return self.total_elixir / self.total_attacks if self.total_attacks > 0 else 0

    def record_attack(self, result: BattleEndResult, searches: int = 0) -> None:
        """Record an attack result."""
        self.total_attacks += 1
        self.session_attacks += 1
        self.total_searches += searches
        self.total_gold += result.gold_looted
        self.session_gold += result.gold_looted
        self.total_elixir += result.elixir_looted
        self.session_elixir += result.elixir_looted
        self.total_dark += result.dark_looted
        self.session_dark += result.dark_looted
        self.total_trophies += result.trophies_change
        self.total_stars += result.stars

    def reset_session(self) -> None:
        """Reset session counters."""
        self.session_attacks = 0
        self.session_gold = 0
        self.session_elixir = 0
        self.session_dark = 0
