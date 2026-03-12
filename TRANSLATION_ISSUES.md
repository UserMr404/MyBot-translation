# GitHub Issues for MyBot AutoIt → Python Translation

> Copy-paste each issue into GitHub. Use labels: `phase-1` through `phase-6`, `critical`, `high`, `medium`, `low`.
> Create milestone: "AutoIt → Python Translation" with 6 sub-milestones (one per phase).

---

## Phase 1: Foundation & Infrastructure

### Issue 1.1: Project Scaffolding
**Labels**: `phase-1`, `critical`, `setup`

**Description:**
Set up the Python project skeleton for the MyBot translation.

**Tasks:**
- [ ] Create `pyproject.toml` with dependencies:
  - opencv-python>=4.9, numpy>=1.26, Pillow>=10.0, PyQt6>=6.6
  - pure-python-adb>=0.3, pytesseract>=0.3, requests>=2.31
  - fastapi>=0.109, uvicorn>=0.27, apprise>=1.7
  - psutil>=5.9, pywin32>=306, cryptography>=42.0, pydantic>=2.6
  - Dev: pytest>=8.0, ruff>=0.2, mypy>=1.8, black>=24.1
- [ ] Create `mybot/__init__.py` with version
- [ ] Configure ruff (linting rules)
- [ ] Configure black (formatting)
- [ ] Configure mypy (strict mode)
- [ ] Set up pytest with `tests/conftest.py`
- [ ] Create GitHub Actions CI: lint → type-check → test
- [ ] Create `.env.example`
- [ ] Create `README.md` with setup instructions
- [ ] Symlink or copy `Languages/`, `CSV/`, `imgxml/`, `images/` from source

**Acceptance Criteria:**
- `pip install -e .` works
- `ruff check mybot/` passes
- `mypy mybot/` passes
- `pytest` runs (even with 0 tests)

---

### Issue 1.2: Global Variables → State Model
**Labels**: `phase-1`, `critical`

**Description:**
Translate `MBR Global Variables.au3` (2,332 lines, 852 globals) into structured Python state.

**Source**: `COCBot/MBR Global Variables.au3`

**Tasks:**
- [ ] Create `mybot/enums.py` — All enum types:
  - `Troop(IntEnum)` — 50+ troop types ($eTroopBarbarian, etc.)
  - `Spell(IntEnum)` — 15+ spell types
  - `Hero(IntEnum)` — 5 heroes (King, Queen, Prince, Warden, Champion)
  - `Siege(IntEnum)` — siege machine types
  - `LootType(IntEnum)` — Gold, Elixir, DarkElixir, Trophy
  - `MatchMode(IntEnum)` — DB, LB, TS
  - `BotAction(IntEnum)` — Start, Stop, SearchMode, Close
- [ ] Create `mybot/constants.py` — Game constants:
  - `GAME_WIDTH = 860`, `GAME_HEIGHT = 732`
  - Color constants: `COLOR_ERROR`, `COLOR_WARNING`, etc.
  - All coordinate constants
- [ ] Create `mybot/state.py` — `BotState` dataclass hierarchy:
  - `BotState.running: threading.Event`
  - `BotState.restart_requested: bool`
  - `BotState.screen: ScreenState` (offsets, dimensions)
  - `BotState.village: VillageState` (loot, TH level, builders)
  - `BotState.army: ArmyState` (is_full, composition)
  - `BotState.android: AndroidState` (window handle, emulator type)
  - `BotState.accounts: AccountState` (current account, timers)
  - `BotState.search: SearchState` (match mode, filters)
  - `BotState.debug: DebugState` (all debug flags)
- [ ] Create `mybot/config/models.py` — Pydantic config models for user settings

**Acceptance Criteria:**
- All 852 globals have a corresponding Python field
- `mypy --strict` passes on all state modules
- Unit tests verify default values match AutoIt defaults

---

### Issue 1.3: Configuration System
**Labels**: `phase-1`, `critical`

**Description:**
Translate config read/save/apply from INI files. Must be backward-compatible with existing `config.ini` files.

**Source**: `COCBot/functions/Config/` (6,594 lines, 8 files)

