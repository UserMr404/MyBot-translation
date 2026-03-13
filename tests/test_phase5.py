"""Tests for Phase 5: Army Training & Attack Systems."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

import numpy as np


# ── Army Training Tests ──────────────────────────────────────────────────────


class TestTrainConfig(unittest.TestCase):
    def test_defaults(self):
        from mybot.army.train import TrainConfig
        config = TrainConfig()
        self.assertTrue(config.use_quick_train)
        self.assertEqual(config.quick_train_slot, 0)
        self.assertFalse(config.double_train)

    def test_train_result_defaults(self):
        from mybot.army.train import TrainResult
        result = TrainResult()
        self.assertFalse(result.army_full)
        self.assertFalse(result.training_started)


class TestSmartWait(unittest.TestCase):
    def test_parse_time_minutes(self):
        from mybot.army.smart_wait import parse_train_time
        self.assertEqual(parse_train_time("5m 30s"), 330.0)

    def test_parse_time_hours(self):
        from mybot.army.smart_wait import parse_train_time
        self.assertEqual(parse_train_time("1h 20m"), 4800.0)

    def test_parse_time_seconds_only(self):
        from mybot.army.smart_wait import parse_train_time
        self.assertEqual(parse_train_time("45s"), 45.0)

    def test_smart_wait_calculation(self):
        from mybot.army.smart_wait import smart_wait_for_train
        wait = smart_wait_for_train("5m")  # 300s → 240s (80%)
        self.assertAlmostEqual(wait, 240.0)

    def test_smart_wait_clamped(self):
        from mybot.army.smart_wait import smart_wait_for_train
        # Very short time → clamped to min_wait
        wait = smart_wait_for_train("5s", min_wait=30.0)
        self.assertEqual(wait, 30.0)


class TestCheckCamp(unittest.TestCase):
    def test_parse_capacity(self):
        from mybot.army.check_camp import _parse_capacity
        self.assertEqual(_parse_capacity("200/200"), (200, 200))
        self.assertEqual(_parse_capacity("150/200"), (150, 200))
        self.assertEqual(_parse_capacity(""), (0, 0))
        self.assertEqual(_parse_capacity("invalid"), (0, 0))

    def test_camp_status_is_full(self):
        from mybot.army.check_camp import ArmyCampStatus
        status = ArmyCampStatus(current_space=200, total_space=200)
        self.assertTrue(status.is_full)

    def test_camp_status_not_full(self):
        from mybot.army.check_camp import ArmyCampStatus
        status = ArmyCampStatus(current_space=150, total_space=200)
        self.assertFalse(status.is_full)
        self.assertAlmostEqual(status.fill_percent, 75.0)


class TestCCContents(unittest.TestCase):
    def test_cc_capacity_table(self):
        from mybot.army.read_cc import CC_CAPACITY
        self.assertEqual(CC_CAPACITY[1], (10, 0))
        self.assertEqual(CC_CAPACITY[14], (55, 4))

    def test_cc_is_full(self):
        from mybot.army.read_cc import CCContents
        cc = CCContents(troop_space=40, troop_capacity=40)
        self.assertTrue(cc.is_full)

    def test_cc_not_full(self):
        from mybot.army.read_cc import CCContents
        cc = CCContents(troop_space=20, troop_capacity=40)
        self.assertFalse(cc.is_full)


class TestHeroStatus(unittest.TestCase):
    def test_defaults(self):
        from mybot.army.read_heroes import HeroStatus
        status = HeroStatus()
        self.assertFalse(status.available)
        self.assertFalse(status.upgrading)


class TestTrainClick(unittest.TestCase):
    def test_train_click(self):
        from mybot.army.train_click import train_click
        clicks = []
        click_func = lambda x, y: clicks.append((x, y))
        result = train_click(100, 200, 3, click_func, delay=0)
        self.assertEqual(result, 3)
        self.assertEqual(len(clicks), 3)
        self.assertTrue(all(c == (100, 200) for c in clicks))

    def test_train_click_zero(self):
        from mybot.army.train_click import train_click
        clicks = []
        result = train_click(0, 0, 0, lambda x, y: clicks.append((x, y)))
        self.assertEqual(result, 0)
        self.assertEqual(len(clicks), 0)


# ── Attack Bar Tests ─────────────────────────────────────────────────────────


class TestAttackBar(unittest.TestCase):
    def test_bar_defaults(self):
        from mybot.attack.attack_bar import AttackBar
        bar = AttackBar()
        self.assertEqual(len(bar.slots), 0)
        self.assertEqual(bar.total_troops, 0)

    def test_get_slot_by_name(self):
        from mybot.attack.attack_bar import AttackBar, AttackBarSlot
        bar = AttackBar(slots=[
            AttackBarSlot(name="Barb", quantity=50, x=100, y=600),
            AttackBarSlot(name="Arch", quantity=100, x=172, y=600),
        ])
        slot = bar.get_slot_by_name("Arch")
        self.assertIsNotNone(slot)
        self.assertEqual(slot.quantity, 100)

    def test_get_slot_not_found(self):
        from mybot.attack.attack_bar import AttackBar
        bar = AttackBar()
        self.assertIsNone(bar.get_slot_by_name("Barb"))
        self.assertIsNone(bar.get_slot(0))

    def test_slot_index_from_x(self):
        from mybot.attack.attack_bar import get_slot_from_x
        self.assertEqual(get_slot_from_x(30), 0)
        self.assertEqual(get_slot_from_x(102), 1)


# ── Deploy Tests ─────────────────────────────────────────────────────────────


class TestDeploy(unittest.TestCase):
    def test_drop_troop_inside_diamond(self):
        from mybot.attack.deploy import drop_troop
        clicks = []
        deployed = drop_troop(lambda x, y: clicks.append((x, y)), 430, 300, 3, delay=0)
        self.assertEqual(deployed, 3)
        self.assertEqual(len(clicks), 3)

    def test_drop_troop_outside_diamond(self):
        from mybot.attack.deploy import drop_troop
        clicks = []
        deployed = drop_troop(lambda x, y: clicks.append((x, y)), 0, 0, 1, delay=0)
        self.assertEqual(deployed, 0)

    def test_drop_on_edge(self):
        from mybot.attack.deploy import drop_on_edge
        clicks = []
        points = [(430, 300), (500, 350), (400, 280)]
        deployed = drop_on_edge(lambda x, y: clicks.append((x, y)), points, 3, delay=0)
        self.assertEqual(deployed, 3)

    def test_drop_cc(self):
        from mybot.attack.deploy import drop_cc
        clicks = []
        result = drop_cc(lambda x, y: clicks.append((x, y)), 430, 300)
        self.assertTrue(result)
        self.assertEqual(len(clicks), 1)

    def test_drop_cc_outside(self):
        from mybot.attack.deploy import drop_cc
        clicks = []
        result = drop_cc(lambda x, y: clicks.append((x, y)), 0, 0)
        self.assertFalse(result)


# ── Drop Order Tests ─────────────────────────────────────────────────────────


class TestDropOrder(unittest.TestCase):
    def test_default_order_exists(self):
        from mybot.attack.drop_order import DEFAULT_DROP_ORDER
        self.assertGreater(len(DEFAULT_DROP_ORDER), 10)

    def test_get_drop_order_default(self):
        from mybot.attack.drop_order import get_drop_order, DEFAULT_DROP_ORDER
        order = get_drop_order()
        self.assertEqual(order, DEFAULT_DROP_ORDER)

    def test_get_drop_order_custom(self):
        from mybot.attack.drop_order import get_drop_order
        custom = [1, 2, 3]
        self.assertEqual(get_drop_order(custom), custom)

    def test_reorder_bar(self):
        from mybot.attack.attack_bar import AttackBarSlot
        from mybot.attack.drop_order import reorder_attack_bar
        from mybot.enums import DropOrder

        slots = [
            AttackBarSlot(index=DropOrder.ARCHER, name="Arch"),
            AttackBarSlot(index=DropOrder.GOLEM, name="Gole"),
        ]
        ordered = reorder_attack_bar(slots, [DropOrder.GOLEM, DropOrder.ARCHER])
        self.assertEqual(ordered[0].name, "Gole")
        self.assertEqual(ordered[1].name, "Arch")


# ── Timing Tests ─────────────────────────────────────────────────────────────


class TestTiming(unittest.TestCase):
    def test_deploy_delay_range(self):
        from mybot.attack.timing import get_deploy_delay
        for _ in range(100):
            delay = get_deploy_delay()
            self.assertGreaterEqual(delay, 0.030)
            self.assertLessEqual(delay, 0.060)

    def test_wave_delay_positive(self):
        from mybot.attack.timing import get_wave_delay
        delay = get_wave_delay()
        self.assertGreater(delay, 0)


# ── Hero Battle State Tests ─────────────────────────────────────────────────


class TestHeroBattleState(unittest.TestCase):
    def test_initial_state(self):
        from mybot.attack.heroes import HeroBattleState
        from mybot.enums import Hero
        state = HeroBattleState()
        self.assertEqual(len(state.deployed), Hero.COUNT)
        self.assertFalse(any(state.deployed))
        self.assertFalse(any(state.ability_used))
        self.assertTrue(all(state.health_ok))


# ── Attack Stats Tests ───────────────────────────────────────────────────────


class TestAttackStats(unittest.TestCase):
    def test_record_attack(self):
        from mybot.attack.stats import AttackStats
        from mybot.attack.return_home import BattleEndResult
        stats = AttackStats()
        result = BattleEndResult(
            gold_looted=100000, elixir_looted=200000,
            dark_looted=3000, trophies_change=10, stars=2,
        )
        stats.record_attack(result, searches=15)
        self.assertEqual(stats.total_attacks, 1)
        self.assertEqual(stats.total_gold, 100000)
        self.assertEqual(stats.total_elixir, 200000)
        self.assertEqual(stats.total_searches, 15)

    def test_averages(self):
        from mybot.attack.stats import AttackStats
        from mybot.attack.return_home import BattleEndResult
        stats = AttackStats()
        for i in range(5):
            stats.record_attack(BattleEndResult(gold_looted=100000, elixir_looted=50000))
        self.assertAlmostEqual(stats.avg_gold_per_attack, 100000.0)
        self.assertAlmostEqual(stats.avg_elixir_per_attack, 50000.0)

    def test_reset_session(self):
        from mybot.attack.stats import AttackStats
        from mybot.attack.return_home import BattleEndResult
        stats = AttackStats()
        stats.record_attack(BattleEndResult(gold_looted=100000))
        stats.reset_session()
        self.assertEqual(stats.session_gold, 0)
        self.assertEqual(stats.total_gold, 100000)  # Total preserved


# ── CSV Parser Tests ─────────────────────────────────────────────────────────


class TestCSVParser(unittest.TestCase):
    def test_parse_make_command(self):
        from mybot.attack.csv.parser import CSVAttackScript
        script = CSVAttackScript()
        script.parse = lambda p: None  # Skip file reading

        # Manual parse test
        script._parse_make(["A", "top-left", "5", "10", "forward"])
        self.assertIn("A", script.vectors)
        self.assertEqual(script.vectors["A"].side, "top-left")
        self.assertEqual(script.vectors["A"].num_points, 5)

    def test_parse_drop_command(self):
        from mybot.attack.csv.parser import CSVAttackScript
        script = CSVAttackScript()
        cmd = script._parse_drop(["A", "0", "4", "10", "Barb", "100", "500"])
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.vector, "A")
        self.assertEqual(cmd.quantity, 10)
        self.assertEqual(cmd.troop_name, "Barb")
        self.assertEqual(cmd.delay_ms, 100)
        self.assertEqual(cmd.sleep_after, 500)

    def test_parse_side_config(self):
        from mybot.attack.csv.parser import CSVAttackScript
        script = CSVAttackScript()
        script._parse_side(["GOLD", "left", "TRUE"])
        self.assertEqual(script.side_config.resource_type, "GOLD")
        self.assertEqual(script.side_config.forced_side, "left")
        self.assertTrue(script.side_config.use_redline)

    def test_parse_full_script(self, tmp_path=None):
        """Parse a complete CSV script from a temp file."""
        import tempfile
        from mybot.attack.csv.parser import CSVAttackScript, DropCommand, MakeCommand, WaitCommand

        csv_content = textwrap.dedent("""\
            NOTE  |Test army: 10 Giants, 50 Archers
            SIDE  |GOLD|left|TRUE
            MAKE  |A|top-left|5|0|forward
            MAKE  |B|bottom-right|5|0|forward
            DROP  |A|0|4|5|Giant|100
            WAIT  |2000
            DROP  |B|0|4|50|Arch|50
        """)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            f.flush()
            path = Path(f.name)

        try:
            script = CSVAttackScript(path)
            self.assertEqual(script.name, path.stem)
            self.assertIn("A", script.vectors)
            self.assertIn("B", script.vectors)
            # Count command types
            drops = [c for c in script.commands if isinstance(c, DropCommand)]
            waits = [c for c in script.commands if isinstance(c, WaitCommand)]
            makes = [c for c in script.commands if isinstance(c, MakeCommand)]
            self.assertEqual(len(drops), 2)
            self.assertEqual(len(waits), 1)
            self.assertEqual(len(makes), 2)
            self.assertEqual(waits[0].delay_ms, 2000)
        finally:
            path.unlink(missing_ok=True)


class TestCSVValidation(unittest.TestCase):
    def test_valid_script(self):
        from mybot.attack.csv.parser import CSVAttackScript
        from mybot.attack.csv.validate import validate_script

        script = CSVAttackScript()
        script.vectors["A"] = None  # Just needs to exist
        from mybot.attack.csv.parser import AttackVector, DropCommand
        script.vectors["A"] = AttackVector(name="A")
        script.commands.append(DropCommand(vector="A", troop_name="Barb", quantity=10))

        result = validate_script(script)
        self.assertTrue(result.valid)

    def test_undefined_vector(self):
        from mybot.attack.csv.parser import CSVAttackScript, DropCommand
        from mybot.attack.csv.validate import validate_script

        script = CSVAttackScript()
        script.commands.append(DropCommand(vector="MISSING", troop_name="Barb", quantity=10))

        result = validate_script(script)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)


# ── Report Tests ─────────────────────────────────────────────────────────────


class TestAttackReport(unittest.TestCase):
    def test_report_format(self):
        from mybot.attack.report import attack_report
        from mybot.attack.return_home import BattleEndResult
        result = BattleEndResult(
            gold_looted=150000, elixir_looted=200000,
            dark_looted=2500, trophies_change=15, stars=3,
        )
        report = attack_report(result, search_count=42)
        self.assertIn("150,000", report)
        self.assertIn("200,000", report)
        self.assertIn("42", report)
        self.assertIn("3★", report)


# ── Integration Smoke Tests ──────────────────────────────────────────────────


class TestAttackPlanDefaults(unittest.TestCase):
    def test_plan_not_ready_by_default(self):
        from mybot.attack.prepare import AttackPlan
        plan = AttackPlan()
        self.assertFalse(plan.ready)

    def test_cycle_config_defaults(self):
        from mybot.attack.cycle import AttackCycleConfig
        from mybot.enums import MatchMode
        config = AttackCycleConfig()
        self.assertEqual(config.match_mode, MatchMode.DEAD_BASE)
        self.assertEqual(config.algorithm, "all_troops")


if __name__ == "__main__":
    unittest.main()
