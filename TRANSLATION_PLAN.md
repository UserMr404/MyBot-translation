# MyBot AutoIt → Python Translation Plan

## Overview

| Metric | Value |
|--------|-------|
| Source language | AutoIt 3 (.au3) |
| Target language | Python 3.12+ |
| Total source files | 577 .au3 files |
| Total lines of code | ~219,000 |
| Estimated effort | 6 phases |

### Goals
1. Translate MyBot from AutoIt 3 to idiomatic Python
2. Preserve all existing functionality (emulator control, image recognition, attack logic, GUI)
3. Improve maintainability with Python's ecosystem (type hints, testing, packaging)
4. Maintain backward compatibility with existing config INI files, CSV attack scripts, and imgxml templates

### Non-Goals (initially)
- Rewriting the image recognition engine (keep OpenCV, replace MBRBot.dll calls with opencv-python)
- Changing the CSV attack script format
- Redesigning the GUI (translate first, modernize later)

---

## Technology Stack (Proposed)

| Component | AutoIt (Current) | Python (Target) | Rationale |
|-----------|-----------------|-----------------|-----------|
| GUI | AutoIt native GUI | PyQt6 or Dear PyGui | PyQt6 for full-featured desktop GUI; Dear PyGui for lighter weight |
| Image recognition | MBRBot.dll + OpenCV 2.2 DLLs | opencv-python (4.x) | Native Python bindings, actively maintained |
| ADB communication | Shell calls to adb.exe | pure-python-adb or adb-shell | Eliminates subprocess overhead, better error handling |
| OCR | Custom XML symbol matching | Tesseract (pytesseract) or EasyOCR | Battle-tested OCR libraries |
| Config | INI files (AutoIt IniRead/Write) | configparser (stdlib) | Drop-in INI compatibility |
| HTTP/API | libcurl.dll | requests / FastAPI | requests for client, FastAPI for bot API server |
| JSON | Newtonsoft.Json.dll | json (stdlib) | Built-in |
| Database | sqlite3.dll | sqlite3 (stdlib) | Built-in |
| Logging | Custom SetLog() | logging (stdlib) | Standard Python logging with handlers |
| Process mgmt | AutoIt Process functions | subprocess / psutil | Better process control |
| Notifications | curl.exe calls | requests + apprise | Multi-platform notification library |
| Crypto | AutoIt Crypt functions | cryptography | Industry standard |
| Scheduling | Timer-based loops | asyncio or APScheduler | Modern async patterns |

---

## Phase Breakdown

### Phase 1: Foundation & Infrastructure (Priority: CRITICAL)
**Lines: ~7,000 | Files to create: ~15**

Set up the Python project structure and translate core infrastructure that everything else depends on.

#### 1.1 Project Scaffolding
- [ ] Create Python project structure with `pyproject.toml`
- [ ] Set up virtual environment and dependency management (uv or poetry)
- [ ] Configure linting (ruff), formatting (black), type checking (mypy)
- [ ] Set up pytest framework
- [ ] Create CI pipeline (GitHub Actions)

#### 1.2 Global Variables → Python Module
**Source**: `COCBot/MBR Global Variables.au3` (187 KB, ~5,800 lines)

This is the single largest file. Translate to:
- `mybot/constants.py` — Enums, game dimensions, color codes
- `mybot/config/models.py` — Dataclasses/Pydantic models for config state
- `mybot/state.py` — Runtime state (replaces mutable globals)

Key translations:
```
AutoIt: Global $g_bRunState = False
Python: class BotState:
            run_state: bool = False
```

#### 1.3 Configuration System
**Source**: `COCBot/functions/Config/` (6,594 lines, 8 files)

- [ ] `mybot/config/reader.py` — Translate `readConfig.au3` (INI → dataclass)
- [ ] `mybot/config/writer.py` — Translate `saveConfig.au3`
- [ ] `mybot/config/applier.py` — Translate `applyConfig.au3`
- [ ] `mybot/config/coordinates.py` — Translate `ScreenCoordinates.au3`
- [ ] `mybot/config/image_dirs.py` — Translate `ImageDirectories.au3`
- [ ] `mybot/config/delays.py` — Translate `DelayTimes.au3`
- [ ] `mybot/config/profiles.py` — Translate `profileFunctions.au3`