**Tasks:**
- [ ] Create `mybot/config/reader.py` — Translate `readConfig.au3` (1,468 lines, 44 functions)
  - Use declarative CONFIG_MAP instead of 700+ individual IniRead calls
  - Handle type conversion (bool, int, float, string)
  - Support profile-specific paths
- [ ] Create `mybot/config/writer.py` — Translate `saveConfig.au3` (1,413 lines, 50 functions)
  - Mirror of reader with IniWrite
- [ ] Create `mybot/config/applier.py` — Translate `applyConfig.au3` (2,422 lines, 43 functions)
  - Apply config to GUI controls (Phase 6 integration)
  - Initially: just load config into BotState
- [ ] Create `mybot/config/coordinates.py` — Translate `ScreenCoordinates.au3` (397 lines)
  - Pure constants — direct translation
- [ ] Create `mybot/config/delays.py` — Translate `DelayTimes.au3` (186 lines)
  - Pure constants
- [ ] Create `mybot/config/image_dirs.py` — Translate `ImageDirectories.au3` (266 lines)
  - Use pathlib.Path for all paths
- [ ] Create `mybot/config/profiles.py` — Translate `profileFunctions.au3` (287 lines, 9 functions)
- [ ] Create `mybot/config/ini_table.py` — Translate `_Ini_Table.au3` (155 lines, 7 functions)

**Acceptance Criteria:**
- Round-trip test: read existing config.ini → write to new file → diff shows no data loss
- All 44 readConfig sections parse correctly
- Profile creation/deletion/switching works
- `configparser` reads existing INI files without errors

---

### Issue 1.4: Logging System
**Labels**: `phase-1`, `high`

**Description:**
Translate `SetLog.au3` (370 lines, 18 functions) to Python stdlib logging.

**Tasks:**
- [ ] Create `mybot/log.py` with:
  - Custom `logging.Handler` for colored console output
  - File handler with rotation
  - GUI handler placeholder (connects in Phase 6)
  - `SetLog()` → `logger.info()`, `SetDebugLog()` → `logger.debug()`
  - Color mapping: `$COLOR_ERROR` → `logging.ERROR`, etc.
- [ ] Preserve log format compatibility

**Acceptance Criteria:**
- Log messages appear in console with colors
- Log file created and rotated properly
- Debug messages only appear when debug enabled

---

### Issue 1.5: Sleep / Control Flow System
**Labels**: `phase-1`, `critical`

**Description:**
Translate `_Sleep.au3` (147 lines, 3 functions). This is called 1,801 times across the codebase — it's the cooperative multitasking mechanism.

**Tasks:**
- [ ] Create `mybot/utils/sleep.py` with:
  - `bot_sleep(ms, state) -> bool` — uses `threading.Event.wait()`
  - Returns `True` if interrupted (stop/restart requested)
  - Microsecond sleep variant (just use `time.sleep()`)
  - Status callback variant for GUI updates

**Acceptance Criteria:**
- Sleep returns immediately when stop_event is set
- Sleep returns `True` when interrupted within 50ms of signal
- Normal sleep timing accuracy within ±50ms

---

### Issue 1.6: Translation / i18n System
**Labels**: `phase-1`, `high`

**Description:**
Translate `Multilanguage.au3` (1,202 lines, 5 functions). Must read existing `Languages/*.ini` files.

**Tasks:**
- [ ] Create `mybot/i18n.py` with:
  - `t(section, key, default, *args)` — main translation function
  - Language auto-detection from system locale
  - Translation caching (dict-based, like original static array)
  - Fallback to English.ini if translation missing
  - `%s` placeholder substitution
  - `\r\n` line break handling
- [ ] Test with all 16 language files

**Acceptance Criteria:**
- Loads all 16 language .ini files without errors
- Cache lookup is O(1)
- Falls back to English for missing keys
- Placeholder substitution works correctly

---

### Issue 1.7: Utility Functions (Phase 1 subset)
**Labels**: `phase-1`, `medium`

**Description:**
Translate Phase 1 utility files from `COCBot/functions/Other/`.

