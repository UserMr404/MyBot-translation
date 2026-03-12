"""Bot state models translated from MBR Global Variables.au3.

Replaces the 852 global variables with structured dataclasses.
Thread-safe access via locks where noted.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path

from mybot.enums import BotAction, Hero, LootType, MatchMode, Siege, Spell, Troop


@dataclass
class DebugState:
    """All debug flags ($g_bDebug*)."""
    set_log: bool = False
    android: bool = False
    click: bool = False
    func_time: bool = False
    func_call: bool = False
    ocr: bool = False
    image_save: bool = False
    building_pos: bool = False
    set_log_train: bool = False
    window_messages: int = 0  # 0=off, 1=most, 2=all
    android_embedded: bool = False
    get_location: bool = False
    red_area: bool = False
    smart_zap: bool = False
    attack_csv: bool = False
    make_img_csv: bool = False
    beta_version: bool = False
    village_search_images: bool = False
    dead_base_image: bool = False
    ocr_donate: bool = False
    disable_zoomout: bool = False
    village_search_always_measure: bool = False
    disable_village_centering: bool = False
    zoomout_failure_not_restarting: bool = False
    multilanguage: bool = False


@dataclass
class ScreenState:
    """Screen/window dimensions and offsets."""
    game_width: int = 860
    game_height: int = 732
    default_width: int = 860
    default_height: int = 780
    mid_offset_y: int = 30
    bottom_offset_y: int = 60
    village_offset: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])


@dataclass
class VillageState:
    """Village resource and status tracking."""
    current_loot: list[int] = field(default_factory=lambda: [0] * LootType.COUNT)
    full_storage: list[bool] = field(default_factory=lambda: [False] * LootType.COUNT)
    town_hall_level: int = 0
    free_builder_count: int = 0
    total_builder_count: int = 0
    gems: int = 0


@dataclass
class ArmyState:
    """Army composition and readiness."""
    is_full: bool = False
    camp_space_total: int = 0
    camp_space_used: int = 0
    spell_space_total: int = 0
    spell_space_used: int = 0
    cc_space_total: int = 0
    cc_space_used: int = 0
    custom_troops: list[int] = field(default_factory=lambda: [0] * Troop.COUNT)
    custom_spells: list[int] = field(default_factory=lambda: [0] * Spell.COUNT)
    custom_sieges: list[int] = field(default_factory=lambda: [0] * Siege.COUNT)
    current_troops: list[int] = field(default_factory=lambda: [0] * Troop.COUNT)
    current_spells: list[int] = field(default_factory=lambda: [0] * Spell.COUNT)
    hero_available: list[bool] = field(default_factory=lambda: [False] * Hero.COUNT)
    hero_upgrading: list[bool] = field(default_factory=lambda: [False] * Hero.COUNT)


@dataclass
class AndroidState:
    """Android emulator state."""
    emulator: str = ""  # "BlueStacks5", "MEmu", "Nox"
    instance: str = ""
    window_handle: int = 0
    pid: int = 0
    adb_port: int = 5555
    embedded: bool = False
    version: str = ""


@dataclass
class SearchState:
    """Search/attack mode state."""
    is_searching: bool = False
    match_mode: MatchMode = MatchMode.DEAD_BASE
    search_count: int = 0
    redline_data: str = ""


@dataclass
class AccountState:
    """Multi-account switching state."""
    current_account: int = 0
    total_accounts: int = 1
    profile_name: str = ""
    config_path: Path = field(default_factory=Path)


@dataclass
class BotState:
    """Root state object replacing all 852 AutoIt global variables.

    Thread-safe: use `lock` for atomic multi-field updates.
    """
    # Core state
    running: bool = False
    restart_requested: bool = False
    action: BotAction = BotAction.NO_ACTION
    paused: bool = False
    first_start: bool = True
    first_run: int = 1
    first_attack: int = 0
    gui_mode: int = 1  # 1=normal, 2=mini, 0=no GUI

    # Stop event for signaling threads
    stop_event: threading.Event = field(default_factory=threading.Event)
    lock: threading.Lock = field(default_factory=threading.Lock)

    # Sub-states
    debug: DebugState = field(default_factory=DebugState)
    screen: ScreenState = field(default_factory=ScreenState)
    village: VillageState = field(default_factory=VillageState)
    army: ArmyState = field(default_factory=ArmyState)
    android: AndroidState = field(default_factory=AndroidState)
    search: SearchState = field(default_factory=SearchState)
    account: AccountState = field(default_factory=AccountState)

    # Timers
    time_since_started: float = 0.0
    time_passed: float = 0.0

    # Attack state
    command_stop: int = -1  # -1=None, 0=Halt Attack, 3=Training halted
    meet_cond_stop: bool = False
    direct_attack_running: bool = False
    idle_state: bool = False
    attack_now_pressed: bool = False
