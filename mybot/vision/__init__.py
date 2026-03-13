"""Vision module — image recognition, template matching, OCR, and pixel operations.

This module replaces the proprietary MBRBot.dll with native Python/OpenCV
implementations. It provides:

- Template matching (replaces SearchMultipleTilesBetweenLevels, FindTile)
- Pixel operations (color checking, pixel search, diamond boundary)
- OCR / text recognition (replaces DllCallMyBot("ocr", ...))
- Red deployment zone detection (replaces getRedArea/SearchRedLines)
- Game element detection (Town Hall, dead base, walls, windows)
- Geometry utilities (coordinate transforms, deployment points)

Phase 3 of the AutoIt → Python translation.
"""

from mybot.vision.dead_base import check_dead_base, check_dead_eagle
from mybot.vision.geometry import (
    get_deployable_points,
    offset_polyline,
    partition_points_by_side,
    pixel_distance,
    screen_to_village,
    sort_by_distance,
    village_to_screen,
)
from mybot.vision.matcher import (
    MatchResult,
    SearchResult,
    find_all_matches,
    find_best_match,
    find_image,
    find_multiple,
    quick_search_bool,
    quick_search_count,
    quick_search_names,
)
from mybot.vision.ocr import (
    BuildingInfo,
    get_builder_count,
    get_building_info,
    read_number,
    read_text,
)
from mybot.vision.pixel import (
    check_pixel,
    color_check,
    get_pixel_color,
    is_inside_diamond,
    multi_pixel_search,
    parse_pixel_list,
    pixel_search,
)
from mybot.vision.red_area import RedArea, detect_red_area, detect_red_lines
from mybot.vision.templates import (
    Template,
    clear_cache,
    load_template_dir,
    load_template_image,
    parse_template_name,
)
from mybot.vision.townhall import TownHallResult, find_town_hall
from mybot.vision.walls import WallSearchResult, find_wall
from mybot.vision.window_detect import find_close_button, is_window_open

__all__ = [
    # Templates
    "Template",
    "clear_cache",
    "load_template_dir",
    "load_template_image",
    "parse_template_name",
    # Matching
    "MatchResult",
    "SearchResult",
    "find_all_matches",
    "find_best_match",
    "find_image",
    "find_multiple",
    "quick_search_bool",
    "quick_search_count",
    "quick_search_names",
    # Pixel
    "check_pixel",
    "color_check",
    "get_pixel_color",
    "is_inside_diamond",
    "multi_pixel_search",
    "parse_pixel_list",
    "pixel_search",
    # OCR
    "BuildingInfo",
    "get_builder_count",
    "get_building_info",
    "read_number",
    "read_text",
    # Geometry
    "get_deployable_points",
    "offset_polyline",
    "partition_points_by_side",
    "pixel_distance",
    "screen_to_village",
    "sort_by_distance",
    "village_to_screen",
    # Red area
    "RedArea",
    "detect_red_area",
    "detect_red_lines",
    # Game elements
    "TownHallResult",
    "check_dead_base",
    "check_dead_eagle",
    "find_close_button",
    "find_town_hall",
    "find_wall",
    "is_window_open",
    "WallSearchResult",
]
