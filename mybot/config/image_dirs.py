"""Image template directory paths translated from ImageDirectories.au3.

All paths are relative to the base directory (repo root or PyInstaller bundle).
Resolved to absolute paths at runtime via resolve().
"""

from pathlib import Path

from mybot.utils.paths import get_base_dir

# Set at startup to the base directory
_script_dir: Path | None = None


def set_script_dir(path: Path) -> None:
    """Set the base script directory (called during bot initialization)."""
    global _script_dir
    _script_dir = path


def resolve(relative: str) -> Path:
    """Resolve a relative imgxml path to absolute.

    Uses the explicitly set script dir, falling back to the
    PyInstaller-aware base dir from utils.paths.
    """
    base = _script_dir if _script_dir is not None else get_base_dir()
    return base / relative


# ── Windows ──────────────────────────────────────────────────────────────────
GENERAL_CLOSE_BUTTON = "imgxml/Windows/CloseButton"

# ── Obstacles / Errors ───────────────────────────────────────────────────────
ERROR = "imgxml/other/Error"
CONNECTION_LOST = "imgxml/other/ConnectionLost"
OOS = "imgxml/other/OoS"
RATE_GAME = "imgxml/other/RateGame"
NOTICE = "imgxml/other/Notice"
MAJOR_UPDATE = "imgxml/other/MajorUpdate"
GP_SERVICES = "imgxml/other/GPServices"
DEVICE = "imgxml/other/Device"
MAINTENANCE = "imgxml/other/Maintenance"
COC_RECONNECTING = "imgxml/other/CocReconnecting"
LOADING = "imgxml/other/Loading"
SURVEY = "imgxml/other/Survey"

# ── Main Village ─────────────────────────────────────────────────────────────
IS_ON_MAIN_VILLAGE = "imgxml/village/NormalVillage"
COLLECT_RESOURCES = "imgxml/Resources/Collect"
COLLECT_LOOT_CART = "imgxml/Resources/LootCart"
BOAT = "imgxml/village/Boat"
ZOOM_OUT = "imgxml/other/ZoomOut"
CHECK_WALL = "imgxml/Walls"
CLEAR_TOMBS = "imgxml/Resources/Tombs"
CLEAN_YARD = "imgxml/Resources/CleanYard"
GEM_BOX = "imgxml/Resources/GemBox"
ACHIEVEMENTS_MAIN = "imgxml/village/Achievements"
ACHIEVEMENTS_PROFILE = "imgxml/village/AchievementsProfile"
TRADER = "imgxml/other/Trader"
DONATE_CC = "imgxml/DonateCC"
LAB_RESEARCH = "imgxml/Research/Laboratory"
HERO_EQUIPMENT = "imgxml/ArmyOverview/HeroEquipment"

# ── Clan Capital ─────────────────────────────────────────────────────────────
CC_MAP = "imgxml/ClanCapital/Map"
CC_GOLD_COLLECT = "imgxml/ClanCapital/GoldCollect"
CC_GOLD_CRAFT = "imgxml/ClanCapital/GoldCraft"
FORGE_HOUSE = "imgxml/ClanCapital/ForgeHouse"
CC_RAID = "imgxml/ClanCapital/Raid"
CC_UPGRADE_BUTTON = "imgxml/ClanCapital/UpgradeButton"

# ── Builder Base ─────────────────────────────────────────────────────────────
COLLECT_RESOURCES_BB = "imgxml/Resources/CollectBB"
BOAT_BB = "imgxml/village/BoatBB"
START_CT_BOOST = "imgxml/BuilderBase/ClockTower"
CLEAN_BB_YARD = "imgxml/Resources/CleanYardBB"
IS_ON_BB = "imgxml/village/BuilderBase"
MASTER_BUILDER_HEAD = "imgxml/BuilderBase/MasterBuilder"
STAR_LABORATORY = "imgxml/BuilderBase/StarLab"
BB_ATTACK_BUTTON = "imgxml/BuilderBase/AttackButton"
BB_ATTACK_START = "imgxml/BuilderBase/AttackStart"
BB_RETURN_HOME = "imgxml/BuilderBase/ReturnHome"

