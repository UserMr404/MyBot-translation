"""Village search loop translated from Search/VillageSearch.au3.

Implements the main enemy village search cycle: capture screenshot,
read resources via OCR, compare against thresholds, detect TH level,
check for dead base, and decide whether to attack.

Source: COCBot/functions/Search/VillageSearch.au3
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.enums import MatchMode
from mybot.log import set_debug_log, set_log
from mybot.search.resources import SearchFilter, SearchLoot, compare_resources, get_resources


@dataclass
class SearchConfig:
    """Configuration for village search.

    Replaces global search settings from MBR Global Variables.au3.
    """
    dead_base_filter: SearchFilter = field(default_factory=SearchFilter)
    live_base_filter: SearchFilter = field(default_factory=SearchFilter)
    bully_filter: SearchFilter = field(default_factory=SearchFilter)
    match_mode: MatchMode = MatchMode.DEAD_BASE

    # TH detection
    th_template_dirs: list[Path] = field(default_factory=list)

    # Dead base detection
    dead_base_dir: Path = field(default_factory=lambda: resolve_img_dir("imgxml/deadbase"))
    collector_level_dir: Path = field(default_factory=lambda: resolve_img_dir("imgxml/deadbase/levels"))

    # Search limits
    max_searches: int = 200
    max_time: float = 1800.0  # 30 minutes
    clouds_timeout: float = 300.0  # 5 minutes waiting for clouds

    # Check dead base
    check_dead_base: bool = True
    min_dead_collectors: int = 3


@dataclass
class SearchResult:
    """Result of village search."""
    found: bool = False
    loot: SearchLoot = field(default_factory=SearchLoot)
    th_level: int = 0
    is_dead_base: bool = False
    match_mode: MatchMode = MatchMode.DEAD_BASE
    search_count: int = 0
    skipped: bool = False


def village_search(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
    config: SearchConfig | None = None,
    on_next: Callable[[], None] | None = None,
) -> SearchResult:
    """Main village search loop.

    Translated from _VillageSearch() in VillageSearch.au3.
    Repeatedly captures screenshots, reads resources, and compares
    against configured thresholds until a suitable base is found.

    The flow per iteration:
    1. Capture screenshot
    2. Read resources via OCR
    3. Compare against thresholds
    4. If resources match, detect TH level
    5. If dead base mode, verify base is dead
    6. Return result or skip to next base

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking 'Next' button.
        config: Search configuration. Uses defaults if None.
        on_next: Callback to press the 'Next' button.

    Returns:
        SearchResult with match details.
    """
    if config is None:
        config = SearchConfig()

    result = SearchResult(match_mode=config.match_mode)
    start_time = time.time()

    for search_num in range(1, config.max_searches + 1):
        result.search_count = search_num

        # Check time limit
        elapsed = time.time() - start_time
        if elapsed > config.max_time:
            set_log(f"Search time limit reached ({elapsed:.0f}s)")
            result.skipped = True
            return result

        # Capture screenshot
        image = capture_func()
        if image is None:
            set_debug_log(f"Search #{search_num}: capture failed")
            time.sleep(1.0)
            continue

        # Read resources via OCR
        loot = get_resources(image)
        result.loot = loot

        # Select filter based on match mode
        if config.match_mode == MatchMode.DEAD_BASE:
            active_filter = config.dead_base_filter
        elif config.match_mode == MatchMode.LIVE_BASE:
            active_filter = config.live_base_filter
        else:
            active_filter = config.bully_filter

        # Compare resources against thresholds
        if not compare_resources(loot, active_filter, search_count=search_num):
            set_debug_log(f"Search #{search_num}: resources below threshold, next")
            if on_next:
                on_next()
            continue

        # Resources match — detect TH level
        th_level = _detect_th_level(image, config.th_template_dirs)
        result.th_level = th_level

        # Check TH level against filter
        if th_level > 0 and th_level > active_filter.max_th_level:
            set_debug_log(f"Search #{search_num}: TH{th_level} too high, next")
            if on_next:
                on_next()
            continue

        # Dead base verification (if in dead base mode)
        if config.match_mode == MatchMode.DEAD_BASE and config.check_dead_base:
            is_dead = _check_dead_base(image, config)
            result.is_dead_base = is_dead
            if not is_dead:
                set_debug_log(f"Search #{search_num}: not a dead base, next")
                if on_next:
                    on_next()
                continue

        # All checks passed — base found
        result.found = True
        set_log(
            f"Match found (#{search_num}): G={loot.gold:,} E={loot.elixir:,} "
            f"DE={loot.dark_elixir:,} TH={th_level} "
            f"{'DEAD' if result.is_dead_base else 'LIVE'}"
        )
        return result

    set_log(f"Search exhausted after {config.max_searches} attempts")
    result.skipped = True
    return result


def _detect_th_level(
    image: np.ndarray,
    th_dirs: list[Path],
) -> int:
    """Detect Town Hall level from search screen.

    Args:
        image: BGR screenshot.
        th_dirs: Template directories for TH detection.

    Returns:
        TH level (0 if not detected).
    """
    if not th_dirs:
        return 0

    from mybot.vision.townhall import find_town_hall
    result = find_town_hall(image, th_dirs, max_retries=1)
    return result.level if result.found else 0


def _check_dead_base(image: np.ndarray, config: SearchConfig) -> bool:
    """Verify the base is dead (abandoned).

    Args:
        image: BGR screenshot.
        config: Search config with dead base directories.

    Returns:
        True if base appears dead.
    """
    from mybot.vision.dead_base import check_dead_base

    if not config.dead_base_dir.is_dir():
        return False

    return check_dead_base(
        image,
        config.dead_base_dir,
        config.collector_level_dir,
        min_collector_matches=config.min_dead_collectors,
    )
