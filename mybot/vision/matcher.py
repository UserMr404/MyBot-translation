"""Template matching engine translated from MBRBot.dll image search functions.

Replaces DllCallMyBot("SearchMultipleTilesBetweenLevels", ...),
DllCallMyBot("FindTile", ...), and related MBRBot.dll search functions
with native OpenCV (cv2.matchTemplate) calls.

Source files translated:
- Image Search/imglocAuxiliary.au3 — findMultiple(), findImage(), etc.
- Image Search/QuickMIS.au3 — QuickMIS() wrapper
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from mybot.log import set_debug_log
from mybot.vision.templates import Template, load_template_dir


@dataclass(slots=True)
class MatchResult:
    """Result of a template match.

    Replaces the pipe-delimited string results from MBRBot.dll.
    In AutoIt, results were returned as "objectname|x,y|x2,y2|..."
    strings that had to be parsed. Here we use structured data.
    """
    name: str
    x: int
    y: int
    level: int = 0
    confidence: float = 0.0


@dataclass
class SearchResult:
    """Aggregated search result with metadata.

    Replaces GetProperty() calls that retrieved metadata from the last
    DLL search: "objectpoints", "objectname", "objectlevel",
    "totalobjects", "redline", "nearpoints", "farpoints".
    """
    matches: list[MatchResult] = field(default_factory=list)
    total_objects: int = 0
    redline: str = ""
    near_points: list[tuple[int, int]] = field(default_factory=list)
    far_points: list[tuple[int, int]] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return len(self.matches) > 0

    @property
    def first(self) -> MatchResult | None:
        return self.matches[0] if self.matches else None


def find_multiple(
    screenshot: np.ndarray,
    template_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    max_results: int = 0,
    min_level: int = 0,
    max_level: int = 1000,
    confidence: float = 0.85,
) -> SearchResult:
    """Search for multiple templates in a screenshot.

    Replaces DllCallMyBot("SearchMultipleTilesBetweenLevels", ...).
    Loads all templates from the specified directory, filters by level range,
    and runs cv2.matchTemplate() against the screenshot region.

    Args:
        screenshot: BGR screenshot as numpy array.
        template_dir: Directory containing template .xml/.png files.
        search_area: (x, y, width, height) region to search. None = full image.
        max_results: Maximum matches to return (0 = unlimited).
        min_level: Minimum template level to include.
        max_level: Maximum template level to include.
        confidence: Minimum match confidence threshold (0.0 - 1.0).

    Returns:
        SearchResult with all matches found.
    """
    templates = load_template_dir(template_dir, min_level, max_level)
    if not templates:
        return SearchResult()

    # Extract search region
    if search_area:
        sx, sy, sw, sh = search_area
        h, w = screenshot.shape[:2]
        sx = max(0, sx)
        sy = max(0, sy)
        sw = min(sw, w - sx)
        sh = min(sh, h - sy)
        region = screenshot[sy:sy + sh, sx:sx + sw]
    else:
        sx, sy = 0, 0
        region = screenshot

    result = SearchResult()

    for template in templates:
        matches = _match_template(region, template, confidence)
        for mx, my, conf in matches:
            result.matches.append(MatchResult(
                name=template.name,
                x=mx + sx,
                y=my + sy,
                level=template.level,
                confidence=conf,
            ))

    # Sort by confidence descending
    result.matches.sort(key=lambda m: m.confidence, reverse=True)

    # Apply NMS to remove overlapping detections
    if result.matches:
        result.matches = _non_max_suppression(result.matches, templates, overlap_thresh=0.3)

    result.total_objects = len(result.matches)

    if max_results > 0:
        result.matches = result.matches[:max_results]

    return result


def find_image(
    screenshot: np.ndarray,
    template_path: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.85,
) -> MatchResult | None:
    """Search for a single template image.

    Replaces DllCallMyBot("FindTile", ...) and findImage() from imglocAuxiliary.au3.

    Args:
        screenshot: BGR screenshot as numpy array.
        template_path: Path to template file.
        search_area: (x, y, w, h) search region. None = full image.
        confidence: Minimum match confidence.

    Returns:
        MatchResult if found, None otherwise.
    """
    from mybot.vision.templates import get_template

    template = get_template(template_path)
    if template is None:
        return None

    if search_area:
        sx, sy, sw, sh = search_area
        h, w = screenshot.shape[:2]
        region = screenshot[max(0, sy):min(sy + sh, h), max(0, sx):min(sx + sw, w)]
    else:
        sx, sy = 0, 0
        region = screenshot

    matches = _match_template(region, template, confidence)
    if matches:
        mx, my, conf = matches[0]
        return MatchResult(
            name=template.name,
            x=mx + sx,
            y=my + sy,
            level=template.level,
            confidence=conf,
        )
    return None


def find_all_matches(
    screenshot: np.ndarray,
    template_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.85,
) -> list[MatchResult]:
    """Return all template matches in a directory.

    Replaces returnMultipleMatches() from imglocAuxiliary.au3.

    Args:
        screenshot: BGR screenshot.
        template_dir: Directory of templates.
        search_area: Optional search region.
        confidence: Minimum confidence.

    Returns:
        List of all MatchResult objects found.
    """
    result = find_multiple(screenshot, template_dir, search_area, confidence=confidence)
    return result.matches


def find_best_match(
    screenshot: np.ndarray,
    template_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.85,
) -> MatchResult | None:
    """Find the single best matching template.

    Args:
        screenshot: BGR screenshot.
        template_dir: Directory of templates.
        search_area: Optional search region.
        confidence: Minimum confidence.

    Returns:
        Best MatchResult, or None if nothing found.
    """
    result = find_multiple(screenshot, template_dir, search_area, max_results=1, confidence=confidence)
    return result.first


# ── QuickMIS Replacements ────────────────────────────────────────────────────
# QuickMIS() from QuickMIS.au3 used string codes like "BC1", "CX", "CNX" etc.
# In Python, we provide typed functions instead.

def quick_search_bool(
    screenshot: np.ndarray,
    template_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.85,
) -> tuple[bool, int, int, str]:
    """Quick search returning bool + first match coords + name.

    Replaces QuickMIS("BC1", ...) from QuickMIS.au3.
    Sets global $g_iQuickMISX, $g_iQuickMISY, $g_iQuickMISName in AutoIt.

    Returns:
        (found, x, y, name) tuple.
    """
    result = find_multiple(screenshot, template_dir, search_area, max_results=1, confidence=confidence)
    if result.first:
        m = result.first
        return True, m.x, m.y, m.name
    return False, 0, 0, ""


def quick_search_names(
    screenshot: np.ndarray,
    template_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.85,
) -> list[str]:
    """Quick search returning list of matched template names.

    Replaces QuickMIS("NX", ...) from QuickMIS.au3.
    """
    result = find_multiple(screenshot, template_dir, search_area, confidence=confidence)
    return [m.name for m in result.matches]


def quick_search_count(
    screenshot: np.ndarray,
    template_dir: Path,
    search_area: tuple[int, int, int, int] | None = None,
    confidence: float = 0.85,
) -> int:
    """Quick search returning count of matches.

    Replaces QuickMIS("QX", ...) from QuickMIS.au3.
    """
    result = find_multiple(screenshot, template_dir, search_area, confidence=confidence)
    return result.total_objects


# ── Internal helpers ─────────────────────────────────────────────────────────

def _match_template(
    region: np.ndarray,
    template: Template,
    confidence: float,
) -> list[tuple[int, int, float]]:
    """Run cv2.matchTemplate and return matches above threshold.

    Returns:
        List of (x, y, confidence) tuples.
    """
    if region.size == 0 or template.image.size == 0:
        return []

    rh, rw = region.shape[:2]
    th, tw = template.image.shape[:2]

    if th > rh or tw > rw:
        return []

    try:
        result = cv2.matchTemplate(region, template.image, cv2.TM_CCOEFF_NORMED)
    except cv2.error as e:
        set_debug_log(f"matchTemplate error for {template.name}: {e}")
        return []

    locations = np.where(result >= confidence)
    matches = []
    for py, px in zip(*locations):
        conf = float(result[py, px])
        # Return center of template match
        cx = int(px) + tw // 2
        cy = int(py) + th // 2
        matches.append((cx, cy, conf))

    # Sort by confidence descending
    matches.sort(key=lambda m: m[2], reverse=True)
    return matches


def _non_max_suppression(
    matches: list[MatchResult],
    templates: list[Template],
    overlap_thresh: float = 0.3,
) -> list[MatchResult]:
    """Remove overlapping detections using Non-Maximum Suppression.

    When multiple templates match overlapping regions, keep only the
    highest confidence match. Uses a simple distance-based approach
    since template sizes are similar.
    """
    if len(matches) <= 1:
        return matches

    # Build a lookup for template sizes
    template_sizes: dict[str, tuple[int, int]] = {}
    for t in templates:
        h, w = t.image.shape[:2]
        template_sizes[t.name] = (w, h)

    # Default size for unknown templates
    default_size = (30, 30)

    kept: list[MatchResult] = []
    suppressed: set[int] = set()

    for i, m in enumerate(matches):
        if i in suppressed:
            continue
        kept.append(m)
        w1, h1 = template_sizes.get(m.name, default_size)

        for j in range(i + 1, len(matches)):
            if j in suppressed:
                continue
            other = matches[j]
            w2, h2 = template_sizes.get(other.name, default_size)

            # Check overlap using center distance
            avg_w = (w1 + w2) / 2
            avg_h = (h1 + h2) / 2
            dx = abs(m.x - other.x)
            dy = abs(m.y - other.y)

            if dx < avg_w * overlap_thresh and dy < avg_h * overlap_thresh:
                suppressed.add(j)

    return kept