**Tasks:**
- [ ] `mybot/utils/timer.py` — From `StopWatch.au3` (120 lines) + `Time.au3` (160 lines)
- [ ] `mybot/utils/formatting.py` — From `_NumberFormat.au3` (33 lines)
- [ ] `mybot/utils/version.py` — From `CheckVersion.au3` (75 lines)
- [ ] `mybot/utils/prerequisites.py` — From `CheckPrerequisites.au3` (153 lines)
- [ ] `mybot/utils/restart.py` — From `RestartBot.au3` (49 lines)
- [ ] Replace `Base64.au3` with `base64` stdlib (no new file needed)
- [ ] Replace `Json.au3` with `json` stdlib (no new file needed)

---

## Phase 2: Android / Emulator Layer

### Issue 2.1: ADB Client
**Labels**: `phase-2`, `critical`

**Description:**
Create Python ADB client replacing shell calls to `adb.exe`.

**Source**: `ADB.au3` (43 lines) + `LaunchConsole.au3` (409 lines, 16 functions) + ADB calls in `Android.au3`

**Tasks:**
- [ ] Create `mybot/android/adb.py` — `AdbClient` class:
  - `shell(command) -> str`
  - `exec_out(command) -> bytes`
  - `push(local, remote)`, `pull(remote, local)`
  - `tap(x, y)`, `swipe(x1, y1, x2, y2, duration)`
  - Connection management with retries
  - Device serial auto-detection
- [ ] Test with running emulator

---

### Issue 2.2: Emulator Abstraction Layer
**Labels**: `phase-2`, `critical`

**Description:**
Redesign `Android.au3` (5,046 lines, 123 functions) using Strategy pattern.
Replace 49 `Execute()` dynamic dispatch calls with proper class hierarchy.

**Tasks:**
- [ ] Create `mybot/android/base.py` — `BaseEmulator` ABC:
  - `open()`, `close()`, `reboot()`
  - `get_window_handle()`, `get_adb_port()`
  - `adjust_click_coordinates(x, y)`
  - `get_emulator_path()`, `get_instance_name()`
- [ ] Create `mybot/android/bluestacks.py` — From `AndroidBluestacks5.au3` (451 lines, 21 functions)
- [ ] Create `mybot/android/memu.py` — From `AndroidMEmu.au3` (436 lines, 13 functions)
- [ ] Create `mybot/android/nox.py` — From `AndroidNox.au3` (489 lines, 18 functions)
- [ ] Create `mybot/android/manager.py` — Emulator lifecycle (open/close/reboot/detect)
  - Auto-detect running emulator
  - `WaitForAndroidBootCompleted()` equivalent

---

### Issue 2.3: Input Simulation
**Labels**: `phase-2`, `critical`

**Description:**
Translate click/drag/touch functions from `Click.au3` (617 lines, 20 functions) and related files.

**Tasks:**
- [ ] Create `mybot/android/input.py`:
  - `InputMethod` ABC with ADB, minitouch, PostMessage implementations
  - `Click(x, y)`, `PureClick(x, y)`, `GemClick(x, y)`, `BuildingClick(x, y)`
  - `ClickDrag(x1, y1, x2, y2)`
  - `ClickP(point_array)`, `ClickZoneR(zone, offset_x, offset_y)`
  - `ClearScreen()`, `ClickOkay()`, `ClickRemove()`
  - Random offset injection for human-like behavior
- [ ] Test all input methods with running emulator

---

### Issue 2.4: Screen Capture
**Labels**: `phase-2`, `critical`

**Description:**
Translate screenshot capture from `_CaptureRegion.au3` (432 lines, 18 functions).

**Tasks:**
- [ ] Create `mybot/android/capture.py`:
  - `capture_screen(adb) -> np.ndarray` — full screen as BGR numpy array
  - `capture_region(adb, x, y, w, h) -> np.ndarray` — region capture
  - `save_debug_screenshot(img, label)` — from `SaveDebugImage.au3`
  - Replace RGBA→BGRA DllCall with numpy conversion

---

### Issue 2.5: Remaining Android Files
**Labels**: `phase-2`, `high`

