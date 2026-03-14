"""Base emulator abstraction translated from Android.au3.

Provides an abstract base class that BlueStacks5, MEmu, and Nox implement.
Replaces the `Execute("Init" & $g_sAndroidEmulator & "()")` strategy pattern.
"""

from __future__ import annotations

import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from mybot.android.adb import AdbClient
from mybot.constants import COLOR_ERROR, COLOR_SUCCESS
from mybot.log import set_debug_log, set_log


@dataclass
class EmulatorConfig:
    """Emulator configuration matching $g_avAndroidAppConfig columns.

    The AutoIt original uses a 2D array with 16 columns per emulator.
    This dataclass replaces that with named fields.
    """
    name: str = ""                  # Col 0: Emulator name ("BlueStacks5", "MEmu", "Nox")
    instance: str = ""              # Col 1: Instance name ("BlueStacks5", "MEmu_0", "Nox_1")
    window_class: str = ""          # Col 2: Win32 window class for FindWindow
    window_title: str = ""          # Col 3: Window title pattern
    adb_port: int = 5555            # Col 4: Default ADB port
    path: Path = field(default_factory=Path)  # Col 5: Emulator install path
    adb_path: Path = field(default_factory=Path)  # Col 6: Path to adb.exe
    adb_device: str = ""            # Col 7: ADB device string (e.g., "127.0.0.1:5555")
    console_path: Path = field(default_factory=Path)  # Col 8: Console/manager executable
    screen_width: int = 860         # Col 9: Game width
    screen_height: int = 732        # Col 10: Game height
    dpi: int = 240                  # Col 11: Display DPI
    features: int = 0               # Col 12: Feature bitflags
    process_name: str = ""          # Col 13: Process name for detection
    second_process: str = ""        # Col 14: Secondary process name
    shortcut_name: str = ""         # Col 15: Desktop shortcut name


