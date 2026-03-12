"""Tests for emulator base class and manager."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from mybot.android.base import BaseEmulator, EmulatorConfig
from mybot.android.manager import (
    EmulatorManager,
    create_emulator,
    detect_emulators,
    get_supported_emulators,
)


class ConcreteEmulator(BaseEmulator):
    """Concrete test implementation of BaseEmulator."""

    def __init__(self):
        super().__init__(EmulatorConfig(name="TestEmu"))
        self._installed = True
        self._instances = ["test_0"]

    def detect_install(self) -> bool:
        return self._installed

    def get_install_path(self) -> Path | None:
        return Path("/fake/install") if self._installed else None

    def get_adb_path(self) -> Path | None:
        return Path("/fake/adb") if self._installed else None

    def get_instance_list(self) -> list[str]:
        return self._instances

    def build_config(self, instance: str = "") -> EmulatorConfig:
        return EmulatorConfig(
            name="TestEmu",
            instance=instance or "test_0",
            adb_port=5555,
            adb_device="127.0.0.1:5555",
            path=Path("/fake/install"),
            adb_path=Path("/fake/adb"),
        )

    def _launch_process(self, **kwargs):
        return MagicMock()

    def _find_window(self) -> int:
        return 12345

    def _get_pid_from_window(self) -> int:
        return 9999


class TestEmulatorConfig:
    def test_defaults(self):
        cfg = EmulatorConfig()
        assert cfg.name == ""
        assert cfg.adb_port == 5555
        assert cfg.screen_width == 860
        assert cfg.screen_height == 732
        assert cfg.dpi == 240

    def test_custom(self):
        cfg = EmulatorConfig(name="MEmu", adb_port=21503)
        assert cfg.name == "MEmu"
        assert cfg.adb_port == 21503


class TestBaseEmulator:
    def test_init(self):
        emu = ConcreteEmulator()
        assert emu.name == "TestEmu"
        assert not emu.is_open
        assert emu.window_handle == 0
        assert emu.pid == 0

    def test_adb_property(self):
        emu = ConcreteEmulator()
        emu.config = emu.build_config()
        adb = emu.adb
        assert adb is not None
        assert adb.device == "127.0.0.1:5555"
        # Same instance on repeated access
        assert emu.adb is adb

    def test_initialize(self):
        emu = ConcreteEmulator()
        assert emu.initialize("test_1")
        assert emu.config.instance == "test_1"

    def test_initialize_not_installed(self):
        emu = ConcreteEmulator()
        emu._installed = False
        assert not emu.initialize()


class TestEmulatorManager:
    def test_supported_emulators(self):
        names = get_supported_emulators()
        assert "BlueStacks5" in names
        assert "MEmu" in names
        assert "Nox" in names

    def test_create_emulator_valid(self):
        emu = create_emulator("BlueStacks5")
        assert emu is not None
        assert emu.name == "BlueStacks5"

    def test_create_emulator_invalid(self):
        emu = create_emulator("FakeEmulator")
        assert emu is None

    def test_manager_initial_state(self):
        mgr = EmulatorManager()
        assert mgr.emulator is None
        assert not mgr.is_ready

    @patch("mybot.android.bluestacks.BlueStacks5.detect_install", return_value=False)
    @patch("mybot.android.memu.MEmu.detect_install", return_value=False)
    @patch("mybot.android.nox.Nox.detect_install", return_value=False)
    def test_detect_none(self, *_):
        found = detect_emulators()
        assert found == []

    @patch("mybot.android.bluestacks.BlueStacks5.detect_install", return_value=True)
    @patch("mybot.android.memu.MEmu.detect_install", return_value=False)
    @patch("mybot.android.nox.Nox.detect_install", return_value=False)
    @patch("mybot.android.bluestacks.BlueStacks5.get_install_path", return_value=Path("/fake"))
    def test_detect_bluestacks(self, *_):
        found = detect_emulators()
        assert "BlueStacks5" in found
