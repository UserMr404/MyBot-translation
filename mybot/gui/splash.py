"""Splash screen translated from MBR GUI Design Splash.au3.

Loading splash displayed while bot initializes subsystems.

Source: COCBot/GUI/MBR GUI Design Splash.au3 (113 lines)
Source: COCBot/GUI/MBR GUI Control Splash.au3 (70 lines)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QProgressBar,
    QSplashScreen,
    QVBoxLayout,
    QWidget,
)

from mybot import __version__


class SplashScreen(QWidget):
    """Loading splash screen shown during initialization.

    Displays version info and a progress bar while subsystems load.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(400, 200)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create splash screen layout."""
        self.setStyleSheet("background-color: #2B2B2B; border: 2px solid #555;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"MyBot v{__version__}")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Clash of Clans Automation")
        subtitle.setStyleSheet("color: #AAAAAA;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addStretch()

        # Status label
        self.lbl_status = QLabel("Initializing...")
        self.lbl_status.setStyleSheet("color: #CCCCCC;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet(
            "QProgressBar { border: 1px solid #555; border-radius: 3px; "
            "background-color: #333; text-align: center; color: white; }"
            "QProgressBar::chunk { background-color: #4CAF50; }"
        )
        layout.addWidget(self.progress)

    def set_status(self, message: str, progress: int = -1) -> None:
        """Update splash status message and optional progress.

        Args:
            message: Status text to display.
            progress: Progress value 0-100, or -1 to leave unchanged.
        """
        self.lbl_status.setText(message)
        if progress >= 0:
            self.progress.setValue(min(progress, 100))

    def finish(self, main_window: QWidget) -> None:
        """Close splash screen and show the main window."""
        main_window.show()
        self.close()
