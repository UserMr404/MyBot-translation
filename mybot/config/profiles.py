"""Profile management translated from profileFunctions.au3.

Handles creation, deletion, switching, and path resolution for bot profiles.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def get_profiles_dir(custom_path: Path | None = None) -> Path:
    """Get the profiles root directory.

    Default: %USERPROFILE%/MyBot/Profiles/
    Overridable via CLI: /profiles=C:\\CustomPath\\
    """
    if custom_path and custom_path.is_dir():
        return custom_path
    return Path.home() / "MyBot" / "Profiles"


def get_profile_path(profiles_dir: Path, profile_name: str) -> Path:
    """Get path for a specific profile."""
    return profiles_dir / profile_name


def get_config_path(profiles_dir: Path, profile_name: str) -> Path:
    """Get the config.ini path for a specific profile."""
    return profiles_dir / profile_name / "config.ini"


def list_profiles(profiles_dir: Path) -> list[str]:
    """List all available profile names."""
    if not profiles_dir.exists():
        return []
    return sorted(
        d.name for d in profiles_dir.iterdir()
        if d.is_dir() and (d / "config.ini").exists()
    )


def create_profile(profiles_dir: Path, profile_name: str) -> Path:
    """Create a new profile directory with default config.

    Returns the profile directory path.
    """
    profile_dir = profiles_dir / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)

    config_file = profile_dir / "config.ini"
    if not config_file.exists():
        config_file.touch()

    # Create subdirectories
    (profile_dir / "logs").mkdir(exist_ok=True)
    (profile_dir / "temp").mkdir(exist_ok=True)

    return profile_dir


def delete_profile(profiles_dir: Path, profile_name: str) -> bool:
    """Delete a profile directory. Returns True if deleted."""
    profile_dir = profiles_dir / profile_name
    if profile_dir.exists() and profile_dir.is_dir():
        shutil.rmtree(profile_dir)
        return True
    return False


def get_default_profile(profiles_dir: Path) -> str:
    """Read the default profile name from profile.ini."""
    profile_ini = profiles_dir / "profile.ini"
    if profile_ini.exists():
        for line in profile_ini.read_text(encoding="utf-8-sig").splitlines():
            if line.strip().lower().startswith("defaultprofile="):
                return line.split("=", 1)[1].strip()
    return "MyVillage"


def set_default_profile(profiles_dir: Path, profile_name: str) -> None:
    """Save the default profile name to profile.ini."""
    profile_ini = profiles_dir / "profile.ini"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    profile_ini.write_text(
        f"[general]\ndefaultprofile={profile_name}\n",
        encoding="utf-8",
    )
