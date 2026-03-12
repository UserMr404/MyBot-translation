# MyBot AutoIt → Python Translation Plan

> **Living document** — Updated as translation progresses.
> Generated from exhaustive static analysis of 577 .au3 files, 5,924 functions, ~219,000 lines of code.

---

## 1. Overview

| Metric | Value |
|--------|-------|
| Source language | AutoIt 3 (.au3) |
| Target language | Python 3.12+ |
| Source files | 577 .au3 files |
| Total lines of code | ~219,000 |
| Unique functions | 5,924 |
| Global variables | 852 (in `MBR Global Variables.au3`) |
| GUI controls | 3,775 (984 labels, 762 icons, 596 checkboxes, 243 inputs, 192 buttons, ...) |
| GUI event handlers | 759 `GUISetOnEvent`/`GUICtrlSetOnEvent` calls |
| DllCall invocations | 244 across 16 Windows DLLs |
| MBRBot.dll API calls | 16 unique functions (image matching, OCR, red area detection) |
| IniRead/IniWrite calls | 809 (configuration persistence) |
| Image templates (imgxml/) | 2,140+ XML files across 227 subdirectories |
| Translation strings | 16 language .ini files |
| CSV attack scripts | 20+ pre-made scripts |
| Estimated phases | 6 phases |
| Translation difficulty | 8/10 (complex Windows desktop app with DLL interop) |

### Goals

1. Translate MyBot from AutoIt 3 to **idiomatic Python** — not a line-by-line port
2. Preserve all existing functionality
3. Maintain backward compatibility with existing config INI files, CSV attack scripts, imgxml templates, and language .ini files
4. Replace MBRBot.dll (proprietary .NET) with native `opencv-python` calls
5. Improve maintainability: type hints, unit tests, proper packaging

### Non-Goals (initially)

- Changing the CSV attack script format
- Changing the imgxml template format
- Redesigning the GUI layout (translate first, modernize later)
- Cross-platform support (stay Windows-only initially, abstract later)

---

## 2. Codebase Metrics by Directory

### Lines of Code by Module

| Directory | Files | Lines | Functions | Complexity |
|-----------|-------|-------|-----------|------------|
| `COCBot/functions/Village/` | 53+ | 25,434 | 200+ | HIGH — largest module, many interdependencies |
| `COCBot/functions/Attack/` | 50+ | 13,561 | 150+ | HIGH — complex deployment algorithms |
| `COCBot/functions/Other/` | 60 | 13,562 | 280+ | MEDIUM — utilities, mostly independent |
| `COCBot/functions/Android/` | 15 | 9,455 | 239 | HIGH — platform-specific, DLL-heavy |
| `COCBot/functions/CreateArmy/` | 30+ | 7,070 | 110+ | MEDIUM — training orchestration |
| `COCBot/functions/Config/` | 8 | 6,594 | 153 | LOW — repetitive INI read/write |
| `COCBot/functions/Search/` | 11 | 2,572 | 58 | MEDIUM — search pipeline |
| `COCBot/functions/Image Search/` | 7 | 2,407 | 48 | CRITICAL — DLL replacement needed |
| `COCBot/functions/Main Screen/` | 9 | 1,978 | 46 | LOW — state checks |
| `COCBot/functions/Pixels/` | 8 | 1,157 | 38 | LOW — pixel utilities |
| `COCBot/functions/Read Text/` | 4 | 912 | 79 | CRITICAL — OCR replacement needed |
| `COCBot/functions/MOD/` | 6 | 644 | 6 | LOW — thin orchestration wrappers |
| `COCBot/GUI/` | 63 | ~22,000 | 500+ | HIGH — tightly coupled to AutoIt GUI |
| Top-level `.au3` files | 8 | ~10,800 | 250+ | HIGH — entry points, global state |
| **TOTAL** | **~330 bot files** | **~118,000** | **~2,200** | — |

> Note: Remaining ~100K lines are in `AutoIt/Include/` (standard library UDFs — not translated, replaced by Python stdlib).

### Top 20 Largest Files (Translation Priority)

