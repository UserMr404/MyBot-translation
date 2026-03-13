"""Debug subtab translated from Design Child Bot - Debug.au3.

Debug flag toggles for troubleshooting.

Source: COCBot/GUI/MBR GUI Design Child Bot - Debug.au3 (201 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState


class DebugSubTab(QWidget):
    """Debug configuration — toggle various debug flags."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        group = QGroupBox("Debug Flags")
        group_layout = QVBoxLayout(group)

        debug_flags = [
            ("Log", "set_log", "Verbose logging"),
            ("Click", "click", "Log all click events"),
            ("Android", "android", "Emulator debug output"),
            ("OCR", "ocr", "OCR debug output"),
            ("Image Save", "image_save", "Save debug screenshots"),
            ("Red Area", "red_area", "Red deployment area debug"),
            ("Attack CSV", "attack_csv", "CSV attack script debug"),
            ("Building Pos", "building_pos", "Building position debug"),
            ("Train", "set_log_train", "Training debug output"),
            ("Smart Zap", "smart_zap", "Smart Zap debug"),
        ]

        self.chk_flags: dict[str, QCheckBox] = {}
        for label, attr, tooltip in debug_flags:
            chk = QCheckBox(f"Debug {label}")
            chk.setToolTip(tooltip)
            chk.setChecked(getattr(self.state.debug, attr, False))
            chk.toggled.connect(lambda checked, a=attr: setattr(self.state.debug, a, checked))
            self.chk_flags[attr] = chk
            group_layout.addWidget(chk)

        layout.addWidget(group)
        layout.addStretch()
