"""Tests for BotState dataclass defaults."""

from mybot.enums import BotAction, Hero, LootType, Spell, Troop
from mybot.state import BotState


def test_default_state(bot_state: BotState):
    assert bot_state.running is False
    assert bot_state.restart_requested is False
    assert bot_state.action == BotAction.NO_ACTION
    assert bot_state.paused is False
    assert bot_state.first_start is True
    assert bot_state.gui_mode == 1


def test_village_defaults(bot_state: BotState):
    assert len(bot_state.village.current_loot) == LootType.COUNT
    assert all(v == 0 for v in bot_state.village.current_loot)
    assert len(bot_state.village.full_storage) == LootType.COUNT
    assert all(v is False for v in bot_state.village.full_storage)


def test_army_defaults(bot_state: BotState):
    assert bot_state.army.is_full is False
    assert len(bot_state.army.custom_troops) == Troop.COUNT
    assert len(bot_state.army.custom_spells) == Spell.COUNT
    assert len(bot_state.army.hero_available) == Hero.COUNT


def test_debug_defaults(bot_state: BotState):
    assert bot_state.debug.set_log is False
    assert bot_state.debug.ocr is False
    assert bot_state.debug.red_area is False


def test_screen_defaults(bot_state: BotState):
    assert bot_state.screen.game_width == 860
    assert bot_state.screen.game_height == 732
    assert bot_state.screen.mid_offset_y == 30
    assert bot_state.screen.bottom_offset_y == 60


def test_stop_event(bot_state: BotState):
    assert not bot_state.stop_event.is_set()
    bot_state.stop_event.set()
    assert bot_state.stop_event.is_set()
