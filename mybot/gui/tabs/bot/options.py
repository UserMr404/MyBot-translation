"""Bot options subtab translated from Design Child Bot - Options.au3.

General bot behavior options: restart, reboot, language.

Source: COCBot/GUI/MBR GUI Design Child Bot - Options.au3 (261 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState


class BotOptionsSubTab(QWidget):
    """General bot behavior options."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        # ── Restart Settings ───────────────────────────────────────────
        restart_group = QGroupBox("Restart Settings")
        restart_layout = QFormLayout(restart_group)

        self.chk_auto_restart = QCheckBox("Auto Restart on Error")
        self.chk_auto_restart.setChecked(True)
        restart_layout.addRow(self.chk_auto_restart)

        self.spn_restart_interval = QSpinBox()
        self.spn_restart_interval.setRange(0, 1440)
        self.spn_restart_interval.setValue(120)
        self.spn_restart_interval.setSuffix(" min")
        restart_layout.addRow("Restart Every:", self.spn_restart_interval)

        self.chk_close_emulator = QCheckBox("Close Emulator on Pause")
        restart_layout.addRow(self.chk_close_emulator)

        layout.addWidget(restart_group)

        # ── Smart Wait ─────────────────────────────────────────────────
        wait_group = QGroupBox("Smart Wait")
        wait_layout = QFormLayout(wait_group)

        self.chk_smart_wait = QCheckBox("Enable Smart Wait")
        self.chk_smart_wait.setChecked(True)
        wait_layout.addRow(self.chk_smart_wait)

        self.spn_close_min = QSpinBox()
        self.spn_close_min.setRange(1, 120)
        self.spn_close_min.setValue(2)
        self.spn_close_min.setSuffix(" min")
        wait_layout.addRow("Min Close Time:", self.spn_close_min)

        self.spn_close_max = QSpinBox()
        self.spn_close_max.setRange(1, 120)
        self.spn_close_max.setValue(5)
        self.spn_close_max.setSuffix(" min")
        wait_layout.addRow("Max Close Time:", self.spn_close_max)

        layout.addWidget(wait_group)

        # ── Language ───────────────────────────────────────────────────
        lang_group = QGroupBox("Language")
        lang_layout = QFormLayout(lang_group)

        self.cmb_language = QComboBox()
        self.cmb_language.addItems([
            "English", "French", "German", "Spanish", "Italian",
            "Portuguese", "Russian", "Turkish", "Korean",
            "Chinese (Simplified)", "Chinese (Traditional)",
            "Arabic", "Persian", "Vietnamese",
        ])
        lang_layout.addRow("Language:", self.cmb_language)

        layout.addWidget(lang_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