#### 1.4 Logging System
**Source**: `COCBot/functions/Other/SetLog.au3`

- [ ] `mybot/logging.py` — Python logging with colored output, file rotation
- [ ] Preserve log color constants ($COLOR_ERROR, etc.)

#### 1.5 Sleep / Control Flow
**Source**: `COCBot/functions/Other/_Sleep.au3`

- [ ] `mybot/utils/sleep.py` — Cancellable sleep that checks `BotState.run_state`
- [ ] Consider `asyncio.sleep()` with cancellation support

#### 1.6 Translation / i18n
**Source**: `COCBot/functions/Other/Multilanguage.au3`

- [ ] `mybot/i18n.py` — Read existing `.ini` language files
- [ ] Maintain compatibility with current `Languages/*.ini` format
- [ ] Cache translations in dict (same pattern as current static array)

**Deliverable**: A Python project that can load config, log messages, and read translations.

---

### Phase 2: Android / Emulator Layer (Priority: CRITICAL)
**Lines: ~9,455 | Files to create: ~10**

The emulator layer is the second dependency — everything interacts with the Android device.

#### 2.1 ADB Communication
**Source**: `COCBot/functions/Other/ADB.au3`

- [ ] `mybot/android/adb.py` — ADB wrapper using pure-python-adb
- [ ] Screen capture via `adb exec-out screencap`
- [ ] Touch/swipe input via ADB or minitouch
- [ ] Shell command execution
- [ ] Device connection management

#### 2.2 Emulator Abstraction
**Source**: `COCBot/functions/Android/` (15 files)

- [ ] `mybot/android/base.py` — Abstract emulator interface
- [ ] `mybot/android/bluestacks.py` — BlueStacks 5 implementation
- [ ] `mybot/android/memu.py` — MEmu implementation
- [ ] `mybot/android/nox.py` — Nox implementation
- [ ] `mybot/android/manager.py` — Emulator open/close/reboot/detect
- [ ] `mybot/android/embed.py` — Window embedding (win32gui)

#### 2.3 Input Simulation
**Source**: `COCBot/functions/Other/Click.au3`, `ClickDrag.au3`

- [ ] `mybot/android/input.py` — Click, drag, swipe via ADB
- [ ] Coordinate translation for different resolutions
- [ ] Random offset injection (human-like behavior)

#### 2.4 Screen Capture
**Source**: `COCBot/functions/Pixels/_CaptureRegion.au3`, `COCBot/functions/Other/MakeScreenshot.au3`

- [ ] `mybot/android/capture.py` — Screenshot capture to numpy array
- [ ] Region-based capture
- [ ] Debug screenshot saving

**Deliverable**: Python can connect to emulator, capture screens, send touches.

---

### Phase 3: Image Recognition & Pixel Detection (Priority: CRITICAL)
**Lines: ~3,560 | Files to create: ~8**

Replace MBRBot.dll image matching with native opencv-python.

#### 3.1 Template Matching
**Source**: `COCBot/functions/Image Search/` (7 files)

- [ ] `mybot/vision/template.py` — OpenCV template matching (replaces MBRBot.dll `findMultiple`)
- [ ] Load base64-encoded XML templates → numpy arrays
- [ ] Multi-scale matching with rotation support
- [ ] Confidence threshold filtering
- [ ] Return match coordinates compatible with existing code

#### 3.2 Pixel Operations
**Source**: `COCBot/functions/Pixels/` (8 files, 1,157 lines)

- [ ] `mybot/vision/pixel.py` — Pixel color reading, search, comparison
- [ ] `mybot/vision/region.py` — Region-based pixel scanning
- [ ] `mybot/vision/geometry.py` — Diamond boundary checks, point-in-polygon