**Tasks:**
- [ ] `mybot/android/embed.py` — From `AndroidEmbed.au3` (1,180 lines, 26 functions)
- [ ] `mybot/android/zoom.py` — From `ZoomOut.au3` (571 lines, 10 functions)
- [ ] `mybot/android/position.py` — From `getBSPos.au3` (384 lines)
- [ ] `mybot/android/app.py` — From `Close_OpenCoC.au3` + `UniversalCloseWaitOpenCoC.au3`
- [ ] `mybot/android/health.py` — From `CheckAndroidRebootCondition.au3`, `CheckBotRestartCondition.au3`, `checkAndroidTimeLag.au3`, `checkAndroidPageError.au3`
- [ ] `mybot/android/distributors.py` — From `Distributors.au3` (121 lines)

---

## Phase 3: Vision & Image Recognition

### Issue 3.1: XML Template Loader
**Labels**: `phase-3`, `critical`

**Description:**
Create loader for 2,140+ XML image templates in `imgxml/`.

**Tasks:**
- [ ] Create `mybot/vision/templates.py`:
  - Parse XML format: `<image><data>base64_png</data></image>`
  - Decode base64 → numpy array via `cv2.imdecode()`
  - Parse filename convention: `Name_Level_Rotation.xml`
  - Memory cache with lazy loading
  - Directory-level batch loading
- [ ] Test: load all 2,140+ templates without errors
- [ ] Benchmark: memory usage and load time

---

### Issue 3.2: Template Matching Engine (MBRBot.dll Replacement)
**Labels**: `phase-3`, `critical`

**Description:**
Replace MBRBot.dll's image matching with native opencv-python. This is the **highest risk** task.

**Source**: `imglocAuxiliary.au3` (886 lines, 25 functions), `QuickMIS.au3` (279 lines)

**MBRBot.dll functions to replicate:**
- `SearchMultipleTilesBetweenLevels` → `find_multiple(screenshot, template_dir, search_area, ...)`
- `FindTile` → `find_image(screenshot, template_path, search_area, ...)`
- `SearchRedLines` → `detect_red_lines(screenshot, diamond_area)`
- `GetProperty` → Return metadata from MatchResult object

**Tasks:**
- [ ] Create `mybot/vision/matcher.py`:
  - `find_multiple()` — multi-template search with level filtering
  - `find_image()` — single template search
  - `find_all_matches()` — return all matches above threshold
  - `find_in_village()` — search within village diamond bounds
  - Configurable confidence threshold (default 0.85)
  - Non-maximum suppression to eliminate duplicate matches
- [ ] **Accuracy benchmark**: capture 50+ reference screenshots from AutoIt version, compare Python results
- [ ] Performance target: < 2 seconds for full directory search

---

### Issue 3.3: Red Area / Deployment Zone Detection
**Labels**: `phase-3`, `critical`

**Description:**
Replace MBRBot.dll's red area detection.

**Tasks:**
- [ ] `detect_red_lines()` — `cv2.inRange()` for red color + `cv2.findContours()`
- [ ] `detect_red_area()` — full deployment zone mapping
- [ ] `detect_red_area_near()` — filtered by building type
- [ ] `get_deployable_points()` — geometry calculation
- [ ] `offset_polyline()` — offset redline by distance

---

### Issue 3.4: Pixel Operations
**Labels**: `phase-3`, `high`

**Source**: `COCBot/functions/Pixels/` (1,157 lines, 38 functions)

**Tasks:**
- [ ] Create `mybot/vision/pixel.py`:
  - `pixel_search(img, color, tolerance, region)` — find pixel of color
  - `multi_pixel_search(img, colors, tolerance, region)` — find multiple
  - `check_pixel(img, x, y, color, tolerance)` — verify color at point
  - `get_pixel_color(img, x, y)` — get hex color string
  - `color_check(color1, color2, tolerance)` — compare colors
- [ ] Create `mybot/vision/geometry.py`:
  - `is_inside_diamond(x, y)` — village boundary check
  - `point_in_polygon(point, polygon)` — general poly check

---

### Issue 3.5: OCR System
**Labels**: `phase-3`, `critical`

