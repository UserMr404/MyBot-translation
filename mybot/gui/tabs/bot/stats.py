"""Stats subtab translated from Design Child Bot - Stats.au3.

Statistics display: attack results, loot totals, session info.

Source: COCBot/GUI/MBR GUI Design Child Bot - Stats.au3 (1,960 lines)
"""

from __future__ import annotations

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mybot.state import BotState


class StatsSubTab(QWidget):
    """Statistics display — attack results, loot, session tracking."""

    def __init__(self, state: BotState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._setup_ui()
        self._start_timer()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        # ── Session Stats ──────────────────────────────────────────────
        session_group = QGroupBox("Current Session")
        session_layout = QFormLayout(session_group)

        self.lbl_attacks = QLabel("0")
        session_layout.addRow("Attacks:", self.lbl_attacks)

        self.lbl_gold = QLabel("0")
        session_layout.addRow("Gold Looted:", self.lbl_gold)

        self.lbl_elixir = QLabel("0")
        session_layout.addRow("Elixir Looted:", self.lbl_elixir)

        self.lbl_dark = QLabel("0")
        session_layout.addRow("Dark Elixir:", self.lbl_dark)

        self.lbl_trophies = QLabel("0")
        session_layout.addRow("Trophies:", self.lbl_trophies)

        self.lbl_searches = QLabel("0")
        session_layout.addRow("Searches:", self.lbl_searches)

        self.lbl_skipped = QLabel("0")
        session_layout.addRow("Skipped Bases:", self.lbl_skipped)

        layout.addWidget(session_group)

        # ── Village Status ─────────────────────────────────────────────
        village_group = QGroupBox("Village Resources")
        village_layout = QFormLayout(village_group)

        self.lbl_cur_gold = QLabel("0")
        village_layout.addRow("Current Gold:", self.lbl_cur_gold)

        self.lbl_cur_elixir = QLabel("0")
        village_layout.addRow("Current Elixir:", self.lbl_cur_elixir)

        self.lbl_cur_dark = QLabel("0")
        village_layout.addRow("Current Dark Elixir:", self.lbl_cur_dark)

        self.lbl_cur_trophies = QLabel("0")
        village_layout.addRow("Current Trophies:", self.lbl_cur_trophies)

        self.lbl_builders = QLabel("0/0")
        village_layout.addRow("Free Builders:", self.lbl_builders)

        self.lbl_th = QLabel("0")
        village_layout.addRow("Town Hall Level:", self.lbl_th)

        layout.addWidget(village_group)

        # ── Averages ───────────────────────────────────────────────────
        avg_group = QGroupBox("Averages")
        avg_layout = QFormLayout(avg_group)

        self.lbl_avg_gold = QLabel("0")
        avg_layout.addRow("Avg Gold/Attack:", self.lbl_avg_gold)

        self.lbl_avg_elixir = QLabel("0")
        avg_layout.addRow("Avg Elixir/Attack:", self.lbl_avg_elixir)

        self.lbl_avg_dark = QLabel("0")
        avg_layout.addRow("Avg DE/Attack:", self.lbl_avg_dark)

        layout.addWidget(avg_group)

        # ── Reset Button ───────────────────────────────────────────────
        self.btn_reset = QPushButton("Reset Statistics")
        self.btn_reset.clicked.connect(self._on_reset)
        layout.addWidget(self.btn_reset)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _start_timer(self) -> None:
        """Start auto-refresh timer."""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(2000)

    def refresh(self) -> None:
        """Update displayed statistics from state."""
        v = self.state.village
        self.lbl_cur_gold.setText(f"{v.current_loot[0]:,}")
        self.lbl_cur_elixir.setText(f"{v.current_loot[1]:,}")
        self.lbl_cur_dark.setText(f"{v.current_loot[2]:,}")
        self.lbl_cur_trophies.setText(f"{v.current_loot[3]:,}")
        self.lbl_builders.setText(f"{v.free_builder_count}/{v.total_builder_count}")
        self.lbl_th.setText(str(v.town_hall_level))

    def _on_reset(self) -> None:
        """Reset session statistics."""
        self.lbl_attacks.setText("0")
        self.lbl_gold.setText("0")
        self.lbl_elixir.setText("0")
        self.lbl_dark.setText("0")
        self.lbl_trophies.setText("0")
        self.lbl_searches.setText("0")
        self.lbl_skipped.setText("0")
