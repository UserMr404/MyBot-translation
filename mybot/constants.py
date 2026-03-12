"""Game constants translated from MBR Global Variables.au3 and Config files."""

# ── Game Dimensions ──────────────────────────────────────────────────────────

GAME_WIDTH = 860
GAME_HEIGHT = 732
DEFAULT_WIDTH = 860
DEFAULT_HEIGHT = 780
MID_OFFSET_Y = (DEFAULT_HEIGHT - 720) // 2  # 30
BOTTOM_OFFSET_Y = DEFAULT_HEIGHT - 720  # 60

# ── Attack Constants ─────────────────────────────────────────────────────────

MODE_COUNT = 3  # Dead, Live, Bully
COLLECT_AT_COUNT = 10  # Run Collect() after this many search attempts
UPGRADE_SLOTS = 14  # Max building upgrade slots
BB_TROOP_COUNT = 13  # Builder Base troop count
CUSTOM_DONATE_CONFIGS = 2  # Custom donate configs (A & B)
SUPER_TROOPS_COUNT = 17
MAX_SUPERS_TROOP = 2

# ── Log Colors (Win32 COLORREF format: 0xBBGGRR) ────────────────────────────

COLOR_BLACK = 0x000000
COLOR_WHITE = 0xFFFFFF
COLOR_RED = 0x0000FF
COLOR_BLUE = 0xFF0000
COLOR_GREEN = 0x008000
COLOR_PURPLE = 0x800080
COLOR_MAROON = 0x000080
COLOR_GRAY = 0x808080
COLOR_OLIVE = 0x008080

COLOR_ERROR = COLOR_RED
COLOR_WARNING = COLOR_MAROON
COLOR_INFO = COLOR_BLUE
COLOR_SUCCESS = 0x006600
COLOR_SUCCESS1 = 0x009900
COLOR_DEBUG = COLOR_PURPLE
COLOR_DEBUG1 = 0x7A00CC
COLOR_DEBUG2 = 0xAA80FF
COLOR_DEBUGS = COLOR_GRAY
COLOR_ACTION = 0xFF8000
COLOR_ACTION1 = 0xCC80FF

# ── Troop Names ──────────────────────────────────────────────────────────────

TROOP_NAMES: list[str] = [
    "Barbarian", "Super Barbarian", "Archer", "Super Archer",
    "Giant", "Super Giant", "Goblin", "Sneaky Goblin",
    "Wall Breaker", "Super Wall Breaker", "Balloon", "Rocket Balloon",
    "Wizard", "Super Wizard", "Healer", "Dragon",
    "Super Dragon", "P.E.K.K.A", "Baby Dragon", "Inferno Dragon",
    "Miner", "Super Miner", "Electro Dragon", "Yeti",
    "Dragon Rider", "Electro Titan", "Root Rider", "Thrower",
    "Ice Minion", "Meteor Golem", "Minion", "Super Minion",
    "Hog Rider", "Super Hog Rider", "Valkyrie", "Super Valkyrie",
    "Golem", "Witch", "Super Witch", "Lava Hound",
    "Ice Hound", "Bowler", "Super Bowler", "Ice Golem",
    "Headhunter", "Apprentice Warden", "Druid", "Super Yeti",
    "Ice Wizard", "Giant Giant", "Azure Dragon", "Firecracker",
    "Ram Rider", "Furnace",
]

TROOP_SHORT_NAMES: list[str] = [
    "Barb", "SBarb", "Arch", "SArch", "Giant", "SGiant",
    "Gobl", "SGobl", "Wall", "SWall", "Ball", "RBall",
    "Wiza", "SWiza", "Heal", "Drag", "SDrag", "Pekk",
    "BabyD", "InfernoD", "Mine", "SMine", "EDrag", "Yeti",
    "RDrag", "ETitan", "RootR", "Thrower", "IceMini", "MeteorG",
    "Mini", "SMini", "Hogs", "SHogs", "Valk", "SValk",
    "Gole", "Witc", "SWitc", "Lava", "IceH", "Bowl",
    "SBowl", "IceG", "Hunt", "AppWard", "Druid", "SYeti",
    "IceWiz", "GGiant", "AzureDragon", "Firecracker",
    "RamRider", "Furn",
]

TROOP_SPACE: list[int] = [
    1, 5, 1, 12, 5, 10, 1, 3, 2, 8, 5, 8,
    4, 10, 14, 20, 40, 25, 10, 15, 6, 24, 30, 18,
    25, 32, 20, 8, 8, 16, 2, 12, 5, 12, 8, 20,
    30, 12, 40, 30, 40, 6, 30, 15, 6, 20, 16, 36,
    4, 10, 30, 6, 10, 15,
]

# ── Spell Names ──────────────────────────────────────────────────────────────

SPELL_NAMES: list[str] = [
    "Lightning", "Heal", "Rage", "Jump", "Freeze", "Clone",
    "Invisibility", "Recall", "Revive", "Totem",
    "Poison", "Earthquake", "Haste", "Skeleton", "Bat",
    "Overgrowth", "IB Spell",
]

SPELL_SHORT_NAMES: list[str] = [
    "LSpell", "HSpell", "RSpell", "JSpell", "FSpell", "CSpell",
    "ISpell", "ReSpell", "RvSpell", "TSpell",
    "PSpell", "ESpell", "HaSpell", "SkSpell", "BtSpell",
    "OgSpell", "IBSpell",
]

SPELL_SPACE: list[int] = [
    1, 2, 2, 2, 1, 3, 1, 2, 4, 1,
    1, 1, 1, 1, 1, 2, 1,
]

# ── Siege Machine Names ──────────────────────────────────────────────────────

SIEGE_NAMES: list[str] = [
    "Wall Wrecker", "Battle Blimp", "Stone Slammer", "Siege Barracks",
    "Log Launcher", "Flame Flinger", "Battle Drill", "Troop Launcher",
]

SIEGE_SHORT_NAMES: list[str] = [
    "WallW", "BattleB", "StoneS", "SiegeB",
    "LogL", "FlameF", "BattleD", "TroopL",
]

# ── Hero Names ───────────────────────────────────────────────────────────────

HERO_NAMES: list[str] = [
    "Barbarian King", "Archer Queen", "Minion Prince",
    "Grand Warden", "Royal Champion", "Dragon Duke",
]

HERO_SHORT_NAMES: list[str] = [
    "King", "Queen", "Prince", "Warden", "Champion", "DragonDuke",
]
