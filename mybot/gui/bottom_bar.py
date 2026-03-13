"""Bottom control bar translated from MBR GUI Design Bottom.au3.

Contains Start/Stop/Pause buttons and status display.

Source: COCBot/GUI/MBR GUI Design Bottom.au3 (303 lines)
Source: COCBot/GUI/MBR GUI Control Bottom.au3 (503 lines)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from mybot.state import BotState


class BottomBar(QWidget):
    """Bottom control bar with Start/Stop/Pause buttons and status.

    Layout:
    [Start] [Stop] [Pause] [Search] | Status: Stopped | Profile: MyVillage
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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

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
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_search)
        layout.addStretch()
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.lbl_profile)

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