| # | File | Lines | Funcs | Translation Notes |
|---|------|-------|-------|-------------------|
| 1 | `Android/Android.au3` | 5,046 | 123 | Emulator abstraction — redesign with Strategy pattern |
| 2 | `GUI/Design Child Village - Donate.au3` | 3,966 | 4 | GUI layout — PyQt6 redesign |
| 3 | `Village/Clan Games/ClanGames.au3` | 2,802 | 33 | Complex game logic with image detection |
| 4 | `Config/applyConfig.au3` | 2,422 | 43 | Repetitive — can auto-generate Python |
| 5 | `MBR Global Variables.au3` | 2,332 | 6 | Convert to enums + dataclasses |
| 6 | `MBR GUI Control.au3` | 2,276 | 71 | Event handlers — framework-dependent |
| 7 | `CreateArmy/getArmyHeroCount.au3` | 2,226 | 17 | Image-based hero detection |
| 8 | `GUI/Design Child Bot - Stats.au3` | 1,960 | 6 | Statistics display layout |
| 9 | `Village/DonateCC.au3` | 1,955 | 20 | Donation logic with image matching |
| 10 | `Village/UpgradeHeroes.au3` | 1,863 | 11 | Hero upgrade automation |
| 11 | `GUI/Design Child Attack - Troops.au3` | 1,760 | 12 | Troop selection layout |
| 12 | `Village/ClanCapital.au3` | 1,720 | 26 | Clan Capital management |
| 13 | `GUI/Control Child Army.au3` | 1,608 | 81 | Army tab event handlers |
| 14 | `CreateArmy/TrainSystem.au3` | 1,607 | 39 | Training orchestrator |
| 15 | `MyBot.run.au3` | 1,600 | 20 | Main entry point |
| 16 | `GUI/Control Child Misc.au3` | 1,585 | 98 | Misc tab handlers |
| 17 | `Village/HelperHut.au3` | 1,518 | 7 | Helper Hut automation |
| 18 | `MyBot.run.MiniGui.au3` | 1,482 | 84 | Mini GUI manager |
| 19 | `Config/readConfig.au3` | 1,468 | 44 | INI reading — auto-generate |
| 20 | `Config/saveConfig.au3` | 1,413 | 50 | INI writing — auto-generate |

---

## 3. Dependency Graph (Load Order)

The codebase has **zero circular dependencies** — a clean DAG:

```
MBR Global Variables.au3          ◄── MUST LOAD FIRST (852 globals)
    │
    ├── Config/DelayTimes.au3
    ├── Config/ScreenCoordinates.au3
    ├── Config/ImageDirectories.au3
    │
    ├── Other/MBRFunc.au3           ◄── DLL wrapper (MBRBot.dll)
    ├── Android/Android.au3         ◄── Emulator abstraction
    │
    ├── MBR GUI Design.au3          ◄── GUI layout
    ├── MBR GUI Control.au3         ◄── GUI event handlers
    │
    └── MBR Functions.au3           ◄── MASTER INCLUDE FILE
        ├── Other/ (14 files)       ◄── Base utilities
        ├── Pixels/ (8 files)       ◄── Low-level pixel ops
        ├── Image Search/ (7 files) ◄── OpenCV matching
        ├── Read Text/ (4 files)    ◄── OCR
        ├── Android/ (15 files)     ◄── Emulator layer
        ├── Main Screen/ (9 files)  ◄── Game state checks
        ├── Village/ (53+ files)    ◄── Village management
        ├── Search/ (11 files)      ◄── Enemy search
        ├── Attack/ (50+ files)     ◄── Battle execution
        ├── CreateArmy/ (30+ files) ◄── Army training
        └── Config/ (8 files)       ◄── Settings persistence
            │
            └── MBR References.au3  ◄── MUST LOAD LAST
```

### Shared State — Critical Global Variables

These globals are referenced across many modules and need careful state management in Python:

| Variable | References | Written By | Read By | Python Approach |
|----------|-----------|------------|---------|-----------------|
| `$g_iMidOffsetY` | 1,313 | `getAndroidPos()` | Every pixel/click op | `BotState.screen.mid_offset_y` |
| `$g_bRunState` | 619 | `BotStart/Stop()` | Every `_Sleep()` call | `BotState.running` (threading.Event) |
| `$g_bDebugSetLog` | 464 | Config | `SetLog()`, many funcs | `logging.getLogger().level` |
| `$g_avBuildingUpgrades` | 297 | Village module | Upgrade funcs | `BotState.village.building_upgrades` |
| `$g_iBottomOffsetY` | 270 | `getAndroidPos()` | Pixel/click ops | `BotState.screen.bottom_offset_y` |
| `$g_iMatchMode` | 270 | `VillageSearch()` | Attack funcs | `BotState.search.match_mode` |
| `$g_aiCurrentLoot[]` | 226 | `GetResources()` | Search, Collect, Village | `BotState.village.current_loot` |
| `$g_iTownHallLevel` | 175 | `GetTownHallLevel()` | Many funcs | `BotState.village.th_level` |
| `$g_iCurAccount` | 167 | `SwitchAccount()` | Account-specific ops | `BotState.accounts.current` |
| `$g_bFullArmy` | ~50 | `CheckFullArmy()` | `AttackCycle()`, Train | `BotState.army.is_full` |
| `$g_bRestart` | 65 | Restart conditions | `_Sleep()` | `BotState.restart_requested` |

