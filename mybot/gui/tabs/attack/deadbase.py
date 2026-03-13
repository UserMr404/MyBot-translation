"""Dead base search subtab translated from Design Child Attack - Deadbase-Search.au3.

Dead base search and attack settings: loot thresholds, algorithm, army percent.

Source: COCBot/GUI/MBR GUI Design Child Attack - Deadbase-Search.au3 (346 lines)
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


class DeadbaseSubTab(QWidget):
    """Dead base search and attack configuration."""

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
        search_group = QGroupBox("Dead Base Search")
        search_layout = QFormLayout(search_group)

        self.chk_enabled = QCheckBox("Enable Dead Base Attack")
        self.chk_enabled.setChecked(True)
        search_layout.addRow(self.chk_enabled)

        self.spn_gold = QSpinBox()
        self.spn_gold.setRange(0, 2_000_000)
        self.spn_gold.setSingleStep(10_000)
        self.spn_gold.setValue(80_000)
        search_layout.addRow("Min Gold:", self.spn_gold)

        self.spn_elixir = QSpinBox()
        self.spn_elixir.setRange(0, 2_000_000)
        self.spn_elixir.setSingleStep(10_000)
        self.spn_elixir.setValue(80_000)
        search_layout.addRow("Min Elixir:", self.spn_elixir)

        self.spn_dark = QSpinBox()
        self.spn_dark.setRange(0, 50_000)
        self.spn_dark.setSingleStep(500)
        search_layout.addRow("Min Dark Elixir:", self.spn_dark)

        self.spn_trophy = QSpinBox()
        self.spn_trophy.setRange(-100, 100)
        search_layout.addRow("Min Trophies:", self.spn_trophy)

        self.spn_th_level = QSpinBox()
        self.spn_th_level.setRange(0, 17)
        search_layout.addRow("Max TH Level:", self.spn_th_level)

        layout.addWidget(search_group)

        # ── Attack Algorithm ───────────────────────────────────────────
        algo_group = QGroupBox("Attack Algorithm")
        algo_layout = QFormLayout(algo_group)

        self.cmb_algorithm = QComboBox()
        self.cmb_algorithm.addItems(["All Troops", "Smart Farm", "Scripted (CSV)"])
        algo_layout.addRow("Algorithm:", self.cmb_algorithm)

        self.cmb_drop_sides = QComboBox()
        self.cmb_drop_sides.addItems(["1 Side", "2 Sides", "3 Sides", "4 Sides", "DE Side", "TH Side"])
        algo_layout.addRow("Deploy Sides:", self.cmb_drop_sides)

        self.chk_smart_attack = QCheckBox("Smart Attack (use red line)")
        self.chk_smart_attack.setChecked(True)
        algo_layout.addRow(self.chk_smart_attack)

        self.chk_near_collectors = QCheckBox("Near Collectors")
        algo_layout.addRow(self.chk_near_collectors)

        self.spn_army_percent = QSpinBox()
        self.spn_army_percent.setRange(50, 100)
        self.spn_army_percent.setValue(100)
        self.spn_army_percent.setSuffix("%")
        algo_layout.addRow("Army Camp %:", self.spn_army_percent)

        layout.addWidget(algo_group)

        # ── Heroes ─────────────────────────────────────────────────────
        hero_group = QGroupBox("Heroes")
        hero_layout = QFormLayout(hero_group)

        self.chk_use_king = QCheckBox("Deploy King")
        self.chk_use_king.setChecked(True)
        hero_layout.addRow(self.chk_use_king)

        self.chk_use_queen = QCheckBox("Deploy Queen")
        self.chk_use_queen.setChecked(True)
        hero_layout.addRow(self.chk_use_queen)

        self.chk_use_warden = QCheckBox("Deploy Warden")
        self.chk_use_warden.setChecked(True)
        hero_layout.addRow(self.chk_use_warden)

        self.chk_use_champion = QCheckBox("Deploy Champion")
        self.chk_use_champion.setChecked(True)
        hero_layout.addRow(self.chk_use_champion)

        self.chk_wait_heroes = QCheckBox("Wait for Heroes")
        hero_layout.addRow(self.chk_wait_heroes)

        layout.addWidget(hero_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
