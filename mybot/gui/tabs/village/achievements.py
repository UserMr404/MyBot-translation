"""Achievements subtab translated from Design Child Village - Achievements.au3.

Achievement tracking and collection settings.

Source: COCBot/GUI/MBR GUI Design Child Village - Achievements.au3 (105 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState


class AchievementsSubTab(QWidget):
    """Achievement tracking settings."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("Achievement Collection")
        form = QFormLayout(group)

        self.chk_collect = QCheckBox("Auto-Collect Achievements")
        form.addRow(self.chk_collect)

        self.chk_daily = QCheckBox("Complete Daily Challenges")
        form.addRow(self.chk_daily)

        self.chk_clan_games = QCheckBox("Participate in Clan Games")
        form.addRow(self.chk_clan_games)

        layout.addWidget(group)
        layout.addStretch()
