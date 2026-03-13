"""Multi-instance launcher translated from MultiBot.au3.

Manages multiple bot instances running concurrently with different profiles.

Source: MultiBot.au3 (1,324 lines) and MyBot.run.MiniGui.au3 (1,482 lines)
"""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from mybot.config.profiles import get_profiles_dir, list_profiles
from mybot.log import get_logger


@dataclass
class BotInstance:
    """Represents a running bot instance."""
    profile_name: str
    process: subprocess.Popen[bytes] | None = None
    port: int = 0
    pid: int = 0

    @property
    def is_alive(self) -> bool:
        """Check if the bot process is still running."""
        return self.process is not None and self.process.poll() is None

    @property
    def exit_code(self) -> int | None:
        """Get the exit code if the process has finished."""
        if self.process is None:
            return None
        return self.process.poll()


class MultiBotManager:
    """Manages multiple concurrent bot instances.

    Each instance runs as a separate process with its own profile,
    emulator instance, and API port.
    """

    BASE_API_PORT = 8080

    def __init__(self, profiles_dir: Path | None = None) -> None:
        self.profiles_dir = profiles_dir or get_profiles_dir()
        self.instances: dict[str, BotInstance] = {}
        self.logger = get_logger()

    def launch(self, profile_name: str, extra_args: list[str] | None = None) -> BotInstance:
        """Launch a bot instance for a given profile.

        Args:
            profile_name: Profile name to use.
            extra_args: Additional CLI arguments.

        Returns:
            The BotInstance tracking the launched process.
        """
        if profile_name in self.instances and self.instances[profile_name].is_alive:
            self.logger.warning(f"Instance for '{profile_name}' already running")
            return self.instances[profile_name]

        port = self.BASE_API_PORT + len(self.instances)
        cmd = [
            sys.executable, "-m", "mybot",
            "--profile", profile_name,
            "--autostart",
            "--nogui",
        ]
        if extra_args:
            cmd.extend(extra_args)

        self.logger.info(f"Launching bot instance: {profile_name} (port {port})")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            instance = BotInstance(
                profile_name=profile_name,
                process=process,
                port=port,
                pid=process.pid,
            )
            self.instances[profile_name] = instance
            return instance
        except OSError as e:
            self.logger.error(f"Failed to launch '{profile_name}': {e}")
            return BotInstance(profile_name=profile_name)

    def launch_all(self, profile_names: list[str] | None = None) -> list[BotInstance]:
        """Launch bot instances for all (or specified) profiles.

        Args:
            profile_names: Profiles to launch. None = all available.

        Returns:
            List of launched instances.
        """
        names = profile_names or list_profiles(self.profiles_dir)
        return [self.launch(name) for name in names]

    def stop(self, profile_name: str) -> None:
        """Stop a specific bot instance."""
        instance = self.instances.get(profile_name)
        if instance and instance.is_alive:
            self.logger.info(f"Stopping instance: {profile_name}")
            assert instance.process is not None
            instance.process.terminate()
            try:
                instance.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                instance.process.kill()

    def stop_all(self) -> None:
        """Stop all running bot instances."""
        for name in list(self.instances.keys()):
            self.stop(name)

    def get_status(self) -> dict[str, dict[str, object]]:
        """Get status of all instances."""
        status: dict[str, dict[str, object]] = {}
        for name, instance in self.instances.items():
            status[name] = {
                "alive": instance.is_alive,
                "pid": instance.pid,
                "port": instance.port,
                "exit_code": instance.exit_code,
            }
        return status

    @property
    def running_count(self) -> int:
        """Number of currently running instances."""
        return sum(1 for inst in self.instances.values() if inst.is_alive)
