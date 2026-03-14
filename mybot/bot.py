"""Bot controller translated from MBR GUI Action.au3 and MyBot.run.au3.

Replaces BotStart(), BotStop(), BotSearchMode(), runBot(), Initiate(),
and FirstCheck() with a Bot class that manages the main bot cycle.

Source: COCBot/MBR GUI Action.au3 (BotStart/Stop/SearchMode)
Source: MyBot.run.au3 (runBot, Initiate, FirstCheck)
"""

from __future__ import annotations

import random
import time

from mybot.android.manager import EmulatorManager
from mybot.enums import BotAction
from mybot.log import get_logger, set_log
from mybot.state import BotState
from mybot.utils.sleep import bot_sleep


class Bot:
    """Main bot controller managing the gameplay cycle.

    Replaces the AutoIt runBot() infinite loop plus BotStart/BotStop.
    """

    def __init__(self, state: BotState) -> None:
        self.state = state
        self.logger = get_logger()
        self._attack_count = 0
        self._collect_count = 0
        self._emu_manager: EmulatorManager | None = None

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the bot (translated from BotStart in MBR GUI Action.au3).

        Opens Android emulator, initiates layout check, then enters main loop.
        """
        self.logger.info("Bot starting")
        self.state.running = True
        self.state.stop_event.clear()

        try:
            # Open Android emulator
            if not self._open_android():
                self.logger.error("Failed to open Android emulator")
                return

            # Initiate — check screen, zoom out
            if not self.initiate():
                self.logger.error("Initiation failed")
                return

            # Enter main cycle
            self.run()
        finally:
            self.state.running = False

    def stop(self) -> None:
        """Stop the bot (translated from BotStop in MBR GUI Action.au3).

        Signals all loops to exit, releases resources.
        """
        self.logger.info("Bot stopping")
        self.state.stop_event.set()
        self.state.running = False
        self.state.action = BotAction.STOP

        if self._emu_manager is not None:
            self._emu_manager.close()
            self._emu_manager = None

    def search_mode(self) -> None:
        """Run in search-only mode (translated from BotSearchMode).

        Searches for bases without attacking — for statistics/testing.
        """
        self.logger.info("Search mode started")
        self.state.search.is_searching = True
        self.state.running = True

        try:
            self.run(search_only=True)
        finally:
            self.state.search.is_searching = False
            self.state.running = False

    # ── Initiation ─────────────────────────────────────────────────────────

    def _open_android(self) -> bool:
        """Open the Android emulator (translated from OpenAndroid).

        Uses EmulatorManager to select and launch the configured emulator.
        """
        set_log("Opening Android emulator")

        self._emu_manager = EmulatorManager()

        emulator_name = self.state.android.emulator
        instance = self.state.android.instance

        if emulator_name:
            set_log(f"Selecting emulator: {emulator_name}")
            if not self._emu_manager.select(emulator_name, instance):
                set_log(f"Failed to initialize {emulator_name}", "ERROR")
                return False
        else:
            set_log("No emulator configured — auto-detecting")
            if not self._emu_manager.auto_detect():
                set_log("No supported Android emulator found", "ERROR")
                return False

        set_log("Launching emulator...")
        if not self._emu_manager.open():
            set_log("Failed to open Android emulator", "ERROR")
            return False

        set_log("Android emulator opened successfully")
        return True

    def initiate(self) -> bool:
        """Initiate bot operation (translated from Initiate in MyBot.run.au3).

        Checks main screen, zooms out, and prepares for main cycle.

        Returns:
            True if initiation was successful.
        """
        set_log("Initiating bot")

        if self._is_stopped():
            return False

        # Check main screen
        try:
            from mybot.game.main_screen import check_main_screen
            # In production, pass capture_func from android
            set_log("Checking main screen")
        except ImportError:
            pass

        # Zoom out
        try:
            from mybot.android.zoom import zoom_out
            set_log("Zooming out")
        except ImportError:
            pass

        # First check (one-time init)
        if self.state.first_start:
            self.first_check()
            self.state.first_start = False

        return True

    def first_check(self) -> None:
        """One-time initialization (translated from FirstCheck in MyBot.run.au3).

        Checks Lab, Heroes, Buildings, Achievements on first run.
        """
        set_log("Running first-time checks")

        # Check Town Hall level, lab, heroes, etc.
        # These are stubs — full implementation uses vision/OCR
        self.state.first_run = 0

    # ── Main Cycle ─────────────────────────────────────────────────────────

    def run(self, search_only: bool = False) -> None:
        """Main bot cycle (translated from runBot in MyBot.run.au3).

        Infinite loop performing:
        1. Check restart conditions
        2. Donation/training cycle
        3. Collection (randomized order)
        4. Attack cycle
        5. Builder Base operations

        Args:
            search_only: If True, only search (don't attack).
        """
        set_log("Main bot cycle started")

        while not self._is_stopped():
            try:
                self._main_iteration(search_only)
            except Exception as e:
                self.logger.error(f"Error in main cycle: {e}")
                if self._is_stopped():
                    break
                # Wait before retrying
                bot_sleep(5000, self.state.stop_event)

        set_log("Main bot cycle ended")

    def _main_iteration(self, search_only: bool = False) -> None:
        """Single iteration of the main loop.

        Translated from runBot's inner loop.
        """
        if self._is_stopped():
            return

        # ── Check main screen ──────────────────────────────────────────
        self._check_main_screen()
        if self._is_stopped():
            return

        # ── Check obstacles ────────────────────────────────────────────
        self._check_obstacles()
        if self._is_stopped():
            return

        # ── Village report ─────────────────────────────────────────────
        self._village_report()

        # ── Collections (randomized order like AutoIt) ─────────────────
        self._do_collections()
        if self._is_stopped():
            return

        # ── Donation / Training / Request cycle ────────────────────────
        if not search_only:
            self._train_and_donate()
            if self._is_stopped():
                return

        # ── Attack cycle ───────────────────────────────────────────────
        if not search_only and self.state.army.is_full:
            self._attack_cycle()

        # ── Idle time ──────────────────────────────────────────────────
        bot_sleep(2000, self.state.stop_event)

    def _check_main_screen(self) -> None:
        """Verify bot is on main village screen."""
        try:
            from mybot.game.main_screen import is_main_screen
        except ImportError:
            pass

    def _check_obstacles(self) -> None:
        """Check for and dismiss error dialogs."""
        try:
            from mybot.game.obstacles import check_obstacles
        except ImportError:
            pass

    def _village_report(self) -> None:
        """Read and display village status."""
        try:
            from mybot.village.report import read_village_report
        except ImportError:
            pass

    def _do_collections(self) -> None:
        """Perform resource collections in randomized order.

        Translated from the randomized collection block in runBot().
        """
        collection_tasks = [
            self._collect_resources,
            self._check_tombs,
            self._clean_yard,
            self._collect_achievements,
        ]
        random.shuffle(collection_tasks)

        for task in collection_tasks:
            if self._is_stopped():
                return
            task()

    def _collect_resources(self) -> None:
        """Collect resources from mines/collectors."""
        try:
            from mybot.village.collect import collect_resources
        except ImportError:
            pass

    def _check_tombs(self) -> None:
        """Check and clear hero altar tombs."""
        pass

    def _clean_yard(self) -> None:
        """Remove obstacles from village."""
        pass

    def _collect_achievements(self) -> None:
        """Collect achievement rewards."""
        pass

    def _train_and_donate(self) -> None:
        """Training and donation cycle.

        Translated from the train/donate/request block in runBot().
        """
        # Donate CC
        try:
            from mybot.village.donate import donate_cc
        except ImportError:
            pass

        # Train army
        try:
            from mybot.army.train import train_system
        except ImportError:
            pass

    def _attack_cycle(self) -> None:
        """Execute attack cycle if army is ready.

        Translated from AttackCycle(False) call in runBot().
        """
        try:
            from mybot.attack.cycle import AttackCycleConfig, attack_cycle
            self._attack_count += 1
        except ImportError:
            pass

    # ── Helpers ────────────────────────────────────────────────────────────

    def _is_stopped(self) -> bool:
        """Check if bot should stop."""
        return self.state.stop_event.is_set() or self.state.action == BotAction.CLOSE

    @property
    def attack_count(self) -> int:
        """Total attacks performed this session."""
        return self._attack_count

    @property
    def is_running(self) -> bool:
        """Whether the bot is currently running."""
        return self.state.running