#### 3.3 OCR
**Source**: `COCBot/functions/Read Text/` (4 files, 912 lines)

- [ ] `mybot/vision/ocr.py` — Text recognition (pytesseract or EasyOCR)
- [ ] `mybot/vision/building_info.py` — Building info extraction
- [ ] Number reading (resources, timers, costs)
- [ ] Game font training data if needed

#### 3.4 XML Template Loader
- [ ] `mybot/vision/templates.py` — Parse `imgxml/**/*.xml` files
- [ ] Decode base64 images to OpenCV format
- [ ] Cache loaded templates in memory
- [ ] Preserve directory structure mapping

**Deliverable**: Python can detect game elements, read text, match templates from existing imgxml files.

---

### Phase 4: Game Logic — Village & Search (Priority: HIGH)
**Lines: ~28,000 | Files to create: ~40**

Translate the core gameplay logic. This is the largest phase.

#### 4.1 Main Screen Detection
**Source**: `COCBot/functions/Main Screen/` (9 files, 1,978 lines)

- [ ] `mybot/game/main_screen.py` — Check/wait for main screen
- [ ] `mybot/game/obstacles.py` — Detect and dismiss popups
- [ ] `mybot/game/builder_base.py` — Builder Base detection

#### 4.2 Village Management
**Source**: `COCBot/functions/Village/` (53 files, 25,434 lines)

Break into submodules:
- [ ] `mybot/village/collect.py` — Resource collection
- [ ] `mybot/village/report.py` — Village status report
- [ ] `mybot/village/donate.py` — CC donations
- [ ] `mybot/village/request.py` — CC requests
- [ ] `mybot/village/laboratory.py` — Lab upgrades
- [ ] `mybot/village/upgrades.py` — Building/wall/hero upgrades
- [ ] `mybot/village/auto_upgrade.py` — Automatic upgrade selection
- [ ] `mybot/village/switch_account.py` — Multi-account switching
- [ ] `mybot/village/boost.py` — Boosting (barracks, super troops, structures)
- [ ] `mybot/village/free_items.py` — Trader/magic items
- [ ] `mybot/village/clan_capital.py` — Clan Capital
- [ ] `mybot/village/special_buildings.py` — Blacksmith, Pet House, Helper Hut
- [ ] `mybot/village/builder_base/` — BB-specific operations
- [ ] `mybot/village/clan_games.py` — Clan Games
- [ ] `mybot/village/daily_challenges.py` — Daily challenges

#### 4.3 Search System
**Source**: `COCBot/functions/Search/` (11 files, 2,572 lines)

- [ ] `mybot/search/village_search.py` — Main search loop
- [ ] `mybot/search/townhall.py` — TH detection
- [ ] `mybot/search/resources.py` — Loot reading and comparison
- [ ] `mybot/search/filters.py` — Base filtering (weak base, dead base)
- [ ] `mybot/search/clouds.py` — Cloud waiting

**Deliverable**: Python can manage village, search for bases, collect resources.

---

### Phase 5: Army & Attack Systems (Priority: HIGH)
**Lines: ~21,000 | Files to create: ~30**

#### 5.1 Army Training
**Source**: `COCBot/functions/CreateArmy/` (30+ files, 7,070 lines)

- [ ] `mybot/army/train.py` — Training orchestrator (TrainSystem)
- [ ] `mybot/army/quick_train.py` — Quick train mode
- [ ] `mybot/army/check.py` — Army readiness checks
- [ ] `mybot/army/composition.py` — Troop/spell/siege reading
- [ ] `mybot/army/cc.py` — CC troops/spells reading

#### 5.2 Attack Execution
**Source**: `COCBot/functions/Attack/` (50+ files, 13,561 lines)

