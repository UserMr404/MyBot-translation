"""Tests for configuration system."""

from pathlib import Path

from mybot.config.profiles import (
    create_profile,
    delete_profile,
    get_default_profile,
    list_profiles,
    set_default_profile,
)
from mybot.config.reader import read_config
from mybot.config.writer import save_config
from mybot.state import BotState


def test_config_round_trip(tmp_path: Path):
    """Write config, read it back, verify values match."""
    config_path = tmp_path / "test_profile" / "config.ini"

    # Write
    state = BotState()
    state.android.emulator = "MEmu"
    state.android.instance = "MEmu_1"
    state.debug.set_log = True
    state.debug.ocr = True
    save_config(config_path, state)

    # Read back
    state2 = BotState()
    read_config(config_path, state2)

    assert state2.android.emulator == "MEmu"
    assert state2.android.instance == "MEmu_1"
    assert state2.debug.set_log is True
    assert state2.debug.ocr is True
    assert state2.debug.click is False  # default


def test_profile_management(tmp_path: Path):
    """Test profile creation, listing, deletion."""
    profiles_dir = tmp_path / "Profiles"

    # Create profiles
    create_profile(profiles_dir, "Village1")
    create_profile(profiles_dir, "Village2")

    # Save a config to make them listable
    save_config(profiles_dir / "Village1" / "config.ini", BotState())
    save_config(profiles_dir / "Village2" / "config.ini", BotState())

    # List
    profiles = list_profiles(profiles_dir)
    assert "Village1" in profiles
    assert "Village2" in profiles

    # Default profile
    set_default_profile(profiles_dir, "Village1")
    assert get_default_profile(profiles_dir) == "Village1"

    # Delete
    assert delete_profile(profiles_dir, "Village2") is True
    profiles = list_profiles(profiles_dir)
    assert "Village2" not in profiles
    assert "Village1" in profiles
