"""Profiles subtab translated from Design Child Bot - Profiles.au3.

Profile management: create, switch, delete profiles.

Source: COCBot/GUI/MBR GUI Design Child Bot - Profiles.au3 (193 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mybot.config.profiles import create_profile, delete_profile, get_profiles_dir, list_profiles
from mybot.state import BotState


class ProfilesSubTab(QWidget):
    """Profile management — create, switch, delete bot profiles."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("Bot Profiles")
        group_layout = QVBoxLayout(group)

        self.lbl_current = QLabel(f"Current: {self.state.account.profile_name}")
        self.lbl_current.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(self.lbl_current)

        self.profile_list = QListWidget()
        group_layout.addWidget(self.profile_list)

        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("New Profile")
        self.btn_new.clicked.connect(self._on_new)
        btn_layout.addWidget(self.btn_new)

        self.btn_switch = QPushButton("Switch To")
        self.btn_switch.clicked.connect(self._on_switch)
        btn_layout.addWidget(self.btn_switch)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self._on_delete)
        btn_layout.addWidget(self.btn_delete)

        group_layout.addLayout(btn_layout)

        # ── Multi-Account Settings ─────────────────────────────────────
        multi_group = QGroupBox("Multi-Account")
        multi_layout = QFormLayout(multi_group)

        self.cmb_accounts = QComboBox()
        self.cmb_accounts.addItems(["1", "2", "3", "4", "5", "6", "7", "8"])
        multi_layout.addRow("Total Accounts:", self.cmb_accounts)

        group_layout.addWidget(multi_group)

        layout.addWidget(group)
        layout.addStretch()

    def _refresh_list(self) -> None:
        """Refresh the profile list."""
        self.profile_list.clear()
        profiles_dir = get_profiles_dir()
        for name in list_profiles(profiles_dir):
            self.profile_list.addItem(name)

    def _on_new(self) -> None:
        """Create a new profile."""
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if ok and name.strip():
            profiles_dir = get_profiles_dir()
            create_profile(profiles_dir, name.strip())
            self._refresh_list()

    def _on_switch(self) -> None:
        """Switch to selected profile."""
        item = self.profile_list.currentItem()
        if item:
            self.state.account.profile_name = item.text()
            self.lbl_current.setText(f"Current: {item.text()}")

    def _on_delete(self) -> None:
        """Delete selected profile."""
        item = self.profile_list.currentItem()
        if not item:
            return
        name = item.text()
        if name == self.state.account.profile_name:
            QMessageBox.warning(self, "Error", "Cannot delete active profile")
            return
        reply = QMessageBox.question(
            self, "Confirm", f"Delete profile '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_profile(get_profiles_dir(), name)
            self._refresh_list()
