"""Configuration reader translated from readConfig.au3.

Reads settings from profile-specific INI files into BotState.
Uses configparser for INI file access (backward-compatible with AutoIt IniRead).
"""

from __future__ import annotations

import configparser
from pathlib import Path
from typing import Any

from mybot.state import BotState


def _read_ini(config: configparser.ConfigParser, section: str, key: str, default: Any) -> str:
    """Read a single INI value with fallback default (mirrors AutoIt IniRead)."""
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return str(default)


def _read_bool(config: configparser.ConfigParser, section: str, key: str, default: bool = False) -> bool:
    """Read a boolean value from INI (AutoIt stores as "True"/"False" or "1"/"0")."""
    val = _read_ini(config, section, key, str(default))
    return val.lower() in ("true", "1", "yes")


def _read_int(config: configparser.ConfigParser, section: str, key: str, default: int = 0) -> int:
    """Read an integer value from INI."""
    try:
        return int(_read_ini(config, section, key, str(default)))
    except ValueError:
        return default


def read_config(config_path: Path, state: BotState) -> None:
    """Read all settings from a profile config.ini into BotState.

    Args:
        config_path: Path to the profile's config.ini file.
        state: BotState instance to populate.
    """
    config = configparser.ConfigParser(interpolation=None)
    # Preserve key case (AutoIt INI keys are case-insensitive but we preserve them)
    config.optionxform = str  # type: ignore[assignment]

    if config_path.exists():
        config.read(str(config_path), encoding="utf-8-sig")

    # ── General ──────────────────────────────────────────────────────────
    state.android.emulator = _read_ini(config, "android", "emulator", "BlueStacks5")
    state.android.instance = _read_ini(config, "android", "instance", "")

    # ── Debug ────────────────────────────────────────────────────────────
    state.debug.set_log = _read_bool(config, "debug", "debugsetlog")
    state.debug.android = _read_bool(config, "debug", "debugandroid")
    state.debug.click = _read_bool(config, "debug", "debugclick")
    state.debug.ocr = _read_bool(config, "debug", "debugocr")
    state.debug.image_save = _read_bool(config, "debug", "debugimagesave")
    state.debug.red_area = _read_bool(config, "debug", "debugredarea")
    state.debug.attack_csv = _read_bool(config, "debug", "debugattackcsv")

    # ── Village / Collection ─────────────────────────────────────────────
    # These will be expanded as more config sections are translated in Phase 4

    # ── Army / Training ──────────────────────────────────────────────────
    # Expanded in Phase 5

    # ── Attack / Search ──────────────────────────────────────────────────
    # Expanded in Phase 4-5