**Source**: `getOcr.au3` (656 lines, 76 functions)

**Tasks:**
- [ ] Create `mybot/vision/ocr.py`:
  - Generic `read_text(img, region, lang, whitelist)` function
  - 76 specialized wrappers (one per original function):
    - `get_gold_village_search()`, `get_elixir_village_search()`
    - `get_trophy_main_screen()`, `get_builder_count()`
    - `get_remain_train_timer()`, `get_hero_upgrade_time()`
    - ... all 76
  - Image preprocessing pipeline: grayscale → threshold → invert
- [ ] **Accuracy test**: compare OCR results on 20+ reference screenshots vs AutoIt
- [ ] Fallback: if pytesseract insufficient, implement custom character matcher using `listSymbols_coc-*.xml`

---

### Issue 3.6: Specialized Image Detection
**Labels**: `phase-3`, `high`

**Tasks:**
- [ ] `mybot/vision/dead_base.py` — From `checkDeadBase.au3` (343 lines, 8 functions)
- [ ] `mybot/vision/tombs.py` — From `CheckTombs.au3` (304 lines, 4 functions)
- [ ] `mybot/vision/townhall.py` — From `imglocTHSearch.au3` (277 lines, 3 functions)
- [ ] `mybot/vision/walls.py` — From `imglocCheckWall.au3` (155 lines, 2 functions)
- [ ] `mybot/vision/window_detect.py` — From `IsWindowOpen.au3` (163 lines, 4 functions)

---

## Phase 4: Game Logic

### Issue 4.1: Main Screen Detection
**Labels**: `phase-4`, `high`

**Source**: `COCBot/functions/Main Screen/` (1,978 lines, 9 files)

**Tasks:**
- [ ] `mybot/game/main_screen.py` — `checkMainScreen()`, `waitMainScreen()`, `isOnBuilderBase()`
- [ ] `mybot/game/obstacles.py` — `checkObstacles()` (850 lines, 16 functions — handles 20+ popup types)
- [ ] `mybot/system/tray.py` — `RemoveGhostTrayIcons.au3` (646 lines — heavy Win32 API, consider simplifying)
- [ ] `mybot/system/dpi.py` — DPI detection

---

### Issue 4.2: Search System
**Labels**: `phase-4`, `high`

**Source**: `COCBot/functions/Search/` (2,572 lines, 11 files)

**Tasks:**
- [ ] `mybot/search/search.py` — `VillageSearch()` main loop
- [ ] `mybot/search/multi.py` — `multiSearch()` (was DLL wrapper, now calls vision.matcher)
- [ ] `mybot/search/resources.py` — `GetResources()`, `CompareResources()`
- [ ] `mybot/search/filters.py` — `IsSearchAttackEnabled()`, `IsSearchModeActive()`
- [ ] `mybot/search/weak_base.py` — `WeakBase()` defense scanning (621 lines)
- [ ] `mybot/search/clouds.py` — `WaitForClouds()` cloud handling
- [ ] `mybot/search/prepare.py` — `PrepareSearch()`, `CheckZoomOut()`
- [ ] `mybot/search/townhall.py` — `FindTownHall()`

---

### Issue 4.3: Resource Collection
**Labels**: `phase-4`, `high`

**Tasks:**
- [ ] `mybot/village/collect.py` — `Collect()` — find and click all collectors
- [ ] `mybot/village/achievements.py` — `CollectAchievements()`
- [ ] `mybot/village/treasury.py` — `TreasuryCollect()`
- [ ] `mybot/village/magic_items.py` — `FreeMagicItems()`
- [ ] `mybot/village/resources.py` — `isGoldFull()`, `isElixirFull()`, `isDarkElixirFull()`

---

### Issue 4.4: Donations & Requests
**Labels**: `phase-4`, `high`

**Tasks:**
- [ ] `mybot/village/donate.py` — `DonateCC()` (1,955 lines, 20 functions) + `DonateCCWBL()`
- [ ] `mybot/village/request.py` — `RequestCC()` (570 lines, 7 functions)

---

