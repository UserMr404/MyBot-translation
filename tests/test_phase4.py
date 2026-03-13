"""Tests for Phase 4: Game Logic — Village, Search & Main Screen."""

from __future__ import annotations

import threading
import unittest

import numpy as np

from mybot.constants import MID_OFFSET_Y


# ── Main Screen Tests ────────────────────────────────────────────────────────


class TestIsMainScreen(unittest.TestCase):
    """Tests for main screen detection."""

    def _make_image(self, width=860, height=780):
        """Create a blank test image."""
        return np.zeros((height, width, 3), dtype=np.uint8)

    def test_is_main_pixel_match(self):
        """Main screen detected when IS_MAIN pixel matches."""
        from mybot.game.main_screen import _check_pixel_tuple
        from mybot.config.coordinates import IS_MAIN

        image = self._make_image()
        x, y, color, tol = IS_MAIN
        # Set pixel to matching color (0xBBGGRR → BGR)
        b = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        r = color & 0xFF
        image[y, x] = [b, g, r]

        self.assertTrue(_check_pixel_tuple(image, IS_MAIN))

    def test_is_main_pixel_no_match(self):
        """Main screen not detected when pixel doesn't match."""
        from mybot.game.main_screen import _check_pixel_tuple
        from mybot.config.coordinates import IS_MAIN

        image = self._make_image()
        # Leave pixel at black (0, 0, 0) — won't match
        self.assertFalse(_check_pixel_tuple(image, IS_MAIN))

    def test_is_main_grayed_detects_gray(self):
        """Grayed detection triggers on desaturated pixels."""
        from mybot.game.main_screen import is_main_grayed

        image = self._make_image()
        # Set gray pixels at check positions
        for x, y in [(378, 7), (380, 8), (390, 9)]:
            image[y, x] = [100, 100, 100]  # Gray BGR

        self.assertTrue(is_main_grayed(image))

    def test_is_main_grayed_not_on_colorful(self):
        """Grayed detection doesn't trigger on colorful pixels."""
        from mybot.game.main_screen import is_main_grayed

        image = self._make_image()
        # Set colorful pixels (high saturation)
        for x, y in [(378, 7), (380, 8), (390, 9)]:
            image[y, x] = [200, 50, 50]  # Strong blue

        self.assertFalse(is_main_grayed(image))

    def test_is_builder_base_grayed(self):
        """Builder base grayed detection on gray pixels."""
        from mybot.game.main_screen import is_builder_base_grayed

        image = self._make_image()
        for x, y in [(440, 7), (450, 8), (465, 9)]:
            image[y, x] = [90, 90, 90]

        self.assertTrue(is_builder_base_grayed(image))


# ── Obstacle Tests ───────────────────────────────────────────────────────────


