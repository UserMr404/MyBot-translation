"""Live base search subtab translated from Design Child Attack - Activebase-Search.au3.

Live base (active base) attack settings: higher thresholds, different algorithms.

Source: COCBot/GUI/MBR GUI Design Child Attack - Activebase-Search.au3 (338 lines)
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


class LivebaseSubTab(QWidget):
    """Live base (active base) attack configuration."""

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

        # ── Search Settings ────────────────────────────────────────────
        search_group = QGroupBox("Live Base Search")
        search_layout = QFormLayout(search_group)

        self.chk_enabled = QCheckBox("Enable Live Base Attack")
        search_layout.addRow(self.chk_enabled)

        self.spn_gold = QSpinBox()
        self.spn_gold.setRange(0, 2_000_000)
        self.spn_gold.setSingleStep(10_000)
        self.spn_gold.setValue(200_000)
        search_layout.addRow("Min Gold:", self.spn_gold)

        self.spn_elixir = QSpinBox()
        self.spn_elixir.setRange(0, 2_000_000)
        self.spn_elixir.setSingleStep(10_000)
        self.spn_elixir.setValue(200_000)
        search_layout.addRow("Min Elixir:", self.spn_elixir)

        self.spn_dark = QSpinBox()
        self.spn_dark.setRange(0, 50_000)
        self.spn_dark.setSingleStep(500)
        self.spn_dark.setValue(1_000)
        search_layout.addRow("Min Dark Elixir:", self.spn_dark)

        self.spn_trophy = QSpinBox()
        self.spn_trophy.setRange(-100, 100)
        search_layout.addRow("Min Trophies:", self.spn_trophy)

        layout.addWidget(search_group)

        # ── Attack Algorithm ───────────────────────────────────────────
        algo_group = QGroupBox("Attack Algorithm")
        algo_layout = QFormLayout(algo_group)

        self.cmb_algorithm = QComboBox()
        self.cmb_algorithm.addItems(["All Troops", "Smart Farm", "Scripted (CSV)"])
        algo_layout.addRow("Algorithm:", self.cmb_algorithm)

        self.cmb_drop_sides = QComboBox()
        self.cmb_drop_sides.addItems(["1 Side", "2 Sides", "3 Sides", "4 Sides"])
        algo_layout.addRow("Deploy Sides:", self.cmb_drop_sides)

        self.chk_smart_attack = QCheckBox("Smart Attack (use red line)")
        self.chk_smart_attack.setChecked(True)
        algo_layout.addRow(self.chk_smart_attack)

        layout.addWidget(algo_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
