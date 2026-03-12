"""Android emulator abstraction layer.

Translated from COCBot/functions/Android/ (15 .au3 files).
Provides emulator detection, ADB communication, input simulation,
screen capture, and health monitoring.
"""

from mybot.android.adb import AdbClient, AdbError
from mybot.android.base import BaseEmulator, EmulatorConfig
from mybot.android.capture import CaptureMode, ScreenCapture
from mybot.android.input import ClickMode
from mybot.android.manager import EmulatorManager

__all__ = [
    "AdbClient",
    "AdbError",
    "BaseEmulator",
    "CaptureMode",
    "ClickMode",
    "EmulatorConfig",
    "EmulatorManager",
    "ScreenCapture",
]
