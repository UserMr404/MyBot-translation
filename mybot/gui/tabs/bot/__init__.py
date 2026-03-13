"""Bot tab translated from MBR GUI Design Bot.au3.

Container for bot configuration subtabs: Options, Profiles, Stats, Android, Debug.

Source: COCBot/GUI/MBR GUI Design Bot.au3 (66 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from mybot.gui.tabs.bot.android import AndroidSubTab
from mybot.gui.tabs.bot.debug import DebugSubTab
from mybot.gui.tabs.bot.options import BotOptionsSubTab
from mybot.gui.tabs.bot.profiles import ProfilesSubTab
from mybot.gui.tabs.bot.stats import StatsSubTab
from mybot.state import BotState


class BotTab(QWidget):
    """Bot configuration tab with subtabs."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.addTab(BotOptionsSubTab(self.state), "Options")
        tabs.addTab(ProfilesSubTab(self.state), "Profiles")
        tabs.addTab(StatsSubTab(self.state), "Stats")
        tabs.addTab(AndroidSubTab(self.state), "Android")
        tabs.addTab(DebugSubTab(self.state), "Debug")

        layout.addWidget(tabs)
