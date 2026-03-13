"""Tests for the vision module (Phase 3).

Tests template loading, template matching, pixel operations, geometry,
OCR helpers, red area detection, and game element detection.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest


# ── Template Tests ───────────────────────────────────────────────────────────

class TestParseTemplateName:
    def test_standard_format(self):
        from mybot.vision.templates import parse_template_name
        assert parse_template_name("TownHall_10_92") == ("TownHall", 10, 92)

    def test_troop_format(self):
        from mybot.vision.templates import parse_template_name
        assert parse_template_name("Barb_100_91") == ("Barb", 100, 91)

    def test_multi_underscore_name(self):
        from mybot.vision.templates import parse_template_name
        # "17A" isn't purely numeric, so it doesn't match the _Level_Rotation pattern
        name, level, rotation = parse_template_name("TownHall_17A_90")
        assert name == "TownHall_17A_90"
        assert level == 0

    def test_no_level_rotation(self):
        from mybot.vision.templates import parse_template_name
        assert parse_template_name("unknown") == ("unknown", 0, 0)

    def test_empty_string(self):
        from mybot.vision.templates import parse_template_name
        assert parse_template_name("") == ("", 0, 0)


class TestLoadTemplateImage:
    def test_load_png(self, tmp_path: Path):
        from mybot.vision.templates import load_template_image

        # Create a test PNG
        img = np.zeros((30, 40, 3), dtype=np.uint8)
        img[10:20, 15:25] = (0, 0, 255)  # Red square
        png_path = tmp_path / "test.png"
        cv2.imwrite(str(png_path), img)

        loaded = load_template_image(png_path)
        assert loaded is not None
        assert loaded.shape == (30, 40, 3)

    def test_load_nonexistent(self):
        from mybot.vision.templates import load_template_image
        assert load_template_image(Path("/nonexistent.png")) is None

    def test_load_xml_with_png_cache(self, tmp_path: Path):
        from mybot.vision.templates import load_template_image

        # Create XML (proprietary, won't load) and PNG cache
        xml_path = tmp_path / "test_10_90.xml"
        xml_path.write_text("notbase64!!!")
        png_path = tmp_path / "test_10_90.png"
        img = np.ones((20, 20, 3), dtype=np.uint8) * 128
        cv2.imwrite(str(png_path), img)

        loaded = load_template_image(xml_path)
        assert loaded is not None
        assert loaded.shape == (20, 20, 3)


class TestLoadTemplateDir:
    def test_load_directory(self, tmp_path: Path):
        from mybot.vision.templates import clear_cache, load_template_dir

        clear_cache()

        # Create test templates
        for name, level in [("Barb", 1), ("Arch", 2), ("Giant", 3)]:
            img = np.zeros((20, 20, 3), dtype=np.uint8)
            path = tmp_path / f"{name}_{level}_90.png"
            cv2.imwrite(str(path), img)

        templates = load_template_dir(tmp_path)
        assert len(templates) == 3

    def test_filter_by_level(self, tmp_path: Path):
        from mybot.vision.templates import clear_cache, load_template_dir

        clear_cache()

        for level in [5, 10, 15, 20]:
            img = np.zeros((20, 20, 3), dtype=np.uint8)
            path = tmp_path / f"Wall_{level}_90.png"
            cv2.imwrite(str(path), img)

        templates = load_template_dir(tmp_path, min_level=10, max_level=15)
        assert len(templates) == 2
        assert all(10 <= t.level <= 15 for t in templates)

    def test_empty_directory(self, tmp_path: Path):
        from mybot.vision.templates import clear_cache, load_template_dir

        clear_cache()
        templates = load_template_dir(tmp_path)
        assert templates == []

    def test_nonexistent_directory(self):
        from mybot.vision.templates import load_template_dir

        templates = load_template_dir(Path("/nonexistent_dir"))
        assert templates == []


# ── Matcher Tests ────────────────────────────────────────────────────────────

class TestMatchResult:
    def test_search_result_found(self):
        from mybot.vision.matcher import MatchResult, SearchResult

        result = SearchResult(matches=[MatchResult(name="test", x=100, y=200)])
        assert result.found is True
        assert result.first is not None
        assert result.first.name == "test"

    def test_search_result_empty(self):
        from mybot.vision.matcher import SearchResult

        result = SearchResult()
        assert result.found is False
        assert result.first is None


class TestFindMultiple:
    def test_find_template_in_screenshot(self, tmp_path: Path):
        from mybot.vision.matcher import find_multiple
        from mybot.vision.templates import clear_cache

        clear_cache()

        # Create a non-uniform template (gradient pattern)
        template_img = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            template_img[i, :, 0] = i * 12  # Blue gradient
            template_img[:, i, 2] = i * 12  # Red gradient

        # Place it in a larger screenshot at known position
        screenshot = np.random.randint(0, 50, (200, 300, 3), dtype=np.uint8)
        screenshot[80:100, 100:120] = template_img

        template_path = tmp_path / "Pattern_1_90.png"
        cv2.imwrite(str(template_path), template_img)

        result = find_multiple(screenshot, tmp_path, confidence=0.90)
        assert result.found is True
        assert result.total_objects >= 1

        # Check that the match is near (110, 90) — center of template
        m = result.first
        assert m is not None
        assert abs(m.x - 110) < 5
        assert abs(m.y - 90) < 5

    def test_no_match(self, tmp_path: Path):
        from mybot.vision.matcher import find_multiple
        from mybot.vision.templates import clear_cache

        clear_cache()

        # Random noise screenshot
        rng = np.random.RandomState(42)
        screenshot = rng.randint(0, 50, (200, 300, 3), dtype=np.uint8)

        # Distinctly different pattern template
        template_img = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            template_img[i, :, 0] = 200 + i * 2
            template_img[:, i, 2] = 200 + i * 2
        template_path = tmp_path / "Unique_1_90.png"
        cv2.imwrite(str(template_path), template_img)

        result = find_multiple(screenshot, tmp_path, confidence=0.95)
        assert result.found is False


class TestFindImage:
    def test_find_single(self, tmp_path: Path):
        from mybot.vision.matcher import find_image

        # Create a patterned template
        template_img = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            template_img[i, :, 1] = i * 12
            template_img[:, i, 2] = i * 12

        # Place it in a noisy screenshot
        rng = np.random.RandomState(42)
        screenshot = rng.randint(0, 30, (100, 100, 3), dtype=np.uint8)
        screenshot[30:50, 40:60] = template_img

        path = tmp_path / "test_1_90.png"
        cv2.imwrite(str(path), template_img)

        match = find_image(screenshot, path, confidence=0.90)
        assert match is not None
        assert abs(match.x - 50) < 5
        assert abs(match.y - 40) < 5


# ── Pixel Tests ──────────────────────────────────────────────────────────────

class TestColorCheck:
    def test_exact_match(self):
        from mybot.vision.pixel import color_check
        assert color_check(0x0000FF, 0x0000FF) is True

    def test_within_tolerance(self):
        from mybot.vision.pixel import color_check
        assert color_check(0x0000FF, 0x0000FC, tolerance=5) is True

    def test_outside_tolerance(self):
        from mybot.vision.pixel import color_check
        assert color_check(0x0000FF, 0x0000F0, tolerance=5) is False

    def test_ignore_red(self):
        from mybot.vision.pixel import color_check
        # 0x0000FF in BBGGRR = B=0, G=0, R=0xFF
        # 0x000000 = B=0, G=0, R=0
        # With ignore="Red", red channel (255 vs 0) is skipped
        # Green (0 vs 0) and Blue (0 vs 0) match → True
        assert color_check(0x0000FF, 0x000000, tolerance=5, ignore="Red") is True
        # Without ignoring red, red channel differs by 255 → False
        assert color_check(0x0000FF, 0x000000, tolerance=5) is False


class TestIsInsideDiamond:
    def test_center_is_inside(self):
        from mybot.vision.pixel import is_inside_diamond
        # Center of default diamond should be inside
        assert is_inside_diamond(430, 307) is True

    def test_corner_is_outside(self):
        from mybot.vision.pixel import is_inside_diamond
        # Far corner should be outside
        assert is_inside_diamond(0, 0) is False
        assert is_inside_diamond(860, 732) is False

    def test_ui_zone_excluded(self):
        from mybot.vision.pixel import is_inside_diamond
        # Top area (builder buttons) should be excluded
        assert is_inside_diamond(430, 50, check_ui_zones=True) is False
        # Same point without UI check should be inside
        assert is_inside_diamond(430, 50, check_ui_zones=False) is True


class TestParsePixelList:
    def test_standard_format(self):
        from mybot.vision.pixel import parse_pixel_list
        result = parse_pixel_list("100-200|300-400|500-600")
        assert result == [(100, 200), (300, 400), (500, 600)]

    def test_empty_string(self):
        from mybot.vision.pixel import parse_pixel_list
        assert parse_pixel_list("") == []

    def test_single_pair(self):
        from mybot.vision.pixel import parse_pixel_list
        assert parse_pixel_list("50-75") == [(50, 75)]

    def test_custom_delimiters(self):
        from mybot.vision.pixel import parse_pixel_list
        result = parse_pixel_list("10,20;30,40", coord_delim=",", pair_delim=";")
        assert result == [(10, 20), (30, 40)]


# ── Geometry Tests ───────────────────────────────────────────────────────────

class TestCoordinateTransform:
    def test_screen_to_village_no_offset(self):
        from mybot.vision.geometry import screen_to_village
        # With no offset, coordinates should map to themselves
        vx, vy = screen_to_village(430, 366, (0.0, 0.0, 1.0))
        assert abs(vx - 430) < 1
        assert abs(vy - 366) < 1

    def test_village_to_screen_roundtrip(self):
        from mybot.vision.geometry import screen_to_village, village_to_screen
        offset = (10.0, 20.0, 1.0)
        vx, vy = screen_to_village(300, 400, offset)
        sx, sy = village_to_screen(vx, vy, offset)
        assert abs(sx - 300) < 2
        assert abs(sy - 400) < 2


class TestPixelSection:
    def test_center_sections(self):
        from mybot.vision.geometry import get_pixel_section
        # Top area
        section = get_pixel_section(430, 50)
        assert section in (1, 4)  # Top-left or top-right

    def test_bottom_left(self):
        from mybot.vision.geometry import get_pixel_section
        section = get_pixel_section(100, 600)
        assert section == 2


class TestPixelDistance:
    def test_horizontal(self):
        from mybot.vision.geometry import pixel_distance
        assert pixel_distance((0, 0), (3, 0)) == 3.0

    def test_diagonal(self):
        from mybot.vision.geometry import pixel_distance
        assert abs(pixel_distance((0, 0), (3, 4)) - 5.0) < 0.01


class TestSortByDistance:
    def test_simple_chain(self):
        from mybot.vision.geometry import sort_by_distance
        points = [(0, 0), (10, 0), (5, 0), (15, 0)]
        sorted_pts = sort_by_distance(points)
        # Should chain: (0,0) -> (5,0) -> (10,0) -> (15,0)
        assert sorted_pts[0] == (0, 0)
        assert sorted_pts[-1] == (15, 0)

    def test_single_point(self):
        from mybot.vision.geometry import sort_by_distance
        assert sort_by_distance([(5, 5)]) == [(5, 5)]

    def test_empty(self):
        from mybot.vision.geometry import sort_by_distance
        assert sort_by_distance([]) == []


class TestOffsetPolyline:
    def test_offset_outward(self):
        from mybot.vision.geometry import offset_polyline
        # Horizontal line above center
        points = [(100, 100), (200, 100), (300, 100)]
        offset = offset_polyline(points, 10.0, outward=True)
        assert len(offset) == 3
        # Offset should move points upward (away from center at 430,366)
        for orig, off in zip(points, offset):
            assert off[1] < orig[1]  # y should decrease (upward)


class TestPartitionPointsBySide:
    def test_four_sides(self):
        from mybot.vision.geometry import partition_points_by_side
        points = [
            (100, 100),   # top-left area
            (100, 500),   # bottom-left area
            (700, 500),   # bottom-right area
            (700, 100),   # top-right area
        ]
        sides = partition_points_by_side(points)
        assert len(sides) == 4
        # At least one side should have points
        total = sum(len(v) for v in sides.values())
        assert total == 4


# ── Red Area Tests ───────────────────────────────────────────────────────────

class TestRedArea:
    def test_red_area_dataclass(self):
        from mybot.vision.red_area import RedArea
        ra = RedArea()
        assert ra.is_valid is False
        assert ra.all_points == []

    def test_external_edge(self):
        from mybot.vision.red_area import get_external_edge
        points = get_external_edge("top_left", point_count=10)
        assert len(points) == 10
        # First point should be near top center, last near left center
        assert points[0][0] > 400  # near top (430, 2)
        assert points[-1][0] < 100  # near left (2, 340)

    def test_detect_red_lines_no_red(self):
        from mybot.vision.red_area import detect_red_lines
        # Black image — no red lines
        black = np.zeros((200, 300, 3), dtype=np.uint8)
        points = detect_red_lines(black)
        assert points == []


# ── OCR Tests ────────────────────────────────────────────────────────────────

class TestReadNumber:
    def test_returns_default_on_empty(self):
        from mybot.vision.ocr import read_number
        # Small black image — OCR should return nothing
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        result = read_number(img, 0, 0, 200, 100, default=42)
        assert result == 42

    def test_invalid_region(self):
        from mybot.vision.ocr import read_number
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        # Region outside image bounds
        result = read_number(img, 100, 100, 50, 50, default=-1)
        assert result == -1


class TestGetBuilderCount:
    def test_returns_zero_on_empty(self):
        from mybot.vision.ocr import get_builder_count
        img = np.zeros((100, 400, 3), dtype=np.uint8)
        free, total = get_builder_count(img)
        assert free == 0
        assert total == 0


class TestGetBuildingInfo:
    def test_returns_empty_on_blank(self):
        from mybot.vision.ocr import get_building_info
        img = np.zeros((600, 860, 3), dtype=np.uint8)
        info = get_building_info(img)
        assert info.level == 0


# ── Window Detection Tests ───────────────────────────────────────────────────

class TestIsWindowOpen:
    def test_no_match_returns_false(self, tmp_path: Path):
        from mybot.vision.window_detect import is_window_open

        # Patterned template that won't match random noise
        template_img = np.zeros((20, 20, 3), dtype=np.uint8)
        for i in range(20):
            template_img[i, :, 0] = 200 + i * 2
            template_img[:, i, 1] = 200 + i * 2
        path = tmp_path / "close_1_90.png"
        cv2.imwrite(str(path), template_img)

        rng = np.random.RandomState(99)
        screenshot = rng.randint(0, 30, (732, 860, 3), dtype=np.uint8)
        found, x, y = is_window_open(screenshot, path)
        assert found is False


# ── Wall Detection Tests ─────────────────────────────────────────────────────

class TestFindWall:
    def test_no_match(self, tmp_path: Path):
        from mybot.vision.templates import clear_cache
        from mybot.vision.walls import find_wall

        clear_cache()

        # Patterned template that won't match random noise
        template_img = np.zeros((15, 15, 3), dtype=np.uint8)
        for i in range(15):
            template_img[i, :, 2] = 180 + i * 4
            template_img[:, i, 0] = 180 + i * 4
        path = tmp_path / "Wall_10_90.png"
        cv2.imwrite(str(path), template_img)

        rng = np.random.RandomState(42)
        screenshot = rng.randint(0, 30, (200, 300, 3), dtype=np.uint8)
        result = find_wall(screenshot, tmp_path, target_level=10)
        assert result.found is False


# ── Town Hall Tests ──────────────────────────────────────────────────────────

class TestFindTownHall:
    def test_empty_dirs(self):
        from mybot.vision.townhall import find_town_hall

        screenshot = np.zeros((200, 300, 3), dtype=np.uint8)
        result = find_town_hall(screenshot, th_dirs=[])
        assert result.found is False

    def test_no_match(self, tmp_path: Path):
        from mybot.vision.templates import clear_cache
        from mybot.vision.townhall import find_town_hall

        clear_cache()

        # Patterned template that won't match random noise
        template_img = np.zeros((30, 30, 3), dtype=np.uint8)
        for i in range(30):
            template_img[i, :, 1] = 150 + i * 3
            template_img[:, i, 2] = 150 + i * 3
        path = tmp_path / "TownHall_10_90.png"
        cv2.imwrite(str(path), template_img)

        rng = np.random.RandomState(42)
        screenshot = rng.randint(0, 30, (200, 300, 3), dtype=np.uint8)
        result = find_town_hall(screenshot, th_dirs=[tmp_path], max_retries=1)
        assert result.found is False
