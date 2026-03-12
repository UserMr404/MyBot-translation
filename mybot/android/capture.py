"""Screen capture module translated from _CaptureRegion.au3 and MakeScreenshot.au3.

Provides screen capture from Android emulators with multiple backends:
- ADB screencap (default, works with all emulators)
- Win32 PrintWindow (faster, requires window handle)
- Win32 BitBlt (fastest, but may capture overlapping windows)

The AutoIt original uses GDI+ to manage bitmaps. This translation uses
Pillow (PIL) and numpy for image manipulation, with optional Win32 capture.
"""

from __future__ import annotations

import io
import time
from enum import IntEnum
from pathlib import Path

import numpy as np
from PIL import Image

from mybot.android.adb import AdbClient, AdbError
from mybot.constants import (
    COLOR_ERROR,
    GAME_HEIGHT,
    GAME_WIDTH,
)
from mybot.log import set_debug_log, set_log


class CaptureMode(IntEnum):
    """Screen capture backend matching AutoIt's capture modes."""
    ADB_SCREENCAP = 0   # ADB exec-out screencap -p (PNG)
    ADB_RAW = 1         # ADB screencap (raw RGBA, faster)
    PRINT_WINDOW = 2    # Win32 PrintWindow API
    BITBLT = 3           # Win32 BitBlt (GDI)