class TestObstacles(unittest.TestCase):
    """Tests for obstacle detection."""

    def _make_image(self, width=860, height=780):
        return np.zeros((height, width, 3), dtype=np.uint8)

    def test_no_obstacles_on_clean_screen(self):
        """No obstacles detected on a normal-colored screen."""
        from mybot.game.obstacles import check_obstacles

        # Use a colorful image (black triggers maintenance, gray triggers grayed check)
        rng = np.random.RandomState(42)
        image = rng.randint(50, 255, (780, 860, 3), dtype=np.uint8)
        result = check_obstacles(image)
        self.assertFalse(result.found)

    def test_obstacle_result_defaults(self):
        """ObstacleResult has correct defaults."""
        from mybot.game.obstacles import ObstacleResult, ObstacleType

        result = ObstacleResult()
        self.assertFalse(result.found)
        self.assertEqual(result.obstacle_type, ObstacleType.NONE)
        self.assertFalse(result.minor)

    def test_gem_window_detection(self):
        """Gem window detected from pixel color."""
        from mybot.game.obstacles import is_gem_window
        from mybot.config.coordinates import IS_GEM_WINDOW

        image = self._make_image()
        x, y, color, tol = IS_GEM_WINDOW
        b = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        r = color & 0xFF
        image[y, x] = [b, g, r]

        self.assertTrue(is_gem_window(image))

    def test_no_gem_window_on_blank(self):
        """Gem window not detected on blank screen."""
        from mybot.game.obstacles import is_gem_window

        image = self._make_image()
        self.assertFalse(is_gem_window(image))

    def test_close_buttons_detected(self):
        """White close button + beige background triggers detection."""
        from mybot.game.obstacles import _check_close_buttons

        image = self._make_image()

        # Set white pixel at (618, 150+MID_OFFSET_Y)
        y1 = 150 + MID_OFFSET_Y
        image[y1, 618] = [255, 255, 255]

        # Set beige pixel at (735, 510+MID_OFFSET_Y)
        y2 = 510 + MID_OFFSET_Y
        image[y2, 735] = [0xE1, 0xE8, 0xE9]  # BGR for 0xE9E8E1

        clicks = []
        click_func = lambda x, y: clicks.append((x, y))

        result = _check_close_buttons(image, click_func)
        self.assertTrue(result)
        self.assertEqual(len(clicks), 1)
        self.assertEqual(clicks[0], (618, y1))


# ── Resource Tests ───────────────────────────────────────────────────────────


class TestSearchLoot(unittest.TestCase):
    """Tests for SearchLoot dataclass."""

    def test_loot_defaults(self):
        from mybot.search.resources import SearchLoot

        loot = SearchLoot()
        self.assertEqual(loot.gold, 0)
        self.assertEqual(loot.elixir, 0)
        self.assertEqual(loot.dark_elixir, 0)
        self.assertEqual(loot.trophies, 0)

    def test_loot_total(self):
        from mybot.search.resources import SearchLoot

        loot = SearchLoot(gold=100000, elixir=200000)
        self.assertEqual(loot.total_loot, 300000)

    def test_loot_index_access(self):
        from mybot.search.resources import SearchLoot
        from mybot.enums import LootType

        loot = SearchLoot(gold=1, elixir=2, dark_elixir=3, trophies=4)
        self.assertEqual(loot[LootType.GOLD], 1)
        self.assertEqual(loot[LootType.ELIXIR], 2)
        self.assertEqual(loot[LootType.DARK_ELIXIR], 3)
        self.assertEqual(loot[LootType.TROPHY], 4)


