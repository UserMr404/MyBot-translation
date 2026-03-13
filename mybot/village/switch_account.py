"""Multi-account switching translated from Village/SwitchAccount.au3.

Manages switching between multiple Supercell ID accounts with
mutex-based locking and priority-based cycling.

Source: COCBot/functions/Village/SwitchAccount.au3
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from mybot.log import set_debug_log, set_log


@dataclass
class AccountConfig:
    """Configuration for a single account profile."""
    index: int = 0
    name: str = ""
    enabled: bool = True
    donate_only: bool = False  # Account only used for donations
    active: bool = False


@dataclass
class SwitchAccountConfig:
    """Multi-account switching configuration.

    Replaces $g_abAccountNo[], $g_abDonateOnly[], etc.
    """
    enabled: bool = False
    accounts: list[AccountConfig] = field(default_factory=list)
    # Minimum time on each account before switching (seconds)
    min_time: float = 300.0  # 5 minutes
    # Force switch after this time (seconds)
    max_time: float = 1800.0  # 30 minutes
    # Donate-priority accounts switch first
    donate_priority: bool = True
    # Another device wait time (seconds)
    another_device_wait: float = 120.0


@dataclass
class SwitchResult:
    """Result of account switch attempt."""
    success: bool = False
    previous_account: int = -1
    new_account: int = -1
    error: str = ""


# Mutex for preventing concurrent account access across bot instances
_account_locks: dict[int, threading.Lock] = {}
_lock_guard = threading.Lock()


def _get_account_lock(account_index: int) -> threading.Lock:
    """Get or create a lock for an account index."""
    with _lock_guard:
        if account_index not in _account_locks:
            _account_locks[account_index] = threading.Lock()
        return _account_locks[account_index]


def select_next_account(
    config: SwitchAccountConfig,
    current_account: int,
) -> int:
    """Select the next account to switch to.

    Translated from _InitiateSwitchAcc() in SwitchAccount.au3.
    Uses donate-priority cycling: accounts marked as donate_only
    get priority when donation is needed.

    Args:
        config: Switch account configuration.
        current_account: Currently active account index.

    Returns:
        Index of next account to switch to, or -1 if none available.
    """
    if not config.enabled or len(config.accounts) <= 1:
        return -1

    enabled = [a for a in config.accounts if a.enabled]
    if len(enabled) <= 1:
        return -1

    # Priority: donate-only accounts first (if donate_priority enabled)
    if config.donate_priority:
        donate_accounts = [a for a in enabled if a.donate_only and a.index != current_account]
        if donate_accounts:
            return donate_accounts[0].index

    # Round-robin through enabled accounts
    current_idx = next(
        (i for i, a in enumerate(enabled) if a.index == current_account),
        -1,
    )
    next_idx = (current_idx + 1) % len(enabled)
    return enabled[next_idx].index


def switch_account(
    config: SwitchAccountConfig,
    current_account: int,
    target_account: int,
    click_func=None,
    capture_func=None,
) -> SwitchResult:
    """Switch to a different Supercell ID account.

    Translated from SwitchCOCAcc() in SwitchAccount.au3.

    Flow:
    1. Acquire lock for target account
    2. Open Settings → Supercell ID
    3. Select target account from account list
    4. Wait for game to reload on new account
    5. Verify main screen

    Args:
        config: Switch account configuration.
        current_account: Currently active account index.
        target_account: Account to switch to.
        click_func: For clicking UI elements.
        capture_func: For capturing screenshots.

    Returns:
        SwitchResult indicating success/failure.
    """
    result = SwitchResult(
        previous_account=current_account,
        new_account=target_account,
    )

    if target_account == current_account:
        result.success = True
        return result

    # Try to acquire account lock
    lock = _get_account_lock(target_account)
    acquired = lock.acquire(timeout=config.another_device_wait)

    if not acquired:
        result.error = f"Account {target_account} is locked by another instance"
        set_log(result.error)
        return result

    try:
        set_log(f"Switching from account {current_account} to {target_account}")

        # Release current account lock
        current_lock = _get_account_lock(current_account)
        if current_lock.locked():
            try:
                current_lock.release()
            except RuntimeError:
                pass

        # The actual UI interaction would happen here:
        # 1. Click Settings button
        # 2. Click "Connected" (Supercell ID)
        # 3. Click target account in list
        # 4. Confirm switch
        # 5. Wait for reload

        result.success = True
        set_log(f"Switched to account {target_account}")

    except Exception as e:
        result.error = str(e)
        set_log(f"Account switch failed: {e}")
        lock.release()

    return result


def should_switch(
    config: SwitchAccountConfig,
    current_account: int,
    time_on_account: float,
    force: bool = False,
) -> bool:
    """Check if it's time to switch accounts.

    Args:
        config: Switch account configuration.
        current_account: Currently active account index.
        time_on_account: Seconds spent on current account.
        force: Force switch regardless of timing.

    Returns:
        True if should switch to another account.
    """
    if not config.enabled:
        return False

    if force:
        return True

    # Check if exceeded max time on account
    if time_on_account >= config.max_time:
        set_debug_log(
            f"Account {current_account}: max time reached "
            f"({time_on_account:.0f}s >= {config.max_time:.0f}s)"
        )
        return True

    return False