### Issue 4.5: Upgrade System
**Labels**: `phase-4`, `high`

**Tasks:**
- [ ] `mybot/village/upgrade_heroes.py` — From `UpgradeHeroes.au3` (1,863 lines)
- [ ] `mybot/village/upgrade_building.py` — From `UpgradeBuilding.au3` (375 lines)
- [ ] `mybot/village/upgrade_wall.py` — From `UpgradeWall.au3` (354 lines)
- [ ] `mybot/village/auto_upgrade.py` — From `Auto Upgrade.au3` (544 lines)
- [ ] `mybot/village/laboratory.py` — From `Laboratory.au3` (403 lines)
- [ ] `mybot/village/locate.py` — All 7 `Locate*.au3` files
- [ ] `mybot/village/locate_upgrade.py` — From `LocateUpgrade.au3` (448 lines)

---

### Issue 4.6: Special Buildings
**Labels**: `phase-4`, `medium`

**Tasks:**
- [ ] `mybot/village/helper_hut.py` — From `HelperHut.au3` (1,518 lines)
- [ ] `mybot/village/pet_house.py` — From `PetHouse.au3` (944 lines)
- [ ] `mybot/village/blacksmith.py` — From `Blacksmith.au3` (416 lines)
- [ ] `mybot/village/boost_super_troop.py` — From `BoostSuperTroop.au3` (465 lines)
- [ ] `mybot/village/boost.py` — From `BoostBarracks.au3`, `BoostHeroes.au3`, `BoostStructure.au3`

---

### Issue 4.7: Multi-Account System
**Labels**: `phase-4`, `high`

**Tasks:**
- [ ] `mybot/village/switch_account.py` — From `SwitchAccount.au3` (954 lines, 19 functions) + `SwitchAccountVariablesReload.au3` (693 lines)
  - Per-account state isolation
  - Account-specific timers
  - Supercell ID switching via image matching

---

### Issue 4.8: Clan Features
**Labels**: `phase-4`, `medium`

**Tasks:**
- [ ] `mybot/village/clan_capital.py` — From `ClanCapital.au3` (1,720 lines, 26 functions)
- [ ] `mybot/village/clan_games.py` — From `ClanGames.au3` (2,802 lines, 33 functions)
- [ ] `mybot/village/daily_challenges.py` — From `DailyChallenges.au3` (201 lines)

---

### Issue 4.9: Builder Base
**Labels**: `phase-4`, `medium`

**Tasks:**
- [ ] All 10 `BuilderBase/*.au3` files → `mybot/village/builder_base/` (10 Python files)
- [ ] `mybot/village/switch_base.py` — Home ↔ Builder Base switching

---

### Issue 4.10: Village Utilities
**Labels**: `phase-4`, `low`

**Tasks:**
- [ ] Remaining 15+ small village files (VillageReport, GetTownHallLevel, shield, trophies, etc.)

---

## Phase 5: Army & Attack

### Issue 5.1: Army Training System
**Labels**: `phase-5`, `high`

**Tasks:**
- [ ] `mybot/army/train.py` — `TrainSystem()` orchestrator (1,607 lines, 39 functions)
- [ ] `mybot/army/quick_train.py` — `QuickTrain()` (583 lines)
- [ ] `mybot/army/double_train.py` — `DoubleTrain()` (353 lines)
- [ ] `mybot/army/army_overview.py` — `OpenArmyOverview()` (314 lines)
- [ ] `mybot/army/train_siege.py` — `TrainSiege()` (209 lines)
- [ ] `mybot/army/train_it.py` — `TrainIt()` (161 lines)
- [ ] Remaining training files (check_camp, check_full, smart_wait, train_click)

---

### Issue 5.2: Army Reading (Detect Current Composition)
**Labels**: `phase-5`, `high`

**Tasks:**
- [ ] `mybot/army/read_troops.py` — 3 files for troop reading
- [ ] `mybot/army/read_spells.py` — 4 files for spell reading
- [ ] `mybot/army/read_heroes.py` — 2 files (2,357 lines combined — hero detection is complex)
- [ ] `mybot/army/read_siege.py` — 1 file for siege machines
- [ ] `mybot/army/read_cc.py` — 5 files for CC contents

