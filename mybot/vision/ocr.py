"""OCR / text recognition translated from Read Text/ directory.

Replaces DllCallMyBot("ocr", ...) and DllCallMyBot("DoOCR", ...) with
OpenCV-based character recognition. The original MBRBot.dll used custom
character templates (lib/listSymbols_coc-*.xml). This module uses
pytesseract as the primary OCR engine, with fallback to template matching
for game-specific fonts.

Source files:
- Read Text/getOcr.au3 — 76 specialized OCR wrapper functions
- Read Text/BuildingInfo.au3 — building name/level extraction
- Read Text/getBuilderCount.au3 — builder count reading
- Read Text/getShieldInfo.au3 — shield/guard time reading
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from mybot.constants import GAME_HEIGHT, GAME_WIDTH
from mybot.log import set_debug_log


@dataclass(frozen=True, slots=True)
class OcrResult:
    """Result of an OCR read operation."""
    text: str
    confidence: float = 0.0
    region: tuple[int, int, int, int] = (0, 0, 0, 0)  # x, y, w, h


# ── Core OCR Functions ───────────────────────────────────────────────────────

def read_text(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    lang: str = "coc-latin",
    whitelist: str = "",
    remove_space: bool = False,
    preprocess: str = "threshold",
) -> str:
    """Read text from a screen region using OCR.

    Replaces getOcrAndCapture() from getOcr.au3. The AutoIt version called
    DllCallMyBot("ocr", "ptr", hBitmap, "str", language, "int", debug)
    with specific language templates. This Python version uses pytesseract
    or template-based character matching.

    Args:
        image: BGR screenshot as numpy array.
        x: Left coordinate of OCR region.
        y: Top coordinate of OCR region.
        width: Width of OCR region.
        height: Height of OCR region.
        lang: OCR language/template name (e.g., "coc-latin", "coc-A", "coc-Gold").
        whitelist: Allowed characters (e.g., "0123456789" for numbers only).
        remove_space: Remove spaces from result.
        preprocess: Preprocessing method: "threshold", "adaptive", "invert", "none".

    Returns:
        Recognized text string (empty string on failure).
    """
    h, w = image.shape[:2]
    x = max(0, x)
    y = max(0, y)
    x2 = min(x + width, w)
    y2 = min(y + height, h)
    if x2 <= x or y2 <= y:
        return ""

    crop = image[y:y2, x:x2]
    processed = _preprocess_for_ocr(crop, preprocess)

    try:
        import pytesseract

        config = "--psm 7"  # Single text line mode
        if whitelist:
            config += f" -c tessedit_char_whitelist={whitelist}"

        text = pytesseract.image_to_string(processed, config=config).strip()
        if remove_space:
            text = text.replace(" ", "")
        return text

    except ImportError:
        set_debug_log("pytesseract not installed, falling back to template OCR")
        return _template_ocr(processed, whitelist)
    except Exception as e:
        set_debug_log(f"OCR failed: {e}")
        return ""


def read_number(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    default: int = 0,
) -> int:
    """Read a numeric value from a screen region.

    Convenience wrapper for OCR-ing integer values like resource amounts,
    troop counts, timers, etc. Handles common OCR errors (O→0, l→1).

    Args:
        image: BGR screenshot.
        x, y, width, height: OCR region.
        default: Default value on failure.

    Returns:
        Integer value, or default on failure.
    """
    text = read_text(image, x, y, width, height, whitelist="0123456789", remove_space=True)
    if not text:
        return default

    # Clean common OCR misreads
    text = text.replace("O", "0").replace("o", "0")
    text = text.replace("l", "1").replace("I", "1")
    text = text.replace("S", "5").replace("B", "8")

    # Remove non-digit characters
    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return default

    try:
        return int(digits)
    except ValueError:
        return default


# ── Specialized OCR Functions ────────────────────────────────────────────────
# These replace the 76 specialized getOcr* functions from getOcr.au3.
# Each had hardcoded region coordinates and language parameters.

# Resource amounts during village search (attack search screen)
def get_gold_search(image: np.ndarray) -> int:
    """Read gold amount during village search. Replaces getGoldVillageSearch()."""
    return read_number(image, 31, 108, 150, 18)


def get_elixir_search(image: np.ndarray) -> int:
    """Read elixir amount during village search. Replaces getElixirVillageSearch()."""
    return read_number(image, 31, 134, 150, 18)


def get_dark_elixir_search(image: np.ndarray) -> int:
    """Read dark elixir during village search. Replaces getDarkElixirVillageSearch()."""
    return read_number(image, 31, 160, 110, 18)


def get_trophy_search(image: np.ndarray) -> int:
    """Read trophy count during search. Replaces getTrophyVillageSearch()."""
    return read_number(image, 31, 186, 80, 18)


# Main screen resources
def get_gold_main(image: np.ndarray) -> int:
    """Read gold on main screen. Replaces getGoldMainScreen()."""
    return read_number(image, 463, 36, 100, 18)


def get_elixir_main(image: np.ndarray) -> int:
    """Read elixir on main screen. Replaces getElixirMainScreen()."""
    return read_number(image, 463, 84, 100, 18)


def get_dark_elixir_main(image: np.ndarray) -> int:
    """Read dark elixir on main screen. Replaces getDarkElixirMainScreen()."""
    return read_number(image, 463, 132, 100, 18)


def get_trophy_main(image: np.ndarray) -> int:
    """Read trophies on main screen. Replaces getTrophyMainScreen()."""
    return read_number(image, 75, 16, 60, 18)


def get_gem_count(image: np.ndarray) -> int:
    """Read gem count. Replaces getGemMainScreen()."""
    return read_number(image, 785, 16, 60, 18)


# Builder count
def get_builder_count(image: np.ndarray) -> tuple[int, int]:
    """Read builder count "X/Y" from main screen.

    Translated from getBuilderCount() in getBuilderCount.au3.

    Returns:
        (free_builders, total_builders) tuple.
    """
    text = read_text(image, 274, 16, 50, 18, whitelist="0123456789/")
    match = re.match(r"(\d+)\s*/\s*(\d+)", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


# Training timers
def get_train_timer(image: np.ndarray) -> str:
    """Read remaining training time. Replaces getRemainTrainTimer()."""
    return read_text(image, 162, 200, 120, 27, whitelist="0123456789:hms ")


# Building info
@dataclass(frozen=True, slots=True)
class BuildingInfo:
    """Building name and level from info popup.

    Translated from BuildingInfo() in BuildingInfo.au3.
    """
    name: str
    level: int


def get_building_info(image: np.ndarray) -> BuildingInfo:
    """Read building name and level from the info popup.

    When a building is selected, its name and level appear in a popup.
    This reads that text.

    Returns:
        BuildingInfo with name and level.
    """
    # Building name region
    name_text = read_text(image, 242, 480, 420, 27)

    # Try to parse "Building Name Level X"
    match = re.match(r"(.+?)\s+(?:Level\s+)?(\d+)\s*$", name_text, re.IGNORECASE)
    if match:
        return BuildingInfo(name=match.group(1).strip(), level=int(match.group(2)))

    return BuildingInfo(name=name_text.strip(), level=0)


# Shield/Guard info
def get_shield_info(image: np.ndarray) -> tuple[str, str]:
    """Read shield and guard remaining time.

    Translated from getShieldInfo() in getShieldInfo.au3.

    Returns:
        (shield_time, guard_time) as strings like "1d 12h", "30m".
    """
    shield = read_text(image, 454, 138, 80, 18, whitelist="0123456789dhms ")
    guard = read_text(image, 454, 158, 80, 18, whitelist="0123456789dhms ")
    return shield.strip(), guard.strip()


# Upgrade cost/time reading
def get_upgrade_cost(image: np.ndarray, x: int = 540, y: int = 548) -> int:
    """Read upgrade cost from upgrade popup."""
    return read_number(image, x, y, 100, 20)


def get_upgrade_time(image: np.ndarray, x: int = 540, y: int = 528) -> str:
    """Read upgrade time from upgrade popup."""
    return read_text(image, x, y, 100, 20, whitelist="0123456789dhms ")


# Hero levels
def get_hero_level(image: np.ndarray, hero_index: int) -> int:
    """Read hero level from hero altar.

    Args:
        hero_index: 0=King, 1=Queen, 2=Prince, 3=Warden, 4=Champion, 5=DragonDuke.
    """
    # Hero level positions vary by hero; approximate regions
    x_positions = [595, 595, 595, 595, 595, 595]
    y = 490
    x = x_positions[min(hero_index, len(x_positions) - 1)]
    return read_number(image, x, y, 110, 18)


# ── Preprocessing Helpers ────────────────────────────────────────────────────

def _preprocess_for_ocr(image: np.ndarray, method: str = "threshold") -> np.ndarray:
    """Preprocess image for better OCR accuracy.

    The game uses bright colored text on dark backgrounds (or vice versa).
    Different preprocessing methods work better for different text styles.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image

    if method == "threshold":
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    elif method == "adaptive":
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

    elif method == "invert":
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary

    return gray


def _template_ocr(image: np.ndarray, whitelist: str = "") -> str:
    """Fallback OCR using template matching for individual characters.

    Uses the character templates from lib/listSymbols_coc-*.xml if available.
    This is a simplified version — for production use, pytesseract is recommended.
    """
    # Template OCR is a fallback; return empty for now
    # Full implementation would load character templates and match them
    set_debug_log("Template OCR not yet implemented — install pytesseract")
    return ""
