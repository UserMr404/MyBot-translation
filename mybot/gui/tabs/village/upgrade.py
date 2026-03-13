"""Upgrade subtab translated from Design Child Village - Upgrade.au3.

Building upgrade configuration: wall upgrades, hero upgrades, auto-upgrade.

Source: COCBot/GUI/MBR GUI Design Child Village - Upgrade.au3 (975 lines)
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

from mybot.constants import HERO_NAMES
from mybot.state import BotState


class UpgradeSubTab(QWidget):
    """Upgrade configuration tab."""

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

        # ── Auto Upgrade ───────────────────────────────────────────────
        auto_group = QGroupBox("Auto Upgrade")
        auto_layout = QFormLayout(auto_group)

        self.chk_auto_upgrade = QCheckBox("Enable Auto Upgrade")
        auto_layout.addRow(self.chk_auto_upgrade)

        self.cmb_priority = QComboBox()
        self.cmb_priority.addItems(["Defense First", "Resource First", "Cheapest First"])
        auto_layout.addRow("Priority:", self.cmb_priority)

        self.spn_min_gold = QSpinBox()
        self.spn_min_gold.setRange(0, 20_000_000)
        self.spn_min_gold.setSingleStep(100_000)
        self.spn_min_gold.setValue(100_000)
        auto_layout.addRow("Min Gold Reserve:", self.spn_min_gold)

        self.spn_min_elixir = QSpinBox()
        self.spn_min_elixir.setRange(0, 20_000_000)
        self.spn_min_elixir.setSingleStep(100_000)
        self.spn_min_elixir.setValue(100_000)
        auto_layout.addRow("Min Elixir Reserve:", self.spn_min_elixir)

        layout.addWidget(auto_group)

        # ── Wall Upgrade ───────────────────────────────────────────────
        wall_group = QGroupBox("Wall Upgrade")
        wall_layout = QFormLayout(wall_group)

        self.chk_wall_upgrade = QCheckBox("Enable Wall Upgrade")
        wall_layout.addRow(self.chk_wall_upgrade)

        self.cmb_wall_resource = QComboBox()
        self.cmb_wall_resource.addItems(["Gold", "Elixir", "Gold then Elixir", "Elixir then Gold"])
        wall_layout.addRow("Use Resource:", self.cmb_wall_resource)

        self.spn_wall_reserve = QSpinBox()
        self.spn_wall_reserve.setRange(0, 20_000_000)
        self.spn_wall_reserve.setSingleStep(100_000)
        wall_layout.addRow("Min Reserve:", self.spn_wall_reserve)

        layout.addWidget(wall_group)

        # ── Hero Upgrade ───────────────────────────────────────────────
        hero_group = QGroupBox("Hero Upgrade")
        hero_layout = QVBoxLayout(hero_group)

        self.chk_heroes: list[QCheckBox] = []
        for name in HERO_NAMES:
            chk = QCheckBox(f"Upgrade {name}")
            self.chk_heroes.append(chk)
            hero_layout.addWidget(chk)

        layout.addWidget(hero_group)

        # ── Laboratory ─────────────────────────────────────────────────
        lab_group = QGroupBox("Laboratory")
        lab_layout = QFormLayout(lab_group)

        self.chk_lab_upgrade = QCheckBox("Enable Lab Upgrade")
        lab_layout.addRow(self.chk_lab_upgrade)

        self.cmb_lab_troop = QComboBox()
        self.cmb_lab_troop.addItems(["Auto Select"] + list(HERO_NAMES))
        lab_layout.addRow("Upgrade:", self.cmb_lab_troop)

        layout.addWidget(lab_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
