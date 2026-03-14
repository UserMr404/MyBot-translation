# Plan: Wire Vision System into Bot Main Cycle

## Context

The vision subsystem is already ~85% implemented in `mybot/vision/` (matcher, templates, pixel, ocr, red_area, geometry, townhall, dead_base, window_detect). The game logic modules (`mybot/game/main_screen.py`, `mybot/game/obstacles.py`) also exist and use the vision system correctly. However, `bot.py` has stubs that don't call any of this — they just log "not yet implemented".

The goal is to wire the existing vision + game logic into the bot's main cycle so it actually captures screenshots, checks the main screen, handles obstacles, reads resources, and zooms out.

---

## Step 1: Create a `ScreenCapture` accessor on `Bot`

**File**: `mybot/bot.py`

The bot needs a `ScreenCapture` instance to take screenshots. Currently `_open_android()` creates an `EmulatorManager` but never exposes a capture interface.

- After emulator opens successfully, create a `ScreenCapture(adb=emulator.adb)` and store it as `self._capture`
- Add a `_screenshot()` helper method that calls `self._capture.capture_full()` and returns the numpy array
- Add a `_click(x, y)` helper that calls `emulator.adb.tap(x, y)` with small random offset

---

## Step 2: Wire `initiate()` — main screen check + zoom out

**File**: `mybot/bot.py`

Replace the stub log messages in `initiate()` with real calls:

1. **Check main screen**: Call `check_main_screen(capture_func=self._screenshot, click_func=self._click)` from `mybot.game.main_screen`
2. **Zoom out**: Call `zoom_out(adb)` from `mybot.android.zoom`
3. If either fails, return False (triggering error path already in place)

---

## Step 3: Wire `_check_main_screen()` in main loop

**File**: `mybot/bot.py`

Replace the try/except ImportError stub with an actual call:

```python
def _check_main_screen(self) -> None:
    image = self._screenshot()
    if image is None:
        return
    if not is_main_screen(image):
        check_main_screen(self._screenshot, self._click)
```

---

## Step 4: Wire `_check_obstacles()` in main loop

**File**: `mybot/bot.py`

Replace stub with:

```python
def _check_obstacles(self) -> None:
    image = self._screenshot()
    if image is None:
        return
    result = check_obstacles(image, self._click)
    if result.found:
        set_log(f"Obstacle handled: {result.action_taken}")
```

---

## Step 5: Wire `_village_report()` — read resources from screen

**File**: `mybot/bot.py` + potentially `mybot/village/report.py`

If `mybot/village/report.py` doesn't exist yet, create a minimal version that:

1. Takes a screenshot
2. Uses OCR (`read_text()` from `mybot/vision/ocr`) to read Gold, Elixir, Dark Elixir, Gems, Trophies from known screen coordinates
3. Updates `self.state.resources` with the read values
4. Logs the village status summary

The OCR read positions come from the AutoIt source (`getResourcesMainScreen` reads at specific (x,y,w,h) regions).

---

## Step 6: Wire `first_check()` — detect TH level on first run

**File**: `mybot/bot.py`

Use the existing `mybot/vision/townhall.py` to detect TH level:

1. Take a screenshot
2. Call townhall detection to find TH level
3. Store in `self.state.village.th_level`
4. Log the detected level

---

## Step 7: Enhance zoom verification

**File**: `mybot/android/zoom.py`

The zoom module has a `verify` parameter that currently says "verification deferred to vision system". Wire it:

1. After pinch gesture, take a screenshot
2. Use `find_multiple()` with the ZoomOut template directory (`imgxml/other/ZoomOut`) to check if the zoom indicator appears
3. If zoom indicator NOT found → zoomed out enough → return True
4. If found → still needs more zoom → retry

---

## Step 8: Add `_do_collections()` skeleton with vision

**File**: `mybot/bot.py`

Create a minimal but functional collection routine:

1. Take screenshot
2. Use `find_multiple()` with `imgxml/Resources/Collect` templates to find collectible resource icons
3. Click each found icon (with small delays between clicks)
4. Log number of resources collected

This replaces the AutoIt `Collect()` function pattern: screenshot → find icons → click them.

---

## Order of Implementation

1. Step 1 (capture accessor) — everything depends on this
2. Step 2 (initiate wiring) — needed for bot startup
3. Steps 3-4 (main screen + obstacles) — needed for stable main loop
4. Step 6 (TH detection) — first-check functionality
5. Step 5 (village report) — status display
6. Step 7 (zoom verification) — stability improvement
7. Step 8 (collections) — first real game interaction

## Files Modified

- `mybot/bot.py` — main changes (Steps 1-6, 8)
- `mybot/android/zoom.py` — zoom verification (Step 7)
- `mybot/village/report.py` — create if missing (Step 5)

## Files Read-Only (already correct)

- `mybot/vision/matcher.py` — template matching engine
- `mybot/vision/pixel.py` — pixel operations
- `mybot/vision/ocr.py` — text recognition
- `mybot/vision/templates.py` — template loading
- `mybot/vision/townhall.py` — TH detection
- `mybot/vision/window_detect.py` — dialog detection
- `mybot/game/main_screen.py` — main screen checks
- `mybot/game/obstacles.py` — obstacle handling
- `mybot/android/capture.py` — screen capture class
- `mybot/config/coordinates.py` — pixel constants
- `mybot/config/image_dirs.py` — template paths