class TestCompareResources(unittest.TestCase):
    """Tests for resource comparison logic."""

    def test_and_condition_all_meet(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=200000, elixir=200000, dark_elixir=2000, trophies=10)
        filt = SearchFilter(
            min_gold=100000, min_elixir=100000, min_dark_elixir=1000,
            meet_condition="and",
        )
        self.assertTrue(compare_resources(loot, filt))

    def test_and_condition_one_fails(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=200000, elixir=50000, dark_elixir=2000)
        filt = SearchFilter(
            min_gold=100000, min_elixir=100000, min_dark_elixir=1000,
            meet_condition="and",
        )
        self.assertFalse(compare_resources(loot, filt))

    def test_or_condition_one_meets(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=500000, elixir=0, dark_elixir=0)
        filt = SearchFilter(
            min_gold=100000, min_elixir=100000, min_dark_elixir=1000,
            meet_condition="or",
        )
        self.assertTrue(compare_resources(loot, filt))

    def test_or_condition_none_meets(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=50000, elixir=50000, dark_elixir=500)
        filt = SearchFilter(
            min_gold=100000, min_elixir=100000, min_dark_elixir=1000,
            meet_condition="or",
        )
        self.assertFalse(compare_resources(loot, filt))

    def test_gpe_condition(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=150000, elixir=150000, dark_elixir=2000)
        filt = SearchFilter(
            min_gold=200000, min_elixir=100000, min_dark_elixir=1000,
            meet_condition="g+e",
        )
        # 150k + 150k = 300k >= 200k + 100k = 300k, and DE 2000 >= 1000
        self.assertTrue(compare_resources(loot, filt))

    def test_th_level_check(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=500000, elixir=500000, dark_elixir=5000, trophies=10)
        filt = SearchFilter(
            min_gold=100000, min_elixir=100000, min_dark_elixir=1000,
            max_th_level=10, meet_condition="and",
        )
        # TH12 > max TH10
        self.assertFalse(compare_resources(loot, filt, th_level=12))
        # TH9 <= max TH10
        self.assertTrue(compare_resources(loot, filt, th_level=9))

    def test_threshold_reduction(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=80000, elixir=80000, dark_elixir=800)
        filt = SearchFilter(
            min_gold=100000, min_elixir=100000, min_dark_elixir=1000,
            meet_condition="and",
            reduce_count=10, reduce_gold=10000, reduce_elixir=10000, reduce_dark_elixir=100,
        )
        # Without reduction: fails (80k < 100k)
        self.assertFalse(compare_resources(loot, filt, search_count=5))
        # After 20 searches (2 reductions): 100k - 20k = 80k, 1000 - 200 = 800
        self.assertTrue(compare_resources(loot, filt, search_count=20))

    def test_trophy_check(self):
        from mybot.search.resources import SearchLoot, SearchFilter, compare_resources

        loot = SearchLoot(gold=500000, elixir=500000, dark_elixir=5000, trophies=-5)
        filt = SearchFilter(
            min_gold=0, min_elixir=0, min_dark_elixir=0,
            min_trophies=0, meet_condition="and",
        )
        self.assertFalse(compare_resources(loot, filt))


# ── Village Report Tests ─────────────────────────────────────────────────────


class TestVillageReport(unittest.TestCase):
    """Tests for village report."""

    def test_report_defaults(self):
        from mybot.village.report import VillageReport

        report = VillageReport()
        self.assertEqual(report.gold, 0)
        self.assertEqual(report.gems, 0)
        self.assertEqual(report.free_builders, 0)

    def test_update_bot_state(self):
        from mybot.village.report import VillageReport, update_bot_state
        from mybot.state import BotState
        from mybot.enums import LootType

        report = VillageReport(
            gold=100000, elixir=200000, dark_elixir=3000,
            gems=500, trophies=2500,
            free_builders=3, total_builders=5,
        )
        state = BotState()
        update_bot_state(report, state)

        self.assertEqual(state.village.current_loot[LootType.GOLD], 100000)
        self.assertEqual(state.village.current_loot[LootType.ELIXIR], 200000)
        self.assertEqual(state.village.current_loot[LootType.DARK_ELIXIR], 3000)
        self.assertEqual(state.village.current_loot[LootType.TROPHY], 2500)
        self.assertEqual(state.village.gems, 500)
        self.assertEqual(state.village.free_builder_count, 3)
        self.assertEqual(state.village.total_builder_count, 5)


# ── Storage Fullness Tests ───────────────────────────────────────────────────


class TestStorageFullness(unittest.TestCase):
    """Tests for is_storage_full."""

    def _make_image(self, width=860, height=780):
        return np.zeros((height, width, 3), dtype=np.uint8)

    def test_gold_storage_full(self):
        from mybot.village.collect import is_storage_full

        image = self._make_image()
        # Gold full pixel: (657, 2+MID_OFFSET_Y, 0xE7C00D)
        y = 2 + MID_OFFSET_Y
        # 0xE7C00D in BBGGRR: B=0xE7, G=0xC0, R=0x0D → BGR = [0xE7, 0xC0, 0x0D]
        # Wait — 0xE7C00D as BBGGRR: B=(0xE7C00D>>16)=0xE7, G=(>>8)=0xC0, R=0x0D
        # So in OpenCV BGR: [0xE7, 0xC0, 0x0D]
        # Hmm, but check_pixel expects BBGGRR integer and image is BGR
        # check_pixel: expected_color & 0xFF = R, >>8 = G, >>16 = B
        # So R=0x0D, G=0xC0, B=0xE7 → BGR image pixel: [0xE7, 0xC0, 0x0D]
        image[y, 657] = [0xE7, 0xC0, 0x0D]

        self.assertTrue(is_storage_full(image, "gold"))

    def test_storage_not_full(self):
        from mybot.village.collect import is_storage_full

        image = self._make_image()
        self.assertFalse(is_storage_full(image, "gold"))
        self.assertFalse(is_storage_full(image, "elixir"))
        self.assertFalse(is_storage_full(image, "dark_elixir"))


