"""Troops subtab translated from Design Child Attack - Troops.au3.

Army composition configuration: troop/spell/siege quantities and training order.

Source: COCBot/GUI/MBR GUI Design Child Attack - Troops.au3 (1,760 lines)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mybot.constants import SIEGE_NAMES, SPELL_NAMES, SPELL_SPACE, TROOP_NAMES, TROOP_SPACE
from mybot.state import BotState


class TroopsSubTab(QWidget):
    """Army composition and training configuration."""

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

        # ── Training Mode ──────────────────────────────────────────────
        mode_group = QGroupBox("Training Mode")
        mode_layout = QFormLayout(mode_group)

        self.chk_quick_train = QCheckBox("Use Quick Train")
        self.chk_quick_train.setChecked(True)
        mode_layout.addRow(self.chk_quick_train)

        self.cmb_quick_slot = QComboBox()
        self.cmb_quick_slot.addItems(["Army 1", "Army 2", "Army 3"])
        mode_layout.addRow("Quick Train Slot:", self.cmb_quick_slot)

        self.chk_double_train = QCheckBox("Double Train (queue 2nd army)")
        mode_layout.addRow(self.chk_double_train)

        layout.addWidget(mode_group)

        # ── Troop Composition ──────────────────────────────────────────
        troop_group = QGroupBox("Troop Composition")
        troop_grid = QGridLayout(troop_group)
        troop_grid.setColumnStretch(1, 0)
        troop_grid.setColumnStretch(2, 0)

        troop_grid.addWidget(QLabel("Troop"), 0, 0)
        troop_grid.addWidget(QLabel("Qty"), 0, 1)
        troop_grid.addWidget(QLabel("Space"), 0, 2)

        self.troop_spins: list[QSpinBox] = []
        # Show first 20 key troops (most commonly used)
        key_troops = [0, 2, 4, 6, 8, 10, 12, 14, 15, 17, 18, 20, 22, 23, 24, 30, 32, 34, 36, 39]
        for row, idx in enumerate(key_troops, start=1):
            if idx < len(TROOP_NAMES):
                troop_grid.addWidget(QLabel(TROOP_NAMES[idx]), row, 0)
                spn = QSpinBox()
                spn.setRange(0, 300)
                spn.setFixedWidth(60)
                self.troop_spins.append(spn)
                troop_grid.addWidget(spn, row, 1)
                troop_grid.addWidget(QLabel(str(TROOP_SPACE[idx])), row, 2)

        layout.addWidget(troop_group)

        # ── Spell Composition ──────────────────────────────────────────
        spell_group = QGroupBox("Spell Composition")
        spell_grid = QGridLayout(spell_group)

        spell_grid.addWidget(QLabel("Spell"), 0, 0)
        spell_grid.addWidget(QLabel("Qty"), 0, 1)
        spell_grid.addWidget(QLabel("Space"), 0, 2)

        self.spell_spins: list[QSpinBox] = []
        for row, (name, space) in enumerate(zip(SPELL_NAMES, SPELL_SPACE), start=1):
            spell_grid.addWidget(QLabel(name), row, 0)
            spn = QSpinBox()
            spn.setRange(0, 20)
            spn.setFixedWidth(60)
            self.spell_spins.append(spn)
            spell_grid.addWidget(spn, row, 1)
            spell_grid.addWidget(QLabel(str(space)), row, 2)

        layout.addWidget(spell_group)

        # ── Siege Machines ─────────────────────────────────────────────
        siege_group = QGroupBox("Siege Machines")
        siege_layout = QFormLayout(siege_group)

        self.cmb_siege = QComboBox()
        self.cmb_siege.addItems(["None"] + list(SIEGE_NAMES))
        siege_layout.addRow("Siege Machine:", self.cmb_siege)

        layout.addWidget(siege_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    @property
    def total_troop_space(self) -> int:
        """Calculate total troop space from current selections."""
        return sum(spn.value() for spn in self.troop_spins)

    @property
    def total_spell_space(self) -> int:
        """Calculate total spell space from current selections."""
        total = 0
        for spn, space in zip(self.spell_spins, SPELL_SPACE):
            total += spn.value() * space
        return total
