"""Builder Base spam attack mode translated from MOD/BBSpam.au3.

Simple spam deployment for Builder Base — deploys all troops
rapidly without strategy.

Source: COCBot/functions/MOD/BBSpam.au3
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from mybot.attack.builder_base.attack import BBAttackResult, attack_builder_base
from mybot.log import set_log


def bb_spam(
    capture_func: Callable[[], np.ndarray | None],
    click_func: Callable[[int, int], None],
) -> BBAttackResult:
    """Execute a BB spam attack.

    Translated from BBSpam() — uses the standard BB attack
    with minimal strategy.
    """
    set_log("BB Spam: starting")
    return attack_builder_base(capture_func, click_func)
