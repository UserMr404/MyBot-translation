"""Tests for the ADB client."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mybot.android.adb import AdbClient, AdbError


class TestAdbClient:
    """Tests for AdbClient."""

    def test_init_defaults(self):
        client = AdbClient()
        assert client.adb_path == Path("adb")
        assert client.device == ""
        assert client.consecutive_errors == 0
        assert not client.needs_reboot

    def test_init_custom(self):
        client = AdbClient(adb_path=Path("/usr/bin/adb"), device="127.0.0.1:5555")
        assert client.adb_path == Path("/usr/bin/adb")
        assert client.device == "127.0.0.1:5555"

    def test_error_counter(self):
        client = AdbClient()
        assert client.consecutive_errors == 0
        client._error_count = 5
        assert client.consecutive_errors == 5
        assert not client.needs_reboot
        client._error_count = 10
        assert client.needs_reboot

    def test_reset_errors(self):
        client = AdbClient()
        client._error_count = 10
        client.reset_errors()
        assert client.consecutive_errors == 0

    @patch("subprocess.run")
    def test_run_builds_command(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        client = AdbClient(adb_path=Path("adb"), device="127.0.0.1:5555")
        client._run(["devices"])
        args = mock_run.call_args[0][0]
        assert args == ["adb", "-s", "127.0.0.1:5555", "devices"]

    @patch("subprocess.run")
    def test_run_no_device(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        client = AdbClient(adb_path=Path("adb"))
        client._run(["devices"])
        args = mock_run.call_args[0][0]
        assert args == ["adb", "devices"]

    @patch("subprocess.run")
    def test_run_error_increments_counter(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error msg")
        client = AdbClient()
        with pytest.raises(AdbError, match="ADB failed"):
            client._run(["fail"], check=True)
        assert client.consecutive_errors == 1

    @patch("subprocess.run")
    def test_run_success_resets_counter(self, mock_run):
        client = AdbClient()
        client._error_count = 5
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        client._run(["ok"])
        assert client.consecutive_errors == 0

    @patch("subprocess.run")
    def test_run_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("adb", 15)
        client = AdbClient()
        with pytest.raises(AdbError, match="timeout"):
            client._run(["slow"])

    @patch("subprocess.run")
    def test_shell(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="  output  ", stderr="")
        client = AdbClient()
        result = client.shell("echo test")
        assert result == "output"

    @patch("subprocess.run")
    def test_devices_parsing(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="List of devices attached\n127.0.0.1:5555\tdevice\nemulator-5556\toffline\n",
            stderr="",
        )
        client = AdbClient()
        devs = client.devices()
        assert devs == ["127.0.0.1:5555"]

    @patch("subprocess.run")
    def test_connect_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="connected to 127.0.0.1:5555", stderr=""
        )
        client = AdbClient(device="127.0.0.1:5555")
        assert client.connect() is True

    @patch("subprocess.run")
    def test_connect_no_device(self, mock_run):
        client = AdbClient()
        assert client.connect() is False

    @patch("subprocess.run")
    def test_get_wm_size(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Physical size: 860x732", stderr=""
        )
        client = AdbClient()
        size = client.get_wm_size()
        assert size == (860, 732)

    @patch("subprocess.run")
    def test_is_boot_completed(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="1", stderr="")
        client = AdbClient()
        assert client.is_boot_completed() is True

    @patch("subprocess.run")
    def test_get_font_scale_default(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="null", stderr="")
        client = AdbClient()
        assert client.get_font_scale() == 1.0
