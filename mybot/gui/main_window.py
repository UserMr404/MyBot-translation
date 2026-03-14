"""Main window translated from MBR GUI Design.au3 and MBR GUI Control.au3.

Creates the primary application window with tabbed interface containing
Village, Attack, Bot, and About tabs, plus bottom control bar and log widget.

Source: COCBot/MBR GUI Design.au3 (681 lines — layout creation)
Source: COCBot/MBR GUI Control.au3 (2,276 lines — event handlers)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mybot import __version__
from mybot.gui.bottom_bar import BottomBar
from mybot.gui.log_widget import LogWidget
from mybot.gui.tabs.about import AboutTab
from mybot.gui.tabs.attack import AttackTab
from mybot.gui.tabs.bot import BotTab
from mybot.gui.tabs.village import VillageTab
from mybot.state import BotState

if TYPE_CHECKING:
    from mybot.bot import Bot


class MainWindow(QMainWindow):
    """Main application window with tabbed interface.

    Layout matches AutoIt GUI:
    ┌──────────────────────────────────────────┐
    │  Menu Bar                                │
    ├──────────────────────────────────────────┤
    │  Tab Bar: [Village] [Attack] [Bot] [About]│
    ├──────────────────────────────────────────┤
    │                                          │
    │           Tab Content Area               │
    │                                          │
    ├──────────────────────────────────────────┤
    │           Log Display                    │
    ├──────────────────────────────────────────┤
    │  [Start] [Stop] [Pause] | Status Bar    │
    └──────────────────────────────────────────┘
    """

    # Signals for thread-safe GUI updates
    log_message = pyqtSignal(str, str)  # message, level
    status_changed = pyqtSignal(str)  # status text
    bot_state_changed = pyqtSignal(bool)  # running state

    WINDOW_WIDTH = 550
    WINDOW_HEIGHT = 780
    WINDOW_TITLE = f"MyBot v{__version__}"

    def __init__(self, state: BotState, bot: Bot | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self.bot = bot

        self._setup_window()
        self._create_widgets()
        self._create_layout()
        self._connect_signals()
        self._start_status_timer()

    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def _create_widgets(self) -> None:
        """Create all child widgets."""
        # Tab widget for main content
        self.tab_widget = QTabWidget()
        self.village_tab = VillageTab(self.state)
        self.attack_tab = AttackTab(self.state)
        self.bot_tab = BotTab(self.state)
        self.about_tab = AboutTab()

        self.tab_widget.addTab(self.village_tab, "Village")
        self.tab_widget.addTab(self.attack_tab, "Attack")
        self.tab_widget.addTab(self.bot_tab, "Bot")
        self.tab_widget.addTab(self.about_tab, "About")

        # Log display
        self.log_widget = LogWidget()

        # Bottom control bar
        self.bottom_bar = BottomBar(self.state)

    def _create_layout(self) -> None:
        """Arrange widgets in the main window layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Splitter between tabs and log for resizable areas
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(self.log_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        layout.addWidget(splitter)
        layout.addWidget(self.bottom_bar)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        # Bottom bar buttons → bot control
        self.bottom_bar.start_clicked.connect(self._on_start)
        self.bottom_bar.stop_clicked.connect(self._on_stop)
        self.bottom_bar.pause_clicked.connect(self._on_pause)
        self.bottom_bar.search_mode_clicked.connect(self._on_search_mode)

        # Thread-safe signal connections
        self.log_message.connect(self.log_widget.append_message)
        self.status_changed.connect(self.bottom_bar.set_status)
        self.bot_state_changed.connect(self._update_button_states)

    def _start_status_timer(self) -> None:
        """Start a timer to periodically update status display."""
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(1000)  # Update every second

    # ── Slots ──────────────────────────────────────────────────────────────

    @pyqtSlot()
    def _on_start(self) -> None:
        """Handle Start button click."""
        if self.bot is None:
            return
        # Save current config before starting
        self._save_config()

        from mybot.app import App
        # Find the parent App and start bot async
        app = self._find_app()
        if app:
            app.start_bot_async()
        self.bot_state_changed.emit(True)

    @pyqtSlot()
    def _on_stop(self) -> None:
        """Handle Stop button click."""
        if self.bot is None:
            return
        app = self._find_app()
        if app:
            app.stop_bot_async()
        self.bot_state_changed.emit(False)

    @pyqtSlot()
    def _on_pause(self) -> None:
        """Handle Pause button click."""
        self.state.paused = not self.state.paused
        status = "Paused" if self.state.paused else "Running"
        self.status_changed.emit(status)
        self.bottom_bar.update_pause_state(self.state.paused)

    @pyqtSlot()
    def _on_search_mode(self) -> None:
        """Handle Search Mode button click."""
        if self.bot is None:
            return
        self.state.search.is_searching = True
        self.status_changed.emit("Search Mode")

    @pyqtSlot(bool)
    def _update_button_states(self, running: bool) -> None:
        """Update button enabled states based on bot running status."""
        self.bottom_bar.set_running(running)

    @pyqtSlot()
    def _update_status(self) -> None:
        """Periodic status update.

        Also syncs button enabled states with actual bot running state,
        so buttons re-enable even if the bot thread exits on its own
        (e.g. due to an error) without going through _on_stop.
        """
        running = self.state.running
        if running:
            status = "Running"
            if self.state.paused:
                status = "Paused"
            elif self.state.search.is_searching:
                status = f"Searching (#{self.state.search.search_count})"
        else:
            status = "Stopped"
        self.bottom_bar.set_status(status)
        self.bottom_bar.set_running(running)
        self.bottom_bar.overview.refresh()

    # ── Config ─────────────────────────────────────────────────────────────

    def _save_config(self) -> None:
        """Save current GUI settings to config file."""
        try:
            from mybot.config.writer import save_config
            save_config(self.state.account.config_path, self.state)
        except ImportError:
            pass

    def _find_app(self) -> object | None:
        """Find the parent App instance."""
        # Walk up the widget hierarchy or use global reference
        return getattr(self, '_app', None)

    def set_app(self, app: object) -> None:
        """Set reference to the parent App for bot control."""
        self._app = app

    # ── Event Overrides ───────────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close — save config, stop bot."""
        self._save_config()
        if self.bot and self.state.running:
            self.state.stop_event.set()
        event.accept()
