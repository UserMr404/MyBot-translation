"""Template loading system translated from MBRBot.dll template handling.

Loads image templates from the imgxml/ directory. Templates are base64-encoded
images in .xml files with naming convention: ElementName_Level_Rotation.xml

The original MBRBot.dll uses a proprietary encrypted format for templates.
This module supports:
1. Proprietary format via MBRBot.dll (.NET DLL) for backward compatibility
2. Standard PNG/BMP templates for new additions
3. Pre-converted template cache (PNG files) for pure-Python operation

To migrate from proprietary to PNG, run the conversion tool (see convert_templates()).
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from mybot.log import set_debug_log, set_log


@dataclass(frozen=True, slots=True)
class Template:
    """A loaded image template for matching.

    Attributes:
        name: Element name from filename (e.g., "TownHall", "Barb").
        level: Level/scale value from filename (e.g., 10, 100).
        rotation: Rotation value from filename (e.g., 92).
        image: Decoded BGR image as numpy array.
        path: Original file path.
    """
    name: str
    level: int
    rotation: int
    image: np.ndarray
    path: Path

    def __hash__(self) -> int:
        return hash(self.path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Template):
            return NotImplemented
        return self.path == other.path


# Regex for template filename parsing: Name_Level_Rotation.xml
_TEMPLATE_NAME_RE = re.compile(r"^(.+?)_(\d+)_(\d+)$")


def parse_template_name(stem: str) -> tuple[str, int, int]:
    """Parse template filename stem into (name, level, rotation).

    Examples:
        >>> parse_template_name("TownHall_10_92")
        ('TownHall', 10, 92)
        >>> parse_template_name("Barb_100_91")
        ('Barb', 100, 91)
        >>> parse_template_name("unknown")
        ('unknown', 0, 0)
    """
    match = _TEMPLATE_NAME_RE.match(stem)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))
    return stem, 0, 0


def load_template_image(path: Path) -> np.ndarray | None:
    """Load a template image from file.

    Supports:
    - Standard image files (.png, .bmp, .jpg)
    - Base64-encoded image files (.xml with valid base64 image data)
    - Pre-converted PNG cache alongside .xml files

    The proprietary MBRBot.dll encrypted format is NOT supported directly.
    Use convert_templates() to convert those to PNG first.

    Args:
        path: Path to the template file.

    Returns:
        BGR numpy array, or None if loading fails.
    """
    if not path.exists():
        return None

    # Check for pre-converted PNG cache
    if path.suffix.lower() == ".xml":
        png_cache = path.with_suffix(".png")
        if png_cache.exists():
            img = cv2.imread(str(png_cache), cv2.IMREAD_COLOR)
            if img is not None:
                return img

    # Try direct image load (PNG, BMP, JPG)
    if path.suffix.lower() in (".png", ".bmp", ".jpg", ".jpeg"):
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is not None:
            return img

    # Try base64-encoded image data (.xml files)
    if path.suffix.lower() == ".xml":
        return _load_base64_template(path)

    return None


def _load_base64_template(path: Path) -> np.ndarray | None:
    """Attempt to load a base64-encoded image from an XML-like file.

    The imgxml templates use raw base64 encoding (no XML structure).
    The content may be a standard image (PNG/BMP/JPEG) encoded in base64,
    or it may be the proprietary MBRBot.dll encrypted format.

    Returns:
        BGR numpy array if successfully decoded, None otherwise.
    """
    try:
        raw = path.read_bytes()
        # Strip UTF-8 BOM
        if raw[:3] == b"\xef\xbb\xbf":
            raw = raw[3:]

        decoded = base64.b64decode(raw)

        # Check for known image magic bytes
        if decoded[:4] == b"\x89PNG" or decoded[:2] == b"\xff\xd8" or decoded[:2] == b"BM":
            img_array = np.frombuffer(decoded, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is not None:
                return img

        # Proprietary MBRBot.dll format — cannot decode without DLL
        set_debug_log(f"Template uses proprietary format (needs conversion): {path.name}")
        return None

    except (ValueError, base64.binascii.Error) as e:  # type: ignore[attr-defined]
        set_debug_log(f"Failed to decode template {path.name}: {e}")
        return None


# Template directory cache: maps dir path -> list of templates
_dir_cache: dict[Path, list[Template]] = {}


def load_template_dir(
    dir_path: Path,
    min_level: int = 0,
    max_level: int = 1000,
    use_cache: bool = True,
) -> list[Template]:
    """Load all templates from a directory.

    Translates the template loading logic from MBRBot.dll's
    SearchMultipleTilesBetweenLevels which scans a directory of templates
    filtered by level range.

    Args:
        dir_path: Directory containing template files.
        min_level: Minimum level to include.
        max_level: Maximum level to include.
        use_cache: Use cached templates if available.

    Returns:
        List of loaded Template objects, filtered by level range.
    """
    if not dir_path.is_dir():
        set_debug_log(f"Template directory not found: {dir_path}")
        return []

    # Load full directory into cache
    if use_cache and dir_path in _dir_cache:
        all_templates = _dir_cache[dir_path]
    else:
        all_templates = []
        for file_path in sorted(dir_path.iterdir()):
            if file_path.suffix.lower() not in (".xml", ".png", ".bmp", ".jpg", ".jpeg"):
                continue
            # Skip PNG cache files that have a corresponding XML
            if file_path.suffix.lower() == ".png" and file_path.with_suffix(".xml").exists():
                continue

            name, level, rotation = parse_template_name(file_path.stem)
            image = load_template_image(file_path)
            if image is not None:
                all_templates.append(Template(
                    name=name,
                    level=level,
                    rotation=rotation,
                    image=image,
                    path=file_path,
                ))

        if use_cache:
            _dir_cache[dir_path] = all_templates

    # Filter by level range
    if min_level > 0 or max_level < 1000:
        return [t for t in all_templates if min_level <= t.level <= max_level]
    return list(all_templates)


def clear_cache() -> None:
    """Clear the template directory cache."""
    _dir_cache.clear()


@lru_cache(maxsize=256)
def get_template(path: Path) -> Template | None:
    """Load a single template file with LRU caching.

    Args:
        path: Path to the template file.

    Returns:
        Template object, or None if loading fails.
    """
    name, level, rotation = parse_template_name(path.stem)
    image = load_template_image(path)
    if image is None:
        return None
    return Template(name=name, level=level, rotation=rotation, image=image, path=path)


def convert_templates(
    src_dir: Path,
    dll_path: Path | None = None,
    recursive: bool = True,
) -> int:
    """Convert proprietary MBRBot.dll templates to PNG format.

    This is a one-time migration tool. For each .xml template, it creates
    a corresponding .png file that can be loaded without the DLL.

    Requires either:
    - MBRBot.dll accessible via pythonnet (clr) for decryption
    - Or manual conversion using a Windows machine with the DLL

    Args:
        src_dir: Root directory to scan for .xml templates.
        dll_path: Path to MBRBot.dll (optional, for automated conversion).
        recursive: Scan subdirectories.

    Returns:
        Number of templates converted.
    """
    count = 0
    pattern = "**/*.xml" if recursive else "*.xml"

    for xml_path in src_dir.glob(pattern):
        png_path = xml_path.with_suffix(".png")
        if png_path.exists():
            continue  # Already converted

        # Try loading as standard base64 image
        img = _load_base64_template(xml_path)
        if img is not None:
            cv2.imwrite(str(png_path), img)
            count += 1
            continue

        # Proprietary format needs DLL — log for manual conversion
        set_debug_log(f"Needs DLL conversion: {xml_path}")

    if count > 0:
        set_log(f"Converted {count} templates to PNG")
    return count