class ScreenCapture:
    """Screen capture from Android emulator.

    Replaces _CaptureRegion() and related functions from _CaptureRegion.au3.
    Captures the emulator screen and provides it as a numpy array for
    image processing (OpenCV template matching, pixel scanning, OCR).

    Args:
        adb: ADB client for ADB-based capture.
        hwnd: Window handle for Win32-based capture.
        mode: Capture backend to use.
    """

    def __init__(
        self,
        adb: AdbClient | None = None,
        hwnd: int = 0,
        mode: CaptureMode = CaptureMode.ADB_SCREENCAP,
    ) -> None:
        self._adb = adb
        self._hwnd = hwnd
        self._mode = mode
        self._last_capture: np.ndarray | None = None
        self._last_capture_time: float = 0.0

    @property
    def mode(self) -> CaptureMode:
        return self._mode

    @mode.setter
    def mode(self, value: CaptureMode) -> None:
        self._mode = value

    @property
    def last_capture(self) -> np.ndarray | None:
        """Last captured frame as numpy array (BGR format for OpenCV)."""
        return self._last_capture

    def capture_region(
        self,
        x: int = 0,
        y: int = 0,
        width: int = GAME_WIDTH,
        height: int = GAME_HEIGHT,
    ) -> np.ndarray | None:
        """Capture a region of the emulator screen.

        Replaces _CaptureRegion($x, $y, $right, $bottom) from _CaptureRegion.au3.
        The AutoIt version stores result in global $g_hHBitmap; this returns
        a numpy array suitable for OpenCV processing.

        Args:
            x: Left coordinate of capture region.
            y: Top coordinate of capture region.
            width: Width of capture region.
            height: Height of capture region.

        Returns:
            BGR numpy array of the captured region, or None on failure.
        """
        full_frame = self._capture_full()
        if full_frame is None:
            return None

        self._last_capture_time = time.monotonic()

        # Crop to requested region
        h, w = full_frame.shape[:2]
        x2 = min(x + width, w)
        y2 = min(y + height, h)
        if x >= w or y >= h:
            return None

        region = full_frame[y:y2, x:x2]
        self._last_capture = region
        return region

    def capture_full(self) -> np.ndarray | None:
        """Capture the full emulator screen.

        Returns:
            BGR numpy array of the full screen, or None on failure.
        """
        frame = self._capture_full()
        if frame is not None:
            self._last_capture = frame
            self._last_capture_time = time.monotonic()
        return frame

    def _capture_full(self) -> np.ndarray | None:
        """Internal: capture full screen using the configured mode."""
        if self._mode == CaptureMode.ADB_SCREENCAP:
            return self._capture_adb_png()
        elif self._mode == CaptureMode.ADB_RAW:
            return self._capture_adb_raw()
        elif self._mode == CaptureMode.PRINT_WINDOW:
            return self._capture_printwindow()
        elif self._mode == CaptureMode.BITBLT:
            return self._capture_bitblt()
        return None

    def _capture_adb_png(self) -> np.ndarray | None:
        """Capture via ADB screencap PNG output."""
        if not self._adb:
            return None
        try:
            png_data = self._adb.screencap_png()
            if not png_data:
                return None
            img = Image.open(io.BytesIO(png_data))
            # Convert to BGR for OpenCV compatibility
            arr = np.array(img)
            if arr.ndim == 3 and arr.shape[2] == 4:
                # RGBA -> BGR
                return arr[:, :, 2::-1]
            elif arr.ndim == 3 and arr.shape[2] == 3:
                # RGB -> BGR
                return arr[:, :, ::-1]
            return arr
        except (AdbError, OSError, ValueError) as e:
            set_debug_log(f"ADB PNG capture failed: {e}")
            return None

    def _capture_adb_raw(self) -> np.ndarray | None:
        """Capture via ADB screencap raw RGBA output.

        Raw format: 4-byte width + 4-byte height + 4-byte format + RGBA pixels.
        Faster than PNG as it skips compression.
        """
        if not self._adb:
            return None
        try:
            raw = self._adb.screencap_raw()
            if not raw or len(raw) < 12:
                return None

            # Parse header (little-endian uint32)
            width = int.from_bytes(raw[0:4], "little")
            height = int.from_bytes(raw[4:8], "little")
            # raw[8:12] = pixel format (1 = RGBA_8888)

            pixel_data = raw[12:]
            expected = width * height * 4
            if len(pixel_data) < expected:
                set_debug_log(f"Raw capture size mismatch: {len(pixel_data)} < {expected}")
                return None

            arr = np.frombuffer(pixel_data[:expected], dtype=np.uint8)
            arr = arr.reshape((height, width, 4))
            # RGBA -> BGR
            return arr[:, :, 2::-1]
        except (AdbError, OSError, ValueError) as e:
            set_debug_log(f"ADB raw capture failed: {e}")
            return None

    def _capture_printwindow(self) -> np.ndarray | None:
        """Capture via Win32 PrintWindow API.

        Works even when the window is behind other windows.
        """
        if not self._hwnd:
            return None
        try:
            import ctypes
            import ctypes.wintypes

            import win32gui
            import win32ui

            # Get window dimensions
            rect = win32gui.GetClientRect(self._hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            if w <= 0 or h <= 0:
                return None

            # Create DC and bitmap
            hwnd_dc = win32gui.GetDC(self._hwnd)
            mem_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mem_dc.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mem_dc, w, h)
            save_dc.SelectObject(bitmap)

            # PrintWindow with PW_CLIENTONLY | PW_RENDERFULLCONTENT
            ctypes.windll.user32.PrintWindow(self._hwnd, save_dc.GetSafeHdc(), 3)

            # Convert to numpy array
            bmp_info = bitmap.GetInfo()
            bmp_data = bitmap.GetBitmapBits(True)
            arr = np.frombuffer(bmp_data, dtype=np.uint8)
            arr = arr.reshape((bmp_info["bmHeight"], bmp_info["bmWidth"], 4))

            # Cleanup
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mem_dc.DeleteDC()
            win32gui.ReleaseDC(self._hwnd, hwnd_dc)

            # BGRA -> BGR
            return arr[:, :, :3]
        except (ImportError, Exception) as e:
            set_debug_log(f"PrintWindow capture failed: {e}")
            return None

    def _capture_bitblt(self) -> np.ndarray | None:
        """Capture via Win32 BitBlt (fastest but captures overlapping windows)."""
        if not self._hwnd:
            return None
        try:
            import win32con
            import win32gui
            import win32ui

            rect = win32gui.GetClientRect(self._hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            if w <= 0 or h <= 0:
                return None

            hwnd_dc = win32gui.GetDC(self._hwnd)
            mem_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mem_dc.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mem_dc, w, h)
            save_dc.SelectObject(bitmap)
            save_dc.BitBlt((0, 0), (w, h), mem_dc, (0, 0), win32con.SRCCOPY)

            bmp_info = bitmap.GetInfo()
            bmp_data = bitmap.GetBitmapBits(True)
            arr = np.frombuffer(bmp_data, dtype=np.uint8)
            arr = arr.reshape((bmp_info["bmHeight"], bmp_info["bmWidth"], 4))

            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mem_dc.DeleteDC()
            win32gui.ReleaseDC(self._hwnd, hwnd_dc)

            return arr[:, :, :3]
        except (ImportError, Exception) as e:
            set_debug_log(f"BitBlt capture failed: {e}")
            return None

    def save_screenshot(
        self,
        path: Path,
        image: np.ndarray | None = None,
    ) -> bool:
        """Save a screenshot to file.

        Replaces MakeScreenshot() from MakeScreenshot.au3.

        Args:
            path: Output file path (.png recommended).
            image: Image to save (default: last capture).

        Returns:
            True if save succeeded.
        """
        img = image if image is not None else self._last_capture
        if img is None:
            return False

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # BGR -> RGB for PIL
            rgb = img[:, :, ::-1] if img.ndim == 3 and img.shape[2] == 3 else img
            Image.fromarray(rgb).save(str(path))
            set_debug_log(f"Screenshot saved: {path}")
            return True
        except (OSError, ValueError) as e:
            set_log(f"Failed to save screenshot: {e}", COLOR_ERROR)
            return False


