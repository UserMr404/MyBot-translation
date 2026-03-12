"""Tests for game app management."""

from unittest.mock import MagicMock, patch

from mybot.android.app import (
    COC_PACKAGE,
    get_coc_distributor,
    is_coc_running,
    start_coc,
    stop_coc,
)


class TestIsCocRunning:
    def test_running(self):
        adb = MagicMock()
        adb.shell.return_value = "12345"
        assert is_coc_running(adb) is True

    def test_not_running(self):
        adb = MagicMock()
        adb.shell.return_value = ""
        assert is_coc_running(adb) is False


class TestStopCoc:
    def test_stop(self):
        adb = MagicMock()
        stop_coc(adb)
        adb.force_stop.assert_called_once_with(COC_PACKAGE)


class TestStartCoc:
    @patch("mybot.android.app.is_coc_running", return_value=True)
    @patch("mybot.android.app.time")
    def test_start_success(self, mock_time, mock_running):
        mock_time.monotonic.side_effect = [0, 1]
        adb = MagicMock()
        result = start_coc(adb, timeout=5.0)
        assert result is True
        adb.start_app.assert_called_once()


class TestGetDistributor:
    def test_google_play(self):
        adb = MagicMock()
        adb.shell.return_value = "package:/data/app/com.supercell.clashofclans"
        result = get_coc_distributor(adb)
        assert result == COC_PACKAGE

    def test_not_installed(self):
        adb = MagicMock()
        adb.shell.return_value = ""
        result = get_coc_distributor(adb)
        assert result == COC_PACKAGE  # Falls back to default
