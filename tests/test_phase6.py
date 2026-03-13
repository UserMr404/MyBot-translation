"""Tests for Phase 6: GUI & Application Shell."""

from __future__ import annotations

import json
import threading
import time
import unittest
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

# ── App & Bot Tests ──────────────────────────────────────────────────────────


class TestParseArgs(unittest.TestCase):
    def test_defaults(self):
        from mybot.app import parse_args
        args = parse_args([])
        self.assertFalse(args.autostart)
        self.assertFalse(args.nogui)
        self.assertFalse(args.debug)
        self.assertIsNone(args.profile)

    def test_autostart(self):
        from mybot.app import parse_args
        args = parse_args(["--autostart"])
        self.assertTrue(args.autostart)

    def test_nogui(self):
        from mybot.app import parse_args
        args = parse_args(["--nogui"])
        self.assertTrue(args.nogui)

    def test_profile(self):
        from mybot.app import parse_args
        args = parse_args(["--profile", "TestVillage"])
        self.assertEqual(args.profile, "TestVillage")

    def test_debug(self):
        from mybot.app import parse_args
        args = parse_args(["--debug"])
        self.assertTrue(args.debug)

    def test_combined(self):
        from mybot.app import parse_args
        args = parse_args(["--autostart", "--nogui", "--debug", "--profile", "X"])
        self.assertTrue(args.autostart)
        self.assertTrue(args.nogui)
        self.assertTrue(args.debug)
        self.assertEqual(args.profile, "X")


class TestApp(unittest.TestCase):
    def test_init_default(self):
        from mybot.app import App, parse_args
        args = parse_args(["--nogui"])
        app = App(args)
        self.assertIsNotNone(app.state)
        self.assertEqual(app.state.gui_mode, 0)

    def test_init_with_profile(self):
        from mybot.app import App, parse_args
        args = parse_args(["--nogui", "--profile", "TestProfile123"])
        app = App(args)
        self.assertEqual(app.state.account.profile_name, "TestProfile123")

    def test_init_debug(self):
        from mybot.app import App, parse_args
        args = parse_args(["--nogui", "--debug"])
        app = App(args)
        self.assertTrue(app.state.debug.set_log)


class TestBot(unittest.TestCase):
    def test_init(self):
        from mybot.bot import Bot
        from mybot.state import BotState
        bot = Bot(BotState())
        self.assertFalse(bot.is_running)
        self.assertEqual(bot.attack_count, 0)

    def test_stop(self):
        from mybot.bot import Bot
        from mybot.state import BotState
        from mybot.enums import BotAction
        state = BotState()
        bot = Bot(state)
        bot.stop()
        self.assertTrue(state.stop_event.is_set())
        self.assertEqual(state.action, BotAction.STOP)

    def test_is_stopped(self):
        from mybot.bot import Bot
        from mybot.state import BotState
        state = BotState()
        bot = Bot(state)
        self.assertFalse(bot._is_stopped())
        state.stop_event.set()
        self.assertTrue(bot._is_stopped())

    def test_first_check(self):
        from mybot.bot import Bot
        from mybot.state import BotState
        state = BotState()
        bot = Bot(state)
        self.assertEqual(state.first_run, 1)
        bot.first_check()
        self.assertEqual(state.first_run, 0)


# ── GUI Widget Tests (headless — no display needed) ─────────────────────────


class TestGUIImports(unittest.TestCase):
    """Test that all GUI modules can be imported."""

    def test_main_window_import(self):
        from mybot.gui.main_window import MainWindow
        self.assertTrue(callable(MainWindow))

    def test_log_widget_import(self):
        from mybot.gui.log_widget import LogWidget, LogHandler
        self.assertTrue(callable(LogWidget))
        self.assertTrue(callable(LogHandler))

    def test_bottom_bar_import(self):
        from mybot.gui.bottom_bar import BottomBar
        self.assertTrue(callable(BottomBar))

    def test_splash_import(self):
        from mybot.gui.splash import SplashScreen
        self.assertTrue(callable(SplashScreen))

    def test_village_tab_import(self):
        from mybot.gui.tabs.village import (
            donate, misc, upgrade, notify, achievements,
        )

    def test_attack_tab_import(self):
        from mybot.gui.tabs.attack import deadbase, livebase, troops, options

    def test_bot_tab_import(self):
        from mybot.gui.tabs.bot import android, debug, options, profiles, stats

    def test_about_tab_import(self):
        from mybot.gui.tabs.about import AboutTab
        self.assertTrue(callable(AboutTab))


