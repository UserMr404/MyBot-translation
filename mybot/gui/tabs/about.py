"""About tab translated from MBR GUI Design About.au3.

Displays version info, credits, and links.

Source: COCBot/GUI/MBR GUI Design About.au3 (161 lines)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from mybot import __version__


class AboutTab(QWidget):
    """About/info tab with version and credits."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel(f"MyBot v{__version__}")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Clash of Clans Automation Bot")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        info = QLabel(
            "Python translation of MyBot.run v8.2.0\n\n"
            "Original: AutoIt 3 (MyBot.run)\n"
            "License: GNU GPL v3\n\n"
            "This bot automates Clash of Clans gameplay including:\n"
            "  - Resource collection\n"
            "  - Army training and management\n"
            "  - Base searching and attacking\n"
            "  - Building upgrades\n"
            "  - Clan Castle donations\n"
            "  - Multi-account switching\n"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()