**Python approach**: Replace 852 mutable globals with a `BotState` class hierarchy using dataclasses, with thread-safe access via `threading.Lock` where needed.

---

## 4. Technology Stack

| Component | AutoIt (Current) | Python (Target) | Rationale |
|-----------|-----------------|-----------------|-----------|
| **GUI** | AutoIt native GUI (3,775 controls) | **PyQt6** | Most capable desktop GUI framework; handles complex tabbed layouts, tree views, custom widgets |
| **Image recognition** | MBRBot.dll + OpenCV 2.2 DLLs | **opencv-python 4.x** | Native Python bindings, actively maintained, replaces proprietary DLL |
| **ADB communication** | Shell calls to `adb.exe` | **pure-python-adb** or **adb-shell** | Eliminates subprocess overhead, better error handling |
| **OCR** | Custom XML symbol matching via MBRBot.dll | **pytesseract** + custom fallback | Battle-tested OCR; custom matcher for game-specific fonts if needed |
| **Config (INI)** | `IniRead()`/`IniWrite()` (809 calls) | **configparser** (stdlib) | Drop-in INI compatibility, same file format |
| **HTTP/API** | libcurl.dll / curl.exe | **requests** (client) + **FastAPI** (server) | Modern Python HTTP stack |
| **JSON** | Custom `Json.au3` via jsmn C parser | **json** (stdlib) | Built-in, faster |
| **Database** | sqlite3.dll | **sqlite3** (stdlib) | Built-in |
| **Logging** | Custom `SetLog()` (370 lines) | **logging** (stdlib) | Standard Python logging with handlers, colors, file rotation |
| **Process mgmt** | AutoIt Process functions + DllCall | **subprocess** + **psutil** | Better process control and monitoring |
| **Notifications** | curl.exe → Telegram API | **requests** + **apprise** | Multi-platform notification library |
| **Crypto** | AutoIt `_Crypt_*` functions | **cryptography** | Industry standard |
| **Window mgmt** | AutoIt `Win*()` + DllCall user32 (251 calls) | **pywin32** (`win32gui`, `win32api`) | Direct Win32 API access |
| **Timers** | `__TimerInit()`/`__TimerDiff()` + waitable timers | **time.perf_counter()** + **threading.Timer** | High-precision timing |
| **Async/events** | `GUIOnEventMode` + `_Sleep()` polling | **threading** + `threading.Event` | Event-driven with cancellable waits |

---

## 5. AutoIt → Python Translation Patterns

### 5.1 Syntax Conversions

| AutoIt | Python | Notes |
|--------|--------|-------|
| `Global $g_var = value` | `class BotState: var: type = value` | Replace globals with state objects |
| `Local $var = value` | `var: type = value` | Local variables |
| `Func Name($p1, $p2)` / `EndFunc` | `def name(p1: type, p2: type) -> type:` | Use snake_case, add type hints |
| `If ... Then` / `ElseIf` / `EndIf` | `if ...:` / `elif ...:` | Standard mapping |
| `For $i = 0 To $n` | `for i in range(n + 1):` | Note: AutoIt `To` is inclusive |
| `For $i = 0 To $n Step 2` | `for i in range(0, n + 1, 2):` | Step parameter |
| `While ... WEnd` | `while ...:` | Direct mapping |
| `Switch $var` / `Case` / `EndSwitch` | `match var:` / `case ...:` | Python 3.10+ match |
| `Select` / `Case` / `EndSelect` | `if/elif/else` chain | No direct equivalent |
| `Dim $arr[n]` | `arr: list = [None] * n` | Or use typed list |
| `Local $arr[3] = [1, 2, 3]` | `arr = [1, 2, 3]` | Direct |
| `$arr[$i][$j]` | `arr[i][j]` | Same indexing |
| `ReDim $arr[n]` | `arr.extend([None] * (n - len(arr)))` | Or use list append |
| `#include "file.au3"` | `from module import ...` | Python imports |
| `#include-once` | _(automatic in Python)_ | Modules imported once by default |
| `True` / `False` | `True` / `False` | Same |
| `Default` | `None` | Default parameter values |
| `@error` | Raise exception or return error | See error handling section |
| `@ScriptDir` | `Path(__file__).parent` | Use `pathlib` |
| `@CRLF` | `"\r\n"` or `os.linesep` | Line endings |
| `@TAB` | `"\t"` | Tab character |

### 5.2 String Operations

