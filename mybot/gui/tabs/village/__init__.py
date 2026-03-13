"""Village tab translated from MBR GUI Design Village.au3.

Container for village management subtabs: Donate, Misc, Upgrade, Notify, Achievements.

Source: COCBot/GUI/MBR GUI Design Village.au3 (47 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from mybot.gui.tabs.village.achievements import AchievementsSubTab
from mybot.gui.tabs.village.donate import DonateSubTab
from mybot.gui.tabs.village.misc import MiscSubTab
from mybot.gui.tabs.village.notify import NotifySubTab
from mybot.gui.tabs.village.upgrade import UpgradeSubTab
from mybot.state import BotState


class VillageTab(QWidget):
    """Village management tab with subtabs."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.addTab(DonateSubTab(self.state), "Donate")
        tabs.addTab(MiscSubTab(self.state), "Misc")
        tabs.addTab(UpgradeSubTab(self.state), "Upgrade")
        tabs.addTab(NotifySubTab(self.state), "Notify")
        tabs.addTab(AchievementsSubTab(self.state), "Achievements")

        layout.addWidget(tabs)
