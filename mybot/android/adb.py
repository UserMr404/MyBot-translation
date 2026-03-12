"""ADB client translated from ADB.au3 and Android.au3 ADB functions.

Provides a Python wrapper around ADB for communicating with Android emulators.
Replaces the AutoIt DllCall-based shell pipe approach with subprocess calls.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from mybot.constants import COLOR_ERROR
from mybot.log import set_debug_log, set_log


class AdbError(Exception):
    """Raised when an ADB command fails."""


class AdbClient:
    """Android Debug Bridge client for emulator communication.

    Wraps ADB command execution, providing typed methods for common operations.
    Replaces AutoIt's AndroidAdbSendShellCommand() and LaunchConsole().

    Args:
        adb_path: Path to adb.exe binary.
        device: ADB device string (e.g., "127.0.0.1:5555").
    """

    def __init__(self, adb_path: Path | None = None, device: str = "") -> None:
        self.adb_path = adb_path or Path("adb")
        self.device = device
        self._error_count = 0
        self._max_errors = 10  # Trigger reboot after this many consecutive errors

    def _run(
        self,
        args: list[str],
        timeout: float = 15.0,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Execute an ADB command.

        Args:
            args: ADB command arguments (without "adb" prefix).
            timeout: Command timeout in seconds.
            check: Raise on non-zero exit code.

        Returns:
            CompletedProcess with stdout/stderr.
        """
        cmd = [str(self.adb_path)]
        if self.device:
            cmd.extend(["-s", self.device])
        cmd.extend(args)

        set_debug_log(f"ADB: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if check and result.returncode != 0:
                self._error_count += 1
                raise AdbError(f"ADB failed ({result.returncode}): {result.stderr.strip()}")
            self._error_count = 0
            return result
        except subprocess.TimeoutExpired as e:
            self._error_count += 1
            raise AdbError(f"ADB timeout after {timeout}s") from e
        except FileNotFoundError as e:
            raise AdbError(f"ADB not found at {self.adb_path}") from e

    @property
    def consecutive_errors(self) -> int:
        """Number of consecutive ADB errors (triggers reboot at threshold)."""
        return self._error_count

    @property
    def needs_reboot(self) -> bool:
        """Whether error count exceeds threshold (matches AutoIt behavior)."""
        return self._error_count >= self._max_errors

    def reset_errors(self) -> None:
        """Reset the consecutive error counter."""
        self._error_count = 0

    # ── Connection Management ────────────────────────────────────────────

    def start_server(self) -> None:
        """Start ADB daemon."""
        self._run(["start-server"], check=False)

    def kill_server(self) -> None:
        """Kill ADB daemon."""
        self._run(["kill-server"], check=False)

    def connect(self, timeout: float = 15.0) -> bool:
        """Connect to ADB device.

        Returns:
            True if connected successfully.
        """
        if not self.device:
            return False
        try:
            result = self._run(["connect", self.device], timeout=timeout, check=False)
            connected = "connected" in result.stdout.lower()
            if connected:
                set_debug_log(f"ADB connected to {self.device}")
            else:
                set_log(f"ADB connect failed: {result.stdout.strip()}", COLOR_ERROR)
            return connected
        except AdbError:
            return False

    def disconnect(self) -> None:
        """Disconnect from ADB device."""
        if self.device:
            self._run(["disconnect", self.device], check=False)

    def devices(self) -> list[str]:
        """List connected ADB devices.

        Returns:
            List of device serial strings.
        """
        result = self._run(["devices"], check=False)
        devs = []
        for line in result.stdout.splitlines()[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 2 and parts[1] == "device":
                devs.append(parts[0])
        return devs

    # ── Shell Commands ───────────────────────────────────────────────────

    def shell(self, command: str, timeout: float = 3.0) -> str:
        """Execute a shell command on the Android device.

        Replaces AutoIt's AndroidAdbSendShellCommand().

        Args:
            command: Shell command to execute.
            timeout: Command timeout in seconds.

        Returns:
            Command output (stdout).
        """
        result = self._run(["shell", command], timeout=timeout, check=False)
        return result.stdout.strip()

    def shell_bytes(self, command: str, timeout: float = 10.0) -> bytes:
        """Execute a shell command and return raw bytes."""
        cmd = [str(self.adb_path)]
        if self.device:
            cmd.extend(["-s", self.device])
        cmd.extend(["shell", command])
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return result.stdout

    # ── Touch Input ──────────────────────────────────────────────────────

    def tap(self, x: int, y: int) -> None:
        """Send a tap event at (x, y).

        Replaces ADB click mode in Click.au3.
        """
        self.shell(f"input tap {x} {y}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 250) -> None:
        """Send a swipe/drag event.

        Replaces ADB click drag in ClickDrag.au3.
        """
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    def send_text(self, text: str) -> None:
        """Send text input to the device.

        Replaces AndroidSendText() in Click.au3.
        """
        # Escape special characters for shell
        escaped = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
        self.shell(f"input text '{escaped}'")

    def key_event(self, keycode: int) -> None:
        """Send a key event (e.g., KEYCODE_BACK=4, KEYCODE_HOME=3)."""
        self.shell(f"input keyevent {keycode}")

    def back_button(self) -> None:
        """Press the Android back button."""
        self.key_event(4)

    def home_button(self) -> None:
        """Press the Android home button."""
        self.key_event(3)

    # ── Screen Capture ───────────────────────────────────────────────────

    def screencap_png(self, timeout: float = 10.0) -> bytes:
        """Capture screen as PNG bytes.

        Replaces ADB screencap path in _CaptureRegion.au3.
        Uses exec-out for direct binary output (faster than file push/pull).

        Returns:
            Raw PNG image data.
        """
        cmd = [str(self.adb_path)]
        if self.device:
            cmd.extend(["-s", self.device])
        cmd.extend(["exec-out", "screencap", "-p"])
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode != 0:
            raise AdbError(f"screencap failed: {result.stderr.decode(errors='replace')}")
        return result.stdout

    def screencap_raw(self, timeout: float = 10.0) -> bytes:
        """Capture screen as raw RGBA bytes (faster than PNG).

        Returns:
            Raw pixel data (header + RGBA pixels).
        """
        return self.shell_bytes("screencap", timeout=timeout)

    # ── App Management ───────────────────────────────────────────────────

    def start_app(self, package: str, activity: str = ".MainActivity") -> None:
        """Launch an Android app.

        Replaces StartAndroidCoC() in Android.au3.
        """
        self.shell(f"am start -n {package}/{activity}", timeout=15.0)

    def force_stop(self, package: str) -> None:
        """Force-stop an Android app.

        Replaces CloseCoC() in Close_OpenCoC.au3.
        """
        self.shell(f"am force-stop {package}")

    # ── System Queries ───────────────────────────────────────────────────

    def get_prop(self, prop: str) -> str:
        """Get an Android system property."""
        return self.shell(f"getprop {prop}")

    def is_boot_completed(self) -> bool:
        """Check if Android has finished booting.

        Replaces WaitForAndroidBootCompleted() check in Android.au3.
        """
        result = self.get_prop("sys.boot_completed")
        return result.strip() == "1"

    def wait_for_boot(self, timeout: float = 120.0) -> bool:
        """Wait for Android to finish booting.

        Args:
            timeout: Maximum wait time in seconds.

        Returns:
            True if boot completed, False on timeout.
        """
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            try:
                if self.is_boot_completed():
                    return True
            except AdbError:
                pass
            time.sleep(2.0)
        return False

    def get_wm_size(self) -> tuple[int, int] | None:
        """Get the device window manager size.

        Returns:
            (width, height) tuple, or None if unavailable.
        """
        output = self.shell("wm size")
        # Output format: "Physical size: 860x732"
        for line in output.splitlines():
            if "size:" in line.lower():
                parts = line.split(":")[-1].strip().split("x")
                if len(parts) == 2:
                    try:
                        return (int(parts[0]), int(parts[1]))
                    except ValueError:
                        pass
        return None

    def set_wm_size(self, width: int, height: int) -> None:
        """Set the device window manager size."""
        self.shell(f"wm size {width}x{height}")

    def set_wm_density(self, dpi: int) -> None:
        """Set the device display density."""
        self.shell(f"wm density {dpi}")

    def get_font_scale(self) -> float:
        """Get the current font scale setting."""
        output = self.shell("settings get system font_scale")
        try:
            return float(output.strip())
        except ValueError:
            return 1.0

    def set_font_scale(self, scale: float = 1.0) -> None:
        """Set font scale to normal (1.0)."""
        self.shell(f"settings put system font_scale {scale}")

    # ── File Operations ──────────────────────────────────────────────────

    def push(self, local: Path, remote: str) -> None:
        """Push a file to the device."""
        self._run(["push", str(local), remote])

    def pull(self, remote: str, local: Path) -> None:
        """Pull a file from the device."""
        self._run(["pull", remote, str(local)])