| AutoIt | Python | Notes |
|--------|--------|-------|
| `StringInStr($s, $find)` | `$find in s` or `s.find(find)` | `in` for boolean, `.find()` for position |
| `StringLeft($s, $n)` | `s[:n]` | Slicing |
| `StringRight($s, $n)` | `s[-n:]` | Slicing |
| `StringMid($s, $start, $len)` | `s[start-1:start-1+length]` | AutoIt is 1-indexed! |
| `StringLen($s)` | `len(s)` | Direct |
| `StringSplit($s, $delim)` | `s.split(delim)` | AutoIt returns [count, parts...]; Python returns [parts] |
| `StringReplace($s, $old, $new)` | `s.replace(old, new)` | Direct |
| `StringUpper($s)` / `StringLower($s)` | `s.upper()` / `s.lower()` | Direct |
| `StringStripWS($s, 3)` | `s.strip()` | Flag 3 = both sides |
| `StringFormat("%02d", $v)` | `f"{v:02d}"` | f-strings preferred |
| `StringRegExp($s, $pattern, 1)` | `re.findall(pattern, s)` | Flag 1 = return array of matches |
| `StringRegExp($s, $pattern, 0)` | `bool(re.search(pattern, s))` | Flag 0 = boolean match |
| `StringRegExpReplace($s, $p, $r)` | `re.sub(p, r, s)` | Direct |
| `StringToBinary($s, 4)` | `s.encode('utf-8')` | Flag 4 = UTF-8 |
| `BinaryToString($b, 4)` | `b.decode('utf-8')` | Flag 4 = UTF-8 |

### 5.3 Array Operations

| AutoIt | Python | Notes |
|--------|--------|-------|
| `_ArrayShuffle($arr)` | `random.shuffle(arr)` | In-place |
| `_ArraySearch($arr, $val)` | `arr.index(val)` | Raises ValueError if not found |
| `_ArrayAdd($arr, $val)` | `arr.append(val)` | Direct |
| `_ArrayDelete($arr, $idx)` | `del arr[idx]` or `arr.pop(idx)` | Direct |
| `_ArraySort($arr)` | `arr.sort()` | In-place |
| `UBound($arr)` | `len(arr)` | Direct |
| `UBound($arr, 2)` | `len(arr[0])` (if 2D) | Column count |
| `_ArrayDisplay($arr)` | `print(arr)` or logging | Debug only |

### 5.4 File I/O

| AutoIt | Python | Notes |
|--------|--------|-------|
| `IniRead($file, $sect, $key, $def)` | `config.get(sect, key, fallback=def)` | `configparser` |
| `IniWrite($file, $sect, $key, $val)` | `config.set(sect, key, val)` | Then `config.write()` |
| `IniReadSection($file, $sect)` | `dict(config[sect])` | Returns dict |
| `FileOpen($path, $mode)` | `open(path, mode)` | Use context manager |
| `FileRead($handle)` | `f.read()` | Direct |
| `FileReadLine($handle)` | `f.readline()` or `next(f)` | Direct |
| `FileWrite($handle, $data)` | `f.write(data)` | Direct |
| `FileExists($path)` | `Path(path).exists()` | Use `pathlib` |
| `DirCreate($path)` | `Path(path).mkdir(parents=True, exist_ok=True)` | Use `pathlib` |
| `FileCopy($src, $dst)` | `shutil.copy2(src, dst)` | Preserves metadata |
| `FileDelete($path)` | `Path(path).unlink(missing_ok=True)` | Use `pathlib` |

### 5.5 Error Handling (CRITICAL — 1,118 occurrences)

AutoIt uses `@error` macro and `SetError()`. Python uses exceptions.

**AutoIt pattern:**
```autoit
$result = SomeFunction()
If @error Then
    SetLog("Error: " & @error, $COLOR_ERROR)
    Return False
EndIf
```

**Python translation:**
```python
try:
    result = some_function()
except BotError as e:
    logger.error(f"Error: {e}")
    return False
```

**Key rules:**
- `@error` after DllCall → catch `ctypes` exceptions or check return codes
- `SetError(n, 0, False)` → raise custom `BotError(code=n)` or return `Result` type
- `@extended` → use exception attributes or named tuple returns
- Functions returning `False`/`-1` on error → raise exceptions instead (more Pythonic)

### 5.6 Dynamic Execution (CRITICAL — 77 occurrences, HIGH RISK)

AutoIt uses `Execute()`, `Eval()`, `Assign()` for dynamic dispatch. **Never use `eval()` in Python.**

**Pattern 1: Emulator dispatch via Execute() (Android.au3)**
```autoit
Execute("Open" & $g_sAndroidEmulator & "()")  ; Calls OpenBlueStacks5() or OpenMEmu() etc.
```
**Python replacement — Strategy pattern:**
```python
class EmulatorManager:
    _emulators: dict[str, BaseEmulator] = {
        "BlueStacks5": BlueStacks5Emulator,
        "MEmu": MEmuEmulator,
        "Nox": NoxEmulator,
    }
    def open(self) -> None:
        self._emulators[self.emulator_name]().open()
```