# ── Switch Account Tests ─────────────────────────────────────────────────────


class TestSwitchAccount(unittest.TestCase):
    """Tests for multi-account switching logic."""

    def test_select_next_round_robin(self):
        from mybot.village.switch_account import (
            AccountConfig, SwitchAccountConfig, select_next_account,
        )

        config = SwitchAccountConfig(
            enabled=True,
            accounts=[
                AccountConfig(index=0, enabled=True),
                AccountConfig(index=1, enabled=True),
                AccountConfig(index=2, enabled=True),
            ],
        )

        self.assertEqual(select_next_account(config, 0), 1)
        self.assertEqual(select_next_account(config, 1), 2)
        self.assertEqual(select_next_account(config, 2), 0)

    def test_select_next_skips_disabled(self):
        from mybot.village.switch_account import (
            AccountConfig, SwitchAccountConfig, select_next_account,
        )

        config = SwitchAccountConfig(
            enabled=True,
            accounts=[
                AccountConfig(index=0, enabled=True),
                AccountConfig(index=1, enabled=False),
                AccountConfig(index=2, enabled=True),
            ],
        )

        # From 0, skip disabled 1, go to 2
        self.assertEqual(select_next_account(config, 0), 2)

    def test_select_next_donate_priority(self):
        from mybot.village.switch_account import (
            AccountConfig, SwitchAccountConfig, select_next_account,
        )

        config = SwitchAccountConfig(
            enabled=True,
            donate_priority=True,
            accounts=[
                AccountConfig(index=0, enabled=True),
                AccountConfig(index=1, enabled=True, donate_only=True),
                AccountConfig(index=2, enabled=True),
            ],
        )

        # From account 0, donate-priority picks account 1
        self.assertEqual(select_next_account(config, 0), 1)

    def test_should_switch_disabled(self):
        from mybot.village.switch_account import SwitchAccountConfig, should_switch

        config = SwitchAccountConfig(enabled=False)
        self.assertFalse(should_switch(config, 0, 9999.0))

    def test_should_switch_max_time(self):
        from mybot.village.switch_account import SwitchAccountConfig, should_switch

        config = SwitchAccountConfig(enabled=True, max_time=1800.0)
        self.assertFalse(should_switch(config, 0, 1000.0))
        self.assertTrue(should_switch(config, 0, 2000.0))

    def test_should_switch_force(self):
        from mybot.village.switch_account import SwitchAccountConfig, should_switch

        config = SwitchAccountConfig(enabled=True)
        self.assertTrue(should_switch(config, 0, 0.0, force=True))

    def test_single_account_no_switch(self):
        from mybot.village.switch_account import (
            AccountConfig, SwitchAccountConfig, select_next_account,
        )

        config = SwitchAccountConfig(
            enabled=True,
            accounts=[AccountConfig(index=0, enabled=True)],
        )
        self.assertEqual(select_next_account(config, 0), -1)


# ── Building Location Tests ─────────────────────────────────────────────────


