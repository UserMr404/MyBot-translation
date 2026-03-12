"""Tests for screen capture and pixel functions."""

import numpy as np

from mybot.android.capture import (
    CaptureMode,
    ScreenCapture,
    check_pixel,
    get_pixel_color,
    multi_pixel_search,
    pixel_search,
)


def _make_image(width: int = 10, height: int = 10, color: tuple = (0, 0, 0)) -> np.ndarray:
    """Create a solid-color BGR test image."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = color
    return img


class TestGetPixelColor:
    def test_black(self):
        img = _make_image(color=(0, 0, 0))
        assert get_pixel_color(img, 0, 0) == 0x000000

    def test_red_bgr(self):
        # BGR: (0, 0, 255) = red in display, but in AutoIt COLORREF 0xBBGGRR = 0x0000FF
        img = _make_image(color=(0, 0, 255))
        assert get_pixel_color(img, 0, 0) == 0x0000FF

    def test_blue_bgr(self):
        img = _make_image(color=(255, 0, 0))
        assert get_pixel_color(img, 0, 0) == 0xFF0000

    def test_out_of_bounds(self):
        img = _make_image(width=5, height=5)
        assert get_pixel_color(img, 10, 10) == 0

    def test_specific_pixel(self):
        img = _make_image(width=5, height=5)
        img[2, 3] = (100, 150, 200)  # BGR
        color = get_pixel_color(img, 3, 2)
        assert color == (100 << 16) | (150 << 8) | 200


class TestCheckPixel:
    def test_exact_match(self):
        img = _make_image(color=(255, 0, 0))
        assert check_pixel(img, 0, 0, 0xFF0000)

    def test_no_match(self):
        img = _make_image(color=(255, 0, 0))
        assert not check_pixel(img, 0, 0, 0x000000)

    def test_tolerance(self):
        img = _make_image(color=(100, 100, 100))
        # Should match within tolerance of 5
        target = (103 << 16) | (98 << 8) | 102
        assert check_pixel(img, 0, 0, target, tolerance=5)

    def test_tolerance_fail(self):
        img = _make_image(color=(100, 100, 100))
        target = (110 << 16) | (100 << 8) | 100
        assert not check_pixel(img, 0, 0, target, tolerance=5)


class TestPixelSearch:
    def test_find_pixel(self):
        img = _make_image(width=20, height=20, color=(0, 0, 0))
        img[5, 10] = (0, 255, 0)  # Green pixel at (10, 5)
        result = pixel_search(img, 0, 0, 20, 20, (0 << 16) | (255 << 8) | 0)
        assert result == (10, 5)

    def test_not_found(self):
        img = _make_image(width=10, height=10, color=(0, 0, 0))
        result = pixel_search(img, 0, 0, 10, 10, 0xFFFFFF)
        assert result is None

    def test_search_region(self):
        img = _make_image(width=20, height=20, color=(0, 0, 0))
        img[5, 10] = (0, 255, 0)
        # Search only in region that excludes the pixel
        result = pixel_search(img, 0, 0, 5, 5, (0 << 16) | (255 << 8) | 0)
        assert result is None


class TestMultiPixelSearch:
    def test_find_multiple(self):
        img = _make_image(width=20, height=20, color=(0, 0, 0))
        img[5, 10] = (0, 255, 0)
        img[8, 15] = (0, 255, 0)
        results = multi_pixel_search(img, 0, 0, 20, 20, (0 << 16) | (255 << 8) | 0)
        assert len(results) == 2
        assert (10, 5) in results
        assert (15, 8) in results


class TestScreenCapture:
    def test_init(self):
        cap = ScreenCapture()
        assert cap.mode == CaptureMode.ADB_SCREENCAP
        assert cap.last_capture is None

    def test_mode_setter(self):
        cap = ScreenCapture()
        cap.mode = CaptureMode.ADB_RAW
        assert cap.mode == CaptureMode.ADB_RAW

    def test_save_screenshot(self, tmp_path):
        img = _make_image(width=100, height=50, color=(128, 64, 32))
        cap = ScreenCapture()
        cap._last_capture = img
        out = tmp_path / "test.png"
        assert cap.save_screenshot(out)
        assert out.exists()

    def test_save_no_capture(self, tmp_path):
        cap = ScreenCapture()
        assert not cap.save_screenshot(tmp_path / "test.png")