class TestLogWidgetHelpers(unittest.TestCase):
    def test_escape_html(self):
        from mybot.gui.log_widget import _escape_html
        self.assertEqual(_escape_html("<b>test</b>"), "&lt;b&gt;test&lt;/b&gt;")
        self.assertEqual(_escape_html("a & b"), "a &amp; b")
        self.assertEqual(_escape_html("normal"), "normal")

    def test_level_colors_defined(self):
        from mybot.gui.log_widget import _LEVEL_COLORS
        self.assertIn("ERROR", _LEVEL_COLORS)
        self.assertIn("INFO", _LEVEL_COLORS)
        self.assertIn("DEBUG", _LEVEL_COLORS)


# ── Handler Tests ───────────────────────────────────────────────────────────


class TestArmyHandler(unittest.TestCase):
    def test_calculate_total_space(self):
        from mybot.gui.handlers.army import calculate_total_space
        troops = {0: 10, 4: 5}  # 10 Barbs (1 space) + 5 Giants (5 space)
        self.assertEqual(calculate_total_space(troops), 35)

    def test_calculate_spell_space(self):
        from mybot.gui.handlers.army import calculate_spell_space
        spells = {0: 2, 2: 1}  # 2 Lightning (1) + 1 Rage (2)
        self.assertEqual(calculate_spell_space(spells), 4)

    def test_validate_army_ok(self):
        from mybot.gui.handlers.army import validate_army_composition
        errors = validate_army_composition({0: 200}, 200)
        self.assertEqual(len(errors), 0)

    def test_validate_army_over(self):
        from mybot.gui.handlers.army import validate_army_composition
        errors = validate_army_composition({0: 300}, 200)
        self.assertGreater(len(errors), 0)

    def test_validate_army_empty(self):
        from mybot.gui.handlers.army import validate_army_composition
        errors = validate_army_composition({}, 200)
        self.assertGreater(len(errors), 0)

    def test_apply_army_config(self):
        from mybot.gui.handlers.army import apply_army_config
        from mybot.state import BotState
        state = BotState()
        apply_army_config(state, {0: 50, 2: 100}, {0: 5}, {0: 1})
        self.assertEqual(state.army.custom_troops[0], 50)
        self.assertEqual(state.army.custom_troops[2], 100)
        self.assertEqual(state.army.custom_spells[0], 5)
        self.assertEqual(state.army.custom_sieges[0], 1)


class TestSearchHandler(unittest.TestCase):
    def test_defaults(self):
        from mybot.gui.handlers.search import SearchSettings
        settings = SearchSettings()
        self.assertTrue(settings.enabled)
        self.assertEqual(settings.min_gold, 80_000)

    def test_validate_high_threshold(self):
        from mybot.gui.handlers.search import SearchSettings, validate_search_settings
        settings = SearchSettings(min_gold=2_000_000)
        warnings = validate_search_settings(settings)
        self.assertGreater(len(warnings), 0)

    def test_validate_ok(self):
        from mybot.gui.handlers.search import SearchSettings, validate_search_settings
        settings = SearchSettings()
        warnings = validate_search_settings(settings)
        self.assertEqual(len(warnings), 0)


class TestDropOrderHandler(unittest.TestCase):
    def test_get_default_order(self):
        from mybot.gui.handlers.drop_order import get_default_drop_order
        order = get_default_drop_order()
        self.assertGreater(len(order), 10)

    def test_validate_order(self):
        from mybot.gui.handlers.drop_order import validate_drop_order
        self.assertTrue(validate_drop_order([0, 1, 2, 3]))
        self.assertFalse(validate_drop_order([0, 0, 1]))  # duplicate

    def test_move_up(self):
        from mybot.gui.handlers.drop_order import move_troop_up
        order = [10, 20, 30]
        result = move_troop_up(order, 1)
        self.assertEqual(result, [20, 10, 30])

    def test_move_down(self):
        from mybot.gui.handlers.drop_order import move_troop_down
        order = [10, 20, 30]
        result = move_troop_down(order, 0)
        self.assertEqual(result, [20, 10, 30])

    def test_move_boundary(self):
        from mybot.gui.handlers.drop_order import move_troop_up, move_troop_down
        order = [10, 20, 30]
        self.assertEqual(move_troop_up(order, 0), order)
        self.assertEqual(move_troop_down(order, 2), order)


class TestDonateHandler(unittest.TestCase):
    def test_donate_config_defaults(self):
        from mybot.gui.handlers.donate import DonateConfig
        config = DonateConfig()
        self.assertTrue(config.enabled)
        self.assertFalse(config.donate_all)
        self.assertEqual(len(config.troop_slots), 3)
        self.assertEqual(len(config.spell_slots), 2)


# ── API Server Tests ────────────────────────────────────────────────────────


