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


# Scale factor for upscaling small crops before OCR.
# pytesseract works much better on larger images (recommended min ~32px height).
# CoC UI text is typically 16-18px tall, so 3x gives ~48-54px.
_OCR_SCALE = 3


# ── Core OCR Functions ───────────────────────────────────────────────────────

def _preprocess_game_text(crop: np.ndarray) -> np.ndarray:
    """Preprocess CoC game text for OCR.

    The game renders white/yellow numbers with dark outlines and drop shadows
    on colored HUD backgrounds. This pipeline:
    1. Converts to HSV and isolates bright pixels (the actual text)
    2. Scales up the small crop for better pytesseract accuracy
    3. Applies morphological close to fill gaps in characters
    4. Returns a clean binary image (white text on black)

    This replaces the simple OTSU threshold which fails on game screenshots
    because the colored background confuses automatic threshold selection.
    """
    if crop.size == 0:
        return crop

    h, w = crop.shape[:2]

    # Convert to HSV and extract Value (brightness) channel.
    # Game text (white/yellow) has high V regardless of hue.
    if crop.ndim == 3:
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        _, _, v_channel = cv2.split(hsv)
    else:
        v_channel = crop

    # Threshold on brightness: game text is bright (V > ~180) while
    # backgrounds and shadows are darker.
    # Use a fixed threshold rather than OTSU since we know text is bright.
    _, bright_mask = cv2.threshold(v_channel, 180, 255, cv2.THRESH_BINARY)

    # Scale up for better OCR accuracy
    scaled = cv2.resize(
        bright_mask,
        (w * _OCR_SCALE, h * _OCR_SCALE),
        interpolation=cv2.INTER_CUBIC,
    )

    # Morphological close to fill small gaps in characters
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(scaled, cv2.MORPH_CLOSE, kernel)

    # Re-threshold after scaling (interpolation introduces gray pixels)
    _, binary = cv2.threshold(cleaned, 127, 255, cv2.THRESH_BINARY)

    return binary


