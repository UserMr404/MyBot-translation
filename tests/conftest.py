"""Shared pytest fixtures for MyBot tests."""

from __future__ import annotations

import threading

import pytest

from mybot.state import BotState


@pytest.fixture
def bot_state() -> BotState:
    """Create a fresh BotState instance for testing."""
    return BotState()


@pytest.fixture
def stop_event() -> threading.Event:
    """Create a threading.Event for sleep testing."""
    return threading.Event()