**Pattern 2: CSV attack vectors via Assign/Eval (ParseAttackCSV.au3)**
```autoit
Assign("ATTACKVECTOR_" & $value1, $tmpArray)
Local $pixel = Execute("$ATTACKVECTOR_" & $value1 & "[" & $i & "]")
```
**Python replacement — Dictionary:**
```python
attack_vectors: dict[str, list] = {}
attack_vectors[value1] = tmp_array
pixel = attack_vectors[value1][i]
```

**Pattern 3: Enum lookup via Eval (various)**
```autoit
$g_iTree = Int(Eval("e" & $sTreeName))
```
**Python replacement — Enum by name:**
```python
tree_value = TroopEnum[tree_name].value
```

### 5.7 DllCall Replacement Map (244 calls across 16 DLLs)

| DLL | Function | Python Replacement |
|-----|----------|--------------------|
| **MBRBot.dll** (16 unique funcs) | | |
| | `SearchMultipleTilesBetweenLevels` | `cv2.matchTemplate()` with multi-scale loop |
| | `FindTile` | `cv2.matchTemplate()` single template |
| | `SearchRedLines` | Custom contour detection with `cv2.findContours()` |
| | `GetProperty` | Return match metadata from Python matching |
| | `getRedArea` | `cv2.inRange()` + contour detection |
| | `getRedAreaSideBuilding` | Combined color + template matching |
| | `getLocation*` (6 variants) | `cv2.matchTemplate()` with template dirs |
| | `ocr` / `DoOCR` | `pytesseract.image_to_string()` or custom matcher |
| | `setGlobalVar`, `setAndroidPID`, etc. | Direct Python state setting |
| | `GetDeployableNextTo` | Geometry calculation in Python |
| | `GetOffSetRedline` | Geometry offset calculation |
| **user32.dll** | `PostMessage`, `SendMessage` | `win32gui.PostMessage()`, `win32gui.SendMessage()` |
| | `FindWindow`, `FindWindowEx` | `win32gui.FindWindow()` |
| | `GetDC`, `ReleaseDC` | `win32gui.GetDC()`, `win32gui.ReleaseDC()` |
| | `PrintWindow` | `win32gui.PrintWindow()` |
| **kernel32.dll** | `OpenProcess`, `CloseHandle` | `ctypes.windll.kernel32` or `psutil` |
| | `ReadProcessMemory`, `WriteProcessMemory` | `ctypes` or `pymem` |
| | `GlobalAlloc`, `GlobalLock` | `ctypes` for clipboard ops |
| | `VirtualAlloc`, `VirtualFree` | Not needed — Python manages memory |
| **gdi32.dll** | `GetPixel`, `CreateDC` | `PIL.Image.getpixel()` or numpy array indexing |
| | `GetDeviceCaps` | `win32print.GetDeviceCaps()` |
| **ntdll.dll** | `ZwDelayExecution` | `time.sleep()` (microsecond precision not needed) |
| | `ZwYieldExecution` | `time.sleep(0)` — thread yield |
| **shell32.dll** | `Shell_NotifyIconW` | `pystray` or `win32gui` tray icon |
| **wininet.dll** | `InternetGetConnectedState` | `requests.get()` with timeout, or `socket.create_connection()` |
| **PowrProf.dll** | `SetSuspendState` | `ctypes.windll.PowrProf.SetSuspendState()` |
| **dwmapi.dll** | `DwmIsCompositionEnabled` | `ctypes.windll.dwmapi` |

### 5.8 GUI Control Translation (3,775 controls → PyQt6)

| AutoIt Control | Count | PyQt6 Widget |
|---------------|-------|-------------|
| `GUICtrlCreateLabel` | 984 | `QLabel` |
| `GUICtrlCreateIcon` | 762 | `QLabel` with `QPixmap` |
| `GUICtrlCreateCheckbox` | 596 | `QCheckBox` |
| `GUICtrlCreateGroup` | 529 | `QGroupBox` |
| `GUICtrlCreateInput` | 243 | `QLineEdit` |
| `GUICtrlCreateButton` | 192 | `QPushButton` |
| `GUICtrlCreateEdit` | 156 | `QTextEdit` |
| `GUICtrlCreateCombo` | 124 | `QComboBox` |
| `GUICtrlCreateTabItem` | 76 | `QTabWidget.addTab()` |
| `GUICtrlCreateRadio` | 32 | `QRadioButton` |
| `GUICtrlCreateTreeViewItem` | 22 | `QTreeWidgetItem` |
| `GUICtrlCreatePic` | 20 | `QLabel` with `QPixmap` |
| `GUICtrlCreateTab` | 17 | `QTabWidget` |
| `GUICtrlCreateSlider` | 7 | `QSlider` |
| `GUICtrlCreateDummy` | 5 | _(no widget, use signal/slot)_ |
| `GUICtrlCreateProgress` | 3 | `QProgressBar` |
| `GUICtrlCreateTreeView` | 1 | `QTreeWidget` |
| `GUICtrlCreateListView` | 1 | `QTableWidget` |
| `GUICtrlCreateMenu` | 1 | `QMenuBar` |
| `GUICtrlCreateGraphic` | 1 | `QGraphicsView` or `QPainter` |