class TestBuildingLocation(unittest.TestCase):
    """Tests for building location dataclass."""

    def test_location_defaults(self):
        from mybot.village.locate import BuildingLocation

        loc = BuildingLocation()
        self.assertFalse(loc.found)
        self.assertEqual(loc.name, "")
        self.assertEqual(loc.level, 0)

    def test_locate_missing_dir(self):
        """Locate returns not-found for missing template directory."""
        from mybot.village.locate import locate_building
        from pathlib import Path

        image = np.zeros((780, 860, 3), dtype=np.uint8)
        result = locate_building(image, Path("/nonexistent/dir"))
        self.assertFalse(result.found)


# ── Upgrade Tests ────────────────────────────────────────────────────────────


class TestUpgradeSlot(unittest.TestCase):
    """Tests for upgrade slot dataclass."""

    def test_slot_defaults(self):
        from mybot.village.upgrade import UpgradeSlot

        slot = UpgradeSlot()
        self.assertFalse(slot.enabled)
        self.assertFalse(slot.in_progress)
        self.assertEqual(slot.cost, 0)

    def test_auto_upgrade_empty_list(self):
        from mybot.village.upgrade import auto_upgrade

        results = auto_upgrade(lambda: None, None, [])
        self.assertEqual(len(results), 0)

    def test_auto_upgrade_skips_in_progress(self):
        from mybot.village.upgrade import auto_upgrade, UpgradeSlot

        slots = [UpgradeSlot(enabled=True, in_progress=True)]
        results = auto_upgrade(lambda: None, None, slots)
        self.assertEqual(len(results), 0)


# ── Search Config Tests ──────────────────────────────────────────────────────


class TestSearchConfig(unittest.TestCase):
    """Tests for search configuration."""

    def test_config_defaults(self):
        from mybot.search.search import SearchConfig
        from mybot.enums import MatchMode

        config = SearchConfig()
        self.assertEqual(config.match_mode, MatchMode.DEAD_BASE)
        self.assertEqual(config.max_searches, 200)
        self.assertTrue(config.check_dead_base)

    def test_search_result_defaults(self):
        from mybot.search.search import SearchResult

        result = SearchResult()
        self.assertFalse(result.found)
        self.assertEqual(result.th_level, 0)
        self.assertFalse(result.is_dead_base)


# ── Donate Config Tests ──────────────────────────────────────────────────────


class TestDonateConfig(unittest.TestCase):
    """Tests for donation configuration."""

    def test_config_defaults(self):
        from mybot.village.donate import DonateConfig

        config = DonateConfig()
        self.assertFalse(config.donate_all)
        self.assertEqual(len(config.enabled_troops), 0)

    def test_donate_result_defaults(self):
        from mybot.village.donate import DonateResult

        result = DonateResult()
        self.assertEqual(result.requests_found, 0)
        self.assertEqual(result.donations_made, 0)


# ── Collect Tests ────────────────────────────────────────────────────────────


class TestCollect(unittest.TestCase):
    """Tests for resource collection."""

    def test_collect_result_defaults(self):
        from mybot.village.collect import CollectResult

        result = CollectResult()
        self.assertEqual(result.total_clicks, 0)

    def test_collect_with_no_capture(self):
        from mybot.village.collect import collect_resources

        result = collect_resources(lambda: None)
        self.assertEqual(result.total_clicks, 0)


# ── Prepare Search Tests ────────────────────────────────────────────────────


class TestPrepareSearch(unittest.TestCase):
    """Tests for search preparation."""

    def test_prepare_result_defaults(self):
        from mybot.search.prepare import PrepareResult

        result = PrepareResult()
        self.assertFalse(result.ready)
        self.assertEqual(result.error, "")


# ── Obstacle Type Tests ─────────────────────────────────────────────────────


class TestObstacleType(unittest.TestCase):
    """Tests for ObstacleType enum values."""

    def test_obstacle_types(self):
        from mybot.game.obstacles import ObstacleType

        self.assertEqual(ObstacleType.CONNECTION_LOST, 0)
        self.assertEqual(ObstacleType.MAJOR_UPDATE, 4)
        self.assertEqual(ObstacleType.NONE, -1)


if __name__ == "__main__":
    unittest.main()
