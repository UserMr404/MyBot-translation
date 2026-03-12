"""Tests for input simulation module."""

from unittest.mock import MagicMock

from mybot.android.input import (
    ClickMode,
    click,
    click_drag,
    key_event,
    send_text,
)


class TestClick:
    def test_click_adb(self):
        adb = MagicMock()
        click(100, 200, adb=adb, mode=ClickMode.ADB)
        adb.tap.assert_called_once_with(100, 200)

    def test_click_multiple(self):
        adb = MagicMock()
        click(100, 200, adb=adb, mode=ClickMode.ADB, clicks=3, delay_ms=0)
        assert adb.tap.call_count == 3

    def test_click_no_adb(self):
        # Should not raise
        click(100, 200, adb=None, mode=ClickMode.ADB)

    def test_click_noise(self):
        """With noise, coordinates should vary."""
        adb = MagicMock()
        clicks = []
        for _ in range(20):
            adb.reset_mock()
            click(100, 200, adb=adb, mode=ClickMode.ADB, noise=5)
            x, y = adb.tap.call_args[0]
            clicks.append((x, y))

        # At least some clicks should differ from exact coords
        xs = {c[0] for c in clicks}
        ys = {c[1] for c in clicks}
        # With noise=5, we expect some variation (not all exactly 100, 200)
        assert len(xs) > 1 or len(ys) > 1


class TestClickDrag:
    def test_drag_adb(self):
        adb = MagicMock()
        click_drag(10, 20, 300, 400, adb=adb, mode=ClickMode.ADB, duration_ms=500)
        adb.swipe.assert_called_once_with(10, 20, 300, 400, 500)


class TestKeyEvent:
    def test_key_event(self):
        adb = MagicMock()
        key_event(4, adb=adb)
        adb.key_event.assert_called_once_with(4)


class TestSendText:
    def test_send_text_adb(self):
        adb = MagicMock()
        send_text("hello", adb=adb, mode=ClickMode.ADB)
        adb.send_text.assert_called_once_with("hello")