# ── Super Troops ─────────────────────────────────────────────────────────────
BOOST_TROOPS_BARREL = "imgxml/SuperTroops/Barrel"
BOOST_TROOPS_WINDOW = "imgxml/SuperTroops/Window"
BOOST_TROOPS_ICONS = "imgxml/SuperTroops/Icons"
BOOST_TROOPS_BUTTONS = "imgxml/SuperTroops/Buttons"
BOOST_TROOPS_POTION = "imgxml/SuperTroops/Potion"
BOOST_TROOPS_CLOCK = "imgxml/SuperTroops/Clock"

# ── Donate CC ────────────────────────────────────────────────────────────────
DONATE_TROOPS = "imgxml/DonateCC/Troops"
DONATE_SPELLS = "imgxml/DonateCC/Spells"
DONATE_SIEGE = "imgxml/DonateCC/Siege"

# ── Training ─────────────────────────────────────────────────────────────────
TRAIN_TROOPS = "imgxml/Train/Troops"
TRAIN_SPELLS = "imgxml/Train/Spells"
TRAIN_SIEGES = "imgxml/Train/Sieges"
ARMY_OVERVIEW_SPELLS = "imgxml/ArmyOverview/Spells"
ARMY_OVERVIEW_HEROES = "imgxml/ArmyOverview/Heroes"
QUICK_TRAIN = "imgxml/Train/QuickTrain"
EDIT_QUICK_TRAIN = "imgxml/Train/EditQuickTrain"

# ── Search ───────────────────────────────────────────────────────────────────
ELIXIR_COLLECTOR_FILL = "imgxml/deadbase/Collectors/Elixir"
ELIXIR_COLLECTOR_LVL = "imgxml/deadbase/Collectors/ElixirLevel"
WEAK_BASE_BUILDINGS = "imgxml/Attack/WeakBase"
WEAK_BASE_EAGLE = "imgxml/Attack/WeakBaseEagle"
SEARCH_DRILL = "imgxml/Attack/SearchDrill"
EASY_BUILDINGS = "imgxml/Attack/EasyBuildings"

# ── Attack ───────────────────────────────────────────────────────────────────
ATTACK_BAR = "imgxml/ArmyOverview/AttackBar"
QUEEN_BAR = "imgxml/ArmyOverview/QueenBar"
KING_BAR = "imgxml/ArmyOverview/KingBar"
PRINCE_BAR = "imgxml/ArmyOverview/PrinceBar"
WARDEN_BAR = "imgxml/ArmyOverview/WardenBar"
CHAMPION_BAR = "imgxml/ArmyOverview/ChampionBar"
DRAGON_DUKE_BAR = "imgxml/ArmyOverview/DragonDukeBar"

# ── Auto Upgrade ─────────────────────────────────────────────────────────────
AUTO_UPGRADE_OBSTACLES = "imgxml/village/AutoUpgrade/Obstacles"
AUTO_UPGRADE_ZERO = "imgxml/village/AutoUpgrade/Zero"
AUTO_UPGRADE_RESOURCES = "imgxml/village/AutoUpgrade/Resources"
RESOURCE_ICON = "imgxml/village/AutoUpgrade/ResourceIcon"
WALL_RESOURCE = "imgxml/village/AutoUpgrade/WallResource"
AUTO_UPGRADE_HEROES = "imgxml/village/AutoUpgrade/Heroes"

# ── Switch Account ───────────────────────────────────────────────────────────
LOGIN_WITH_SUPERCELL_ID = "imgxml/SwitchAccounts/LoginSCID"
SUPERCELL_ID_CONNECTED = "imgxml/SwitchAccounts/Connected"
SUPERCELL_ID_WINDOWS = "imgxml/SwitchAccounts/Windows"
SUPERCELL_ID_SLOTS = "imgxml/SwitchAccounts/Slots"

# ── Clan Games ───────────────────────────────────────────────────────────────
CARAVAN = "imgxml/Resources/ClanGames/Caravan"
CG_START = "imgxml/Resources/ClanGames/Start"
CG_REWARD = "imgxml/Resources/ClanGames/Reward"
CG_WINDOW = "imgxml/Resources/ClanGames/Window"
CG_GAME_COMPLETE = "imgxml/Resources/ClanGames/GameComplete"

# ── Daily Challenge ──────────────────────────────────────────────────────────
DAILY_CHALLENGE_OKAY = "imgxml/village/DailyChallenge/Okay"
MINI_CUP_BUTTON = "imgxml/village/DailyChallenge/MiniCup"
