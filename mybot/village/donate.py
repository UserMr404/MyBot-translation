"""Clan Castle donation translated from Village/DonateCC.au3.

Detects donation requests in clan chat and donates matching troops/spells.
Uses template matching to identify requested troops and available donations.

Source: COCBot/functions/Village/DonateCC.au3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.constants import MID_OFFSET_Y
from mybot.log import set_debug_log, set_log


@dataclass
class DonateConfig:
    """Donation configuration per troop/spell type.

    Replaces $g_abChkDonateTroop[], $g_abChkDonateAllTroop[], etc.
    """
    # Troop indices that are enabled for donation
    enabled_troops: list[int] = field(default_factory=list)
    # Whether to donate to any request (regardless of what's asked)
    donate_all: bool = False
    # Template directory for detecting donation requests
    request_template_dir: Path = field(
        default_factory=lambda: Path("imgxml/DonateCC/Army")
    )
    # Template directory for troop selection in donate window
    troop_template_dir: Path = field(
        default_factory=lambda: Path("imgxml/DonateCC/Troops")
    )


@dataclass
class DonateResult:
    """Result of a donation cycle."""
    requests_found: int = 0
    donations_made: int = 0
    troops_donated: list[str] = field(default_factory=list)


def donate_cc(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None] | None = None,
    config: DonateConfig | None = None,
) -> DonateResult:
    """Process clan castle donation requests.

    Translated from DonateCC() in DonateCC.au3.

    Flow:
    1. Open clan chat
    2. Scan for donation request buttons (yellow "Donate" buttons)
    3. For each request, click to open donation window
    4. Match requested troop type against enabled donations
    5. Click matching troops to donate
    6. Close donation window and continue

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking UI elements.
        config: Donation configuration.

    Returns:
        DonateResult with donation statistics.
    """
    if config is None:
        config = DonateConfig()

    result = DonateResult()

    image = capture_func()
    if image is None:
        return result

    # Find donation request buttons in clan chat
    requests = _find_donation_requests(image, config.request_template_dir)
    result.requests_found = len(requests)

    if not requests:
        set_debug_log("DonateCC: no donation requests found")
        return result

    set_log(f"DonateCC: found {len(requests)} donation requests")

    for req_x, req_y in requests:
        # Click the donation request to open donate window
        if click_func:
            click_func(req_x, req_y)

        import time
        time.sleep(0.5)

        # Capture donate window
        donate_image = capture_func()
        if donate_image is None:
            continue

        # Find and click matching troops
        donated = _donate_troops(donate_image, click_func, config)
        if donated:
            result.donations_made += 1
            result.troops_donated.extend(donated)

        time.sleep(0.3)

    if result.donations_made > 0:
        set_log(f"DonateCC: completed {result.donations_made} donations")

    return result


def _find_donation_requests(
    image: np.ndarray,
    template_dir: Path,
) -> list[tuple[int, int]]:
    """Find donation request buttons in clan chat.

    Searches for the yellow "Donate" button that appears next to
    each clan member's troop request.
    """
    if not template_dir.is_dir():
        return []

    from mybot.vision.matcher import find_multiple

    search_result = find_multiple(
        image,
        template_dir,
        max_results=10,
        confidence=0.80,
    )

    if not search_result.found:
        return []

    return [(m.x, m.y) for m in search_result.matches]


def _donate_troops(
    image: np.ndarray,
    click_func: Callable[[int, int], None] | None,
    config: DonateConfig,
) -> list[str]:
    """Donate troops from the open donation window.

    Scans the donation window for available troops and clicks
    the ones that are enabled in config.
    """
    if not config.troop_template_dir.is_dir():
        return []

    from mybot.vision.matcher import find_multiple

    donated = []

    search_result = find_multiple(
        image,
        config.troop_template_dir,
        max_results=20,
        confidence=0.80,
    )

    if not search_result.found:
        return donated

    for match in search_result.matches:
        # Check if this troop type is enabled for donation
        if config.donate_all or match.level in config.enabled_troops:
            if click_func:
                click_func(match.x, match.y)
            donated.append(match.name)
            set_debug_log(f"DonateCC: donated {match.name}")

            import time
            time.sleep(0.2)

    return donated
