"""Game state detection and recovery module.

Phase 4: Main screen verification, obstacle detection/dismissal.

- main_screen: Detect if bot is on the main village or builder base screen
- obstacles: Detect and dismiss 15+ popup types that block the bot
"""

from mybot.game.main_screen import (
    check_main_screen,
    is_builder_base_grayed,
    is_main_grayed,
    is_main_screen,
    is_on_builder_base,
    is_on_main_village,
    wait_main_screen,
)
from mybot.game.obstacles import (
    ObstacleResult,
    ObstacleType,
    check_obstacles,
    is_gem_window,
    is_no_upgrade_loot,
)

__all__ = [
    "check_main_screen",
    "check_obstacles",
    "is_builder_base_grayed",
    "is_gem_window",
    "is_main_grayed",
    "is_main_screen",
    "is_no_upgrade_loot",
    "is_on_builder_base",
    "is_on_main_village",
    "ObstacleResult",
    "ObstacleType",
    "wait_main_screen",
]
