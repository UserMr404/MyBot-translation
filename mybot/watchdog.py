"""Watchdog process translated from MyBot.run.Watchdog.au3.

Monitors the bot process and restarts it if it crashes or becomes unresponsive.

Source: MyBot.run.Watchdog.au3 (196 lines)
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from mybot.log import get_logger


class Watchdog:
    """Bot process watchdog — monitors and restarts the bot on failure.

    The AutoIt version runs as a separate process that monitors the main bot
    window via window messages. This Python version monitors the bot process
    directly.
    """

    def __init__(
        self,
        bot_command: list[str] | None = None,
        check_interval: float = 30.0,
        max_restarts: int = 10,
        restart_delay: float = 5.0,
    ) -> None:
        """Initialize the watchdog.

        Args:
            bot_command: Command to launch the bot process.
            check_interval: Seconds between health checks.
            max_restarts: Maximum restart attempts before giving up.
            restart_delay: Seconds to wait before restarting.
        """
        self.bot_command = bot_command or [sys.executable, "-m", "mybot", "--autostart"]
        self.check_interval = check_interval
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self._process: subprocess.Popen[bytes] | None = None
        self._restart_count = 0
        self._running = False
        self.logger = get_logger()

    def start(self) -> None:
        """Start the watchdog monitoring loop."""
        self._running = True
        self.logger.info("Watchdog started")

        while self._running and self._restart_count < self.max_restarts:
            if self._process is None or self._process.poll() is not None:
                # Process not running — start or restart it
                if self._process is not None:
                    exit_code = self._process.returncode
                    self.logger.warning(
                        f"Bot process exited with code {exit_code} "
                        f"(restart {self._restart_count + 1}/{self.max_restarts})"
                    )
                    time.sleep(self.restart_delay)

                self._start_bot()
                self._restart_count += 1
            else:
                # Process running — check health
                if not self._check_health():
                    self.logger.warning("Bot unresponsive — killing and restarting")
                    self._kill_bot()
                    time.sleep(self.restart_delay)
                    continue

            time.sleep(self.check_interval)

        if self._restart_count >= self.max_restarts:
            self.logger.error(f"Max restarts ({self.max_restarts}) exceeded — watchdog giving up")

        self._running = False

    def stop(self) -> None:
        """Stop the watchdog and the bot process."""
        self._running = False
        self._kill_bot()
        self.logger.info("Watchdog stopped")

    def _start_bot(self) -> None:
        """Start the bot process."""
        self.logger.info(f"Starting bot: {' '.join(self.bot_command)}")
        try:
            self._process = subprocess.Popen(
                self.bot_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except OSError as e:
            self.logger.error(f"Failed to start bot: {e}")

    def _kill_bot(self) -> None:
        """Kill the bot process if running."""
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def _check_health(self) -> bool:
        """Check if the bot process is healthy.

        Uses API health endpoint if available, otherwise just checks if alive.
        """
        if self._process is None or self._process.poll() is not None:
            return False

        try:
            from mybot.api.client import BotAPIClient
            client = BotAPIClient()
            return client.is_reachable()
        except Exception:
            # API not available — just check if process is alive
            return self._process.poll() is None

    @property
    def restart_count(self) -> int:
        """Number of restarts performed."""
        return self._restart_count

    @property
    def is_running(self) -> bool:
        """Whether the watchdog is active."""
        return self._running
