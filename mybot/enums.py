"""All enum types translated from MBR Global Variables.au3."""

from enum import IntEnum, IntFlag

# ── Troop Types (army bar index) ──────────────────────────────────────────────
# Maps to $eBarb..$eTroopL in AutoIt. These are the combined army bar indices
# used for attack bar slot identification.

class ArmyIndex(IntEnum):
    """Combined army bar index (troops + heroes + spells + sieges)."""
    BARB = 0
    S_BARB = 1
    ARCH = 2
    S_ARCH = 3
    GIANT = 4
    S_GIANT = 5
    GOBL = 6
    S_GOBL = 7
    WALL = 8
    S_WALL = 9
    BALL = 10
    R_BALL = 11
    WIZA = 12
    S_WIZA = 13
    HEAL = 14
    DRAG = 15
    S_DRAG = 16
    PEKK = 17
    BABY_D = 18
    INFERNO_D = 19
    MINE = 20
    S_MINE = 21
    E_DRAG = 22
    YETI = 23
    R_DRAG = 24
    E_TITAN = 25
    ROOT_R = 26
    THROWER = 27
    ICE_MINI = 28
    METEOR_G = 29
    MINI = 30
    S_MINI = 31
    HOGS = 32
    S_HOGS = 33
    VALK = 34
    S_VALK = 35
    GOLE = 36
    WITC = 37
    S_WITC = 38
    LAVA = 39
    ICE_H = 40
    BOWL = 41
    S_BOWL = 42
    ICE_G = 43
    HUNT = 44
    APP_WARD = 45
    DRUID = 46
    S_YETI = 47
    ICE_WIZ = 48
    G_GIANT = 49
    AZURE_DRAGON = 50
    FIRECRACKER = 51
    RAM_RIDER = 52
    FURN = 53
    # Heroes
    KING = 54
    QUEEN = 55
    PRINCE = 56
    WARDEN = 57
    CHAMPION = 58
    DRAGON_DUKE = 59
    # Clan Castle
    CASTLE = 60
    # Spells
    L_SPELL = 61
    H_SPELL = 62
    R_SPELL = 63
    J_SPELL = 64
    F_SPELL = 65
    C_SPELL = 66
    I_SPELL = 67
    RE_SPELL = 68
    RV_SPELL = 69
    T_SPELL = 70
    P_SPELL = 71
    E_SPELL = 72
    HA_SPELL = 73
    SK_SPELL = 74
    BT_SPELL = 75
    OG_SPELL = 76
    IB_SPELL = 77
    # Siege machines
    WALL_W = 78
    BATTLE_B = 79
    STONE_S = 80
    SIEGE_B = 81
    LOG_L = 82
    FLAME_F = 83
    BATTLE_D = 84
    TROOP_L = 85
    ARMY_COUNT = 86


# ── Troop Enums ───────────────────────────────────────────────────────────────

class Troop(IntEnum):
    """Troop types ($eTroopBarbarian .. $eTroopFurnace)."""
    BARBARIAN = 0
    SUPER_BARBARIAN = 1
    ARCHER = 2
    SUPER_ARCHER = 3
    GIANT = 4
    SUPER_GIANT = 5
    GOBLIN = 6
    SNEAKY_GOBLIN = 7
    WALL_BREAKER = 8
    SUPER_WALL_BREAKER = 9
    BALLOON = 10
    ROCKET_BALLOON = 11
    WIZARD = 12
    SUPER_WIZARD = 13
    HEALER = 14
    DRAGON = 15
    SUPER_DRAGON = 16
    PEKKA = 17
    BABY_DRAGON = 18
    INFERNO_DRAGON = 19
    MINER = 20
    SUPER_MINER = 21
    ELECTRO_DRAGON = 22
    YETI = 23
    DRAGON_RIDER = 24
    ELECTRO_TITAN = 25
    ROOT_RIDER = 26
    THROWER = 27
    ICE_MINION = 28
    METEOR_GOLEM = 29
    MINION = 30
    SUPER_MINION = 31
    HOG_RIDER = 32
    SUPER_HOG_RIDER = 33
    VALKYRIE = 34
    SUPER_VALKYRIE = 35
    GOLEM = 36
    WITCH = 37
    SUPER_WITCH = 38
    LAVA_HOUND = 39
    ICE_HOUND = 40
    BOWLER = 41
    SUPER_BOWLER = 42
    ICE_GOLEM = 43
    HEADHUNTER = 44
    APPRENTICE_WARDEN = 45
    DRUID = 46
    SUPER_YETI = 47
    ICE_WIZARD = 48
    G_GIANT = 49
    AZURE_DRAGON = 50
    FIRECRACKER = 51
    RAM_RIDER = 52
    FURNACE = 53
    COUNT = 54


# ── Spell Enums ───────────────────────────────────────────────────────────────

class Spell(IntEnum):
    """Spell types ($eSpellLightning .. $eSpellIBSpell)."""
    LIGHTNING = 0
    HEAL = 1
    RAGE = 2
    JUMP = 3
    FREEZE = 4
    CLONE = 5
    INVISIBILITY = 6
    RECALL = 7
    REVIVE = 8
    TOTEM = 9
    POISON = 10
    EARTHQUAKE = 11
    HASTE = 12
    SKELETON = 13
    BAT = 14
    OVERGROWTH = 15
    IB_SPELL = 16
    COUNT = 17


# ── Siege Machine Enums ──────────────────────────────────────────────────────

