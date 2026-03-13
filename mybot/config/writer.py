"""Configuration writer translated from saveConfig.au3.

Saves BotState settings back to profile-specific INI files.
"""

from __future__ import annotations

import configparser
from pathlib import Path

from mybot.state import BotState


def save_config(config_path: Path, state: BotState) -> None:
    """Save all settings from BotState to a profile config.ini.

    Args:
        config_path: Path to the profile's config.ini file.
        state: BotState instance to save from.
    """
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str  # type: ignore[assignment]

    # Read existing config to preserve sections we don't manage yet
    if config_path.exists():
        config.read(str(config_path), encoding="utf-8-sig")

    # ── General ──────────────────────────────────────────────────────────
    if not config.has_section("android"):
        config.add_section("android")
    config.set("android", "emulator", state.android.emulator)
    config.set("android", "instance", state.android.instance)

    # ── Debug ────────────────────────────────────────────────────────────
    if not config.has_section("debug"):
        config.add_section("debug")
    config.set("debug", "debugsetlog", str(state.debug.set_log))
    config.set("debug", "debugandroid", str(state.debug.android))
    config.set("debug", "debugclick", str(state.debug.click))
    config.set("debug", "debugocr", str(state.debug.ocr))
    config.set("debug", "debugimagesave", str(state.debug.image_save))
    config.set("debug", "debugredarea", str(state.debug.red_area))
    config.set("debug", "debugattackcsv", str(state.debug.attack_csv))

    # ── Attack ─────────────────────────────────────────────────────────
    if not config.has_section("attack"):
        config.add_section("attack")
    config.set("attack", "ContinuousAttack", str(state.continuous_attack))
    config.set("attack", "ContinuousDelayMin", str(state.continuous_delay_min))
    config.set("attack", "ContinuousDelayMax", str(state.continuous_delay_max))

    # Write
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)
