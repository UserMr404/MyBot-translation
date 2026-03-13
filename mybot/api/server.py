"""HTTP API server translated from Api.au3 and ApiHost.au3.

Provides a REST API for external control and monitoring of the bot.
Uses Python stdlib http.server (no external dependencies).

Source: COCBot/functions/Other/Api.au3 (92 lines)
Source: COCBot/functions/Other/ApiHost.au3 (273 lines)
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mybot.state import BotState


class BotAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for bot API endpoints.

    Endpoints:
        GET  /api/status   — Bot status and state
        GET  /api/health   — Health check
        GET  /api/stats    — Attack statistics
        GET  /api/village  — Village resources
        POST /api/start    — Start the bot
        POST /api/stop     — Stop the bot
        POST /api/pause    — Toggle pause
    """

    server: BotHTTPServer  # type annotation for the server

    def do_GET(self) -> None:
        """Handle GET requests."""
        path = self.path.rstrip("/")

        if path == "/api/health":
            self._respond_json({"status": "ok", "version": self._get_version()})
        elif path == "/api/status":
            self._respond_json(self._get_status())
        elif path == "/api/stats":
            self._respond_json(self._get_stats())
        elif path == "/api/village":
            self._respond_json(self._get_village())
        else:
            self._respond_json({"error": "Not Found"}, 404)

    def do_POST(self) -> None:
        """Handle POST requests."""
        path = self.path.rstrip("/")

        if path == "/api/start":
            self._handle_start()
        elif path == "/api/stop":
            self._handle_stop()
        elif path == "/api/pause":
            self._handle_pause()
        else:
            self._respond_json({"error": "Not Found"}, 404)

    def _respond_json(self, data: dict[str, Any], status: int = 200) -> None:
        """Send a JSON response."""
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _get_version(self) -> str:
        try:
            from mybot import __version__
            return __version__
        except ImportError:
            return "unknown"

    def _get_status(self) -> dict[str, Any]:
        state = self.server.bot_state
        if state is None:
            return {"running": False}
        return {
            "running": state.running,
            "paused": state.paused,
            "action": state.action.name,
            "profile": state.account.profile_name,
            "emulator": state.android.emulator,
            "searching": state.search.is_searching,
            "search_count": state.search.search_count,
            "army_full": state.army.is_full,
        }

    def _get_stats(self) -> dict[str, Any]:
        state = self.server.bot_state
        if state is None:
            return {}
        return {
            "attack_count": 0,
            "total_gold": 0,
            "total_elixir": 0,
            "total_dark": 0,
        }

    def _get_village(self) -> dict[str, Any]:
        state = self.server.bot_state
        if state is None:
            return {}
        v = state.village
        return {
            "gold": v.current_loot[0],
            "elixir": v.current_loot[1],
            "dark_elixir": v.current_loot[2],
            "trophies": v.current_loot[3],
            "town_hall": v.town_hall_level,
            "free_builders": v.free_builder_count,
            "total_builders": v.total_builder_count,
        }

    def _handle_start(self) -> None:
        state = self.server.bot_state
        if state:
            from mybot.enums import BotAction
            state.action = BotAction.START
            self._respond_json({"result": "started"})
        else:
            self._respond_json({"error": "No state"}, 500)

    def _handle_stop(self) -> None:
        state = self.server.bot_state
        if state:
            state.stop_event.set()
            self._respond_json({"result": "stopped"})
        else:
            self._respond_json({"error": "No state"}, 500)

    def _handle_pause(self) -> None:
        state = self.server.bot_state
        if state:
            state.paused = not state.paused
            self._respond_json({"paused": state.paused})
        else:
            self._respond_json({"error": "No state"}, 500)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default request logging."""
        pass


class BotHTTPServer(HTTPServer):
    """HTTP server with bot state reference."""

    def __init__(self, address: tuple[str, int], bot_state: BotState | None = None) -> None:
        self.bot_state = bot_state
        super().__init__(address, BotAPIHandler)


class APIServer:
    """Threaded API server for bot control.

    Usage:
        server = APIServer(state, port=8080)
        server.start()  # Runs in background thread
        ...
        server.stop()
    """

    def __init__(self, bot_state: BotState, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.bot_state = bot_state
        self.host = host
        self.port = port
        self._server: BotHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the API server in a background thread."""
        self._server = BotHTTPServer((self.host, self.port), self.bot_state)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="APIServer",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the API server."""
        if self._server:
            self._server.shutdown()
            self._server = None

    @property
    def is_running(self) -> bool:
        """Whether the API server is running."""
        return self._thread is not None and self._thread.is_alive()