---

### Issue 5.3: CSV Attack Script Engine
**Labels**: `phase-5`, `critical`

**Description:**
Rewrite the CSV attack parser to eliminate `Assign()`/`Eval()` usage. Use dict-based vector storage.

**Source**: `AttackCSV/` (14 files, ~2,500 lines)

**Tasks:**
- [ ] `mybot/attack/csv/parser.py` — Parse all CSV commands (NOTE, SIDE, SIDEB, MAKE, DROP, WAIT)
  - Replace `Assign("ATTACKVECTOR_X", array)` with `vectors["X"] = array`
  - Replace `Execute("$ATTACKVECTOR_X[i]")` with `vectors["X"][i]`
- [ ] `mybot/attack/csv/executor.py` — Execute parsed commands
- [ ] All supporting CSV files (drop, drop_points, drop_line, sides, settings, validate, slice, geometry, debug, clean)
- [ ] **Test all 20+ existing CSV scripts** — verify same troop deployment as AutoIt

---

### Issue 5.4: Attack Algorithms
**Labels**: `phase-5`, `high`

**Tasks:**
- [ ] `mybot/attack/algorithms/smart_farm.py` — `SmartFarm()` (950 lines, 10 functions)
- [ ] `mybot/attack/algorithms/csv_attack.py` — `Algorithm_AttackCSV()` (949 lines)
- [ ] `mybot/attack/algorithms/all_troops.py` — `algorithm_AllTroops()` (559 lines)

---

### Issue 5.5: Red Area & Deployment
**Labels**: `phase-5`, `high`

**Tasks:**
- [ ] `mybot/attack/red_area.py` — From `_GetRedArea.au3` (468 lines)
- [ ] `mybot/attack/geometry.py` — From 8 RedArea geometry files (~500 lines)
- [ ] `mybot/attack/location.py` — From `GetLocation.au3` (473 lines, 12 DllCallMyBot calls)
- [ ] `mybot/attack/deploy.py` — From DropTroop, DropOnPixel, DropOnEdge files

---

### Issue 5.6: Troop & Hero Management
**Labels**: `phase-5`, `high`

**Tasks:**
- [ ] `mybot/attack/heroes.py` — Hero deployment + health monitoring (442 lines combined)
- [ ] `mybot/attack/launch.py` — `LaunchTroop()` (269 lines)
- [ ] `mybot/attack/drop_order.py` — `DropOrderTroops()` (241 lines)
- [ ] Remaining troop files (select, CC drop, old drop, slot index)

---

### Issue 5.7: Attack Coordination & Modes
**Labels**: `phase-5`, `high`

**Tasks:**
- [ ] `mybot/attack/cycle.py` — `AttackCycle()` coordinator
- [ ] `mybot/attack/prepare.py` — `PrepareAttack()` (463 lines)
- [ ] `mybot/attack/attack_bar.py` — `GetAttackBar()` (513 lines)
- [ ] `mybot/attack/return_home.py` — `ReturnHome()` (424 lines)
- [ ] `mybot/attack/report.py` — `AttackReport()` (292 lines)
- [ ] Attack modes: BB spam, CC spam, direct, ranked, revenge (5 files)

---

### Issue 5.8: Smart Zap & Builder Base Attack
**Labels**: `phase-5`, `medium`

**Tasks:**
- [ ] Smart Zap: `smartZap.au3`, `drillSearch.au3`, `easyPreySearch.au3`
- [ ] Builder Base: `AttackBB.au3`, `PrepareAttackBB.au3`, `GetAttackBarBB.au3`

---

## Phase 6: GUI & Application

### Issue 6.1: Application Entry Point & Bot Controller
**Labels**: `phase-6`, `critical`

**Tasks:**
- [ ] `mybot/app.py` — `App` class: CLI args, init subsystems, launch GUI
- [ ] `mybot/bot.py` — `Bot` class: `start()`, `stop()`, `run()`, `search_mode()`
- [ ] `mybot/watchdog.py` — Watchdog process for crash recovery
- [ ] `mybot/__main__.py` — `python -m mybot` entry point

