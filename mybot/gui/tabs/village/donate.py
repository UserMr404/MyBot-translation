"""Donate subtab translated from Design Child Village - Donate.au3.

Donation configuration: troop/spell/siege donate settings per slot,
custom text matching, keyword-based request detection.

Source: COCBot/GUI/MBR GUI Design Child Village - Donate.au3 (3,966 lines — LARGEST GUI file)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mybot.constants import TROOP_NAMES, SPELL_NAMES, SIEGE_NAMES
from mybot.state import BotState


class DonateSubTab(QWidget):
    """Donation settings — troop/spell/siege slot configuration.

    The AutoIt version has ~400 controls across 3,966 lines.
    This provides the key settings: enable/disable, troop selection,
    keyword matching, and quantity limits.
    """

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

        # ── General Donate Settings ────────────────────────────────────
        general_group = QGroupBox("General Donation Settings")
        general_layout = QFormLayout(general_group)

        self.chk_donate = QCheckBox("Enable Donation")
        self.chk_donate.setChecked(True)
        general_layout.addRow(self.chk_donate)

        self.chk_donate_all = QCheckBox("Donate to All Requests")
        general_layout.addRow(self.chk_donate_all)

        self.spn_donate_delay = QSpinBox()
        self.spn_donate_delay.setRange(0, 60)
        self.spn_donate_delay.setValue(5)
        self.spn_donate_delay.setSuffix(" sec")
        general_layout.addRow("Donate Check Delay:", self.spn_donate_delay)

        layout.addWidget(general_group)

        # ── Troop Donation Slots ───────────────────────────────────────
        troop_group = QGroupBox("Troop Donations")
        troop_layout = QVBoxLayout(troop_group)

        self.troop_slots: list[DonateSlotWidget] = []
        for i in range(3):
            slot = DonateSlotWidget(f"Slot {i + 1}", TROOP_NAMES, f"troop_{i}")
            self.troop_slots.append(slot)
            troop_layout.addWidget(slot)

        layout.addWidget(troop_group)

        # ── Spell Donation Slots ───────────────────────────────────────
        spell_group = QGroupBox("Spell Donations")
        spell_layout = QVBoxLayout(spell_group)

        self.spell_slots: list[DonateSlotWidget] = []
        for i in range(2):
            slot = DonateSlotWidget(f"Spell Slot {i + 1}", SPELL_NAMES, f"spell_{i}")
            self.spell_slots.append(slot)
            spell_layout.addWidget(slot)

        layout.addWidget(spell_group)

        # ── Siege Donation ─────────────────────────────────────────────
        siege_group = QGroupBox("Siege Machine Donation")
        siege_layout = QVBoxLayout(siege_group)

        self.siege_slot = DonateSlotWidget("Siege", SIEGE_NAMES, "siege_0")
        siege_layout.addWidget(self.siege_slot)

        layout.addWidget(siege_group)

        # ── Custom Keywords ────────────────────────────────────────────
        keyword_group = QGroupBox("Request Keywords")
        keyword_layout = QFormLayout(keyword_group)

        self.txt_keywords = QLineEdit()
        self.txt_keywords.setPlaceholderText("Comma-separated keywords to match")
        keyword_layout.addRow("Match Keywords:", self.txt_keywords)

        self.txt_blacklist = QLineEdit()
        self.txt_blacklist.setPlaceholderText("Keywords to ignore")
        keyword_layout.addRow("Blacklist:", self.txt_blacklist)

        layout.addWidget(keyword_group)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)


class DonateSlotWidget(QWidget):
    """Single donation slot configuration.

    Each slot has: enable checkbox, troop selector, quantity, keywords.
    """

    def __init__(self, label: str, names: list[str], key: str,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.key = key

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        self.chk_enable = QCheckBox(label)
        self.chk_enable.setFixedWidth(100)
        layout.addWidget(self.chk_enable)

        self.cmb_unit = QComboBox()
        self.cmb_unit.addItems(names)
        self.cmb_unit.setFixedWidth(150)
        layout.addWidget(self.cmb_unit)

        self.spn_qty = QSpinBox()
        self.spn_qty.setRange(1, 50)
        self.spn_qty.setValue(1)
        self.spn_qty.setFixedWidth(60)
        layout.addWidget(self.spn_qty)

        self.txt_keyword = QLineEdit()
        self.txt_keyword.setPlaceholderText("Keywords")
        layout.addWidget(self.txt_keyword)
