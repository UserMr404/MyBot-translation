"""Bottom control bar translated from MBR GUI Design Bottom.au3.

Contains village overview panel, Start/Stop/Pause buttons, and status display.

Source: COCBot/GUI/MBR GUI Design Bottom.au3 (303 lines)
Source: COCBot/GUI/MBR GUI Control Bottom.au3 (503 lines)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mybot.enums import LootType
from mybot.state import BotState


class _OverviewPanel(QFrame):
    """Small panel showing current Gold / Elixir / Dark Elixir and TH level."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame { background-color: #2b2b2b; border-radius: 4px; padding: 2px; }"
            "QLabel { color: #e0e0e0; font-size: 11px; }"
        )
        self._setup_ui()
        self._refresh()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(16)

        # TH level
        self.lbl_th = QLabel()
        self.lbl_th.setStyleSheet("QLabel { font-weight: bold; color: #90caf9; }")
        layout.addWidget(self.lbl_th)

        # Gold
        self.lbl_gold = QLabel()
        self.lbl_gold.setStyleSheet("QLabel { color: #ffd740; }")
        layout.addWidget(self.lbl_gold)

        # Elixir
        self.lbl_elixir = QLabel()
        self.lbl_elixir.setStyleSheet("QLabel { color: #e040fb; }")
        layout.addWidget(self.lbl_elixir)

        # Dark Elixir
        self.lbl_dark = QLabel()
        self.lbl_dark.setStyleSheet("QLabel { color: #78909c; }")
        layout.addWidget(self.lbl_dark)

        layout.addStretch()

    def _refresh(self) -> None:
        """Update labels from current state."""
        th = self.state.village.town_hall_level
        self.lbl_th.setText(f"TH {th}" if th > 0 else "TH --")

        gold = self.state.village.current_loot[LootType.GOLD]
        elixir = self.state.village.current_loot[LootType.ELIXIR]
        dark = self.state.village.current_loot[LootType.DARK_ELIXIR]

        self.lbl_gold.setText(f"Gold: {gold:,}")
        self.lbl_elixir.setText(f"Elixir: {elixir:,}")
        self.lbl_dark.setText(f"Dark: {dark:,}")

    @pyqtSlot()
    def refresh(self) -> None:
        """Public slot to update the overview from state."""
        self._refresh()


class BottomBar(QWidget):
    """Bottom control bar with village overview, buttons, and status.

    Layout:
    ┌─ TH 14 │ Gold: 1,234,567 │ Elixir: 987,654 │ Dark: 12,345 ─┐
    ├─────────────────────────────────────────────────────────────────┤
    │ [Start] [Stop] [Pause] [Search]    Status: Stopped  Profile   │
    └─────────────────────────────────────────────────────────────────┘
    """

    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    search_mode_clicked = pyqtSignal()

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the bottom bar layout."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)

        # ── Overview panel ────────────────────────────────────────────
        self.overview = _OverviewPanel(self.state)
        outer.addWidget(self.overview)

        # ── Button row ────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(4, 2, 4, 2)

        # Control buttons
        self.btn_start = QPushButton("Start")
        self.btn_start.setFixedWidth(70)
        self.btn_start.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.btn_start.clicked.connect(self.start_clicked.emit)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setFixedWidth(70)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("QPushButton { background-color: #F44336; color: white; }")
        self.btn_stop.clicked.connect(self.stop_clicked.emit)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setFixedWidth(70)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.pause_clicked.emit)

        self.btn_search = QPushButton("Search")
        self.btn_search.setFixedWidth(70)
        self.btn_search.clicked.connect(self.search_mode_clicked.emit)

        # Status labels
        self.lbl_status = QLabel("Status: Stopped")
        self.lbl_status.setStyleSheet("QLabel { font-weight: bold; }")

        self.lbl_profile = QLabel(f"Profile: {self.state.account.profile_name}")

        # Layout
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_pause)
        btn_row.addWidget(self.btn_search)
        btn_row.addStretch()
        btn_row.addWidget(self.lbl_status)
        btn_row.addWidget(self.lbl_profile)

        outer.addLayout(btn_row)

    @pyqtSlot(str)
    def set_status(self, status: str) -> None:
        """Update the status label."""
        self.lbl_status.setText(f"Status: {status}")

    @pyqtSlot(bool)
    def set_running(self, running: bool) -> None:
        """Update button states based on running status."""
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_pause.setEnabled(running)
        self.btn_search.setEnabled(not running)

    def update_pause_state(self, paused: bool) -> None:
        """Update pause button text."""
        self.btn_pause.setText("Resume" if paused else "Pause")

    def set_profile(self, profile_name: str) -> None:
        """Update the profile label."""
        self.lbl_profile.setText(f"Profile: {profile_name}")