class Siege(IntEnum):
    """Siege machine types ($eSiegeWallWrecker .. $eSiegeTroopLauncher)."""
    WALL_WRECKER = 0
    BATTLE_BLIMP = 1
    STONE_SLAMMER = 2
    SIEGE_BARRACKS = 3
    LOG_LAUNCHER = 4
    FLAME_FLINGER = 5
    BATTLE_DRILL = 6
    TROOP_LAUNCHER = 7
    COUNT = 8


# ── Hero Enums ────────────────────────────────────────────────────────────────

class Hero(IntEnum):
    """Hero index types ($eHeroBarbarianKing .. $eHeroDragonDukeIndex)."""
    BARBARIAN_KING = 0
    ARCHER_QUEEN = 1
    MINION_PRINCE = 2
    GRAND_WARDEN = 3
    ROYAL_CHAMPION = 4
    DRAGON_DUKE = 5
    COUNT = 6


class HeroFlag(IntFlag):
    """Hero bitmask flags for deployment ($eHeroNone .. $eHeroDragonDuke)."""
    NONE = 0
    KING = 1
    QUEEN = 2
    PRINCE = 4
    WARDEN = 8
    CHAMPION = 16
    DRAGON_DUKE = 32


# ── Loot Type Enums ──────────────────────────────────────────────────────────

class LootType(IntEnum):
    """Resource/loot types ($eLootGold .. $eLootTrophy)."""
    GOLD = 0
    ELIXIR = 1
    DARK_ELIXIR = 2
    TROPHY = 3
    COUNT = 4


class LootTypeBB(IntEnum):
    """Builder Base loot types."""
    GOLD = 0
    ELIXIR = 1
    TROPHY = 2
    COUNT = 3


# ── League Enums ─────────────────────────────────────────────────────────────

class League(IntEnum):
    """Home village leagues ($eLeagueUnranked .. $eLeagueLegend)."""
    UNRANKED = 0
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    CRYSTAL = 4
    MASTER = 5
    CHAMPION = 6
    TITAN = 7
    LEGEND = 8
    COUNT = 9


class BBLeague(IntEnum):
    """Builder Base leagues."""
    UNRANKED = 0
    WOOD = 1
    CLAY = 2
    STONE = 3
    COPPER = 4
    BRASS = 5
    IRON = 6
    STEEL = 7
    TITANIUM = 8
    PLATINUM = 9
    EMERALD = 10
    RUBY = 11
    DIAMOND = 12
    COUNT = 13


# ── Attack Mode Enums ────────────────────────────────────────────────────────

class MatchMode(IntEnum):
    """Attack match modes ($DB, $LB, $TB, $DT)."""
    DEAD_BASE = 0
    LIVE_BASE = 1
    BULLY = 2
    DROP_TROPHY = 3


# ── Bot Action Enums ─────────────────────────────────────────────────────────

class BotAction(IntEnum):
    """Bot action states ($eBotNoAction .. $eBotClose)."""
    NO_ACTION = 0
    START = 1
    STOP = 2
    SEARCH_MODE = 3
    CLOSE = 4


# ── Red Line / Drop Line Enums ──────────────────────────────────────────────

class RedLineMode(IntEnum):
    """Red line detection modes."""
    IMGLOC_RAW = 0
    IMGLOC = 1
    ORIGINAL = 2
    NONE = 3


class DropLineMode(IntEnum):
    """Drop line calculation modes."""
    EDGE_FIXED = 0
    EDGE_FIRST = 1
    FULL_EDGE_FIXED = 2
    FULL_EDGE_FIRST = 3
    DROPPOINTS_ONLY = 4


# ── Drop Order Enums ─────────────────────────────────────────────────────────

class DropOrder(IntEnum):
    """Troop drop order indices (includes troops + heroes + CC)."""
    BARBARIAN = 0
    SUPER_BARBARIAN = 1
    ARCHER = 2
    SUPER_ARCHER = 3
    GIANT = 4
    SUPER_GIANT = 5
    GOBLIN = 6
    SNEAKY_GOBLIN = 7
    WALL_BREAKER = 8
    SUPER_WALL_BREAKER = 9
    BALLOON = 10
    ROCKET_BALLOON = 11
    WIZARD = 12
    SUPER_WIZARD = 13
    HEALER = 14
    DRAGON = 15
    SUPER_DRAGON = 16
    PEKKA = 17
    BABY_DRAGON = 18
    INFERNO_DRAGON = 19
    MINER = 20
    SUPER_MINER = 21
    ELECTRO_DRAGON = 22
    YETI = 23
    DRAGON_RIDER = 24
    ELECTRO_TITAN = 25
    ROOT_RIDER = 26
    THROWER = 27
    ICE_MINION = 28
    METEOR_GOLEM = 29
    MINION = 30
    SUPER_MINION = 31
    HOG_RIDER = 32
    SUPER_HOG_RIDER = 33
    VALKYRIE = 34
    SUPER_VALKYRIE = 35
    GOLEM = 36
    WITCH = 37
    SUPER_WITCH = 38
    LAVA_HOUND = 39
    ICE_HOUND = 40
    BOWLER = 41
    SUPER_BOWLER = 42
    ICE_GOLEM = 43
    HEADHUNTER = 44
    APPRENTICE_WARDEN = 45
    DRUID = 46
    SUPER_YETI = 47
    ICE_WIZARD = 48
    G_GIANT = 49
    AZURE_DRAGON = 50
    FIRECRACKER = 51
    RAM_RIDER = 52
    FURNACE = 53
    HEROES = 54
    CLAN_CASTLE = 55
    COUNT = 56
