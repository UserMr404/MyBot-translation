"""Translation / i18n system translated from Multilanguage.au3.

Reads existing Languages/*.ini files from the MyBot directory.
Supports 16 languages with fallback to English.

Usage:
    from mybot.i18n import t
    text = t("MBR GUI Design", "Start", "Start Bot")
"""

from __future__ import annotations

import configparser
import locale
from pathlib import Path

# Translation cache: "Section§Key" -> translated text
_cache: dict[str, str] = {}
_language: str = "English"
_languages_dir: Path = Path()
_initialized: bool = False

# Windows LCID hex -> language name (subset from DetectLanguage in Multilanguage.au3)
_LCID_MAP: dict[str, str] = {
    "0409": "English", "0809": "English", "0c09": "English",
    "0407": "German", "0807": "German", "0c07": "German",
    "040c": "French", "080c": "French", "0c0c": "French",
    "0410": "Italian",
    "0c0a": "Spanish", "040a": "Spanish",
    "0416": "Portuguese", "0816": "Portuguese",
    "0419": "Russian",
    "041f": "Turkish",
    "042a": "Vietnamese",
    "0421": "Bahasa",
    "0804": "Chinese_Simplified", "1004": "Chinese_Simplified",
    "0404": "Chinese_Traditional", "0c04": "Chinese_Traditional",
    "0412": "Korean",
    "0429": "Persian",
    "0401": "Arabic", "0801": "Arabic",
    "042c": "Azerbaijani",
}


def init(languages_dir: Path, language: str | None = None) -> None:
    """Initialize the translation system.

    Args:
        languages_dir: Path to the Languages/ directory containing .ini files.
        language: Language name (e.g., "English", "German"). None for auto-detect.
    """
    global _language, _languages_dir, _initialized, _cache

    _languages_dir = languages_dir
    _cache.clear()

    if language:
        _language = language
    else:
        _language = _detect_language()

    # Pre-load all translations into cache
    _load_language(_language)
    _initialized = True


def _detect_language() -> str:
    """Auto-detect language from system locale."""
    try:
        loc = locale.getdefaultlocale()[0] or "en_US"
        # Try mapping Windows LCID
        for lcid, lang in _LCID_MAP.items():
            if lcid in loc.lower().replace("-", "").replace("_", ""):
                lang_file = _languages_dir / f"{lang}.ini"
                if lang_file.exists():
                    return lang
    except Exception:
        pass
    return "English"


def _load_language(language: str) -> None:
    """Load all translations from a language .ini file into cache."""
    lang_file = _languages_dir / f"{language}.ini"
    if not lang_file.exists():
        return

    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str  # type: ignore[assignment]

    try:
        config.read(str(lang_file), encoding="utf-8-sig")
    except configparser.Error:
        return

    for section in config.sections():
        for key, value in config.items(section):
            cache_key = f"{section}§{key}"
            _cache[cache_key] = value


def t(section: str, key: str, default: str = "", *args: str) -> str:
    """Get translated text (replaces GetTranslatedFileIni).

    Args:
        section: INI section name.
        key: INI key name.
        default: Fallback text if translation not found.
        *args: Format arguments to replace %s placeholders.

    Returns:
        Translated and formatted text.
    """
    if not _initialized:
        text = default
    else:
        cache_key = f"{section}§{key}"
        text = _cache.get(cache_key, "")

        if not text and _language != "English":
            # Fallback to English
            en_file = _languages_dir / "English.ini"
            if en_file.exists():
                en_config = configparser.ConfigParser(interpolation=None)
                en_config.optionxform = str  # type: ignore[assignment]
                try:
                    en_config.read(str(en_file), encoding="utf-8-sig")
                    text = en_config.get(section, key, fallback="")
                except configparser.Error:
                    pass

        if not text:
            text = default

    return _parse_text(text, *args)


def _parse_text(text: str, *args: str) -> str:
    """Apply variable substitution and line break handling.

    Replaces GetTranslatedParsedText from Multilanguage.au3.
    """
    # Replace literal \r\n with actual line breaks
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n")

    # Replace %s placeholders with args
    if args:
        try:
            text = text % args
        except (TypeError, ValueError):
            # Fallback: replace %s one by one
            for arg in args:
                text = text.replace("%s", str(arg), 1)

    return text


def get_language() -> str:
    """Return the current language name."""
    return _language


def get_available_languages(languages_dir: Path | None = None) -> list[str]:
    """List all available language names from .ini files."""
    lang_dir = languages_dir or _languages_dir
    if not lang_dir.exists():
        return []
    return sorted(
        f.stem for f in lang_dir.glob("*.ini")
        if f.stem != "template"
    )
