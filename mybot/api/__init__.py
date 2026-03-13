"""API module — HTTP server and client for external bot control.

Phase 6: REST API for monitoring and controlling the bot.
"""

from mybot.api.client import BotAPIClient
from mybot.api.server import APIServer

__all__ = [
    "APIServer",
    "BotAPIClient",
]
