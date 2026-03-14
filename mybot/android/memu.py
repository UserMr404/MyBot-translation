"""MEmu emulator implementation translated from AndroidMEmu.au3.

Handles MEmu detection, initialization, and instance management.
MEmu uses VirtualBox-based backend with memuc.exe for instance control.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from mybot.android.adb import _default_adb_path
from mybot.android.base import BaseEmulator, EmulatorConfig, _read_registry
from mybot.constants import COLOR_ERROR
from mybot.log import set_debug_log, set_log

# MEmu constants (from AndroidMEmu.au3)
_MEMU_REG_KEY = r"SOFTWARE\Microvirt\MEmu"
_MEMU_WINDOW_CLASS = "Qt5QWindowIcon"
_MEMU_PROCESS = "MEmu.exe"
_MEMU_SVC_PROCESS = "MEmuHeadless.exe"
_MEMU_DEFAULT_PORT = 21503  # MEmu starts at 21503, increments by 10
_MEMU_DEFAULT_DPI = 240


class MEmu(BaseEmulator):
    """MEmu emulator control.

    Detection: Registry key SOFTWARE\\Microvirt\\MEmu with InstallDir.
    Instances: Managed via memuc.exe (MEmu Command line utility).
    ADB: Uses adb.exe in the install directory.
    Window: Class "Qt5QWindowIcon", title "MEmu [index]" or custom name.
    Port: Base 21503, each instance increments by 10 (21503, 21513, 21523...).
    """

    def __init__(self) -> None:
        super().__init__(EmulatorConfig(name="MEmu"))

    def detect_install(self) -> bool:
        return self.get_install_path() is not None

    def get_install_path(self) -> Path | None:
        """Find MEmu install directory from registry or default paths.

        Registry: HKLM SOFTWARE\\Microvirt\\MEmu -> InstallDir
        Fallback: C:\\Program Files\\Microvirt\\MEmu
        """
        install_dir = _read_registry(_MEMU_REG_KEY, "InstallDir")
        if install_dir:
            path = Path(install_dir)
            if path.exists():
                return path

        for fallback in [
            Path(r"C:\Program Files\Microvirt\MEmu"),
            Path(r"C:\Program Files (x86)\Microvirt\MEmu"),
        ]:
            if fallback.exists():
                return fallback

        return None

    def get_adb_path(self) -> Path | None:
        """Find adb.exe in MEmu installation."""
        install = self.get_install_path()
        if install:
            adb = install / "adb.exe"
            if adb.exists():
                return adb
        return None

    def _get_memuc(self) -> Path | None:
        """Get path to memuc.exe (MEmu command-line utility)."""
        install = self.get_install_path()
        if install:
            memuc = install / "memuc.exe"
            if memuc.exists():
                return memuc
        return None

    def get_instance_list(self) -> list[str]:
        """List MEmu instances using memuc.exe.

        memuc listvms outputs: index, title, window_handle, is_running, pid, disk_usage
        """
        memuc = self._get_memuc()
        if not memuc:
            return ["MEmu"]

        try:
            result = subprocess.run(
                [str(memuc), "listvms"],
                capture_output=True,
                text=True,
                timeout=10.0,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            instances = []
            for line in result.stdout.splitlines():
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    # parts[0] = index, parts[1] = name
                    name = parts[1].strip()
                    if name:
                        instances.append(name)
            return instances if instances else ["MEmu"]
        except (subprocess.TimeoutExpired, OSError):
            return ["MEmu"]

    def _get_instance_index(self, instance: str) -> int:
        """Get the numeric index for an instance name.

        MEmu names: "MEmu" = index 0, "MEmu_1" = index 1, etc.
        """
        if instance == "MEmu":
            return 0
        match = re.search(r"_(\d+)$", instance)
        if match:
            return int(match.group(1))
        return 0

    def build_config(self, instance: str = "") -> EmulatorConfig:
        if not instance:
            instance = "MEmu"

        install_path = self.get_install_path() or Path()
        adb_path = self.get_adb_path() or _default_adb_path()

        # Port calculation: base 21503 + (index * 10)
        idx = self._get_instance_index(instance)
        port = _MEMU_DEFAULT_PORT + (idx * 10)

        # Window title: "MEmu" for default, "MEmu 1" etc for others
        if idx == 0:
            window_title = "MEmu"
        else:
            window_title = f"MEmu {idx}"

        return EmulatorConfig(
            name="MEmu",
            instance=instance,
            window_class=_MEMU_WINDOW_CLASS,
            window_title=window_title,
            adb_port=port,
            path=install_path,
            adb_path=adb_path,
            adb_device=f"127.0.0.1:{port}",
            console_path=install_path / "MEmuConsole.exe",
            screen_width=860,
            screen_height=732,
            dpi=_MEMU_DEFAULT_DPI,
            process_name=_MEMU_PROCESS,
            second_process=_MEMU_SVC_PROCESS,
            shortcut_name="MEmu",
        )

    def _launch_process(self) -> subprocess.Popen | None:  # type: ignore[type-arg]
        """Launch MEmu instance using MEmuConsole.exe."""
        console = self.config.console_path
        if not console.exists():
            # Try MEmu.exe directly
            exe = self.config.path / _MEMU_PROCESS
            if not exe.exists():
                set_log(f"MEmu not found: {exe}", COLOR_ERROR)
                return None
            cmd = [str(exe)]
        else:
            # MEmuConsole.exe startvm <instance>
            cmd = [str(console), "startvm", self.config.instance]

        set_debug_log(f"Launching: {' '.join(cmd)}")
        try:
            return subprocess.Popen(
                cmd,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as e:
            set_log(f"Failed to launch MEmu: {e}", COLOR_ERROR)
            return None

    def _find_window(self) -> int:
        """Find MEmu window by class and title."""
        try:
            import win32gui
            def _callback(hwnd: int, results: list[int]) -> bool:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                cls = win32gui.GetClassName(hwnd)
                title = win32gui.GetWindowText(hwnd)
                if cls == _MEMU_WINDOW_CLASS and "MEmu" in title:
                    if (self.config.window_title == title or
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
        if not self._window_handle:
            return 0
        try:
            import win32process
            _, pid = win32process.GetWindowThreadProcessId(self._window_handle)
            return pid
        except ImportError:
            return 0
