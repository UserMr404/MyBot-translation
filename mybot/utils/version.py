"""Version checking translated from CheckVersion.au3."""

from __future__ import annotations

from mybot import __version__


def get_version() -> str:
    """Return the bot version string."""
    return __version__


def is_beta_version() -> bool:
    """Check if this is a beta/dev version (contains 'b' or 'dev')."""
    v = __version__.lower()
    return "b" in v or "dev" in v or "alpha" in v or "rc" in v