def read_text(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    lang: str = "coc-latin",
    whitelist: str = "",
    remove_space: bool = False,
    preprocess: str = "game",
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
        preprocess: Preprocessing method: "game" (default), "threshold", "adaptive",
                     "invert", "none".

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

    if preprocess == "game":
        processed = _preprocess_game_text(crop)
    else:
        processed = _preprocess_for_ocr(crop, preprocess)

    try:
        import pytesseract

        # PSM 7 = single text line; PSM 8 = single word (better for short numbers)
        psm = 8 if width < 80 else 7
        config = f"--psm {psm}"
        if whitelist:
            config += f" -c tessedit_char_whitelist={whitelist}"

        text = pytesseract.image_to_string(processed, config=config).strip()
        if remove_space:
            text = text.replace(" ", "")

        set_debug_log(f"OCR [{x},{y},{width},{height}] raw='{text}'")
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
# Coordinates from GetResources.au3: getGoldVillageSearch(48, 69+7)=48,76 etc.
def get_gold_search(image: np.ndarray) -> int:
    """Read gold amount during village search. Replaces getGoldVillageSearch()."""
    return read_number(image, 48, 76, 100, 18)


def get_elixir_search(image: np.ndarray) -> int:
    """Read elixir amount during village search. Replaces getElixirVillageSearch()."""
    return read_number(image, 48, 105, 100, 18)


def get_dark_elixir_search(image: np.ndarray) -> int:
    """Read dark elixir during village search. Replaces getDarkElixirVillageSearch()."""
    return read_number(image, 48, 133, 100, 18)


def get_trophy_search(image: np.ndarray) -> int:
    """Read trophy count during search. Replaces getTrophyVillageSearch()."""
    return read_number(image, 48, 175, 80, 18)


# Main screen resources
# Coordinates from VillageReport.au3: getResourcesMainScreen(696, 23) etc.
# Width=110 from AutoIt getOcr.au3 (getResourcesMainScreen uses 110x16)
def get_gold_main(image: np.ndarray) -> int:
    """Read gold on main screen. Replaces getResourcesMainScreen(696, 23)."""
    return read_number(image, 696, 23, 110, 16)


def get_elixir_main(image: np.ndarray) -> int:
    """Read elixir on main screen. Replaces getResourcesMainScreen(696, 74)."""
    return read_number(image, 696, 74, 110, 16)


def get_dark_elixir_main(image: np.ndarray) -> int:
    """Read dark elixir on main screen. Replaces getResourcesMainScreen(728, 123)."""
    return read_number(image, 728, 123, 110, 16)


def get_trophy_main(image: np.ndarray) -> int:
    """Read trophies on main screen. From ScreenCoordinates.au3: $aTrophies=[69, 84]."""
    return read_number(image, 69, 84, 60, 18)


def get_gem_count(image: np.ndarray, has_dark_elixir: bool = True) -> int:
    """Read gem count. From VillageReport.au3: getResourcesMainScreen(740, 171/123).

    The gem position shifts depending on whether Dark Elixir storage exists.
    """
    if has_dark_elixir:
        return read_number(image, 740, 171, 110, 16)
    return read_number(image, 740, 123, 110, 16)


# Builder count
# Coordinates from ScreenCoordinates.au3: $aBuildersDigits=[424, 21]
# Width=40 from AutoIt getOcr.au3 (getBuilders uses 40x18)
def get_builder_count(image: np.ndarray) -> tuple[int, int]:
    """Read builder count "X/Y" from main screen.

    Translated from getBuilderCount() in getBuilderCount.au3.
    AutoIt uses: getOcrAndCapture("coc-Builders", 424, 21, 40, 18, True)
    Width is 40px (not 60) — wider captures background noise causing misreads.

    Returns:
        (free_builders, total_builders) tuple.
    """
    text = read_text(
        image, 424, 21, 40, 18,
        whitelist="0123456789/",
        remove_space=True,
    )
    set_debug_log(f"Builder OCR raw: '{text}'")
    match = re.match(r"(\d+)/(\d+)", text)
    if match:
        free = int(match.group(1))
        total = int(match.group(2))
        # Sanity check: total builders is always 2-7 in CoC
        if 1 <= total <= 7 and 0 <= free <= total:
            return free, total
        set_debug_log(f"Builder count out of range: {free}/{total}, rejecting")
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
    """OCR using contour segmentation and multi-scale template matching.

    Since the original listSymbols_coc-*.xml files use a proprietary MBRBot.dll
    format, this implementation:
    1. Thresholds the image to get binary text
    2. Finds individual character contours
    3. Normalizes each character to a fixed height
    4. Matches against digit templates rendered at that same fixed height

    Works best for the white/yellow numeric text the game uses for resource
    amounts, troop counts, timers, etc.
    """
    # Ensure grayscale
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    h_img, w_img = gray.shape
    if h_img < 6 or w_img < 4:
        return ""

    # Determine if text is light-on-dark or dark-on-light
    mean_val = np.mean(gray)
    if mean_val > 127:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours (each character should be a separate contour)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return ""

    # Filter and sort contours left-to-right
    char_boxes: list[tuple[int, int, int, int]] = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < h_img * 0.25 or w < 2 or h < 3:
            continue
        char_boxes.append((x, y, w, h))

    if not char_boxes:
        return ""

    char_boxes.sort(key=lambda b: b[0])

    # Use a fixed target height for normalization
    target_h = _NORM_H
    allowed = set(whitelist) if whitelist else None
    templates = _get_normalized_templates(allowed)

    result_chars: list[str] = []

    for x, y, w, h in char_boxes:
        char_img = binary[y:y + h, x:x + w]

        # Resize to fixed height, preserving aspect ratio
        aspect = w / h
        new_w = max(2, round(target_h * aspect))
        char_resized = cv2.resize(char_img, (new_w, target_h), interpolation=cv2.INTER_AREA)

        best_char = ""
        best_score = -1.0

        for char, tmpl_list in templates.items():
            for tmpl in tmpl_list:
                th, tw = tmpl.shape
                # Pad whichever is narrower so both have the same width
                if tw == new_w:
                    t = tmpl
                    c = char_resized
                elif tw < new_w:
                    pad = new_w - tw
                    t = cv2.copyMakeBorder(tmpl, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=0)
                    c = char_resized
                else:
                    pad = tw - new_w
                    c = cv2.copyMakeBorder(char_resized, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=0)
                    t = tmpl

                # Compute similarity via normalized correlation
                t_f = t.astype(np.float32)
                c_f = c.astype(np.float32)
                norm_t = np.linalg.norm(t_f)
                norm_c = np.linalg.norm(c_f)
                if norm_t < 1e-6 or norm_c < 1e-6:
                    continue
                score = float(np.sum(t_f * c_f) / (norm_t * norm_c))

                if score > best_score:
                    best_score = score
                    best_char = char

        if best_score > 0.45 and best_char:
            result_chars.append(best_char)

    return "".join(result_chars)


# ── Digit Template Generation ────────────────────────────────────────────────

_NORM_H = 32  # Fixed height for normalized character comparison
_norm_templates: dict[str, list[np.ndarray]] | None = None


def _get_normalized_templates(
    allowed: set[str] | None = None,
) -> dict[str, list[np.ndarray]]:
    """Get digit templates normalized to _NORM_H height.

    Generates multiple variants per character using different fonts and
    thicknesses for robustness. Each template is cropped to its tight
    bounding box and resized to _NORM_H, preserving aspect ratio.

    Returns:
        Dict mapping character -> list of template images (binary, height=_NORM_H).
    """
    global _norm_templates
    if _norm_templates is not None:
        if allowed:
            return {k: v for k, v in _norm_templates.items() if k in allowed}
        return _norm_templates

    chars = "0123456789/"
    templates: dict[str, list[np.ndarray]] = {c: [] for c in chars}

    fonts = [
        cv2.FONT_HERSHEY_SIMPLEX,
        cv2.FONT_HERSHEY_DUPLEX,
        cv2.FONT_HERSHEY_COMPLEX_SMALL,
    ]

    for char in chars:
        seen_shapes: set[tuple[int, int]] = set()
        for font in fonts:
            for scale in (0.8, 1.0, 1.2):
                for thickness in (1, 2):
                    # Render character on a big canvas
                    canvas = np.zeros((60, 40), dtype=np.uint8)
                    (tw, th), _ = cv2.getTextSize(char, font, scale, thickness)
                    ox = (40 - tw) // 2
                    oy = (60 + th) // 2
                    cv2.putText(canvas, char, (ox, oy), font, scale, 255, thickness)

                    # Crop to tight bounding box
                    coords = cv2.findNonZero(canvas)
                    if coords is None:
                        continue
                    bx, by, bw, bh = cv2.boundingRect(coords)
                    cropped = canvas[by:by + bh, bx:bx + bw]

                    # Resize to normalized height, preserving aspect ratio
                    aspect = bw / bh
                    new_w = max(2, round(_NORM_H * aspect))
                    resized = cv2.resize(cropped, (new_w, _NORM_H), interpolation=cv2.INTER_AREA)
                    _, resized = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY)

                    # Skip near-duplicate shapes
                    shape_key = (new_w, int(np.count_nonzero(resized) / 10))
                    if shape_key in seen_shapes:
                        continue
                    seen_shapes.add(shape_key)

                    templates[char].append(resized)

    _norm_templates = templates
    if allowed:
        return {k: v for k, v in templates.items() if k in allowed}
    return templates
