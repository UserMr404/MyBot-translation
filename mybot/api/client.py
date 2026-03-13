"""HTTP API client translated from ApiClient.au3.

Client for bot-to-bot communication and external monitoring.

Source: COCBot/functions/Other/ApiClient.au3 (356 lines)
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any


class BotAPIClient:
    """HTTP client for communicating with a running bot's API server.

    Usage:
        client = BotAPIClient("http://127.0.0.1:8080")
        status = client.get_status()
        client.start_bot()
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8080", timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str) -> dict[str, Any]:
        """Send a GET request and return JSON response."""
        url = f"{self.base_url}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            return {"error": str(e)}

    def _post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a POST request and return JSON response."""
        url = f"{self.base_url}{path}"
        body = json.dumps(data or {}).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            return {"error": str(e)}

    def health(self) -> dict[str, Any]:
        """Check if the bot API is healthy."""
        return self._get("/api/health")

    def get_status(self) -> dict[str, Any]:
        """Get current bot status."""
        return self._get("/api/status")

    def get_stats(self) -> dict[str, Any]:
        """Get attack statistics."""
        return self._get("/api/stats")

    def get_village(self) -> dict[str, Any]:
        """Get village resource info."""
        return self._get("/api/village")

    def start_bot(self) -> dict[str, Any]:
        """Send start command to the bot."""
        return self._post("/api/start")

    def stop_bot(self) -> dict[str, Any]:
        """Send stop command to the bot."""
        return self._post("/api/stop")

    def toggle_pause(self) -> dict[str, Any]:
        """Toggle bot pause state."""
        return self._post("/api/pause")

    def is_reachable(self) -> bool:
        """Check if the bot API server is reachable."""
        result = self.health()
        return "error" not in result