**Event handling translation:**
```autoit
; AutoIt
GUISetOnEvent($GUI_EVENT_CLOSE, "OnClose")
GUICtrlSetOnEvent($btnStart, "BtnStartClick")
```
```python
# PyQt6
self.closeEvent = self.on_close
self.btn_start.clicked.connect(self.btn_start_click)
```

### 5.9 Win32 Window Management (251 calls → pywin32)

| AutoIt Function | Count | Python (pywin32) |
|----------------|-------|-----------------|
| `WinMove()` | 93 | `win32gui.MoveWindow()` |
| `ProcessExists()` | 42 | `psutil.pid_exists()` |
| `WinGetPos()` | 35 | `win32gui.GetWindowRect()` |
| `ControlClick()` | 27 | `win32gui.PostMessage(WM_LBUTTONDOWN/UP)` |
| `WinGetHandle()` | 20 | `win32gui.FindWindow()` |
| `ControlSend()` | 14 | `win32gui.PostMessage(WM_CHAR)` |
| `WinSetState()` | 8 | `win32gui.ShowWindow()` |
| `WinGetTitle()` | 8 | `win32gui.GetWindowText()` |
| `WinActivate()` | 4 | `win32gui.SetForegroundWindow()` |
| `WinClose()` | 3 | `win32gui.PostMessage(WM_CLOSE)` |
| `ProcessClose()` | 3 | `psutil.Process(pid).terminate()` |
| `WinKill()` | 2 | `psutil.Process(pid).kill()` |

---

## 6. Phase 1: Foundation & Infrastructure

**Priority**: CRITICAL — everything depends on this
**Source lines**: ~12,000 | **Target files**: ~20 Python modules
**Dependencies**: None (starting point)

### 6.1 Project Scaffolding

Create the Python project skeleton:

```
mybot/
├── pyproject.toml
├── README.md
├── mybot/
│   ├── __init__.py
│   └── ...
├── tests/
│   ├── __init__.py
│   └── ...
├── Languages/          ← symlink or copy from MyBot/Languages/
├── CSV/                ← symlink or copy from MyBot/CSV/
├── imgxml/             ← symlink or copy from MyBot/imgxml/
└── images/             ← symlink or copy from MyBot/images/
```

**Tasks:**
- [ ] Create `pyproject.toml` with all dependencies (see Section 4)
- [ ] Configure ruff (linting), black (formatting), mypy (type checking)
- [ ] Set up pytest with fixtures for test screenshots
- [ ] Create GitHub Actions CI: lint → type-check → test
- [ ] Create `.env.example` for user-configurable paths

### 6.2 Global Variables → Python State Model

**Source file**: `COCBot/MBR Global Variables.au3` (2,332 lines, 6 functions, 852 globals)

This is the most important translation decision. All 852 globals become structured state:

**Target files:**

| Python file | What it contains | Source lines |
|-------------|-----------------|--------------|
| `mybot/constants.py` | Game dimensions, color codes, delay constants, enum values | ~800 |
| `mybot/enums.py` | All enum types (troops, spells, heroes, buildings, loot types) | ~500 |
| `mybot/state.py` | `BotState` dataclass hierarchy (runtime mutable state) | ~600 |
| `mybot/config/models.py` | `BotConfig` pydantic models (user settings from INI) | ~400 |

**Translation rules for each global variable:**

| Global pattern | Python target | Example |
|---------------|--------------|---------|
| `$eTroop*`, `$eSpell*`, `$eHero*` | `enum.IntEnum` in `enums.py` | `class Troop(IntEnum): BARBARIAN = 0` |
| `$g_iGAME_WIDTH`, `$COLOR_*` | Constants in `constants.py` | `GAME_WIDTH = 860` |
| `$DELAY*` | Constants in `config/delays.py` | `DELAY_GETTHLEVEL1 = 500` |
| `$g_bRunState`, `$g_bRestart` | `BotState` with `threading.Event` | `state.running.is_set()` |
| `$g_aiCurrentLoot[]` | `BotState.village.loot: LootState` | `state.village.loot.gold` |
| `$g_sProfileCurrentName` | `BotConfig.profile.name` | `config.profile.name` |
| `$g_hAndroidWindow` | `BotState.android.window_handle` | `state.android.hwnd` |
| `$g_abChkDonate*[]` | `BotConfig.donate.*` | `config.donate.troop_enabled[Troop.BARBARIAN]` |
| `$g_iTownHallLevel` | `BotState.village.th_level` | `state.village.th_level` |
| `$g_h*` (GUI handles) | PyQt6 widget references | `self.btn_start` (not in state) |

