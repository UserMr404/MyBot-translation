"""Misc subtab translated from Design Child Village - Misc.au3.

Miscellaneous village settings: halt mode, treasury, obstacles, boost.

Source: COCBot/GUI/MBR GUI Design Child Village - Misc.au3 (1,030 lines)
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


class MiscSubTab(QWidget):
    """Miscellaneous village settings."""

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

        # ── Halt Mode ──────────────────────────────────────────────────
        halt_group = QGroupBox("Halt Mode")
        halt_layout = QFormLayout(halt_group)

        self.chk_halt_enabled = QCheckBox("Enable Halt Attack")
        halt_layout.addRow(self.chk_halt_enabled)

        self.cmb_halt_condition = QComboBox()
        self.cmb_halt_condition.addItems([
            "Gold Full", "Elixir Full", "Dark Elixir Full",
            "Trophy Limit", "Time Limit",
        ])
        halt_layout.addRow("Halt When:", self.cmb_halt_condition)

        self.spn_halt_gold = QSpinBox()
        self.spn_halt_gold.setRange(0, 20_000_000)
        self.spn_halt_gold.setSingleStep(100_000)
        halt_layout.addRow("Gold Threshold:", self.spn_halt_gold)

        self.spn_halt_elixir = QSpinBox()
        self.spn_halt_elixir.setRange(0, 20_000_000)
        self.spn_halt_elixir.setSingleStep(100_000)
        halt_layout.addRow("Elixir Threshold:", self.spn_halt_elixir)

        layout.addWidget(halt_group)

        # ── Collection Settings ────────────────────────────────────────
        collect_group = QGroupBox("Collection")
        collect_layout = QFormLayout(collect_group)

        self.chk_collect_treasury = QCheckBox("Collect Treasury")
        collect_layout.addRow(self.chk_collect_treasury)

        self.chk_collect_loot_cart = QCheckBox("Collect Loot Cart")
        self.chk_collect_loot_cart.setChecked(True)
        collect_layout.addRow(self.chk_collect_loot_cart)

        self.chk_clean_yard = QCheckBox("Remove Obstacles")
        self.chk_clean_yard.setChecked(True)
        collect_layout.addRow(self.chk_clean_yard)

        self.chk_collect_achievements = QCheckBox("Collect Achievements")
        collect_layout.addRow(self.chk_collect_achievements)

        self.chk_collect_free_magic = QCheckBox("Collect Free Magic Items")
        self.chk_collect_free_magic.setChecked(True)
        collect_layout.addRow(self.chk_collect_free_magic)

        layout.addWidget(collect_group)

        # ── Boost Settings ─────────────────────────────────────────────
        boost_group = QGroupBox("Boost Settings")
        boost_layout = QFormLayout(boost_group)

        self.chk_boost_barracks = QCheckBox("Boost Barracks")
        boost_layout.addRow(self.chk_boost_barracks)

        self.chk_boost_spell = QCheckBox("Boost Spell Factory")
        boost_layout.addRow(self.chk_boost_spell)

        self.chk_boost_heroes = QCheckBox("Boost Heroes")
        boost_layout.addRow(self.chk_boost_heroes)

        self.chk_training_potion = QCheckBox("Use Training Potion")
        boost_layout.addRow(self.chk_training_potion)

        layout.addWidget(boost_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
