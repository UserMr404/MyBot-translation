"""Android subtab translated from Design Child Bot - Android.au3.

Android emulator configuration: emulator type, instance, ADB settings.

Source: COCBot/GUI/MBR GUI Design Child Bot - Android.au3 (188 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState


class AndroidSubTab(QWidget):
    """Android emulator configuration."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("Emulator Settings")
        form = QFormLayout(group)

        self.cmb_emulator = QComboBox()
        self.cmb_emulator.addItems(["BlueStacks5", "MEmu", "Nox"])
        self.cmb_emulator.setCurrentText(self.state.android.emulator or "BlueStacks5")
        form.addRow("Emulator:", self.cmb_emulator)

        self.txt_instance = QLineEdit()
        self.txt_instance.setText(self.state.android.instance)
        self.txt_instance.setPlaceholderText("Default instance")
        form.addRow("Instance Name:", self.txt_instance)

        self.spn_adb_port = QSpinBox()
        self.spn_adb_port.setRange(1024, 65535)
        self.spn_adb_port.setValue(self.state.android.adb_port)
        form.addRow("ADB Port:", self.spn_adb_port)

        self.chk_embed = QCheckBox("Embed Emulator Window")
        form.addRow(self.chk_embed)

        self.chk_hide = QCheckBox("Hide Emulator Taskbar Entry")
        form.addRow(self.chk_hide)

        layout.addWidget(group)

        # ── ADB Settings ──────────────────────────────────────────────
        adb_group = QGroupBox("ADB Settings")
        adb_layout = QFormLayout(adb_group)

        self.txt_adb_path = QLineEdit()
        self.txt_adb_path.setPlaceholderText("Auto-detect")
        adb_layout.addRow("ADB Path:", self.txt_adb_path)

        self.chk_adb_shared = QCheckBox("Share ADB Connection")
        adb_layout.addRow(self.chk_adb_shared)

        layout.addWidget(adb_group)
        layout.addStretch()
