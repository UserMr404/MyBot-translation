"""Application entry point translated from MyBot.run.au3.

Replaces InitializeBot() + MainLoop() with a Python App class that handles
CLI argument parsing, subsystem initialization, and event loop dispatching.

Source: MyBot.run.au3 — InitializeBot(), MainLoop()
"""

from __future__ import annotations

import argparse
import signal
import sys
import threading
from pathlib import Path

from mybot import __version__
from mybot.config.profiles import (
    create_profile,
    get_config_path,
    get_default_profile,
    get_profiles_dir,
)
from mybot.config.reader import read_config
from mybot.enums import BotAction
from mybot.log import get_logger, setup_logging
from mybot.state import BotState
from mybot.utils.paths import init_base_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments matching AutoIt's ProcessCommandLine().

    Supports the same flags as the AutoIt version:
      /restart, /autostart, /nowatchdog, /nogui, /console,
      /profiles=<path>, /debug, /minigui
    """
    parser = argparse.ArgumentParser(
        prog="mybot",
        description=f"MyBot v{__version__} — Clash of Clans automation bot",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--profile", default=None, help="Profile name to load")
    parser.add_argument("--profiles-dir", default=None, type=Path, help="Custom profiles directory")
    parser.add_argument("--autostart", action="store_true", help="Auto-start bot on launch")
    parser.add_argument("--restart", action="store_true", help="Restart mode (skip splash)")
    parser.add_argument("--nogui", action="store_true", help="Run headless (no GUI)")
    parser.add_argument("--minigui", action="store_true", help="Use minimal GUI")
    parser.add_argument("--console", action="store_true", help="Enable console logging")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--nowatchdog", action="store_true", help="Disable watchdog process")
    return parser.parse_args(argv)


class App:
    """Main application class replacing InitializeBot() + MainLoop().

    Coordinates all subsystems: config, state, logging, GUI, bot thread.
    """

    def __init__(self, args: argparse.Namespace | None = None) -> None:
        if args is None:
            args = parse_args([])
        self.args = args
        self.state = BotState()
        self.bot: Bot | None = None
        self.gui: object | None = None
        self._bot_thread: threading.Thread | None = None

        # Initialize base directory for resource resolution (PyInstaller-safe)
        base_dir = init_base_dir()

        # Set image template directory and i18n language directory
        from mybot.config import image_dirs
        image_dirs.set_script_dir(base_dir)

        from mybot import i18n
        i18n.init(base_dir / "Languages")

        # Resolve profile
        self._profiles_dir = get_profiles_dir(args.profiles_dir)
        profile_name = args.profile or get_default_profile(self._profiles_dir)
        self.state.account.profile_name = profile_name
        self.state.account.config_path = get_config_path(self._profiles_dir, profile_name)

        # Ensure profile exists
        create_profile(self._profiles_dir, profile_name)

        # Set GUI mode
        if args.nogui:
            self.state.gui_mode = 0
        elif getattr(args, "minigui", False):
            self.state.gui_mode = 2

        # Initialize logging
        log_dir = self._profiles_dir / profile_name / "logs"
        self.logger = setup_logging(
            log_dir=log_dir,
            debug=args.debug,
            console=True,
        )

        # Read config
        if self.state.account.config_path.exists():
            read_config(self.state.account.config_path, self.state)

        if args.debug:
            self.state.debug.set_log = True

    def _init_bot(self) -> None:
        """Initialize the Bot controller (lazy import to avoid circular deps)."""
        from mybot.bot import Bot
        self.bot = Bot(self.state)

    def _init_gui(self) -> None:
        """Initialize the GUI if not running headless."""
        if self.state.gui_mode == 0:
            return
        try:
            from PyQt6.QtWidgets import QApplication
            # QApplication must exist before any QWidget is created
            self._qapp = QApplication.instance() or QApplication(sys.argv)
            from mybot.gui.main_window import MainWindow
            self.gui = MainWindow(self.state, self.bot)
            self.gui.set_app(self)
            # Route log messages to the GUI log widget
            from mybot.gui.log_widget import LogHandler
            log_handler = LogHandler(self.gui.log_widget)
            self.logger.addHandler(log_handler)
        except ImportError:
            self.logger.warning("PyQt6 not available — running headless")
            self.state.gui_mode = 0

    def run(self) -> int:
        """Run the application main loop.

        Translated from MainLoop() in MyBot.run.au3.
        Dispatches on state.action: START, STOP, SEARCH_MODE, CLOSE.

        Returns:
            Exit code (0 = normal, 1 = error).
        """
        self._init_bot()
        assert self.bot is not None

        self.logger.info(f"MyBot v{__version__} starting (profile: {self.state.account.profile_name})")

        # Handle SIGINT/SIGTERM gracefully
        def _signal_handler(signum: int, frame: object) -> None:
            self.logger.info("Shutdown signal received")
            self.state.action = BotAction.CLOSE
            self.state.stop_event.set()

        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        # Auto-start if requested
        if self.args.autostart:
            self.state.action = BotAction.START

        # If GUI mode, init and run GUI event loop
        if self.state.gui_mode > 0:
            self._init_gui()
            if self.gui is not None:
                return self._run_gui()

        # Headless mode — run the event loop directly
        return self._run_headless()

    def _run_headless(self) -> int:
        """Run in headless mode (no GUI)."""
        assert self.bot is not None
        self.logger.info("Running in headless mode")

        while self.state.action != BotAction.CLOSE:
            action = self.state.action

            if action == BotAction.START:
                self.state.running = True
                try:
                    self.bot.start()
                except Exception as e:
                    self.logger.error(f"Bot error: {e}")
                    self.state.running = False
                    self.state.action = BotAction.STOP

            elif action == BotAction.STOP:
                self.bot.stop()
                self.state.running = False
                if not self.args.autostart:
                    self.state.action = BotAction.CLOSE

            elif action == BotAction.SEARCH_MODE:
                self.state.running = True
                try:
                    self.bot.search_mode()
                except Exception as e:
                    self.logger.error(f"Search mode error: {e}")
                    self.state.action = BotAction.STOP

            else:
                # NO_ACTION — wait for signal
                self.state.stop_event.wait(timeout=1.0)

        self.logger.info("MyBot shutting down")
        return 0

    def _run_gui(self) -> int:
        """Run with GUI event loop."""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        assert app is not None, "QApplication must be created in _init_gui()"
        self.gui.show()  # type: ignore[union-attr]
        return app.exec()

    def start_bot_async(self) -> None:
        """Start the bot in a background thread (for GUI mode)."""
        assert self.bot is not None
        if self._bot_thread and self._bot_thread.is_alive():
            return

        self.state.action = BotAction.START
        self.state.stop_event.clear()
        self._bot_thread = threading.Thread(
            target=self._bot_worker, name="BotThread", daemon=True,
        )
        self._bot_thread.start()

    def stop_bot_async(self) -> None:
        """Signal the bot to stop."""
        self.state.action = BotAction.STOP
        self.state.stop_event.set()
        self.state.running = False

    def _bot_worker(self) -> None:
        """Bot thread worker."""
        assert self.bot is not None
        self.state.running = True
        try:
            self.bot.start()
        except Exception as e:
            self.logger.error(f"Bot thread error: {e}")
        finally:
            self.state.running = False