class BaseEmulator(ABC):
    """Abstract base class for Android emulator control.

    Replaces Android.au3's emulator abstraction. Each emulator type
    (BlueStacks5, MEmu, Nox) subclasses this with specific detection,
    initialization, and control logic.
    """

    def __init__(self, config: EmulatorConfig | None = None) -> None:
        self.config = config or EmulatorConfig()
        self._adb: AdbClient | None = None
        self._window_handle: int = 0
        self._pid: int = 0
        self._is_open: bool = False

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def adb(self) -> AdbClient:
        """Get or create the ADB client."""
        if self._adb is None:
            self._adb = AdbClient(
                adb_path=self.config.adb_path,
                device=self.config.adb_device or f"127.0.0.1:{self.config.adb_port}",
            )
        return self._adb

    @property
    def window_handle(self) -> int:
        return self._window_handle

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def is_open(self) -> bool:
        return self._is_open

    # ── Abstract Methods (emulator-specific) ─────────────────────────────

    @abstractmethod
    def detect_install(self) -> bool:
        """Detect if this emulator is installed.

        Check registry keys, default install paths, etc.

        Returns:
            True if emulator is found on the system.
        """

    @abstractmethod
    def get_install_path(self) -> Path | None:
        """Find the emulator installation directory.

        Returns:
            Path to emulator install dir, or None if not found.
        """

    @abstractmethod
    def get_adb_path(self) -> Path | None:
        """Find the ADB binary for this emulator.

        Returns:
            Path to adb.exe, or None if not found.
        """

    @abstractmethod
    def get_instance_list(self) -> list[str]:
        """List available emulator instances.

        Returns:
            List of instance names.
        """

    @abstractmethod
    def build_config(self, instance: str = "") -> EmulatorConfig:
        """Build EmulatorConfig for a specific instance.

        Args:
            instance: Instance name (empty for default).

        Returns:
            Populated EmulatorConfig.
        """

    @abstractmethod
    def _launch_process(self) -> subprocess.Popen | None:  # type: ignore[type-arg]
        """Launch the emulator process.

        Returns:
            Popen object for the launched process, or None on failure.
        """

    @abstractmethod
    def _find_window(self) -> int:
        """Find the emulator window handle.

        Returns:
            Win32 HWND as integer, or 0 if not found.
        """

    @abstractmethod
    def _get_pid_from_window(self) -> int:
        """Get the process ID from the window handle.

        Returns:
            Process ID, or 0 if not found.
        """

    # ── Common Methods ───────────────────────────────────────────────────

    def initialize(self, instance: str = "") -> bool:
        """Initialize emulator configuration.

        Replaces InitBlueStacks5/InitMEmu/InitNox functions.

        Args:
            instance: Instance name (empty for default).

        Returns:
            True if initialization succeeded.
        """
        if not self.detect_install():
            set_log(f"{self.name} not found on this system", COLOR_ERROR)
            return False

        self.config = self.build_config(instance)
        self._adb = None  # Reset ADB client with new config
        set_debug_log(f"Initialized {self.name} instance '{self.config.instance}'")
        return True

    def open(self, timeout: float = 120.0) -> bool:
        """Open the emulator and wait for it to be ready.

        Replaces OpenAndroid() in Android.au3.

        Args:
            timeout: Maximum wait time in seconds.

        Returns:
            True if emulator opened and ADB connected.
        """
        set_log(f"Opening {self.name}...")

        # Check if already running
        hwnd = self._find_window()
        if hwnd:
            self._window_handle = hwnd
            self._pid = self._get_pid_from_window()
            set_debug_log(f"{self.name} already running (HWND={hwnd}, PID={self._pid})")
        else:
            # Launch emulator process
            proc = self._launch_process()
            if proc is None:
                set_log(f"Failed to launch {self.name}", COLOR_ERROR)
                return False

            # Wait for window to appear
            start = time.monotonic()
            while time.monotonic() - start < timeout:
                hwnd = self._find_window()
                if hwnd:
                    self._window_handle = hwnd
                    self._pid = self._get_pid_from_window()
                    break
                time.sleep(2.0)
            else:
                set_log(f"{self.name} window did not appear within {timeout}s", COLOR_ERROR)
                return False

        # Connect ADB
        self.adb.start_server()
        if not self.adb.connect(timeout=30.0):
            set_log(f"ADB connection to {self.name} failed", COLOR_ERROR)
            return False

        # Wait for boot
        if not self.adb.wait_for_boot(timeout=timeout):
            set_log(f"{self.name} did not finish booting within {timeout}s", COLOR_ERROR)
            return False

        # Configure screen resolution to match imgxml templates (860x732 @ 240dpi)
        if not self.setup_screen():
            set_log(f"Failed to configure {self.name} screen resolution", COLOR_ERROR)
            return False

        self._is_open = True
        set_log(f"{self.name} opened successfully", COLOR_SUCCESS)
        return True

    def close(self) -> None:
        """Close the emulator.

        Replaces CloseAndroid() in Android.au3.
        """
        set_log(f"Closing {self.name}...")

        # Disconnect ADB
        if self._adb:
            self._adb.disconnect()

        # Kill emulator process
        if self._pid:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(self._pid)],
                    capture_output=True,
                    timeout=10.0,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        self._window_handle = 0
        self._pid = 0
        self._is_open = False
        set_log(f"{self.name} closed")

    def reboot(self, timeout: float = 120.0) -> bool:
        """Reboot the emulator (close + reopen).

        Replaces RebootAndroid() in Android.au3.

        Args:
            timeout: Maximum wait time for reopen.

        Returns:
            True if reboot succeeded.
        """
        set_log(f"Rebooting {self.name}...")
        self.close()
        time.sleep(5.0)
        return self.open(timeout=timeout)

    def setup_screen(self) -> bool:
        """Configure emulator screen for the game.

        Sets resolution to 860x732 (game area) and DPI to 240.
        Replaces InitiateLayout() display setup portion.

        Returns:
            True if screen setup succeeded.
        """
        try:
            self.adb.set_wm_size(self.config.screen_width, self.config.screen_height)
            self.adb.set_wm_density(self.config.dpi)
            self.adb.set_font_scale(1.0)
            return True
        except Exception as e:
            set_log(f"Screen setup failed: {e}", COLOR_ERROR)
            return False

    def get_screen_size(self) -> tuple[int, int] | None:
        """Get current emulator screen size via ADB.

        Returns:
            (width, height) tuple or None.
        """
        return self.adb.get_wm_size()


def _read_registry(key: str, value: str) -> str | None:
    """Read a Windows registry value.

    Args:
        key: Registry key path (e.g., r"SOFTWARE\\BlueStacks_nxt").
        value: Value name to read.

    Returns:
        Value string, or None if not found.
    """
    try:
        import winreg
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(hive, key) as reg_key:
                    data, _ = winreg.QueryValueEx(reg_key, value)
                    return str(data)
            except FileNotFoundError:
                continue
    except ImportError:
        # Not on Windows
        pass
    return None
