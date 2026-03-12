"""Emulator lifecycle manager translated from Android.au3.

Provides a factory and manager for emulator instances.
Replaces the `Execute("Init" & $g_sAndroidEmulator & "()")` dispatch pattern
with a proper strategy pattern using BaseEmulator subclasses.
"""

from __future__ import annotations

from mybot.android.base import BaseEmulator
from mybot.android.bluestacks import BlueStacks5
from mybot.android.memu import MEmu
from mybot.android.nox import Nox
from mybot.constants import COLOR_ERROR
from mybot.log import set_debug_log, set_log

# Registry of supported emulators
_EMULATOR_CLASSES: dict[str, type[BaseEmulator]] = {
    "BlueStacks5": BlueStacks5,
    "MEmu": MEmu,
    "Nox": Nox,
}


def get_supported_emulators() -> list[str]:
    """Return list of supported emulator names."""
    return list(_EMULATOR_CLASSES.keys())


def create_emulator(name: str) -> BaseEmulator | None:
    """Create an emulator instance by name.

    Args:
        name: Emulator name ("BlueStacks5", "MEmu", "Nox").

    Returns:
        BaseEmulator instance, or None if name is unknown.
    """
    cls = _EMULATOR_CLASSES.get(name)
    if cls is None:
        set_log(f"Unknown emulator: {name}", COLOR_ERROR)
        return None
    return cls()


def detect_emulators() -> list[str]:
    """Detect which emulators are installed on this system.

    Returns:
        List of installed emulator names.
    """
    found = []
    for name, cls in _EMULATOR_CLASSES.items():
        try:
            emu = cls()
            if emu.detect_install():
                found.append(name)
                set_debug_log(f"Detected {name} installation")
        except Exception:
            pass
    return found


class EmulatorManager:
    """Manages the active emulator instance for the bot.

    Replaces global emulator state in Android.au3.
    Provides a single point of control for emulator lifecycle.
    """

    def __init__(self) -> None:
        self._emulator: BaseEmulator | None = None

    @property
    def emulator(self) -> BaseEmulator | None:
        return self._emulator

    @property
    def is_ready(self) -> bool:
        """Whether an emulator is initialized and open."""
        return self._emulator is not None and self._emulator.is_open

    def select(self, name: str, instance: str = "") -> bool:
        """Select and initialize an emulator.

        Args:
            name: Emulator name.
            instance: Instance name (empty for default).

        Returns:
            True if emulator was initialized.
        """
        emu = create_emulator(name)
        if emu is None:
            return False

        if not emu.initialize(instance):
            return False

        self._emulator = emu
        return True

    def auto_detect(self) -> bool:
        """Auto-detect and select the first available emulator.

        Returns:
            True if an emulator was found and selected.
        """
        detected = detect_emulators()
        if not detected:
            set_log("No supported Android emulator found", COLOR_ERROR)
            return False

        set_debug_log(f"Auto-detected emulators: {detected}")
        return self.select(detected[0])

    def open(self, timeout: float = 120.0) -> bool:
        """Open the selected emulator.

        Returns:
            True if emulator opened successfully.
        """
        if self._emulator is None:
            set_log("No emulator selected", COLOR_ERROR)
            return False
        return self._emulator.open(timeout=timeout)

    def close(self) -> None:
        """Close the active emulator."""
        if self._emulator:
            self._emulator.close()

    def reboot(self, timeout: float = 120.0) -> bool:
        """Reboot the active emulator.

        Returns:
            True if reboot succeeded.
        """
        if self._emulator is None:
            set_log("No emulator selected", COLOR_ERROR)
            return False
        return self._emulator.reboot(timeout=timeout)
