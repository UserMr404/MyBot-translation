"""Input simulation translated from Click.au3 and ClickDrag.au3.

Provides click, tap, swipe, and text input functions with multiple backends:
- ADB touch commands (default, most reliable)
- Win32 PostMessage (faster, works with embedded windows)
- Win32 ControlClick (fallback)

The AutoIt original supports 4 click modes with random noise injection.
This translation preserves that behavior.
"""

from __future__ import annotations

import random
import time
from enum import IntEnum

from mybot.android.adb import AdbClient
from mybot.log import set_debug_log
from mybot.utils.sleep import sleep_ms


class ClickMode(IntEnum):
    """Click input methods matching AutoIt's click mode constants."""
    ADB = 0       # ADB input tap (default)
    POST_MSG = 1  # Win32 PostMessage WM_LBUTTONDOWN/UP
    CTRL_CLICK = 2  # Win32 ControlClick
    CTRL_SEND = 3   # Win32 ControlSend


# Win32 message constants
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_MOUSEMOVE = 0x0200
MK_LBUTTON = 0x0001


def _make_lparam(x: int, y: int) -> int:
    """Pack x, y into LPARAM (MAKELPARAM macro)."""
    return (y << 16) | (x & 0xFFFF)


def click(
    x: int,
    y: int,
    adb: AdbClient | None = None,
    hwnd: int = 0,
    mode: ClickMode = ClickMode.ADB,
    clicks: int = 1,
    delay_ms: int = 50,
    noise: int = 0,
) -> None:
    """Send a click/tap at (x, y).

    Replaces Click(), PureClick(), GemClick() from Click.au3.
    Supports random noise injection to avoid pattern detection.

    Args:
        x: X coordinate.
        y: Y coordinate.
        adb: ADB client (required for ADB mode).
        hwnd: Window handle (required for PostMessage/ControlClick modes).
        mode: Click input method.
        clicks: Number of clicks to send.
        delay_ms: Delay between multiple clicks.
        noise: Maximum random pixel offset (0 = exact coordinates).
    """
    for i in range(clicks):
        # Apply random noise
        cx = x + random.randint(-noise, noise) if noise else x
        cy = y + random.randint(-noise, noise) if noise else y

        if mode == ClickMode.ADB:
            _click_adb(cx, cy, adb)
        elif mode == ClickMode.POST_MSG:
            _click_postmessage(cx, cy, hwnd)
        elif mode == ClickMode.CTRL_CLICK:
            _click_controlclick(cx, cy, hwnd)
        else:
            _click_adb(cx, cy, adb)

        if i < clicks - 1 and delay_ms > 0:
            sleep_ms(delay_ms)

    set_debug_log(f"Click({x}, {y}) mode={mode.name} clicks={clicks}")


def _click_adb(x: int, y: int, adb: AdbClient | None) -> None:
    """Send tap via ADB."""
    if adb is None:
        return
    adb.tap(x, y)


def _click_postmessage(x: int, y: int, hwnd: int) -> None:
    """Send click via Win32 PostMessage.

    Sends WM_LBUTTONDOWN + WM_LBUTTONUP to the window.
    Works even when the window is not in the foreground.
    """
    if not hwnd:
        return
    try:
        import win32gui
        lparam = _make_lparam(x, y)
        win32gui.PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
        time.sleep(0.02)
        win32gui.PostMessage(hwnd, WM_LBUTTONUP, 0, lparam)
    except ImportError:
        pass


def _click_controlclick(x: int, y: int, hwnd: int) -> None:
    """Send click via Win32 ControlClick (using ctypes)."""
    if not hwnd:
        return
    try:
        import ctypes
        lparam = _make_lparam(x, y)
        ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
        time.sleep(0.02)
        ctypes.windll.user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lparam)
    except (AttributeError, OSError):
        pass


def click_drag(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    adb: AdbClient | None = None,
    hwnd: int = 0,
    mode: ClickMode = ClickMode.ADB,
    duration_ms: int = 250,
    noise: int = 0,
) -> None:
    """Send a click-drag (swipe) from (x1, y1) to (x2, y2).

    Replaces ClickDrag() from ClickDrag.au3.

    Args:
        x1, y1: Start coordinates.
        x2, y2: End coordinates.
        adb: ADB client (required for ADB mode).
        hwnd: Window handle (required for PostMessage mode).
        mode: Input method.
        duration_ms: Swipe duration in milliseconds.
        noise: Maximum random pixel offset.
    """
    # Apply noise
    if noise:
        x1 += random.randint(-noise, noise)
        y1 += random.randint(-noise, noise)
        x2 += random.randint(-noise, noise)
        y2 += random.randint(-noise, noise)

    if mode == ClickMode.ADB:
        if adb:
            adb.swipe(x1, y1, x2, y2, duration_ms)
    elif mode in (ClickMode.POST_MSG, ClickMode.CTRL_CLICK):
        _drag_postmessage(x1, y1, x2, y2, hwnd, duration_ms)

    set_debug_log(f"ClickDrag({x1},{y1} -> {x2},{y2}) mode={mode.name}")


def _drag_postmessage(
    x1: int, y1: int, x2: int, y2: int, hwnd: int, duration_ms: int
) -> None:
    """Send drag via Win32 PostMessage with intermediate moves."""
    if not hwnd:
        return
    try:
        import win32gui

        # Mouse down at start
        win32gui.PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, _make_lparam(x1, y1))

        # Send intermediate mouse move events
        steps = max(5, duration_ms // 20)
        for i in range(1, steps + 1):
            t = i / steps
            cx = int(x1 + (x2 - x1) * t)
            cy = int(y1 + (y2 - y1) * t)
            win32gui.PostMessage(hwnd, WM_MOUSEMOVE, MK_LBUTTON, _make_lparam(cx, cy))
            time.sleep(duration_ms / steps / 1000.0)

        # Mouse up at end
        win32gui.PostMessage(hwnd, WM_LBUTTONUP, 0, _make_lparam(x2, y2))
    except ImportError:
        pass


def send_text(
    text: str,
    adb: AdbClient | None = None,
    hwnd: int = 0,
    mode: ClickMode = ClickMode.ADB,
) -> None:
    """Send text input.

    Replaces AndroidSendText() from Click.au3.
    """
    if mode == ClickMode.ADB and adb:
        adb.send_text(text)
    elif hwnd:
        try:
            import win32con
            import win32gui
            for char in text:
                win32gui.PostMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
                time.sleep(0.01)
        except ImportError:
            pass


def key_event(
    keycode: int,
    adb: AdbClient | None = None,
) -> None:
    """Send a key event via ADB.

    Args:
        keycode: Android keycode (e.g., 4=BACK, 3=HOME).
    """
    if adb:
        adb.key_event(keycode)
