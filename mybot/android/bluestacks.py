"""BlueStacks 5 emulator implementation translated from AndroidBluestacks5.au3.

Handles BlueStacks 5 detection, initialization, and instance management.
BlueStacks 5 uses Hyper-V backend and stores config in registry + JSON.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from mybot.android.base import BaseEmulator, EmulatorConfig, _read_registry
from mybot.constants import COLOR_ERROR
from mybot.log import set_debug_log, set_log

# BlueStacks 5 constants (from AndroidBluestacks5.au3)
_BS5_REG_KEY = r"SOFTWARE\BlueStacks_nxt"
_BS5_REG_KEY_USER = r"SOFTWARE\BlueStacks_nxt"
_BS5_WINDOW_CLASS = "HwndWrapper[BstkPlayer*"
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
            if entry.is_dir() and entry.name.startswith("Nougat"):
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
        adb_path = self.get_adb_path() or Path("adb")
        port = self._get_instance_port(instance)

        # Window title pattern: "BlueStacks App Player" or instance-specific
        if instance == "Nougat64":
            window_title = "BlueStacks App Player"
        else:
            window_title = f"BlueStacks App Player {instance}"

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

    def _launch_process(self) -> subprocess.Popen | None:  # type: ignore[type-arg]
        """Launch BlueStacks instance."""
        exe = self.config.path / _BS5_PROCESS
        if not exe.exists():
            set_log(f"BlueStacks player not found: {exe}", COLOR_ERROR)
            return None

        cmd = [str(exe), "--instance", self.config.instance]
        set_debug_log(f"Launching: {' '.join(cmd)}")

        try:
            return subprocess.Popen(
                cmd,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as e:
            set_log(f"Failed to launch BlueStacks: {e}", COLOR_ERROR)
            return None

    def _find_window(self) -> int:
        """Find BlueStacks window by class and title."""
        try:
            import win32gui
            def _callback(hwnd: int, results: list[int]) -> bool:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                cls = win32gui.GetClassName(hwnd)
                title = win32gui.GetWindowText(hwnd)
                if cls.startswith("HwndWrapper[BstkPlayer"):
                    if (self.config.window_title in title or
                            self.config.instance in title):
                        results.append(hwnd)
                        return False
                return True

            results: list[int] = []
            try:
                win32gui.EnumWindows(_callback, results)
            except Exception:
                pass
            return results[0] if results else 0
        except ImportError:
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
