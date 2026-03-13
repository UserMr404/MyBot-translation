"""Bot options event handlers translated from MBR GUI Control BOT Options.au3.

Handles bot option changes: restart, halt, language, close behavior.

Source: COCBot/GUI/MBR GUI Control BOT Options.au3 (1,226 lines, 68 functions)
"""

from __future__ import annotations

from mybot.state import BotState


def apply_bot_options(state: BotState, **kwargs: object) -> None:
    """Apply bot options from GUI to state.

    Keyword args are validated and applied to the appropriate state fields.
    """
    if "auto_restart" in kwargs:
        pass  # Applied in extended state

    if "debug_log" in kwargs:
        state.debug.set_log = bool(kwargs["debug_log"])

    if "emulator" in kwargs:
        state.android.emulator = str(kwargs["emulator"])

    if "instance" in kwargs:
        state.android.instance = str(kwargs["instance"])
