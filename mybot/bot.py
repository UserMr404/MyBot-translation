"""Bot controller translated from MBR GUI Action.au3 and MyBot.run.au3.

Replaces BotStart(), BotStop(), BotSearchMode(), runBot(), Initiate(),
and FirstCheck() with a Bot class that manages the main bot cycle.

Source: COCBot/MBR GUI Action.au3 (BotStart/Stop/SearchMode)
Source: MyBot.run.au3 (runBot, Initiate, FirstCheck)
"""

from __future__ import annotations

import random
import time

import numpy as np

from mybot.android.capture import ScreenCapture
from mybot.android.input import click as adb_click
from mybot.android.manager import EmulatorManager
from mybot.constants import COLOR_ERROR, COLOR_INFO, COLOR_SUCCESS, COLOR_WARNING
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
        self._capture: ScreenCapture | None = None

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
            # Fire emulator-specific bot stop event (e.g. restore system bar)
            if self._emu_manager.emulator is not None:
                self._emu_manager.emulator.on_bot_stop()
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
                set_log(f"Failed to initialize {emulator_name}", COLOR_ERROR)
                return False
        else:
            set_log("No emulator configured — auto-detecting")
            if not self._emu_manager.auto_detect():
                set_log("No supported Android emulator found", COLOR_ERROR)
                return False

        set_log("Launching emulator...")
        if not self._emu_manager.open():
            set_log("Failed to open Android emulator", COLOR_ERROR)
            return False

        set_log("Android emulator opened successfully")

        # Create screen capture instance for vision system
        emulator = self._emu_manager.emulator
        if emulator is not None and emulator.adb is not None:
            self._capture = ScreenCapture(adb=emulator.adb)

        # Fire emulator-specific bot start event (e.g. hide system bar)
        if emulator is not None:
            emulator.on_bot_start()

        # Launch Clash of Clans (like _RestartAndroidCoC in Android.au3)
        from mybot.android.app import start_coc
        emulator = self._emu_manager.emulator
        if emulator is not None and emulator.adb is not None:
            if not start_coc(emulator.adb):
                set_log("Failed to launch Clash of Clans", COLOR_ERROR)
                return False

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

        # Wait for main screen to load after CoC launch
        from mybot.game.main_screen import wait_main_screen
        set_log("Waiting for main screen...")
        if not wait_main_screen(self._screenshot, self._click):
            set_log("Main screen not found during initiation", COLOR_WARNING)

        # Zoom out to ensure consistent screenshot coordinates
        from mybot.android.zoom import zoom_out
        if self._emu_manager and self._emu_manager.emulator and self._emu_manager.emulator.adb:
            set_log("Zooming out...")
            zoom_out(self._emu_manager.emulator.adb)

        # First check (one-time init)
        if self.state.first_start:
            self.first_check()
            self.state.first_start = False

        return True

    def first_check(self) -> None:
        """One-time initialization (translated from FirstCheck in MyBot.run.au3).

        Detects Town Hall level via image search, reads initial village
        status, and updates bot state.
        """
        set_log("Running first-time checks")

        image = self._screenshot()
        if image is not None:
            # Detect Town Hall level
            from mybot.config.image_dirs import resolve as resolve_img_dir
            from mybot.vision.townhall import find_town_hall

            th_dirs = [
                resolve_img_dir("imgxml/Buildings/Townhall"),
                resolve_img_dir("imgxml/Buildings/Townhall2"),
            ]
            # Filter to only directories that actually exist
            th_dirs = [d for d in th_dirs if d.is_dir()]

            if th_dirs:
                th_result = find_town_hall(image, th_dirs)
                if th_result.found:
                    self.state.village.town_hall_level = th_result.level
                    set_log(f"Town Hall level detected: {th_result.level}", COLOR_SUCCESS)
                else:
                    set_log("Town Hall not detected on first check", COLOR_WARNING)
            else:
                self.logger.debug("No TH template directories found, skipping detection")

            # Read initial village report
            self._village_report()

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

        self._collect_count += 1
        set_log(f"Main loop iteration #{self._collect_count}", COLOR_INFO)

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
        set_log("Cycle complete, waiting...", COLOR_INFO)
        bot_sleep(5000, self.state.stop_event)

    def _check_main_screen(self) -> None:
        """Verify bot is on main village screen.

        Takes a screenshot and checks if we're on the main screen.
        If not, runs the full check_main_screen recovery loop which
        handles obstacles and retries.
        """
        from mybot.game.main_screen import check_main_screen, is_main_screen

        image = self._screenshot()
        if image is None:
            return

        if not is_main_screen(image):
            set_log("Not on main screen, attempting recovery...")
            if not check_main_screen(self._screenshot, self._click):
                set_log("Main screen recovery failed", COLOR_WARNING)
                self.state.restart_requested = True

    def _check_obstacles(self) -> None:
        """Check for and dismiss error dialogs/popups.

        Takes a screenshot and runs the full obstacle detection pipeline.
        Logs any obstacles found and handled.
        """
        from mybot.game.obstacles import check_obstacles

        image = self._screenshot()
        if image is None:
            return

        result = check_obstacles(image, self._click)
        if result.found:
            set_log(f"Obstacle handled: {result.action_taken}")
            if not result.minor:
                # Non-minor obstacles may need a brief pause for the game to recover
                bot_sleep(2000, self.state.stop_event)

    def _village_report(self) -> None:
        """Read and display village status via OCR.

        Takes a screenshot, reads resources/builders/trophies from known
        screen positions, and updates bot state.
        """
        from mybot.village.report import read_village_report, update_bot_state

        image = self._screenshot()
        if image is None:
            return

        report = read_village_report(image)
        update_bot_state(report, self.state)

    def _do_collections(self) -> None:
        """Perform resource collections in randomized order.

        Translated from the randomized collection block in runBot().
        Uses template matching to find collector buildings with ready
        resources and clicks each one to collect.
        """
        from mybot.village.collect import collect_resources

        result = collect_resources(self._screenshot, self._click)
        if result.total_clicks > 0:
            set_log(f"Collected from {result.total_clicks} buildings")

    def _train_and_donate(self) -> None:
        """Training and donation cycle.

        Translated from the train/donate/request block in runBot().
        """
        self.logger.debug("Train/donate not yet implemented, skipping")

    def _attack_cycle(self) -> None:
        """Execute attack cycle if army is ready.

        Translated from AttackCycle(False) call in runBot().
        """
        self.logger.debug("Attack cycle not yet implemented, skipping")

    # ── Vision Helpers ────────────────────────────────────────────────────

    def _screenshot(self) -> np.ndarray | None:
        """Capture a full screenshot from the emulator.

        Used as capture_func callback for vision/game modules.
        """
        if self._capture is None:
            return None
        return self._capture.capture_full()

    def _click(self, x: int, y: int) -> None:
        """Click at position on the emulator screen.

        Used as click_func callback for vision/game modules.
        Adds small random noise (±2px) to avoid pattern detection.
        """
        if self._emu_manager is None or self._emu_manager.emulator is None:
            return
        adb = self._emu_manager.emulator.adb
        if adb is None:
            return
        noise = random.randint(-2, 2)
        adb_click(x + noise, y + noise, adb=adb, noise=0)

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
