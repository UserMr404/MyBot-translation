"""Tests for emulator health monitoring."""

import time
from unittest.mock import MagicMock, patch

from mybot.android.adb import AdbClient
from mybot.android.health import (
    check_android_reboot_condition,
    check_bot_restart_condition,
)


class TestCheckAndroidReboot:
    def test_no_reboot_needed(self):
        adb = MagicMock(spec=AdbClient)
        adb.needs_reboot = False
        result = check_android_reboot_condition(adb, pid=0)
        assert result is None

    def test_adb_error_threshold(self):
        adb = MagicMock(spec=AdbClient)
        adb.needs_reboot = True
        adb.consecutive_errors = 10
        result = check_android_reboot_condition(adb)
        assert result is not None
        assert "consecutive errors" in result

    @patch("mybot.android.health._is_process_alive", return_value=False)
    def test_dead_process(self, _):
        adb = MagicMock(spec=AdbClient)
        adb.needs_reboot = False
        result = check_android_reboot_condition(adb, pid=12345)
        assert result is not None
        assert "not running" in result

    @patch("mybot.android.health._is_process_alive", return_value=True)
    def test_alive_process(self, _):
        adb = MagicMock(spec=AdbClient)
        adb.needs_reboot = False
        result = check_android_reboot_condition(adb, pid=12345)
        assert result is None

    def test_scheduled_reboot(self):
        adb = MagicMock(spec=AdbClient)
        adb.needs_reboot = False
        # last_reboot was 2 hours ago, interval is 1 hour
        result = check_android_reboot_condition(
            adb,
            reboot_interval_hours=1.0,
            last_reboot_time=time.monotonic() - 7200,
        )
        assert result is not None
        assert "Scheduled" in result


class TestCheckBotRestart:
    def test_no_restart(self):
        adb = MagicMock(spec=AdbClient)
        adb.devices.return_value = ["127.0.0.1:5555"]
        adb.device = "127.0.0.1:5555"
        result = check_bot_restart_condition(adb)
        assert result is None

    def test_scheduled_restart(self):
        adb = MagicMock(spec=AdbClient)
        adb.devices.return_value = []
        adb.device = ""
        result = check_bot_restart_condition(
            adb,
            restart_interval_hours=1.0,
            bot_start_time=time.monotonic() - 7200,
        )
        assert result is not None
        assert "Scheduled" in result

    def test_adb_device_missing(self):
        adb = MagicMock(spec=AdbClient)
        adb.devices.return_value = ["127.0.0.1:5555"]
        adb.device = "127.0.0.1:9999"
        result = check_bot_restart_condition(adb)
        assert result is not None
        assert "not in device list" in result
