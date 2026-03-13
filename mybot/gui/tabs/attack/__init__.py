"""Attack tab translated from MBR GUI Design Attack.au3.

Container for attack configuration subtabs.

Source: COCBot/GUI/MBR GUI Design Attack.au3 (143 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from mybot.gui.tabs.attack.deadbase import DeadbaseSubTab
from mybot.gui.tabs.attack.livebase import LivebaseSubTab
from mybot.gui.tabs.attack.options import AttackOptionsSubTab
from mybot.gui.tabs.attack.troops import TroopsSubTab
from mybot.state import BotState


class AttackTab(QWidget):
    """Attack configuration tab with subtabs."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.addTab(DeadbaseSubTab(self.state), "Dead Base")
        tabs.addTab(LivebaseSubTab(self.state), "Live Base")
        tabs.addTab(TroopsSubTab(self.state), "Troops")
        tabs.addTab(AttackOptionsSubTab(self.state), "Options")

        layout.addWidget(tabs)
