"""Attack reporting translated from Attack/AttackReport.au3.

Logs attack results and maintains statistics.

Source: COCBot/functions/Attack/AttackReport.au3
"""

from __future__ import annotations

from mybot.attack.return_home import BattleEndResult
from mybot.log import set_log


def attack_report(result: BattleEndResult, search_count: int = 0) -> str:
    """Generate and log an attack report.

    Translated from AttackReport() in AttackReport.au3.

    Args:
        result: Battle end result with loot data.
        search_count: Number of bases searched before attacking.

    Returns:
        Formatted report string.
    """
    report = (
        f"Attack Report: {result.stars}★ | "
        f"Gold: {result.gold_looted:,} | "
        f"Elixir: {result.elixir_looted:,} | "
        f"DE: {result.dark_looted:,} | "
        f"Trophies: {result.trophies_change:+d}"
    )
    if search_count > 0:
        report += f" | Searches: {search_count}"

    set_log(report)
    return report
