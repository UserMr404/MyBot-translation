"""Tests for PyInstaller-compatible path resolution."""

import sys
from pathlib import Path
from unittest.mock import patch

from mybot.utils.paths import (
    data_dir,
    get_base_dir,
    init_base_dir,
    resource_path,
)


class TestInitBaseDir:
    def test_explicit_base(self, tmp_path):
        result = init_base_dir(tmp_path)
        assert result == tmp_path.resolve()
        assert get_base_dir() == tmp_path.resolve()

    def test_source_mode(self):
        """In source mode (no sys.frozen), base should be repo root."""
        # Ensure frozen is not set
        with patch.object(sys, "frozen", False, create=True):
            result = init_base_dir()
            # Should be grandparent of utils/paths.py → mybot/ → repo root
            assert result.is_dir()

    def test_frozen_mode(self, tmp_path):
        """In frozen mode, base should be sys._MEIPASS."""
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
            result = init_base_dir()
            assert result == tmp_path


class TestResourcePath:
    def test_resolves_relative(self, tmp_path):
        init_base_dir(tmp_path)
        result = resource_path("imgxml/Windows/CloseButton")
        assert result == tmp_path.resolve() / "imgxml" / "Windows" / "CloseButton"

    def test_data_dir(self, tmp_path):
        init_base_dir(tmp_path)
        result = data_dir("Languages")
        assert result == tmp_path.resolve() / "Languages"

    def test_frozen_paths(self, tmp_path):
        """Paths work correctly in frozen (PyInstaller) mode."""
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "_MEIPASS", str(tmp_path), create=True):
            init_base_dir()
            result = resource_path("imgxml/Train/Troops")
            assert result == tmp_path / "imgxml" / "Train" / "Troops"
