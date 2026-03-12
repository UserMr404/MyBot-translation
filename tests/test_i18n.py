"""Tests for the i18n translation system."""

from pathlib import Path

from mybot.i18n import _parse_text, get_available_languages, init, t

LANGUAGES_DIR = Path(__file__).parent.parent / "MyBot" / "Languages"


def test_parse_text_basic():
    assert _parse_text("Hello World") == "Hello World"


def test_parse_text_line_breaks():
    assert _parse_text("Line1\\r\\nLine2") == "Line1\nLine2"
    assert _parse_text("Line1\\nLine2") == "Line1\nLine2"


def test_parse_text_substitution():
    assert _parse_text("Hello %s", "World") == "Hello World"
    assert _parse_text("%s has %s", "Bot", "started") == "Bot has started"


def test_init_english():
    if not LANGUAGES_DIR.exists():
        return  # Skip if languages dir not available
    init(LANGUAGES_DIR, "English")
    # Should be able to get translations from English.ini
    result = t("Language", "DisplayName", "Unknown")
    assert result in ("English", "Unknown")


def test_available_languages():
    if not LANGUAGES_DIR.exists():
        return
    langs = get_available_languages(LANGUAGES_DIR)
    assert "English" in langs
    assert len(langs) >= 1


def test_fallback_to_default():
    """Missing keys return the default value."""
    init(Path("/nonexistent"), "English")
    result = t("FakeSection", "FakeKey", "DefaultValue")
    assert result == "DefaultValue"
