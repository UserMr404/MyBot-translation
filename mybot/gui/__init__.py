"""GUI module — PyQt6 application interface.

Phase 6: Main window, tabs, controls, and event handlers.

Imports are lazy to avoid triggering the full PyQt6 widget chain
when only handler utilities are needed.
"""

__all__ = [
    "BottomBar",
    "LogHandler",
    "LogWidget",
    "MainWindow",
    "SplashScreen",
]


def __getattr__(name: str) -> object:
    """Lazy import GUI classes only when accessed."""
    if name == "MainWindow":
        from mybot.gui.main_window import MainWindow
        return MainWindow
    if name == "LogWidget":
        from mybot.gui.log_widget import LogWidget
        return LogWidget
    if name == "LogHandler":
        from mybot.gui.log_widget import LogHandler
        return LogHandler
    if name == "BottomBar":
        from mybot.gui.bottom_bar import BottomBar
        return BottomBar
    if name == "SplashScreen":
        from mybot.gui.splash import SplashScreen
        return SplashScreen
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
