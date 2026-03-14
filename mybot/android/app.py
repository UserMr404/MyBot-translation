"""Game app management translated from Android.au3 and Close_OpenCoC.au3.

Handles starting and stopping the Clash of Clans app on the emulator.
Replaces StartAndroidCoC(), CloseCoC(), and related functions.
"""

from __future__ import annotations

import time

from mybot.android.adb import AdbClient, AdbError
from mybot.constants import COLOR_ERROR, COLOR_SUCCESS, COLOR_WARNING
from mybot.log import set_debug_log, set_log

# Clash of Clans package info
COC_PACKAGE = "com.supercell.clashofclans"
COC_ACTIVITY = "com.supercell.titan.GameApp"

# Google Play distributor
GP_COC_PACKAGE = "com.supercell.clashofclans"
# Amazon distributor
AMAZON_COC_PACKAGE = "com.supercell.clashofclans.amazon"
# Kunlun (Chinese) distributor
KUNLUN_COC_PACKAGE = "com.supercell.clashofclans.kunlun"


def start_coc(
    adb: AdbClient,
    package: str = COC_PACKAGE,
    timeout: float = 30.0,
) -> bool:
    """Start Clash of Clans on the emulator.

    Replaces StartAndroidCoC() from Android.au3.

    Args:
        adb: ADB client.
        package: CoC package name (varies by distributor).
        timeout: Maximum wait time for app to start.

    Returns:
        True if app started successfully.
    """
    set_log("Starting Clash of Clans...")
    set_log(f"ADB path: {adb.adb_path}")
    set_log(f"ADB device: {adb.device}")

    # Verify ADB connectivity first
    devs: list[str] = []
    try:
        devs = adb.devices()
        set_log(f"ADB devices: {devs}")
    except AdbError as e:
        set_log(f"ADB devices query failed: {e}", COLOR_ERROR)

    try:
        # Check if CoC is installed on the configured device
        pm_output = adb.shell(f"pm path {package}", timeout=10.0)
        if "package:" not in pm_output:
            set_log(
                f"CoC ({package}) not found on {adb.device}, checking other devices...",
                COLOR_WARNING,
            )
            # Try other connected devices
            switched = False
            for dev in devs:
                if dev == adb.device:
                    continue
                set_log(f"Trying device: {dev}")
                adb.device = dev
                pm_output = adb.shell(f"pm path {package}", timeout=10.0)
                if "package:" in pm_output:
                    set_log(f"Found CoC on device: {dev}", COLOR_SUCCESS)
                    switched = True
                    break
            if not switched:
                set_log(
                    f"Clash of Clans ({package}) is not installed on any device",
                    COLOR_ERROR,
                )
                return False
        set_log(f"CoC installed: {pm_output}")

        # Launch the app using _run directly to capture stderr
        cmd = f"am start -W -n {package}/{COC_ACTIVITY}"
        set_log(f"Launch command: {cmd}")
        result = adb._run(
            ["shell", cmd], timeout=60.0, check=False
        )
        set_log(f"Launch stdout: {result.stdout.strip()}")
        if result.stderr.strip():
            set_log(f"Launch stderr: {result.stderr.strip()}", COLOR_WARNING)
        if result.returncode != 0:
            set_log(f"Launch exit code: {result.returncode}", COLOR_WARNING)
        time.sleep(3.0)

        # Verify it's running
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if is_coc_running(adb, package):
                set_log("Clash of Clans started", COLOR_SUCCESS)
                return True
            set_debug_log("CoC not yet running, waiting...")
            time.sleep(2.0)

        set_log("Clash of Clans did not start in time", COLOR_WARNING)
        return False

    except AdbError as e:
        set_log(f"Failed to start CoC: {e}", COLOR_ERROR)
        return False


def stop_coc(
    adb: AdbClient,
    package: str = COC_PACKAGE,
) -> None:
    """Stop Clash of Clans on the emulator.

    Replaces CloseCoC() from Close_OpenCoC.au3.
    """
    set_log("Closing Clash of Clans...")
    try:
        adb.force_stop(package)
        time.sleep(1.0)
        set_debug_log("CoC force-stopped")
    except AdbError as e:
        set_debug_log(f"Failed to stop CoC: {e}")


def restart_coc(
    adb: AdbClient,
    package: str = COC_PACKAGE,
    timeout: float = 30.0,
) -> bool:
    """Restart Clash of Clans (close + reopen).

    Replaces CloseOpen() from Close_OpenCoC.au3.

    Returns:
        True if restart succeeded.
    """
    set_log("Restarting Clash of Clans...")
    stop_coc(adb, package)
    time.sleep(3.0)
    return start_coc(adb, package, timeout)


def is_coc_running(
    adb: AdbClient,
    package: str = COC_PACKAGE,
) -> bool:
    """Check if Clash of Clans is currently running.

    Uses `pidof` to check if the process is alive.
    """
    try:
        output = adb.shell(f"pidof {package}")
        return output.strip() != ""
    except AdbError:
        return False


def get_coc_distributor(adb: AdbClient) -> str:
    """Detect which CoC distributor is installed.

    Checks for Google Play, Amazon, and Kunlun versions.

    Returns:
        Package name of the installed version, or default GP package.
    """
    for package in (GP_COC_PACKAGE, AMAZON_COC_PACKAGE, KUNLUN_COC_PACKAGE):
        try:
            output = adb.shell(f"pm path {package}")
            if "package:" in output:
                set_debug_log(f"Detected CoC distributor: {package}")
                return package
        except AdbError:
            continue

    return GP_COC_PACKAGE