**Critical gotcha**: AutoIt globals are freely read/written from any function. In Python, pass `BotState` as dependency injection parameter, not as module-level global.

### 6.3 Configuration System

**Source directory**: `COCBot/functions/Config/` (6,594 lines, 8 files)

| Source file | Lines | Funcs | Target file | Notes |
|-------------|-------|-------|-------------|-------|
| `readConfig.au3` | 1,468 | 44 | `mybot/config/reader.py` | 44 functions like `ReadConfig_600_1()` — each reads a section of INI. Consolidate into single `read_config()` with section handlers |
| `saveConfig.au3` | 1,413 | 50 | `mybot/config/writer.py` | Mirror of readConfig. 50 functions like `SaveConfig_600_1()`. Consolidate similarly |
| `applyConfig.au3` | 2,422 | 43 | `mybot/config/applier.py` | Applies loaded config to GUI controls. 43 functions like `ApplyConfig_600_1()`. In PyQt6, bind config model to widgets directly |
| `ScreenCoordinates.au3` | 397 | 0 | `mybot/config/coordinates.py` | Pure constants — game screen pixel positions. Direct translation |
| `ImageDirectories.au3` | 266 | 0 | `mybot/config/image_dirs.py` | Paths to imgxml template directories. Use `pathlib.Path` |
| `DelayTimes.au3` | 186 | 0 | `mybot/config/delays.py` | Delay constants in milliseconds. Direct translation |
| `profileFunctions.au3` | 287 | 9 | `mybot/config/profiles.py` | Profile creation, switching, listing. 9 funcs: `frmBotAddProfile`, `frmBotDeleteProfile`, `profileSwitch`, etc. |
| `_Ini_Table.au3` | 155 | 7 | `mybot/config/ini_table.py` | INI batch operations. 7 funcs for table-based read/write |

**Translation approach for readConfig/saveConfig:**
These files are extremely repetitive (each line reads one INI key into one global variable). Generate Python code that maps INI sections/keys to config model fields:

```python
# Instead of 1,468 lines of IniRead, use declarative mapping:
CONFIG_MAP = {
    ("General", "SearchMode"): ("search.enabled", bool, False),
    ("General", "TownHallLevel"): ("village.th_level", int, 0),
    # ... ~700 mappings
}

def read_config(path: Path) -> BotConfig:
    parser = configparser.ConfigParser()
    parser.read(path)
    config = BotConfig()
    for (section, key), (attr, type_, default) in CONFIG_MAP.items():
        set_nested_attr(config, attr, type_(parser.get(section, key, fallback=default)))
    return config
```

### 6.4 Logging System

**Source file**: `COCBot/functions/Other/SetLog.au3` (370 lines, 18 functions)

| Function | Purpose | Python equivalent |
|----------|---------|-------------------|
| `SetLog($msg, $color)` | Main log function | `logger.info(msg)` with color handler |
| `SetDebugLog($msg)` | Debug-only log | `logger.debug(msg)` |
| `_SetLog($msg, $color)` | Internal log impl | Custom `logging.Handler` |
| `_GUICtrlRichEdit_AppendTextColor()` | GUI log with color | PyQt6 `QTextEdit.appendHtml()` |
| `FlushGuiLog()` | Flush log buffer | Handler `flush()` |
| Plus 13 more utility functions | Various | Logging module features |

**Target files:**
- `mybot/log.py` — Custom logging handler that writes to file + GUI log widget
- Color constants from `$COLOR_ERROR`, `$COLOR_WARNING`, etc. → logging levels

### 6.5 Sleep / Control Flow

**Source file**: `COCBot/functions/Other/_Sleep.au3` (147 lines, 3 functions)

| Function | Lines | Purpose | Python replacement |
|----------|-------|---------|-------------------|
| `_Sleep($ms)` | 80 | Sleep that checks `$g_bRunState` and `$g_bRestart` every iteration | `bot_sleep()` using `threading.Event.wait(timeout)` |
| `_SleepMilli($ms)` | 30 | Microsecond-precision sleep via `ZwDelayExecution` | `time.sleep(ms / 1000)` |
| `_SleepStatus($ms)` | 37 | Sleep with status bar update | `bot_sleep()` with callback |

**Target file**: `mybot/utils/sleep.py`

**Critical**: `_Sleep()` is called **1,801 times** across the codebase. It's the primary mechanism for cooperative multitasking — every operation checks if the bot should stop/restart. Python translation:

