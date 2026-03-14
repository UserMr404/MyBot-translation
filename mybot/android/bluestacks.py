"""BlueStacks 5 emulator implementation translated from AndroidBluestacks5.au3.

Handles BlueStacks 5 detection, initialization, and instance management.
BlueStacks 5 uses Hyper-V backend and stores config in registry + JSON.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from mybot.android.adb import _default_adb_path
from mybot.android.base import BaseEmulator, EmulatorConfig, _read_registry
from mybot.constants import COLOR_ERROR, COLOR_INFO, COLOR_SUCCESS, COLOR_WARNING
from mybot.log import set_debug_log, set_log

# BlueStacks 5 constants (from AndroidBluestacks5.au3)
_BS5_REG_KEY = r"SOFTWARE\BlueStacks_nxt"
_BS5_REG_KEY_USER = r"SOFTWARE\BlueStacks_nxt"
_BS5_WINDOW_CLASS = "HwndWrapper[BstkPlayer*"
_BS5_WINDOW_CLASS_QT = "Qt672QWindowIcon"  # Newer BlueStacks versions use Qt
_BS5_PROCESS = "HD-Player.exe"
_BS5_FRONTEND = "BlueStacks X.exe"
_BS5_DEFAULT_PORT = 5555
_BS5_DEFAULT_DPI = 240


class BlueStacks5(BaseEmulator):
    """BlueStacks 5 emulator control.

    Detection: Registry key SOFTWARE\\BlueStacks_nxt with UserDefinedDir/InstallDir.
    Instances: Managed via BlueStacks Multi-Instance Manager (HD-MultiInstanceManager.exe).
    ADB: Uses its own adb.exe in the install directory.
    Window: Class "HwndWrapper[BstkPlayer*", title "BlueStacks App Player [instance]".
    """

    def __init__(self) -> None:
        super().__init__(EmulatorConfig(name="BlueStacks5"))

    def detect_install(self) -> bool:
        """Check if BlueStacks 5 is installed via registry."""
        return self.get_install_path() is not None

    def get_install_path(self) -> Path | None:
        """Find BlueStacks 5 install directory from registry.

        Checks: HKLM/HKCU SOFTWARE\\BlueStacks_nxt -> InstallDir
        Fallback: C:\\Program Files\\BlueStacks_nxt
        """
        # Try registry
        install_dir = _read_registry(_BS5_REG_KEY, "InstallDir")
        if install_dir:
            path = Path(install_dir)
            if path.exists():
                return path

        # Fallback paths
        for fallback in [
            Path(r"C:\Program Files\BlueStacks_nxt"),
            Path(r"C:\Program Files (x86)\BlueStacks_nxt"),
        ]:
            if fallback.exists():
                return fallback

        return None

    def get_adb_path(self) -> Path | None:
        """Find adb.exe in BlueStacks installation."""
        install = self.get_install_path()
        if install:
            adb = install / "HD-Adb.exe"
            if adb.exists():
                return adb
            # Some versions use standard adb
            adb = install / "adb.exe"
            if adb.exists():
                return adb
        return None

    def _get_data_dir(self) -> Path | None:
        """Get BlueStacks data directory (UserDefinedDir from registry)."""
        data_dir = _read_registry(_BS5_REG_KEY, "UserDefinedDir")
        if data_dir:
            path = Path(data_dir)
            if path.exists():
                return path

        # Fallback to ProgramData
        fallback = Path(r"C:\ProgramData\BlueStacks_nxt")
        if fallback.exists():
            return fallback
        return None

    def get_instance_list(self) -> list[str]:
        """List BlueStacks instances from bluestacks.conf or Engine directory.

        BlueStacks 5 stores instances as directories in the data folder:
        Engine/Nougat64, Engine/Nougat64_1, etc.
        """
        data_dir = self._get_data_dir()
        if not data_dir:
            return []

        engine_dir = data_dir / "Engine"
        if not engine_dir.exists():
            return []

        instances = []
        for entry in engine_dir.iterdir():
            if entry.is_dir() and (
                entry.name.startswith("Nougat") or entry.name.startswith("Pie")
            ):
                instances.append(entry.name)

        return sorted(instances) if instances else ["Nougat64"]

    def _get_instance_port(self, instance: str) -> int:
        """Get ADB port for a specific instance from bluestacks.conf."""
        data_dir = self._get_data_dir()
        if not data_dir:
            return _BS5_DEFAULT_PORT

        conf_file = data_dir / "bluestacks.conf"
        if not conf_file.exists():
            return _BS5_DEFAULT_PORT

        try:
            text = conf_file.read_text(encoding="utf-8", errors="replace")
            # Format: bst.instance.Nougat64.status.adb_port="5555"
            prefix = f"bst.instance.{instance}.status.adb_port="
            for line in text.splitlines():
                if line.startswith(prefix):
                    port_str = line.split("=", 1)[1].strip().strip('"')
                    return int(port_str)
        except (ValueError, OSError):
            pass

        return _BS5_DEFAULT_PORT

    def build_config(self, instance: str = "") -> EmulatorConfig:
        """Build configuration for a BlueStacks 5 instance."""
        if not instance:
            instances = self.get_instance_list()
            instance = instances[0] if instances else "Nougat64"

        install_path = self.get_install_path() or Path()
        adb_path = self.get_adb_path() or _default_adb_path()
        port = self._get_instance_port(instance)

        # Window title pattern varies by BlueStacks version:
        #   Legacy: "BlueStacks App Player" / "BlueStacks App Player Pie64"
        #   Current: "BlueStacks5-Pie64" / "BlueStacks5-Nougat64"
        if instance == "Nougat64":
            window_title = "BlueStacks"
        else:
            window_title = "BlueStacks"

        return EmulatorConfig(
            name="BlueStacks5",
            instance=instance,
            window_class=_BS5_WINDOW_CLASS,
            window_title=window_title,
            adb_port=port,
            path=install_path,
            adb_path=adb_path,
            adb_device=f"127.0.0.1:{port}",
            console_path=install_path / "HD-MultiInstanceManager.exe",
            screen_width=860,
            screen_height=732,
            dpi=_BS5_DEFAULT_DPI,
            process_name=_BS5_PROCESS,
            second_process=_BS5_FRONTEND,
            shortcut_name="BlueStacks 5",
        )

    def _read_conf(self) -> tuple[Path | None, list[str]]:
        """Read bluestacks.conf lines. Returns (path, lines)."""
        data_dir = self._get_data_dir()
        if not data_dir:
            return None, []
        conf = data_dir / "bluestacks.conf"
        if not conf.exists():
            return None, []
        try:
            return conf, conf.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return None, []

    def _write_conf(self, conf_path: Path, lines: list[str]) -> bool:
        """Write bluestacks.conf lines back to disk."""
        try:
            conf_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
        except OSError as e:
            set_log(f"Failed to write bluestacks.conf: {e}", COLOR_ERROR)
            return False

    def ensure_adb_enabled(self) -> bool:
        """Check and enable ADB access in bluestacks.conf if disabled.

        BlueStacks 5 requires ``bst.enable_adb_access="1"`` in
        ``bluestacks.conf`` for ADB to work.  The original AutoIt bot
        assumed the user had already toggled this in the BlueStacks UI.
        This method does it automatically so the bot can connect.

        Must be called **before** BlueStacks is launched, because
        BlueStacks reads this config at startup.

        Returns:
            True if ADB is (now) enabled, False on error.
        """
        conf_path, lines = self._read_conf()
        if conf_path is None:
            set_debug_log("Cannot find bluestacks.conf — skipping ADB enable check")
            return True  # optimistic: maybe ADB is already on

        adb_key = 'bst.enable_adb_access='
        found = False
        changed = False
        for i, line in enumerate(lines):
            if line.startswith(adb_key):
                found = True
                if '"1"' not in line:
                    set_log(
                        "ADB is disabled in BlueStacks settings — enabling automatically",
                        COLOR_WARNING,
                    )
                    lines[i] = 'bst.enable_adb_access="1"'
                    changed = True
                else:
                    set_debug_log("ADB is already enabled in bluestacks.conf")
                break

        if not found:
            set_log("ADB setting missing from bluestacks.conf — adding it", COLOR_WARNING)
            lines.append('bst.enable_adb_access="1"')
            changed = True

        if changed:
            if not self._write_conf(conf_path, lines):
                return False
            set_log("ADB enabled in bluestacks.conf", COLOR_SUCCESS)
        return True

    def set_screen_config(self) -> bool:
        """Ensure ADB is enabled before launch.

        Screen resolution is managed by the user through the BlueStacks UI,
        but ADB access must be enabled for the bot to communicate with the
        emulator.
        """
        return self.ensure_adb_enabled()

    def on_bot_start(self) -> None:
        """Event called when the bot starts.

        Translated from BlueStacks5BotStartEvent() in AndroidBluestacks5.au3.
        Hides the Android system/navigation bar via ADB to maximize game area.
        """
        try:
            # Android Pie+ uses immersive mode policy
            result = self.adb.shell(
                "settings put global policy_control immersive.status=*"
            )
            set_debug_log(f"Closed BlueStacks system bar: {result}")
        except Exception as e:
            set_debug_log(f"Failed to close system bar (immersive), trying legacy: {e}")
            try:
                result = self.adb.shell(
                    "service call activity 42 s16 com.android.systemui"
                )
                set_debug_log(f"Closed BlueStacks system bar (legacy): {result}")
            except Exception as e2:
                set_log(f"Cannot close BlueStacks system bar: {e2}", COLOR_WARNING)

    def on_bot_stop(self) -> None:
        """Event called when the bot stops.

        Translated from BlueStacks5BotStopEvent() in AndroidBluestacks5.au3.
        Restores the Android system bar.
        """
        try:
            result = self.adb.shell(
                "am startservice -n com.android.systemui/.SystemUIService"
            )
            set_debug_log(f"Restored BlueStacks system bar: {result}")
        except Exception as e:
            set_debug_log(f"Failed to restore system bar: {e}")

    def _launch_process(self) -> subprocess.Popen | None:  # type: ignore[type-arg]
        """Launch BlueStacks instance."""
        exe = self.config.path / _BS5_PROCESS
        if not exe.exists():
            set_log(f"BlueStacks player not found: {exe}", COLOR_ERROR)
            return None

        cmd = [str(exe), "--instance", self.config.instance]
        set_debug_log(f"Launching: {' '.join(cmd)}")

        # Retry up to 3 times matching AutoIt LaunchAndroid() behaviour
        for attempt in range(1, 4):
            try:
                proc = subprocess.Popen(cmd, cwd=str(self.config.path))
            except OSError as e:
                set_log(f"Failed to launch BlueStacks (attempt {attempt}): {e}", COLOR_ERROR)
                proc = None

            # Wait 3 seconds then verify the process is still alive
            time.sleep(3)
            if proc and proc.poll() is None:
                # Post-launch settle delay (10s, matching AutoIt)
                time.sleep(10)
                return proc

        set_log("BlueStacks failed to start after 3 attempts", COLOR_ERROR)
        return None

    def _find_window(self) -> int:
        """Find BlueStacks window by class and title."""
        try:
            import win32gui
        except ImportError:
            set_log(
                "pywin32 is not installed — window detection unavailable. "
                "Install with: pip install pywin32",
                COLOR_ERROR,
            )
            return 0

        candidates: list[tuple[int, str, str]] = []  # (hwnd, class, title)

        def _callback(hwnd: int, results: list[int]) -> bool:
            if not win32gui.IsWindowVisible(hwnd):
                return True
            cls = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd)
            # Collect near-misses for diagnostics
            if cls.startswith("HwndWrapper") or "BlueStacks" in title or "Qt" in cls:
                if "BlueStacks" in title or "BstkPlayer" in cls:
                    candidates.append((hwnd, cls, title))
            # Match legacy class (HwndWrapper[BstkPlayer*) or new Qt class
            is_bs_class = (
                cls.startswith("HwndWrapper[BstkPlayer")
                or (cls.startswith("Qt") and cls.endswith("QWindowIcon"))
            )
            if is_bs_class and "BlueStacks" in title:
                if self.config.instance in title:
                    results.append(hwnd)
                    return False
            return True

        results: list[int] = []
        try:
            win32gui.EnumWindows(_callback, results)
        except Exception as e:
            set_log(f"EnumWindows failed: {e}", COLOR_WARNING)

        if results:
            set_debug_log(f"BlueStacks window found: HWND={results[0]}")
            return results[0]

        # Log what we did find to help diagnose mismatches
        if candidates:
            set_debug_log(
                f"No match for class='HwndWrapper[BstkPlayer*' "
                f"title='{self.config.window_title}' or instance='{self.config.instance}'. "
                f"Candidate windows: {candidates[:5]}"
            )
        return 0

    def _get_pid_from_window(self) -> int:
        """Get process ID from window handle."""
        if not self._window_handle:
            return 0
        try:
            import win32process
            _, pid = win32process.GetWindowThreadProcessId(self._window_handle)
            return pid
        except ImportError:
            return 0
