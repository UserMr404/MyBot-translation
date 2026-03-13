"""Path resolution utilities for PyInstaller compatibility.

When running as a PyInstaller-frozen executable, data files are extracted
to a temporary directory accessible via sys._MEIPASS. This module provides
a single function to resolve resource paths correctly in both development
and frozen (compiled .exe) modes.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Base directory for resolving data file paths.
# Set once at startup via init_base_dir().
_base_dir: Path | None = None


def init_base_dir(base: Path | None = None) -> Path:
    """Initialize the base directory for resource resolution.

    Call this once during application startup. It determines the correct
    base path depending on whether the app is frozen (PyInstaller) or
    running from source.

    Args:
        base: Explicit base directory override. If None, auto-detects:
              - Frozen: sys._MEIPASS (PyInstaller extraction dir)
              - Source: repository root (parent of mybot/ package)

    Returns:
        The resolved base directory.
    """
    global _base_dir

    if base is not None:
        _base_dir = base.resolve()
    elif getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as PyInstaller bundle
        _base_dir = Path(sys._MEIPASS)
    else:
        # Running from source — base is the repo root (contains MyBot/, mybot/)
        _base_dir = Path(__file__).resolve().parent.parent.parent

    return _base_dir


def get_base_dir() -> Path:
    """Get the base directory, initializing with defaults if needed."""
    if _base_dir is None:
        return init_base_dir()
    return _base_dir


def resource_path(relative: str | Path) -> Path:
    """Resolve a relative path to an absolute resource path.

    Works in both development mode and PyInstaller frozen mode.

    Args:
        relative: Path relative to the base directory
                  (e.g., "imgxml/Windows/CloseButton", "Languages/English.ini").

    Returns:
        Absolute path to the resource.
    """
    return get_base_dir() / relative


def data_dir(name: str) -> Path:
    """Get path to a top-level data directory.

    Convenience wrapper for common directories:
    - imgxml/   — image templates
    - Languages/ — translation INI files
    - CSV/      — attack scripts
    - images/   — UI graphics
    - lib/      — external libraries/DLLs

    Args:
        name: Directory name (e.g., "imgxml", "Languages").

    Returns:
        Absolute path to the directory.
    """
    return resource_path(name)
