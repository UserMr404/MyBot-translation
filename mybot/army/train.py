"""Main training system translated from CreateArmy/TrainSystem.au3.

Orchestrates the full army training cycle: check readiness,
open army overview, train troops/spells/siege via Quick Train
or custom composition, then close.

Source: COCBot/functions/CreateArmy/TrainSystem.au3
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from mybot.army.army_overview import (
    ArmyTab,
    close_army_overview,
    is_army_overview_open,
    open_army_overview,
    switch_army_tab,
)
from mybot.army.check_camp import ArmyCampStatus, check_army_camp
from mybot.army.check_full import check_full_army
from mybot.army.double_train import double_train
from mybot.army.quick_train import quick_train
from mybot.army.smart_wait import smart_wait_for_train
from mybot.army.train_it import train_it
from mybot.army.train_siege import train_siege
from mybot.config.image_dirs import resolve as resolve_img_dir
from mybot.constants import TROOP_SHORT_NAMES, SPELL_SHORT_NAMES
from mybot.enums import Spell, Troop
from mybot.log import set_debug_log, set_log


@dataclass
class TrainConfig:
    """Army training configuration.

    Replaces $g_bQuickTrainEnable, $g_aiArmyCustomTrain[], etc.
    """
    use_quick_train: bool = True
    quick_train_slot: int = 0  # 0, 1, or 2

    # Custom army composition (indexed by Troop enum)
    custom_troops: list[int] = field(default_factory=lambda: [0] * Troop.COUNT)
    custom_spells: list[int] = field(default_factory=lambda: [0] * Spell.COUNT)
    custom_siege: list[int] = field(default_factory=lambda: [0] * 8)

    # Double train (queue second army)
    double_train: bool = False

    # Training template directories
    troop_template_dir: Path = field(default_factory=lambda: resolve_img_dir("imgxml/Train/Troops"))
    spell_template_dir: Path = field(default_factory=lambda: resolve_img_dir("imgxml/Train/Spells"))


@dataclass
class TrainResult:
    """Result of a training cycle."""
    army_full: bool = False
    training_started: bool = False
    wait_time: float = 0.0
    error: str = ""


def train_system(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    config: TrainConfig | None = None,
) -> TrainResult:
    """Execute the full army training system.

    Translated from TrainSystem() in TrainSystem.au3.
    This is the main orchestrator that coordinates all training
    sub-functions.

    Flow:
    1. Check if army is already full → skip if so
    2. Open army overview
    3. Check army camp status
    4. Train via Quick Train or custom composition
    5. Optionally queue second army (double train)
    6. Read remaining training time
    7. Close army overview

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking UI.
        config: Training configuration.

    Returns:
        TrainResult with status.
    """
    if config is None:
        config = TrainConfig()

    result = TrainResult()

    # Step 1: Open army overview
    if not open_army_overview(capture_func, click_func):
        result.error = "Failed to open army overview"
        return result

    time.sleep(0.5)

    # Step 2: Check if army is full
    image = capture_func()
    if image is not None and check_full_army(image, army_overview_open=True):
        result.army_full = True
        set_log("Army is full — no training needed")

        if config.double_train:
            double_train(capture_func, click_func, config.quick_train_slot)

        close_army_overview(click_func)
        return result

    # Step 3: Check camp status
    if image is not None:
        camp_status = check_army_camp(image)
        set_debug_log(f"Camp: {camp_status.current_space}/{camp_status.total_space}")

    # Step 4: Train
    if config.use_quick_train:
        success = quick_train(capture_func, click_func, config.quick_train_slot)
        result.training_started = success
    else:
        result.training_started = _train_custom_army(capture_func, click_func, config)

    # Step 5: Train siege machines
    if any(q > 0 for q in config.custom_siege):
        train_siege(capture_func, click_func, config.custom_siege)

    # Step 6: Read remaining time
    from mybot.vision.ocr import get_train_timer
    image = capture_func()
    if image is not None:
        timer = get_train_timer(image)
        if timer:
            result.wait_time = smart_wait_for_train(timer)

    # Step 7: Close
    close_army_overview(click_func)

    if result.training_started:
        set_log("Training initiated")
    else:
        set_debug_log("No training was performed")

    return result


def _train_custom_army(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
    config: TrainConfig,
) -> bool:
    """Train troops and spells from custom configuration.

    Args:
        capture_func: Returns BGR screenshot.
        click_func: For clicking.
        config: Training configuration with custom troop/spell counts.

    Returns:
        True if any training was performed.
    """
    trained_any = False

    # Switch to troops tab
    switch_army_tab(ArmyTab.TROOPS, click_func)
    time.sleep(0.5)

    # Train each troop type
    for troop_idx in range(min(len(config.custom_troops), Troop.COUNT)):
        count = config.custom_troops[troop_idx]
        if count <= 0:
            continue

        name = TROOP_SHORT_NAMES[troop_idx] if troop_idx < len(TROOP_SHORT_NAMES) else f"Troop{troop_idx}"
        success = train_it(
            capture_func, click_func, name, count,
            template_dir=config.troop_template_dir,
        )
        if success:
            trained_any = True

    # Switch to spells tab
    switch_army_tab(ArmyTab.SPELLS, click_func)
    time.sleep(0.5)

    # Train each spell type
    for spell_idx in range(min(len(config.custom_spells), Spell.COUNT)):
        count = config.custom_spells[spell_idx]
        if count <= 0:
            continue

        name = SPELL_SHORT_NAMES[spell_idx] if spell_idx < len(SPELL_SHORT_NAMES) else f"Spell{spell_idx}"
        success = train_it(
            capture_func, click_func, name, count,
            template_dir=config.spell_template_dir,
        )
        if success:
            trained_any = True

    return trained_any
