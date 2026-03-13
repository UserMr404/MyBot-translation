"""Attack options subtab translated from Design Child Attack - Options-Attack.au3.

Attack behavior options: end battle, smart zap, drop order, CSV script selection.

Source: COCBot/GUI/MBR GUI Design Child Attack - Options-Attack.au3 (465 lines)
Source: COCBot/GUI/MBR GUI Design Child Attack - Options-Search.au3 (158 lines)
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState


class AttackOptionsSubTab(QWidget):
    """Attack behavior and options configuration."""

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

        # ── End Battle Settings ────────────────────────────────────────
        end_group = QGroupBox("End Battle")
        end_layout = QFormLayout(end_group)

        self.cmb_end_battle = QComboBox()
        self.cmb_end_battle.addItems([
            "When All Troops Deployed",
            "On 1 Star", "On 2 Stars", "On 3 Stars",
            "At % Damage", "On Time Limit",
        ])
        end_layout.addRow("End Battle:", self.cmb_end_battle)

        self.spn_end_percent = QSpinBox()
        self.spn_end_percent.setRange(0, 100)
        self.spn_end_percent.setValue(50)
        self.spn_end_percent.setSuffix("%")
        end_layout.addRow("Damage %:", self.spn_end_percent)

        self.spn_end_time = QSpinBox()
        self.spn_end_time.setRange(10, 180)
        self.spn_end_time.setValue(60)
        self.spn_end_time.setSuffix(" sec")
        end_layout.addRow("Time Limit:", self.spn_end_time)

        self.chk_remain_troops = QCheckBox("Wait for Remaining Troops")
        end_layout.addRow(self.chk_remain_troops)

        layout.addWidget(end_group)

        # ── Smart Zap Settings ─────────────────────────────────────────
        zap_group = QGroupBox("Smart Zap")
        zap_layout = QFormLayout(zap_group)

        self.chk_smart_zap = QCheckBox("Enable Smart Zap")
        zap_layout.addRow(self.chk_smart_zap)

        self.spn_min_de = QSpinBox()
        self.spn_min_de.setRange(0, 10_000)
        self.spn_min_de.setSingleStep(100)
        self.spn_min_de.setValue(200)
        zap_layout.addRow("Min DE per Zap:", self.spn_min_de)

        self.chk_zap_after = QCheckBox("Zap After Attack (use remaining spells)")
        zap_layout.addRow(self.chk_zap_after)

        layout.addWidget(zap_group)

        # ── CSV Script Selection ───────────────────────────────────────
        csv_group = QGroupBox("CSV Attack Script")
        csv_layout = QFormLayout(csv_group)

        csv_row = QHBoxLayout()
        self.txt_csv_db = QLineEdit()
        self.txt_csv_db.setPlaceholderText("Dead Base CSV script")
        csv_row.addWidget(self.txt_csv_db)
        self.btn_csv_db = QPushButton("Browse...")
        self.btn_csv_db.clicked.connect(lambda: self._browse_csv(self.txt_csv_db))
        csv_row.addWidget(self.btn_csv_db)
        csv_layout.addRow("Dead Base Script:", csv_row)

        csv_row2 = QHBoxLayout()
        self.txt_csv_lb = QLineEdit()
        self.txt_csv_lb.setPlaceholderText("Live Base CSV script")
        csv_row2.addWidget(self.txt_csv_lb)
        self.btn_csv_lb = QPushButton("Browse...")
        self.btn_csv_lb.clicked.connect(lambda: self._browse_csv(self.txt_csv_lb))
        csv_row2.addWidget(self.btn_csv_lb)
        csv_layout.addRow("Live Base Script:", csv_row2)

        layout.addWidget(csv_group)

        # ── Drop Order ─────────────────────────────────────────────────
        drop_group = QGroupBox("Drop Order")
        drop_layout = QFormLayout(drop_group)

        self.chk_custom_drop = QCheckBox("Use Custom Drop Order")
        drop_layout.addRow(self.chk_custom_drop)

        layout.addWidget(drop_group)

        # ── Attack Timing ──────────────────────────────────────────────
        timing_group = QGroupBox("Attack Timing")
        timing_layout = QFormLayout(timing_group)

        self.spn_delay_min = QSpinBox()
        self.spn_delay_min.setRange(0, 300)
        self.spn_delay_min.setValue(0)
        self.spn_delay_min.setSuffix(" sec")
        timing_layout.addRow("Delay Between Attacks (min):", self.spn_delay_min)

        self.spn_delay_max = QSpinBox()
        self.spn_delay_max.setRange(0, 300)
        self.spn_delay_max.setValue(30)
        self.spn_delay_max.setSuffix(" sec")
        timing_layout.addRow("Delay Between Attacks (max):", self.spn_delay_max)

        self.spn_max_attacks = QSpinBox()
        self.spn_max_attacks.setRange(1, 100)
        self.spn_max_attacks.setValue(10)
        timing_layout.addRow("Max Attacks per Session:", self.spn_max_attacks)

        layout.addWidget(timing_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _browse_csv(self, line_edit: QLineEdit) -> None:
        """Open file dialog to select a CSV attack script."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV Attack Script", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            line_edit.setText(path)