- [ ] `mybot/attack/cycle.py` — Attack cycle coordinator (from MOD/)
- [ ] `mybot/attack/prepare.py` — Pre-attack setup
- [ ] `mybot/attack/deploy.py` — Troop deployment
- [ ] `mybot/attack/red_area.py` — Red area detection
- [ ] `mybot/attack/troops.py` — Troop dropping, hero deployment
- [ ] `mybot/attack/csv_parser.py` — CSV attack script parser
- [ ] `mybot/attack/csv_executor.py` — CSV attack executor
- [ ] `mybot/attack/algorithms/` — All troops, smart farm
- [ ] `mybot/attack/smart_zap.py` — Dark elixir zapping
- [ ] `mybot/attack/builder_base.py` — BB attacks
- [ ] `mybot/attack/special.py` — Direct, ranked, revenge attacks

**Deliverable**: Python can train armies and execute attacks including CSV scripts.

---

### Phase 6: GUI & Application Shell (Priority: MEDIUM)
**Lines: ~50,000+ | Files to create: ~30**

#### 6.1 Main Application
**Source**: `MyBot.run.au3`, `MBR GUI Action.au3`

- [ ] `mybot/app.py` — Application entry point
- [ ] `mybot/bot.py` — Bot controller (start/stop/search mode)
- [ ] `mybot/watchdog.py` — Watchdog process

#### 6.2 GUI Translation
**Source**: `COCBot/GUI/` (63 files) + `MBR GUI Design.au3` + `MBR GUI Control.au3`

This is the most labor-intensive part due to AutoIt's GUI being tightly coupled.

- [ ] `mybot/gui/main_window.py` — Main window with tabs
- [ ] `mybot/gui/tabs/village.py` — Village tab
- [ ] `mybot/gui/tabs/attack.py` — Attack tab
- [ ] `mybot/gui/tabs/bot.py` — Bot options tab
- [ ] `mybot/gui/tabs/log.py` — Log display
- [ ] `mybot/gui/tabs/about.py` — About tab
- [ ] `mybot/gui/widgets/` — Reusable widgets
- [ ] `mybot/gui/controls.py` — Event handlers
- [ ] `mybot/gui/splash.py` — Splash screen
- [ ] `mybot/gui/mini.py` — Mini GUI (from MiniGui.au3)

#### 6.3 API Server
**Source**: `COCBot/functions/Other/Api.au3`, `ApiClient.au3`, `ApiHost.au3`

- [ ] `mybot/api/server.py` — FastAPI-based control API
- [ ] `mybot/api/models.py` — Request/response models

#### 6.4 Notifications
**Source**: `COCBot/functions/Other/Notify.au3`

- [ ] `mybot/notifications.py` — Push notification support via apprise

**Deliverable**: Full working Python application with GUI.

---

## Proposed Python Project Structure

