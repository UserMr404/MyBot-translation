"""Notify subtab translated from Design Child Village - Notify.au3.

Push notification configuration.

Source: COCBot/GUI/MBR GUI Design Child Village - Notify.au3 (212 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState


class NotifySubTab(QWidget):
    """Notification settings tab."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("Push Notifications")
        form = QFormLayout(group)

        self.chk_notify = QCheckBox("Enable Notifications")
        form.addRow(self.chk_notify)

        self.txt_token = QLineEdit()
        self.txt_token.setPlaceholderText("Notification service token")
        self.txt_token.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Token:", self.txt_token)

        self.chk_on_attack = QCheckBox("Notify on Attack")
        form.addRow(self.chk_on_attack)

        self.chk_on_found = QCheckBox("Notify on Base Found")
        form.addRow(self.chk_on_found)

        self.chk_on_upgrade = QCheckBox("Notify on Upgrade Complete")
        form.addRow(self.chk_on_upgrade)

        self.chk_on_maintenance = QCheckBox("Notify on Maintenance")
        form.addRow(self.chk_on_maintenance)

        layout.addWidget(group)
        layout.addStretch()