```python
def bot_sleep(ms: int, state: BotState) -> bool:
    """Sleep for ms milliseconds. Returns True if interrupted (restart/stop requested)."""
    if state.stop_event.wait(timeout=ms / 1000):
        return True  # Interrupted
    return False
```

### 6.6 Translation / i18n

**Source file**: `COCBot/functions/Other/Multilanguage.au3` (1,202 lines, 5 functions)

| Function | Lines | Purpose | Python replacement |
|----------|-------|---------|-------------------|
| `GetTranslatedFileIni($section, $key, $default, ...)` | 600+ | Main translation lookup with caching and fallback | `i18n.t(section, key, default, *args)` |
| `DetectLanguage()` | 200+ | Detect system language | `locale.getdefaultlocale()` |
| `InitLanguage()` | 150+ | Load language file | Load `.ini` file at startup |
| `SetLanguage()` | 100+ | Switch language | Reload `.ini` and refresh |
| `TestLanguageComplete()` | 100+ | Check for missing translations | Validation function |

**Target file**: `mybot/i18n.py`

**Key requirement**: Must read existing `Languages/*.ini` files without modification. Use `configparser` to parse them.

### 6.7 Other Utilities (Other/ directory — 60 files)

Files to translate in Phase 1 (infrastructure utilities):

| Source file | Lines | Funcs | Target file | Priority |
|-------------|-------|-------|-------------|----------|
| `StopWatch.au3` | 120 | 11 | `mybot/utils/timer.py` | HIGH — used for timing |
| `Time.au3` | 160 | 6 | `mybot/utils/time.py` | HIGH — time formatting |
| `_TicksToDay.au3` | 30 | 1 | _(inline in timer.py)_ | LOW |
| `_StatusUpdateTime.au3` | 22 | 1 | _(inline in timer.py)_ | LOW |
| `_NumberFormat.au3` | 33 | 1 | `mybot/utils/formatting.py` | LOW |
| `_PadStringCenter.au3` | 38 | 1 | _(inline)_ | LOW |
| `Base64.au3` | 134 | 9 | `base64` stdlib | NONE — use stdlib |
| `Json.au3` | 552 | 23 | `json` stdlib | NONE — use stdlib |
| `CreateLogFile.au3` | 127 | 3 | _(part of log.py)_ | MEDIUM |
| `DeleteFiles.au3` | 68 | 1 | _(inline)_ | LOW |
| `KillProcess.au3` | 58 | 1 | _(use psutil)_ | LOW |
| `RestartBot.au3` | 49 | 1 | `mybot/utils/restart.py` | MEDIUM |
| `CheckVersion.au3` | 75 | 4 | `mybot/utils/version.py` | LOW |
| `CheckPrerequisites.au3` | 153 | 6 | `mybot/utils/prerequisites.py` | MEDIUM |
| `TogglePause.au3` | 99 | 4 | `mybot/bot.py` (pause method) | MEDIUM |
| `Tab.au3` | 22 | 1 | _(not needed)_ | NONE |
| `GUICtrlGetBkColor.au3` | 24 | 1 | _(PyQt6 native)_ | NONE |

**Files deferred to later phases** (depend on Android/GUI):
- `Click.au3`, `ClickDrag.au3`, `ClickRemove.au3`, `ClickOkay.au3`, `ClickZoneR.au3` → Phase 2
- `MakeScreenshot.au3`, `FindPos.au3`, `FindAButton.au3` → Phase 2
- `MBRFunc.au3`, `BinaryCall.au3` → Phase 3 (DLL replacement)
- `WindowsArrange.au3`, `AppUserModelId.au3`, `WindowSystemMenu.au3` → Phase 6 (GUI)
- `Api.au3`, `ApiClient.au3`, `ApiHost.au3` → Phase 6
- `Notify.au3` → Phase 6
- `UpdateStats.au3`, `UpdateStats.Mini.au3` → Phase 6
- All remaining Other/ files → Phase they logically belong to

### Phase 1 Deliverable

A Python project that can:
1. Load a profile config from existing INI file
2. Save config back to INI
3. Log messages with color levels
4. Read translations from existing language .ini files
5. Provide cancellable sleep with stop/restart checking
6. Run with `python -m mybot` (no functionality yet, just infrastructure)

### Phase 1 Validation Checklist

- [ ] `pytest` passes with >80% coverage on config read/write
- [ ] Round-trip test: read existing INI → write → diff shows no changes
- [ ] Language loading test: load English.ini, verify all sections parse
- [ ] `bot_sleep()` test: verify interruption within 50ms
- [ ] `mypy --strict` passes on all Phase 1 modules
- [ ] `ruff check` passes with zero warnings
