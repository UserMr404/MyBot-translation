"""Log display widget translated from MBR GUI Design Log.au3.

Rich text log display with color-coded messages matching AutoIt's log colors.

Source: COCBot/GUI/MBR GUI Design Log.au3 (93 lines)
"""

from __future__ import annotations

import logging
from datetime import datetime

from PyQt6.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QTextCursor
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from mybot.constants import (
    COLOR_ACTION,
    COLOR_DEBUG,
    COLOR_ERROR,
    COLOR_INFO,
    COLOR_SUCCESS,
    COLOR_WARNING,
)

# Map log level names to display colors
_LEVEL_COLORS: dict[str, str] = {
    "ERROR": "#FF0000",
    "WARNING": "#CC6600",
    "INFO": "#0066CC",
    "SUCCESS": "#006600",
    "ACTION": "#FF8000",
    "DEBUG": "#800080",
}

MAX_LOG_LINES = 5000


class LogWidget(QWidget):
    """Scrolling log display with colored messages.

    Replaces AutoIt's rich edit control with a QTextEdit.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the log text display."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(120)
        self.text_edit.setStyleSheet(
            "QTextEdit { background-color: #1E1E1E; color: #CCCCCC; "
            "font-family: 'Consolas', 'Courier New', monospace; font-size: 10pt; }"
        )
        layout.addWidget(self.text_edit)

    @pyqtSlot(str, str)
    def append_message(self, message: str, level: str = "INFO") -> None:
        """Append a colored log message.

        Args:
            message: Log message text.
            level: Log level name (ERROR, WARNING, INFO, SUCCESS, ACTION, DEBUG).
        """
        color = _LEVEL_COLORS.get(level.upper(), "#CCCCCC")
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        html = (
            f'<span style="color: #888888;">[{timestamp}]</span> '
            f'<span style="color: {color};">{_escape_html(message)}</span>'
        )
        self.text_edit.append(html)

        # Auto-scroll to bottom
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)

        # Trim excess lines
        self._trim_lines()

    def append_log_record(self, record: logging.LogRecord) -> None:
        """Append a message from a logging.LogRecord."""
        level = record.levelname
        if level == "ACTION":
            level = "ACTION"
        self.append_message(record.getMessage(), level)

    def clear(self) -> None:
        """Clear all log messages."""
        self.text_edit.clear()

    def _trim_lines(self) -> None:
        """Remove oldest lines if exceeding MAX_LOG_LINES."""
        doc = self.text_edit.document()
        if doc.blockCount() > MAX_LOG_LINES:
            cursor = QTextCursor(doc)
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Down,
                QTextCursor.MoveMode.KeepAnchor,
                doc.blockCount() - MAX_LOG_LINES,
            )
            cursor.removeSelectedText()

    @property
    def line_count(self) -> int:
        """Number of lines currently displayed."""
        return self.text_edit.document().blockCount()


class _LogBridge(QObject):
    """Signal bridge for thread-safe log routing.

    QMetaObject.invokeMethod with Q_ARG is unreliable in PyQt6 for
    Python-defined slots. Using a signal is the idiomatic and reliable
    approach for cross-thread GUI updates.
    """

    message = pyqtSignal(str, str)


class LogHandler(logging.Handler):
    """Logging handler that routes messages to a LogWidget.

    Thread-safe: uses a QObject signal bridge so that emit() from any
    thread safely queues the message to the GUI thread's event loop.
    """

    def __init__(self, log_widget: LogWidget) -> None:
        super().__init__()
        self._bridge = _LogBridge()
        self._bridge.message.connect(log_widget.append_message)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the widget via the signal bridge."""
        try:
            msg = self.format(record) if self.formatter else record.getMessage()
            level = record.levelname
            self._bridge.message.emit(msg, level)
        except Exception:
            self.handleError(record)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