def get_pixel_color(image: np.ndarray, x: int, y: int) -> int:
    """Get pixel color at (x, y) from a captured image.

    Replaces _GetPixelColor() from _GetPixelColor.au3.

    Args:
        image: BGR numpy array.
        x: X coordinate.
        y: Y coordinate.

    Returns:
        Color as 0xBBGGRR integer (AutoIt COLORREF format).
    """
    h, w = image.shape[:2]
    if x < 0 or x >= w or y < 0 or y >= h:
        return 0
    b, g, r = image[y, x, :3]
    return (int(b) << 16) | (int(g) << 8) | int(r)


def check_pixel(
    image: np.ndarray,
    x: int,
    y: int,
    color: int,
    tolerance: int = 0,
) -> bool:
    """Check if pixel at (x, y) matches the expected color.

    Replaces _CheckPixel() from _CheckPixel.au3.

    Args:
        image: BGR numpy array.
        x: X coordinate.
        y: Y coordinate.
        color: Expected color (0xBBGGRR).
        tolerance: Color distance tolerance per channel.

    Returns:
        True if the pixel matches within tolerance.
    """
    actual = get_pixel_color(image, x, y)
    if tolerance == 0:
        return actual == color

    # Compare per channel
    for shift in (0, 8, 16):
        ac = (actual >> shift) & 0xFF
        ec = (color >> shift) & 0xFF
        if abs(ac - ec) > tolerance:
            return False
    return True


def pixel_search(
    image: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: int,
    tolerance: int = 0,
) -> tuple[int, int] | None:
    """Search for a pixel color in a region.

    Replaces _PixelSearch() from _PixelSearch.au3.

    Args:
        image: BGR numpy array.
        x1, y1: Top-left of search region.
        x2, y2: Bottom-right of search region.
        color: Color to find (0xBBGGRR).
        tolerance: Color distance tolerance.

    Returns:
        (x, y) of first match, or None.
    """
    h, w = image.shape[:2]
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    # Extract target BGR
    tb = (color >> 16) & 0xFF
    tg = (color >> 8) & 0xFF
    tr = color & 0xFF

    region = image[y1:y2, x1:x2]

    if tolerance == 0:
        mask = (
            (region[:, :, 0] == tb) &
            (region[:, :, 1] == tg) &
            (region[:, :, 2] == tr)
        )
    else:
        mask = (
            (np.abs(region[:, :, 0].astype(int) - tb) <= tolerance) &
            (np.abs(region[:, :, 1].astype(int) - tg) <= tolerance) &
            (np.abs(region[:, :, 2].astype(int) - tr) <= tolerance)
        )

    matches = np.argwhere(mask)
    if len(matches) > 0:
        ry, rx = matches[0]
        return (x1 + int(rx), y1 + int(ry))
    return None


def multi_pixel_search(
    image: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: int,
    tolerance: int = 0,
) -> list[tuple[int, int]]:
    """Search for all pixels matching a color in a region.

    Replaces _MultiPixelSearch() from _MultiPixelSearch.au3.

    Returns:
        List of (x, y) coordinates of all matches.
    """
    h, w = image.shape[:2]
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    tb = (color >> 16) & 0xFF
    tg = (color >> 8) & 0xFF
    tr = color & 0xFF

    region = image[y1:y2, x1:x2]

    if tolerance == 0:
        mask = (
            (region[:, :, 0] == tb) &
            (region[:, :, 1] == tg) &
            (region[:, :, 2] == tr)
        )
    else:
        mask = (
            (np.abs(region[:, :, 0].astype(int) - tb) <= tolerance) &
            (np.abs(region[:, :, 1].astype(int) - tg) <= tolerance) &
            (np.abs(region[:, :, 2].astype(int) - tr) <= tolerance)
        )

    matches = np.argwhere(mask)
    return [(x1 + int(rx), y1 + int(ry)) for ry, rx in matches]