```
mybot/
├── pyproject.toml
├── README.md
├── mybot/
│   ├── __init__.py
│   ├── app.py                    # Entry point
│   ├── bot.py                    # Bot controller
│   ├── constants.py              # Enums, game constants
│   ├── state.py                  # Runtime state
│   ├── i18n.py                   # Translation system
│   ├── watchdog.py               # Watchdog process
│   ├── notifications.py          # Push notifications
│   ├── config/
│   │   ├── models.py             # Config dataclasses
│   │   ├── reader.py             # INI reader
│   │   ├── writer.py             # INI writer
│   │   ├── applier.py            # Config → state
│   │   ├── coordinates.py        # Screen coordinates
│   │   ├── delays.py             # Delay constants
│   │   ├── image_dirs.py         # Image template paths
│   │   └── profiles.py           # Profile management
│   ├── android/
│   │   ├── adb.py                # ADB communication
│   │   ├── base.py               # Emulator interface
│   │   ├── bluestacks.py         # BlueStacks impl
│   │   ├── memu.py               # MEmu impl
│   │   ├── nox.py                # Nox impl
│   │   ├── manager.py            # Emulator lifecycle
│   │   ├── embed.py              # Window embedding
│   │   ├── input.py              # Touch/click/drag
│   │   └── capture.py            # Screen capture
│   ├── vision/
│   │   ├── template.py           # OpenCV template matching
│   │   ├── pixel.py              # Pixel operations
│   │   ├── region.py             # Region scanning
│   │   ├── geometry.py           # Boundary checks
│   │   ├── ocr.py                # Text recognition
│   │   ├── building_info.py      # Building info reader
│   │   └── templates.py          # XML template loader
│   ├── game/
│   │   ├── main_screen.py        # Main screen checks
│   │   ├── obstacles.py          # Popup handling
│   │   └── builder_base.py       # BB detection
│   ├── village/
│   │   ├── collect.py            # Resource collection
│   │   ├── report.py             # Village report
│   │   ├── donate.py             # CC donation
│   │   ├── request.py            # CC request
│   │   ├── laboratory.py         # Lab upgrades
│   │   ├── upgrades.py           # Building upgrades
│   │   ├── auto_upgrade.py       # Auto upgrade
│   │   ├── switch_account.py     # Account switching
│   │   ├── boost.py              # Boosting
│   │   ├── free_items.py         # Magic items
│   │   ├── clan_capital.py       # Clan Capital
│   │   ├── clan_games.py         # Clan Games
│   │   ├── daily_challenges.py   # Challenges
│   │   └── builder_base/         # BB village ops
│   ├── army/
│   │   ├── train.py              # Training system
│   │   ├── quick_train.py        # Quick train
│   │   ├── check.py              # Army checks
│   │   ├── composition.py        # Read army
│   │   └── cc.py                 # CC troops
│   ├── search/
│   │   ├── village_search.py     # Search loop
│   │   ├── townhall.py           # TH detection
│   │   ├── resources.py          # Loot reading
│   │   ├── filters.py            # Base filtering
│   │   └── clouds.py             # Cloud handling
│   ├── attack/
│   │   ├── cycle.py              # Attack cycle
│   │   ├── prepare.py            # Pre-attack
│   │   ├── deploy.py             # Deployment
│   │   ├── red_area.py           # Red area
│   │   ├── troops.py             # Troop management
│   │   ├── csv_parser.py         # CSV parser
│   │   ├── csv_executor.py       # CSV executor
│   │   ├── smart_zap.py          # Zap attacks
│   │   ├── builder_base.py       # BB attack
│   │   ├── special.py            # Special modes
│   │   └── algorithms/           # Attack algorithms
│   ├── gui/
│   │   ├── main_window.py        # Main GUI window
│   │   ├── controls.py           # Event handlers
│   │   ├── splash.py             # Splash screen
│   │   ├── mini.py               # Mini GUI
│   │   ├── tabs/                 # Tab implementations
│   │   └── widgets/              # Reusable widgets
│   ├── api/
│   │   ├── server.py             # FastAPI server
│   │   └── models.py             # API models
│   └── utils/
│       ├── sleep.py              # Cancellable sleep
│       ├── process.py            # Process management
│       └── encoding.py           # Base64, JSON helpers
├── tests/                        # pytest test suite
├── Languages/                    # Existing .ini translations (reused)
├── CSV/Attack/                   # Existing CSV scripts (reused)
├── imgxml/                       # Existing templates (reused)
└── images/                       # Existing UI graphics
```

---

## AutoIt → Python Translation Patterns

### Common Conversions

| AutoIt | Python |
|--------|--------|
| `Global $g_var = value` | `class State: var: type = value` |
| `Local $var = value` | `var: type = value` |
| `Func name()` / `EndFunc` | `def name():` |
| `If ... Then` / `EndIf` | `if ...:` |
| `For $i = 0 To $n` | `for i in range(n + 1):` |
| `While ... WEnd` | `while ...:` |
| `Switch ... EndSwitch` | `match ... case` (3.10+) |
| `Dim $arr[n]` | `arr: list = [None] * n` |
| `IniRead()` | `configparser.get()` |
| `StringInStr()` | `str.find()` or `in` |
| `StringSplit()` | `str.split()` |
| `MsgBox()` | `QMessageBox` (PyQt6) |
| `GUICtrlCreateButton()` | `QPushButton()` (PyQt6) |
| `DllCall()` | `ctypes` or native Python lib |
| `_ArrayShuffle()` | `random.shuffle()` |
| `Execute()` | `eval()` (avoid) or dispatch dict |
| `#include "file.au3"` | `from module import ...` |
| `$array[$enum]` | `dataclass.field` or `dict[enum]` |

