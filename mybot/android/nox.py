"""Nox emulator implementation translated from AndroidNox.au3.

Handles Nox Player detection, initialization, and instance management.
Nox uses VirtualBox backend with Nox.exe for instance control.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from mybot.android.adb import _default_adb_path
from mybot.android.base import BaseEmulator, EmulatorConfig, _read_registry
from mybot.constants import COLOR_ERROR
from mybot.log import set_debug_log, set_log

# Nox constants (from AndroidNox.au3)
_NOX_REG_KEY = r"SOFTWARE\BigNox\VirtualBox"
_NOX_REG_KEY_ALT = r"SOFTWARE\Duodian\dnplayer"
_NOX_WINDOW_CLASS = "Qt5154QWindowIcon"
_NOX_WINDOW_CLASS_ALT = "Qt5QWindowIcon"
_NOX_PROCESS = "Nox.exe"
_NOX_SVC_PROCESS = "NoxVMHandle.exe"
_NOX_DEFAULT_PORT = 62001  # Nox: 62001, 62025, 62025+n*...
_NOX_DEFAULT_DPI = 240


class Nox(BaseEmulator):
    """Nox Player emulator control.

    Detection: Registry key SOFTWARE\\BigNox\\VirtualBox with InstallDir.
    Instances: Managed via MultiPlayerManager or Nox.exe -clone:name.
    ADB: Uses nox_adb.exe or adb.exe in install/bin directory.
    Window: Class "Qt5154QWindowIcon" or "Qt5QWindowIcon", title "NoxPlayer [index]".
    Port: Base 62001, incrementing (62001, 62025, 62026...).
    """

    def __init__(self) -> None:
        super().__init__(EmulatorConfig(name="Nox"))

    def detect_install(self) -> bool:
        return self.get_install_path() is not None

    def get_install_path(self) -> Path | None:
        """Find Nox install directory from registry or default paths.

        Registry: HKLM SOFTWARE\\BigNox\\VirtualBox -> InstallDir
        Fallback: C:\\Program Files\\Nox\\bin or C:\\Program Files (x86)\\Nox\\bin
        """
        install_dir = _read_registry(_NOX_REG_KEY, "InstallDir")
        if install_dir:
            path = Path(install_dir)
            if path.exists():
                return path

        install_dir = _read_registry(_NOX_REG_KEY_ALT, "InstallDir")
        if install_dir:
            path = Path(install_dir)
            if path.exists():
                return path

        for fallback in [
            Path(r"C:\Program Files\Nox\bin"),
            Path(r"C:\Program Files (x86)\Nox\bin"),
            Path(r"D:\Program Files\Nox\bin"),
        ]:
            if fallback.exists():
                return fallback

        return None

    def get_adb_path(self) -> Path | None:
        """Find adb in Nox installation (nox_adb.exe or adb.exe)."""
        install = self.get_install_path()
        if install:
            # Nox uses nox_adb.exe
            nox_adb = install / "nox_adb.exe"
            if nox_adb.exists():
                return nox_adb
            adb = install / "adb.exe"
            if adb.exists():
                return adb
        return None

    def get_instance_list(self) -> list[str]:
        """List Nox instances from BignoxVMS directory.

        Nox stores VM configs in: <install>/../BignoxVMS/nox_<index>/
        Or uses MultiPlayerManager to list instances.
        """
        install = self.get_install_path()
        if not install:
            return ["Nox"]

        vms_dir = install.parent / "BignoxVMS"
        if not vms_dir.exists():
            return ["Nox"]

        instances = []
        for entry in vms_dir.iterdir():
            if entry.is_dir() and entry.name.startswith("nox"):
                instances.append(entry.name)

        return sorted(instances) if instances else ["Nox"]

    def _get_instance_index(self, instance: str) -> int:
        """Get numeric index from instance name (e.g., 'nox_1' -> 1)."""
        if instance in ("Nox", "nox"):
            return 0
        match = re.search(r"_(\d+)$", instance)
        if match:
            return int(match.group(1))
        return 0

    def build_config(self, instance: str = "") -> EmulatorConfig:
        if not instance:
            instance = "Nox"

        install_path = self.get_install_path() or Path()
        adb_path = self.get_adb_path() or _default_adb_path()

        # Port calculation: index 0 = 62001, index 1 = 62025, index n = 62025 + (n-1)
        idx = self._get_instance_index(instance)
        if idx == 0:
            port = 62001
        else:
            port = 62025 + (idx - 1)

        # Window title: "NoxPlayer" for default, "NoxPlayer1" etc
        if idx == 0:
            window_title = "NoxPlayer"
        else:
            window_title = f"NoxPlayer{idx}"

        return EmulatorConfig(
            name="Nox",
            instance=instance,
            window_class=_NOX_WINDOW_CLASS,
            window_title=window_title,
            adb_port=port,
            path=install_path,
            adb_path=adb_path,
            adb_device=f"127.0.0.1:{port}",
            console_path=install_path / "MultiPlayerManager.exe",
            screen_width=860,
            screen_height=732,
            dpi=_NOX_DEFAULT_DPI,
            process_name=_NOX_PROCESS,
            second_process=_NOX_SVC_PROCESS,
            shortcut_name="Nox",
        )

    def _launch_process(self) -> subprocess.Popen | None:  # type: ignore[type-arg]
        """Launch Nox instance."""
        exe = self.config.path / _NOX_PROCESS
        if not exe.exists():
            set_log(f"Nox not found: {exe}", COLOR_ERROR)
            return None

        idx = self._get_instance_index(self.config.instance)
        if idx == 0:
            cmd = [str(exe)]
        else:
            cmd = [str(exe), f"-clone:Nox_{idx}"]

        set_debug_log(f"Launching: {' '.join(cmd)}")
        try:
            return subprocess.Popen(
                cmd,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as e:
            set_log(f"Failed to launch Nox: {e}", COLOR_ERROR)
            return None

    def _find_window(self) -> int:
        """Find Nox window by class and title."""
        try:
            import win32gui
            def _callback(hwnd: int, results: list[int]) -> bool:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                cls = win32gui.GetClassName(hwnd)
                title = win32gui.GetWindowText(hwnd)
                if cls in (_NOX_WINDOW_CLASS, _NOX_WINDOW_CLASS_ALT):
                    if ("Nox" in title and
                            (self.config.window_title in title or
                             self.config.instance in title)):
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