class TestAPIServer(unittest.TestCase):
    def test_server_init(self):
        from mybot.api.server import APIServer
        from mybot.state import BotState
        server = APIServer(BotState(), port=0)
        self.assertFalse(server.is_running)

    def test_server_start_stop(self):
        from mybot.api.server import APIServer
        from mybot.state import BotState
        state = BotState()
        state.account.profile_name = "TestProfile"
        server = APIServer(state, port=0)

        # Use port 0 to let OS assign free port
        server._server = None
        from mybot.api.server import BotHTTPServer
        http_server = BotHTTPServer(("127.0.0.1", 0), state)
        actual_port = http_server.server_address[1]
        http_server.server_close()
        self.assertGreater(actual_port, 0)

    def test_handler_health(self):
        from mybot.api.server import APIServer, BotHTTPServer
        from mybot.state import BotState
        import urllib.request

        state = BotState()
        http_server = BotHTTPServer(("127.0.0.1", 0), state)
        port = http_server.server_address[1]
        thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        thread.start()

        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/health")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                self.assertEqual(data["status"], "ok")
        finally:
            http_server.shutdown()

    def test_handler_status(self):
        from mybot.api.server import BotHTTPServer
        from mybot.state import BotState
        import urllib.request

        state = BotState()
        state.account.profile_name = "TestProfile"
        http_server = BotHTTPServer(("127.0.0.1", 0), state)
        port = http_server.server_address[1]
        thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        thread.start()

        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/status")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                self.assertFalse(data["running"])
                self.assertEqual(data["profile"], "TestProfile")
        finally:
            http_server.shutdown()

    def test_handler_village(self):
        from mybot.api.server import BotHTTPServer
        from mybot.state import BotState
        import urllib.request

        state = BotState()
        state.village.current_loot[0] = 500_000
        state.village.town_hall_level = 12
        http_server = BotHTTPServer(("127.0.0.1", 0), state)
        port = http_server.server_address[1]
        thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        thread.start()

        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/village")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                self.assertEqual(data["gold"], 500_000)
                self.assertEqual(data["town_hall"], 12)
        finally:
            http_server.shutdown()

    def test_handler_not_found(self):
        from mybot.api.server import BotHTTPServer
        from mybot.state import BotState
        import urllib.request
        import urllib.error

        state = BotState()
        http_server = BotHTTPServer(("127.0.0.1", 0), state)
        port = http_server.server_address[1]
        thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        thread.start()

        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/nonexistent")
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(req, timeout=2)
            self.assertEqual(ctx.exception.code, 404)
        finally:
            http_server.shutdown()


class TestAPIClient(unittest.TestCase):
    def test_client_init(self):
        from mybot.api.client import BotAPIClient
        client = BotAPIClient("http://localhost:9999")
        self.assertEqual(client.base_url, "http://localhost:9999")

    def test_client_unreachable(self):
        from mybot.api.client import BotAPIClient
        client = BotAPIClient("http://127.0.0.1:1", timeout=0.5)
        self.assertFalse(client.is_reachable())

    def test_client_health_error(self):
        from mybot.api.client import BotAPIClient
        client = BotAPIClient("http://127.0.0.1:1", timeout=0.5)
        result = client.health()
        self.assertIn("error", result)


# ── Watchdog Tests ──────────────────────────────────────────────────────────


class TestWatchdog(unittest.TestCase):
    def test_init(self):
        from mybot.watchdog import Watchdog
        wd = Watchdog(max_restarts=3)
        self.assertEqual(wd.max_restarts, 3)
        self.assertEqual(wd.restart_count, 0)
        self.assertFalse(wd.is_running)

    def test_stop_no_process(self):
        from mybot.watchdog import Watchdog
        wd = Watchdog()
        wd.stop()  # Should not raise
        self.assertFalse(wd.is_running)


# ── Multi-Bot Tests ─────────────────────────────────────────────────────────


class TestMultiBot(unittest.TestCase):
    def test_init(self):
        from mybot.multi_bot import MultiBotManager
        mgr = MultiBotManager()
        self.assertEqual(mgr.running_count, 0)

    def test_status_empty(self):
        from mybot.multi_bot import MultiBotManager
        mgr = MultiBotManager()
        self.assertEqual(mgr.get_status(), {})

    def test_bot_instance(self):
        from mybot.multi_bot import BotInstance
        inst = BotInstance(profile_name="Test")
        self.assertFalse(inst.is_alive)
        self.assertIsNone(inst.exit_code)


# ── Integration: __main__ ──────────────────────────────────────────────────


class TestMainEntry(unittest.TestCase):
    def test_main_module_import(self):
        from mybot.__main__ import main
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()
