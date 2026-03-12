"""Tests for enum definitions matching AutoIt values."""

from mybot.enums import (
    ArmyIndex,
    BotAction,
    DropOrder,
    Hero,
    HeroFlag,
    League,
    LootType,
    MatchMode,
    Siege,
    Spell,
    Troop,
)


def test_troop_count():
    assert Troop.COUNT == 54


def test_spell_count():
    assert Spell.COUNT == 17


def test_siege_count():
    assert Siege.COUNT == 8


def test_hero_count():
    assert Hero.COUNT == 6


def test_loot_count():
    assert LootType.COUNT == 4


def test_league_count():
    assert League.COUNT == 9


def test_match_modes():
    assert MatchMode.DEAD_BASE == 0
    assert MatchMode.LIVE_BASE == 1
    assert MatchMode.BULLY == 2
    assert MatchMode.DROP_TROPHY == 3


def test_bot_actions():
    assert BotAction.NO_ACTION == 0
    assert BotAction.START == 1
    assert BotAction.STOP == 2
    assert BotAction.SEARCH_MODE == 3
    assert BotAction.CLOSE == 4


def test_army_index_heroes():
    assert ArmyIndex.KING == 54
    assert ArmyIndex.QUEEN == 55
    assert ArmyIndex.PRINCE == 56
    assert ArmyIndex.WARDEN == 57
    assert ArmyIndex.CHAMPION == 58
    assert ArmyIndex.DRAGON_DUKE == 59


def test_army_index_castle():
    assert ArmyIndex.CASTLE == 60


def test_army_index_spells_start():
    assert ArmyIndex.L_SPELL == 61


def test_army_index_siege_start():
    assert ArmyIndex.WALL_W == 78


def test_army_count():
    assert ArmyIndex.ARMY_COUNT == 86


def test_hero_flags():
    assert HeroFlag.NONE == 0
    assert HeroFlag.KING == 1
    assert HeroFlag.QUEEN == 2
    assert HeroFlag.PRINCE == 4
    assert HeroFlag.WARDEN == 8
    assert HeroFlag.CHAMPION == 16
    assert HeroFlag.DRAGON_DUKE == 32


def test_hero_flag_combinations():
    combo = HeroFlag.KING | HeroFlag.QUEEN
    assert combo == 3
    assert HeroFlag.KING in combo
    assert HeroFlag.QUEEN in combo
    assert HeroFlag.WARDEN not in combo


def test_drop_order_count():
    assert DropOrder.COUNT == 56
    assert DropOrder.HEROES == 54
    assert DropOrder.CLAN_CASTLE == 55


def test_troop_values():
    """Verify key troop values match AutoIt enum values."""
    assert Troop.BARBARIAN == 0
    assert Troop.ARCHER == 2
    assert Troop.GIANT == 4
    assert Troop.GOBLIN == 6
    assert Troop.PEKKA == 17
    assert Troop.ELECTRO_DRAGON == 22
    assert Troop.HOG_RIDER == 32
    assert Troop.GOLEM == 36
    assert Troop.LAVA_HOUND == 39
    assert Troop.BOWLER == 41
    assert Troop.FURNACE == 53


def test_spell_values():
    assert Spell.LIGHTNING == 0
    assert Spell.RAGE == 2
    assert Spell.FREEZE == 4
    assert Spell.POISON == 10
    assert Spell.BAT == 14


def test_siege_values():
    assert Siege.WALL_WRECKER == 0
    assert Siege.BATTLE_BLIMP == 1
    assert Siege.STONE_SLAMMER == 2
    assert Siege.LOG_LAUNCHER == 4
    assert Siege.TROOP_LAUNCHER == 7