---

### Issue 6.2: PyQt6 Main Window
**Labels**: `phase-6`, `high`

**Tasks:**
- [ ] `mybot/gui/main_window.py` — QMainWindow with tabbed layout
- [ ] `mybot/gui/bottom_bar.py` — Start/Stop/Pause buttons, status indicators
- [ ] `mybot/gui/log_widget.py` — QTextEdit with colored log messages
- [ ] `mybot/gui/splash.py` — Loading splash screen

---

### Issue 6.3: Village Tab (5 subtabs)
**Labels**: `phase-6`, `high`

**Tasks:**
- [ ] Donate subtab (3,966 lines source — largest GUI file)
- [ ] Misc subtab (1,030 lines)
- [ ] Upgrade subtab (975 lines)
- [ ] Notify subtab (212 lines)
- [ ] Achievements subtab (105 lines)

---

### Issue 6.4: Bot Tab (5 subtabs)
**Labels**: `phase-6`, `medium`

**Tasks:**
- [ ] Stats subtab (1,960 lines)
- [ ] Options subtab (261 lines)
- [ ] Debug subtab (201 lines)
- [ ] Profiles subtab (193 lines)
- [ ] Android subtab (188 lines)

---

### Issue 6.5: Attack Tab (12+ subtabs)
**Labels**: `phase-6`, `high`

**Tasks:**
- [ ] Troops subtab (1,760 lines)
- [ ] All search subtabs (Deadbase, Activebase, Options)
- [ ] All attack subtabs (Standard, Scripted, Smart Farm)
- [ ] End battle subtabs
- [ ] SmartZap subtab
- [ ] Strategies subtab

---

### Issue 6.6: Event Handlers (15 control files)
**Labels**: `phase-6`, `high`

**Tasks:**
- [ ] Translate all 15 GUI control files (listed in Phase 6 of TRANSLATION_PLAN.md)
- [ ] Wire PyQt6 signals/slots to bot logic
- [ ] Config ↔ GUI two-way binding

---

### Issue 6.7: API Server
**Labels**: `phase-6`, `low`

**Tasks:**
- [ ] `mybot/api/server.py` — FastAPI server for external control
- [ ] `mybot/api/client.py` — HTTP client for bot-to-bot IPC
- [ ] Endpoints: `/status`, `/start`, `/stop`, `/config`

---

### Issue 6.8: Multi-Instance Support
**Labels**: `phase-6`, `medium`

**Tasks:**
- [ ] `mybot/gui/mini_window.py` — Mini GUI (from `MBR GUI Design Mini.au3`)
- [ ] `mybot/gui/mini_manager.py` — Multi-instance manager (from `MyBot.run.MiniGui.au3`, 1,482 lines)
- [ ] `mybot/multi_bot.py` — Multi-instance launcher (from `MultiBot.au3`, 1,324 lines)

---

## Cross-Cutting Issues

### Issue X.1: Integration Testing Framework
**Labels**: `testing`, `all-phases`

**Tasks:**
- [ ] Set up test screenshot fixtures (capture from running AutoIt version)
- [ ] Create comparison framework: run both AutoIt and Python, diff results
- [ ] CSV attack script regression tests (all 20+ scripts)
- [ ] Config round-trip tests
- [ ] OCR accuracy benchmarks

---

### Issue X.2: Performance Benchmarking
**Labels**: `performance`, `phase-3`

**Tasks:**
- [ ] Benchmark template matching speed (target: < 2s per directory)
- [ ] Benchmark screenshot capture latency (target: < 200ms)
- [ ] Benchmark OCR speed (target: < 500ms per region)
- [ ] Memory profiling (template cache size with 2,140+ templates)
- [ ] Compare overall bot cycle time: AutoIt vs Python

---

### Issue X.3: Documentation
**Labels**: `docs`, `phase-6`

**Tasks:**
- [ ] API documentation (auto-generated from FastAPI)
- [ ] Configuration guide (all INI settings documented)
- [ ] Developer setup guide
- [ ] Architecture overview with diagrams
- [ ] CSV attack script authoring guide