### Patterns to Modernize

| AutoIt Pattern | Python Improvement |
|---------------|-------------------|
| Global mutable state | Dependency injection, state objects |
| Flag-based restart checking | `asyncio` cancellation or threading events |
| Numeric enums (`$eTroopBarbarian = 0`) | `enum.IntEnum` or `enum.Enum` |
| INI section/key string matching | Typed config models with validation |
| Manual error checking | Exception handling with context managers |
| Sleep-based polling | `asyncio.Event.wait()` or threading conditions |
| String-based function dispatch | First-class functions, strategy pattern |

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| MBRBot.dll replacement | HIGH — core image matching | Prototype opencv-python matching first, validate accuracy against AutoIt version |
| GUI complexity | HIGH — 63 GUI files, tightly coupled | Start with CLI/headless mode, add GUI incrementally |
| OCR accuracy | MEDIUM — custom symbol matching | Test pytesseract/EasyOCR against game screenshots before committing |
| ADB timing | MEDIUM — race conditions | Add proper async/await, connection retry logic |
| Windows-specific APIs | MEDIUM — win32gui, WMI | Use pywin32, keep Windows-only for now, abstract for future cross-platform |
| Config compatibility | LOW — INI format unchanged | configparser reads same format, add migration tests |
| CSV compatibility | LOW — format unchanged | Parse identically, add unit tests for each CSV script |

---

## Migration Strategy

### Approach: **Strangler Fig** (incremental replacement)

Rather than a full rewrite, build Python modules alongside AutoIt and gradually shift:

1. **Phase 1-3** can be developed and tested independently (no GUI needed)
2. Start with a **headless/CLI mode** that runs the bot without GUI
3. Add GUI in Phase 6 after core logic is verified
4. Each phase produces a testable, runnable subset
5. Validate each phase against the AutoIt version by comparing behavior on same game state

### Testing Strategy
- **Unit tests** for each translated module (config parsing, coordinate math, template loading)
- **Integration tests** with emulator screenshots (captured reference images)
- **Comparison tests** — run both AutoIt and Python versions, compare outputs
- **CSV attack tests** — verify CSV parser produces identical drop sequences

---

## Dependencies (pyproject.toml)

```toml
[project]
name = "mybot"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "opencv-python>=4.9",
    "numpy>=1.26",
    "Pillow>=10.0",
    "PyQt6>=6.6",
    "pure-python-adb>=0.3",
    "pytesseract>=0.3",
    "requests>=2.31",
    "fastapi>=0.109",
    "uvicorn>=0.27",
    "apprise>=1.7",
    "psutil>=5.9",
    "pywin32>=306",
    "cryptography>=42.0",
    "pydantic>=2.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.2",
    "mypy>=1.8",
    "black>=24.1",
    "pre-commit>=3.6",
]
```

---

## Phase Execution Order & Priority

```
Phase 1: Foundation ──────► Phase 2: Android ──────► Phase 3: Vision
   (config, logging,          (ADB, emulators,        (OpenCV, OCR,
    state, i18n)               input, capture)          templates)
                                                            │
                              ┌─────────────────────────────┤
                              ▼                             ▼
                    Phase 4: Game Logic          Phase 5: Army & Attack
                    (village, search,            (training, deployment,
                     collection)                  CSV scripts)
                              │                             │
                              └──────────┬──────────────────┘
                                         ▼
                              Phase 6: GUI & App Shell
                              (PyQt6 GUI, API server,
                               entry point, watchdog)
```

Phases 4 and 5 can be developed **in parallel** once Phases 1-3 are complete.
