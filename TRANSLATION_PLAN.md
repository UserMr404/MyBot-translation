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

---

## 7. Phase 2: Android / Emulator Layer

**Priority**: CRITICAL — all game interaction goes through this layer
**Source lines**: ~9,455 (Android/) + ~1,500 (Click/Screenshot from Other/)
**Target files**: ~12 Python modules
**Dependencies**: Phase 1 (config, logging, sleep)

### 7.1 Core Emulator Management

**Source file**: `COCBot/functions/Android/Android.au3` (5,046 lines, 123 functions)

This is the **second largest file** in the codebase. It uses `Execute()` for dynamic dispatch to emulator-specific functions. Must be redesigned with Strategy pattern.

**Key function groups in Android.au3:**

| Function group | Count | Purpose | Python target |
|---------------|-------|---------|---------------|
| `Open*()`, `Close*()`, `Reboot*()` | 15 | Emulator lifecycle | `mybot/android/manager.py` |
| `Android*Click()`, `AndroidFastClick()` | 8 | Touch input via ADB/minitouch | `mybot/android/input.py` |
| `AndroidScreencap()` | 5 | Screenshot capture via ADB | `mybot/android/capture.py` |
| `AndroidEmbed*()` | 12 | Window docking/embedding | `mybot/android/embed.py` |
| `AndroidShield*()` | 10 | Shield overlay management | `mybot/android/shield.py` |
| `AndroidAdb*()` | 20 | ADB shell communication | `mybot/android/adb.py` |
| `AndroidZoomOut()` | 3 | Zoom control | `mybot/android/zoom.py` |
| `WaitForAndroid*()` | 8 | Wait for emulator boot | `mybot/android/manager.py` |
| `getAndroid*()` | 15 | Get emulator properties | `mybot/android/base.py` |
| `Android*Config()` | 10 | Emulator config detection | `mybot/android/config.py` |
| Remaining utility funcs | 17 | Misc helpers | Distributed |

**Architecture redesign:**

```python
# mybot/android/base.py — Abstract emulator interface
class BaseEmulator(ABC):
    @abstractmethod
    def open(self) -> bool: ...
    @abstractmethod
    def close(self) -> bool: ...
    @abstractmethod
    def reboot(self) -> bool: ...
    @abstractmethod
    def get_window_handle(self) -> int: ...
    @abstractmethod
    def get_adb_port(self) -> int: ...
    @abstractmethod
    def adjust_click_coordinates(self, x: int, y: int) -> tuple[int, int]: ...

# mybot/android/bluestacks.py
class BlueStacks5Emulator(BaseEmulator):
    def open(self) -> bool: ...  # From OpenBlueStacks5()

# mybot/android/memu.py
class MEmuEmulator(BaseEmulator):
    def open(self) -> bool: ...  # From OpenMEmu()

# mybot/android/nox.py
class NoxEmulator(BaseEmulator):
    def open(self) -> bool: ...  # From OpenNox()
```

**Replaces 49 `Execute()` calls** that dynamically dispatch like:
```autoit
Execute("Open" & $g_sAndroidEmulator & "()")
```

### 7.2 Emulator-Specific Implementations

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `AndroidBluestacks5.au3` | 451 | 21 | `mybot/android/bluestacks.py` | `OpenBlueStacks5()`, `GetBlueStacks5Path()`, `BlueStacks5AdjustClickCoordinates()`, `InitBlueStacks5()` |
| `AndroidMEmu.au3` | 436 | 13 | `mybot/android/memu.py` | `OpenMEmu()`, `GetMEmuPath()`, `MEmuAdjustClickCoordinates()`, `InitMEmu()` |
| `AndroidNox.au3` | 489 | 18 | `mybot/android/nox.py` | `OpenNox()`, `GetNoxPath()`, `NoxAdjustClickCoordinates()`, `InitNox()` |

### 7.3 Remaining Android/ Files

| Source file | Lines | Funcs | Target file | Notes |
|-------------|-------|-------|-------------|-------|
| `AndroidEmbed.au3` | 1,180 | 26 | `mybot/android/embed.py` | Window docking into bot GUI. Heavy use of `WinMove()`, `WinGetPos()`. Uses pywin32 |
| `ZoomOut.au3` | 571 | 10 | `mybot/android/zoom.py` | Zoom control via keyboard/mouse/ADB. Contains emulator-specific `ZoomOut*()` funcs — move into each emulator class |
| `getBSPos.au3` | 384 | 3 | `mybot/android/position.py` | Get emulator window position/size. Uses `WinGetPos()`, `ControlGetPos()` |
| `Close_OpenCoC.au3` | 233 | 5 | `mybot/android/app.py` | Open/close Clash of Clans app via ADB `am start`/`am force-stop` |
| `UniversalCloseWaitOpenCoC.au3` | 173 | 2 | `mybot/android/app.py` | Generic close-wait-open with retries |
| `Distributors.au3` | 121 | 6 | `mybot/android/distributors.py` | Google Play, Amazon, Kunlun distributor detection |
| `checkAndroidTimeLag.au3` | 116 | 2 | `mybot/android/health.py` | Check if emulator clock is synced |
| `checkAndroidPageError.au3` | 75 | 3 | `mybot/android/health.py` | Check for emulator error pages |
| `CheckAndroidRebootCondition.au3` | 74 | 2 | `mybot/android/health.py` | Determine if reboot needed |
| `CheckBotRestartCondition.au3` | 61 | 3 | `mybot/android/health.py` | Determine if bot restart needed |
| `AndroidMenuShortcuts.au3` | 45 | 2 | `mybot/android/shortcuts.py` | Keyboard shortcuts for emulator |

### 7.4 Input Simulation (from Other/)

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `Click.au3` | 617 | 20 | `mybot/android/input.py` | `Click()`, `PureClick()`, `GemClick()`, `BuildingClick()`, `ClickP()`, `isClickAway()`, `ClearScreen()` |
| `ClickDrag.au3` | 130 | 3 | `mybot/android/input.py` | `ClickDrag()` — uses PostMessage via DllCall to user32.dll |
| `ClickRemove.au3` | 44 | 1 | `mybot/android/input.py` | `ClickRemove()` — click to dismiss |
| `ClickOkay.au3` | 39 | 1 | `mybot/android/input.py` | `ClickOkay()` — click OK buttons |
| `ClickZoneR.au3` | 206 | 4 | `mybot/android/input.py` | `ClickZoneR()` — randomized click in zone |
| `FindPos.au3` | 36 | 1 | `mybot/android/input.py` | `FindPos()` — find position by image |
| `MoveMouseOutBS.au3` | 45 | 2 | `mybot/android/input.py` | Move mouse outside emulator window |

**Input method hierarchy:**
1. ADB touch events (default) — `adb shell input tap x y`
2. Minitouch protocol (faster) — binary touch event protocol
3. Windows PostMessage (fallback) — `PostMessage(WM_LBUTTONDOWN)`

```python
# mybot/android/input.py
class InputMethod(ABC):
    @abstractmethod
    def click(self, x: int, y: int) -> None: ...
    @abstractmethod
    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: int) -> None: ...

class AdbInput(InputMethod): ...
class MinitouchInput(InputMethod): ...
class PostMessageInput(InputMethod): ...
```

### 7.5 Screen Capture (from Other/ and Pixels/)

| Source file | Lines | Funcs | Target file | Notes |
|-------------|-------|-------|-------------|-------|
| `MakeScreenshot.au3` | 65 | 1 | `mybot/android/capture.py` | Save debug screenshots to file |
| `SaveDebugImage.au3` | 373 | 5 | `mybot/android/capture.py` | Save annotated debug images |
| `_CaptureRegion.au3` | 432 | 18 | `mybot/android/capture.py` | Core screenshot capture — ADB screencap, RGBA→BGRA conversion, region cropping |

**ADB screencap pipeline (from `_CaptureRegion.au3`):**
```autoit
; Current AutoIt flow:
1. $g_aiAndroidAdbScreencapBuffer = adb exec-out screencap (raw RGBA bytes)
2. DllCall(helper_functions.dll, "RGBA2BGRA", ...) → convert to BGRA
3. Store in GDI+ bitmap $g_hHBitmap2
4. All image operations use $g_hHBitmap2
```

**Python replacement:**
```python
# mybot/android/capture.py
def capture_screen(adb: AdbClient) -> np.ndarray:
    """Capture emulator screen as BGR numpy array."""
    raw = adb.exec_out("screencap -p")  # PNG format
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    return img  # BGR numpy array — ready for cv2.matchTemplate()

def capture_region(adb: AdbClient, x: int, y: int, w: int, h: int) -> np.ndarray:
    """Capture a region of the screen."""
    full = capture_screen(adb)
    return full[y:y+h, x:x+w]
```

### 7.6 ADB Communication

**Source file**: `COCBot/functions/Other/ADB.au3` (43 lines, 1 function) + ADB calls scattered in `Android.au3` (~200 lines) and `LaunchConsole.au3` (409 lines, 16 functions)

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `ADB.au3` | 43 | 1 | `mybot/android/adb.py` | `ConnectAndroidAdb()` |
| `LaunchConsole.au3` | 409 | 16 | `mybot/android/adb.py` | `LaunchConsole()`, `AndroidAdbSendShellCommand()`, `AndroidAdbLaunchShellInstance()`, etc. |

**Python ADB client:**
```python
# mybot/android/adb.py
class AdbClient:
    def __init__(self, device_serial: str, adb_path: Path = None):
        self._device = ...  # pure-python-adb device

    def shell(self, command: str) -> str: ...
    def exec_out(self, command: str) -> bytes: ...
    def push(self, local: Path, remote: str) -> None: ...
    def pull(self, remote: str, local: Path) -> None: ...
    def tap(self, x: int, y: int) -> None: ...
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int) -> None: ...
```

### Phase 2 Deliverable

A Python module that can:
1. Detect and connect to BlueStacks5 / MEmu / Nox emulators
2. Capture screenshots as numpy arrays
3. Send touch/click/drag commands via ADB
4. Open/close/reboot the emulator
5. Open/close the Clash of Clans app

### Phase 2 Validation Checklist

- [ ] Connect to running emulator and capture screenshot
- [ ] Screenshot → numpy array → save as PNG matches expected game screen
- [ ] Click at coordinates → verify emulator receives input
- [ ] Drag operation works (for scrolling, zooming)
- [ ] Open/close CoC app via ADB
- [ ] Emulator auto-detection works for all 3 emulators
- [ ] Zoom out function works
- [ ] Window embedding/docking works (if GUI available)

---

## 8. Phase 3: Vision & Image Recognition

**Priority**: CRITICAL — replaces proprietary MBRBot.dll
**Source lines**: ~4,476 (Image Search/ + Pixels/ + Read Text/)
**Target files**: ~10 Python modules
**Dependencies**: Phase 1 (config), Phase 2 (screen capture)
**Risk**: HIGHEST phase — must match MBRBot.dll accuracy

### 8.1 MBRBot.dll API Replacement

The bot calls 16 unique functions in MBRBot.dll via `DllCallMyBot()`. Every one must be replicated:

| MBRBot.dll Function | Called From | What It Does | Python Replacement |
|---------------------|------------|--------------|-------------------|
| `SearchMultipleTilesBetweenLevels` | multiSearch, WeakBase, DonateCC, QuickMIS, imglocCheckWall, TrainSystem | Search multiple XML templates in a directory, filtered by level range, within a defined area | `template_search_multi()` — loop `cv2.matchTemplate()` over directory of templates |
| `FindTile` | imglocAuxiliary, TrainIt | Find single template match | `template_search_single()` — `cv2.matchTemplate()` on one template |
| `SearchRedLines` | imglocAuxiliary | Detect red deployment boundary | `detect_red_lines()` — `cv2.inRange()` for red color + `cv2.findContours()` |
| `GetProperty` | multiSearch, QuickMIS, imglocAuxiliary | Get metadata from last search (redline, objectpoints, totalobjects) | Return metadata from Python search result object |
| `getRedArea` | _GetRedArea | Get full red deployment zone | `detect_red_area()` — color-based contour detection |
| `getRedAreaSideBuilding` | _GetRedArea | Get red area near specific building type | `detect_red_area_near()` — filtered contour detection |
| `getLocationTownHall` | GetLocation | Find Town Hall coordinates | `locate_town_hall()` — template match against TH images |
| `getLocationDarkElixirStorage` | GetLocation | Find DE storage | `locate_building("de_storage")` |
| `getLocationDarkElixirStorageWithLevel` | GetLocation | Find DE storage with level | `locate_building("de_storage", with_level=True)` |
| `getLocationElixirExtractorWithLevel` | GetLocation | Find elixir collectors with level | `locate_building("elixir_extractor", with_level=True)` |
| `getLocationSnowElixirExtractorWithLevel` | GetLocation | Find snow-themed elixir collectors | `locate_building("snow_elixir_extractor", with_level=True)` |
| `getLocationMineExtractorWithLevel` | GetLocation | Find gold mines with level | `locate_building("mine_extractor", with_level=True)` |
| `getLocationSnowMineExtractorWithLevel` | GetLocation | Find snow-themed gold mines | `locate_building("snow_mine_extractor", with_level=True)` |
| `ocr` | getOcr | OCR on bitmap region | `pytesseract.image_to_string()` or custom OCR |
| `DoOCR` | getOcr | Alternative OCR entry point | Same as above |
| `GetDeployableNextTo` | imglocAuxiliary | Calculate deployable points near a line | `geometry.get_deployable_points()` — pure Python geometry |
| `GetOffSetRedline` | imglocAuxiliary | Offset redline by distance | `geometry.offset_polyline()` — pure Python geometry |
| `setGlobalVar` | MBRFunc | Set debug flags in DLL | Direct Python state setting (no DLL needed) |
| `setAndroidPID` | MBRFunc | Pass Android PID to DLL | Not needed — Python manages its own state |
| `SetBotGuiPID` | MBRFunc | Pass GUI PID to DLL | Not needed |
| `setVillageOffset` | MBRFunc | Set village coordinate offset | Direct Python state setting |
| `ConvertVillagePos` | MBRFunc | Convert screen → village coords | Pure Python coordinate math |
| `ConvertToVillagePos` | MBRFunc | Same | Pure Python |
| `ConvertFromVillagePos` | MBRFunc | Village → screen coords | Pure Python |

### 8.2 Template Matching Engine

**Source files**: `Image Search/imglocAuxiliary.au3` (886 lines, 25 functions)

| Function | Lines | Purpose | Python target |
|----------|-------|---------|---------------|
| `findMultiple()` | 80 | Multi-template search in directory | `mybot/vision/matcher.py: find_multiple()` |
| `findImage()` / `findButton()` | 60 | Single image search | `mybot/vision/matcher.py: find_image()` |
| `returnMultipleMatches()` | 50 | Return all match coordinates | `mybot/vision/matcher.py: find_all_matches()` |
| `returnMultipleMatchesOwnVillage()` | 30 | Search within own village bounds | `mybot/vision/matcher.py: find_in_village()` |
| `GetDeployableNextTo()` | 20 | Geometry calculation | `mybot/vision/geometry.py` |
| `GetOffSetRedline()` | 20 | Redline offset | `mybot/vision/geometry.py` |
| `decodeSingleCoord()` | 15 | Parse "x,y" from DLL result | Not needed — return tuples directly |
| `decodeMultipleCoords()` | 30 | Parse "x1,y1|x2,y2" result | Not needed |
| Remaining 17 utility funcs | ~580 | Various helpers | Distributed |

**Core matching algorithm:**
```python
# mybot/vision/matcher.py
def find_multiple(
    screenshot: np.ndarray,
    template_dir: Path,
    search_area: tuple[int, int, int, int],  # x, y, w, h
    max_results: int = 0,
    min_level: int = 0,
    max_level: int = 1000,
    confidence: float = 0.85,
    redlines: str = "",
) -> list[MatchResult]:
    """Replace DllCallMyBot("SearchMultipleTilesBetweenLevels", ...)"""
    results = []
    for template_path in template_dir.glob("*.xml"):
        name, level, rotation = parse_template_name(template_path.stem)
        if not (min_level <= level <= max_level):
            continue
        template_img = load_xml_template(template_path)
        region = screenshot[y:y+h, x:x+w]
        match_result = cv2.matchTemplate(region, template_img, cv2.TM_CCOEFF_NORMED)
        locations = np.where(match_result >= confidence)
        for pt in zip(*locations[::-1]):
            results.append(MatchResult(name=name, x=pt[0]+x, y=pt[1]+y, level=level, confidence=match_result[pt[1], pt[0]]))
    return results[:max_results] if max_results > 0 else results
```

### 8.3 XML Template Loader

**No source file** — template loading is embedded in MBRBot.dll. Must reverse-engineer the format.

**imgxml template format** (2,140+ files):
```xml
<?xml version="1.0" encoding="utf-8"?>
<image>
  <data>base64_encoded_png_data</data>
</image>
```

**Template naming convention**: `ElementName_Scale_Rotation.xml`
- Example: `Barb_100_91.xml` = Barbarian at 100% scale, 91° rotation

**Target file**: `mybot/vision/templates.py`

```python
# mybot/vision/templates.py
@dataclass
class Template:
    name: str
    level: int
    rotation: int
    image: np.ndarray  # Decoded OpenCV image

_template_cache: dict[Path, list[Template]] = {}

def load_xml_template(path: Path) -> np.ndarray:
    """Load base64-encoded image from XML template file."""
    tree = ET.parse(path)
    b64_data = tree.find(".//data").text
    img_bytes = base64.b64decode(b64_data)
    return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

def load_template_dir(dir_path: Path) -> list[Template]:
    """Load all templates from a directory, with caching."""
    if dir_path in _template_cache:
        return _template_cache[dir_path]
    templates = []
    for xml_file in dir_path.glob("*.xml"):
        name_parts = xml_file.stem.rsplit("_", 2)
        # Parse: ElementName_Level_Rotation
        ...
    _template_cache[dir_path] = templates
    return templates
```

### 8.4 Pixel Operations

**Source directory**: `COCBot/functions/Pixels/` (1,157 lines, 38 functions, 8 files)

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `_CaptureRegion.au3` | 432 | 18 | _(Phase 2 capture.py)_ | Already covered in Phase 2 |
| `_PixelSearch.au3` | 205 | 2 | `mybot/vision/pixel.py` | `_PixelSearch()` — find pixel of specific color in region |
| `_MultiPixelSearch.au3` | 134 | 5 | `mybot/vision/pixel.py` | `_MultiPixelSearch()` — find multiple color matches |
| `_CheckPixel.au3` | 66 | 3 | `mybot/vision/pixel.py` | `_CheckPixel()` — verify pixel color at coordinates |
| `_ColorCheck.au3` | 43 | 1 | `mybot/vision/pixel.py` | `_ColorCheck()` — compare two colors with tolerance |
| `_GetPixelColor.au3` | 33 | 1 | `mybot/vision/pixel.py` | `_GetPixelColor()` — get hex color at coordinates |
| `isInsideDiamond.au3` | 162 | 3 | `mybot/vision/geometry.py` | `isInsideDiamond()` — check if point is inside village diamond boundary |
| `GetListPixel.au3` | 82 | 5 | `mybot/vision/pixel.py` | `GetListPixel()` — DLL call to get pixel lists from MBRBot.dll |

**Python pixel operations on numpy arrays:**
```python
# mybot/vision/pixel.py
def pixel_search(img: np.ndarray, color: tuple[int,int,int], tolerance: int = 15,
                 region: tuple[int,int,int,int] = None) -> tuple[int,int] | None:
    """Find first pixel matching color within tolerance."""
    if region:
        x, y, w, h = region
        img = img[y:y+h, x:x+w]
    target = np.array(color, dtype=np.uint8)
    diff = np.abs(img.astype(int) - target.astype(int))
    mask = np.all(diff <= tolerance, axis=2)
    matches = np.argwhere(mask)
    if len(matches) > 0:
        return (matches[0][1] + (region[0] if region else 0),
                matches[0][0] + (region[1] if region else 0))
    return None
```

### 8.5 OCR / Text Recognition

**Source directory**: `COCBot/functions/Read Text/` (912 lines, 79 functions, 4 files)

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `getOcr.au3` | 656 | 76 | `mybot/vision/ocr.py` | 76 specialized OCR functions: `getNameBuilding()`, `getGoldVillageSearch()`, `getElixirVillageSearch()`, `getRemainTrainTimer()`, `getTrophyMainScreen()`, `getHeroUpgradeTime()`, etc. |
| `BuildingInfo.au3` | 70 | 1 | `mybot/vision/building_info.py` | `BuildingInfo()` — extract building name + level from info popup |
| `getBuilderCount.au3` | 75 | 1 | `mybot/vision/ocr.py` | `getBuilderCount()` — read "X/Y" builder count |
| `getShieldInfo.au3` | 111 | 1 | `mybot/vision/ocr.py` | `getShieldInfo()` — read shield/guard remaining time |

**OCR strategy**: Each of the 76 `getOcr*()` functions reads text from a specific screen region with specific parameters. In Python, consolidate into a generic OCR function with region/language parameters:

```python
# mybot/vision/ocr.py
def read_text(img: np.ndarray, region: tuple[int,int,int,int],
              lang: str = "coc-latin", whitelist: str = "") -> str:
    """Read text from screen region using pytesseract."""
    x, y, w, h = region
    crop = img[y:y+h, x:x+w]
    # Preprocess: grayscale, threshold, invert
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    config = f"--psm 7"  # Single line
    if whitelist:
        config += f" -c tessedit_char_whitelist={whitelist}"
    return pytesseract.image_to_string(binary, config=config).strip()

# Specialized wrappers (replace 76 functions):
def get_gold_village_search(img: np.ndarray) -> int:
    return int(read_text(img, (x, y, w, h), whitelist="0123456789") or "0")
```

**Existing OCR templates**: The `lib/listSymbols_coc-*.xml` files (150+) are character templates for the custom OCR in MBRBot.dll. With pytesseract, these are not directly needed, but may be useful as training data if pytesseract accuracy is insufficient.

### 8.6 Additional Image Search Files

| Source file | Lines | Funcs | Target file | Notes |
|-------------|-------|-------|-------------|-------|
| `checkDeadBase.au3` | 343 | 8 | `mybot/vision/dead_base.py` | Dead base detection via collector fullness |
| `CheckTombs.au3` | 304 | 4 | `mybot/vision/tombs.py` | Tombstone detection and removal |
| `QuickMIS.au3` | 279 | 2 | `mybot/vision/quick_search.py` | Quick multi-image search — wrapper around `SearchMultipleTilesBetweenLevels` |
| `imglocTHSearch.au3` | 277 | 3 | `mybot/vision/townhall.py` | Town Hall image search with level detection |
| `IsWindowOpen.au3` | 163 | 4 | `mybot/vision/window_detect.py` | Detect if game windows/dialogs are open |
| `imglocCheckWall.au3` | 155 | 2 | `mybot/vision/walls.py` | Wall level detection via image matching |

### Phase 3 Deliverable

A Python vision module that can:
1. Load XML templates from imgxml/ directories
2. Match templates against screenshots with configurable confidence
3. Detect red deployment zone boundaries
4. Read text/numbers from specific screen regions (OCR)
5. Check pixel colors with tolerance
6. Detect dead bases, buildings, walls, town halls

### Phase 3 Validation Checklist

- [ ] Load all 2,140+ XML templates without errors
- [ ] Template matching accuracy ≥ 95% vs MBRBot.dll results on same screenshots
- [ ] OCR reads resource amounts correctly (gold, elixir, DE, trophies)
- [ ] OCR reads timer text correctly (upgrade times, training times)
- [ ] Red area detection matches MBRBot.dll output on test screenshots
- [ ] Dead base detection works on sample collector images
- [ ] Pixel color checking works at all game screen positions
- [ ] Performance: full template directory search < 2 seconds

---

## 9. Phase 4: Game Logic — Village, Search & Main Screen

**Priority**: HIGH — core gameplay automation
**Source lines**: ~29,984 (Village 25,434 + Search 2,572 + Main Screen 1,978)
**Target files**: ~40 Python modules
**Dependencies**: Phase 1-3 (config, android, vision)

### 9.1 Main Screen Detection

**Source directory**: `COCBot/functions/Main Screen/` (1,978 lines, 46 functions, 9 files)

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `checkObstacles.au3` | 850 | 16 | `mybot/game/obstacles.py` | `checkObstacles()` — detect & dismiss error popups, maintenance, connection lost, rate limits. Uses image matching for ~20 different popup types |
| `RemoveGhostTrayIcons.au3` | 646 | 15 | `mybot/system/tray.py` | Heavy Win32 API: `ReadProcessMemory`, `SendMessage`, toolbar button enumeration. Uses 15 DllCalls. Consider skipping or simplifying |
| `checkMainScreen.au3` | 142 | 4 | `mybot/game/main_screen.py` | `checkMainScreen()`, `IsMainPage()`, `IsMainPageOffset()` — verify bot is on village screen via pixel checks |
| `waitMainScreen.au3` | 116 | 2 | `mybot/game/main_screen.py` | `waitMainScreen()` — wait for main screen with timeout |
| `GetDPI_Ratio.au3` | 75 | 3 | `mybot/system/dpi.py` | DPI detection via `GetDeviceCaps`. Uses DllCall to gdi32.dll |
| `isOnBuilderBase.au3` | 56 | 3 | `mybot/game/main_screen.py` | `isOnBuilderBase()` — detect if on Builder Base via pixel color |
| `isProblemAffect.au3` | 36 | 1 | `mybot/game/obstacles.py` | `isProblemAffect()` — check for known issues |
| `isGemOpen.au3` | 31 | 1 | `mybot/game/obstacles.py` | `isGemOpen()` — detect gem purchase dialog |
| `isNoUpgradeLoot.au3` | 26 | 1 | `mybot/game/obstacles.py` | `isNoUpgradeLoot()` — detect insufficient resources dialog |

### 9.2 Search System

**Source directory**: `COCBot/functions/Search/` (2,572 lines, 58 functions, 11 files)

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `WeakBase.au3` | 621 | 14 | `mybot/search/weak_base.py` | `checkDefense()` — scan for defense levels using image templates, calculate weakness score |
| `VillageSearch.au3` | 580 | 4 | `mybot/search/search.py` | `VillageSearch()`, `_VillageSearch()` — main search loop: cycle through bases, check loot, match criteria |
| `multiSearch.au3` | 277 | 12 | `mybot/search/multi.py` | `multiSearch()` — DllCallMyBot wrapper for multi-template search. In Python, call `vision.matcher` directly |
| `IsSearchAttackEnabled.au3` | 254 | 9 | `mybot/search/filters.py` | `IsSearchAttackEnabled()` — check if attack mode is configured for current mode |
| `WaitForClouds.au3` | 213 | 6 | `mybot/search/clouds.py` | `WaitForClouds()` — handle cloud screen during matchmaking, with timeout |
| `IsSearchModeActive.au3` | 193 | 5 | `mybot/search/filters.py` | `IsSearchModeActive()` — check if specific search mode is active |
| `PrepareSearch.au3` | 143 | 2 | `mybot/search/prepare.py` | `PrepareSearch()` — open attack screen, set up search parameters |
| `CompareResources.au3` | 129 | 2 | `mybot/search/resources.py` | `CompareResources()` — compare target base loot against thresholds |
| `GetResources.au3` | 86 | 2 | `mybot/search/resources.py` | `GetResources()` — OCR read gold/elixir/DE/trophies from search screen |
| `FindTownHall.au3` | 42 | 1 | `mybot/search/townhall.py` | `FindTownHall()` — detect TH level via image matching |
| `CheckZoomOut.au3` | 34 | 1 | `mybot/search/prepare.py` | `CheckZoomOut()` — verify zoom level during search |

### 9.3 Village Management

**Source directory**: `COCBot/functions/Village/` (25,434 lines, 200+ functions, 53+ files)

This is the **largest module**. Organized by sub-function:

#### Resource Collection

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `Collect.au3` | 168 | 2 | `mybot/village/collect.py` |
| `CollectAchievements.au3` | 112 | 3 | `mybot/village/achievements.py` |
| `TreasuryCollect.au3` | 95 | 1 | `mybot/village/treasury.py` |
| `FreeMagicItems.au3` | 164 | 3 | `mybot/village/magic_items.py` |
| `isDarkElixirFull.au3` | 36 | 1 | `mybot/village/resources.py` |
| `isGoldFull.au3` | 31 | 1 | `mybot/village/resources.py` |
| `isElixirFull.au3` | 31 | 1 | `mybot/village/resources.py` |
| `isAtkDarkElixirFull.au3` | 22 | 1 | `mybot/village/resources.py` |
| `GainCost.au3` | 93 | 2 | `mybot/village/gain_cost.py` |
| `AddIdleTime.au3` | 24 | 1 | `mybot/village/idle.py` |

#### Donations & Clan

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `DonateCC.au3` | 1,955 | 20 | `mybot/village/donate.py` |
| `DonateCCWBL.au3` | 125 | 1 | `mybot/village/donate.py` |
| `RequestCC.au3` | 570 | 7 | `mybot/village/request.py` |
| `ClanCapital.au3` | 1,720 | 26 | `mybot/village/clan_capital.py` |
| `Clan Games/ClanGames.au3` | 2,802 | 33 | `mybot/village/clan_games.py` |

#### Upgrades

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `UpgradeHeroes.au3` | 1,863 | 11 | `mybot/village/upgrade_heroes.py` |
| `UpgradeBuilding.au3` | 375 | 3 | `mybot/village/upgrade_building.py` |
| `UpgradeWall.au3` | 354 | 5 | `mybot/village/upgrade_wall.py` |
| `Auto Upgrade.au3` | 544 | 5 | `mybot/village/auto_upgrade.py` |
| `LocateUpgrade.au3` | 448 | 5 | `mybot/village/locate_upgrade.py` |
| `Laboratory.au3` | 403 | 11 | `mybot/village/laboratory.py` |

#### Special Buildings

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `HelperHut.au3` | 1,518 | 7 | `mybot/village/helper_hut.py` |
| `PetHouse.au3` | 944 | 8 | `mybot/village/pet_house.py` |
| `Blacksmith.au3` | 416 | 3 | `mybot/village/blacksmith.py` |
| `BoostSuperTroop.au3` | 465 | 7 | `mybot/village/boost_super_troop.py` |
| `BoostBarracks.au3` | 116 | 5 | `mybot/village/boost.py` |
| `BoostHeroes.au3` | 123 | 6 | `mybot/village/boost.py` |
| `BoostStructure.au3` | 157 | 3 | `mybot/village/boost.py` |

#### Multi-Account & Profile

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `SwitchAccount.au3` | 954 | 19 | `mybot/village/switch_account.py` |
| `SwitchAccountVariablesReload.au3` | 693 | 1 | `mybot/village/switch_account.py` |
| `SwitchBetweenBases.au3` | 141 | 2 | `mybot/village/switch_base.py` |
| `ProfileReport.au3` | 110 | 1 | `mybot/village/profile_report.py` |

#### Village Status & Utility

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `VillageReport.au3` | 68 | 1 | `mybot/village/report.py` |
| `GetVillageSize.au3` | 513 | 5 | `mybot/village/village_size.py` |
| `GetTownHallLevel.au3` | 59 | 1 | `mybot/village/townhall.py` |
| `BotCommand.au3` | 302 | 4 | `mybot/bot.py` (command handler) |
| `BotDetectFirstTime.au3` | 121 | 1 | `mybot/village/first_time.py` |
| `DropTrophy.au3` | 349 | 2 | `mybot/village/drop_trophy.py` |
| `chkShieldStatus.au3` | 90 | 2 | `mybot/village/shield.py` |
| `BreakPersonalShield.au3` | 83 | 1 | `mybot/village/shield.py` |
| `ReplayShare.au3` | 82 | 1 | `mybot/village/replay.py` |
| `StarBonus.au3` | 35 | 1 | `mybot/village/star_bonus.py` |
| `CheckBaseQuick.au3` | 76 | 1 | `mybot/village/base_check.py` |
| `CheckNeedOpenTrain.au3` | 49 | 1 | `mybot/village/train_check.py` |
| `CheckImageType.au3` | 33 | 1 | `mybot/village/image_type.py` |
| `ConvertOCRTime.au3` | 66 | 1 | `mybot/village/time_convert.py` |
| `Notify.au3` | 780 | 16 | `mybot/notifications.py` |
| `Personal Challenges/DailyChallenges.au3` | 201 | 5 | `mybot/village/daily_challenges.py` |

#### Building Location

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `LocateTownHall.au3` | 103 | 1 | `mybot/village/locate.py` |
| `LocateClanCastle.au3` | 152 | 1 | `mybot/village/locate.py` |
| `LocateLab.au3` | 165 | 3 | `mybot/village/locate.py` |
| `LocateHeroHall.au3` | 167 | 3 | `mybot/village/locate.py` |
| `LocatePetHouse.au3` | 160 | 3 | `mybot/village/locate.py` |
| `LocateBlacksmith.au3` | 160 | 3 | `mybot/village/locate.py` |
| `LocateHelperHut.au3` | 146 | 3 | `mybot/village/locate.py` |

#### Builder Base

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `BuilderBase/LocateBuilderHall.au3` | 1,076 | 9 | `mybot/village/builder_base/locate.py` |
| `BuilderBase/BOBBuildingUpgrades.au3` | 622 | 5 | `mybot/village/builder_base/upgrades.py` |
| `BuilderBase/SuggestedUpgrades.au3` | 579 | 10 | `mybot/village/builder_base/suggested.py` |
| `BuilderBase/StarLaboratory.au3` | 520 | 7 | `mybot/village/builder_base/star_lab.py` |
| `BuilderBase/UpgradeBattleCopter.au3` | 310 | 5 | `mybot/village/builder_base/battle_copter.py` |
| `BuilderBase/UpgradeBattleMachine.au3` | 281 | 4 | `mybot/village/builder_base/battle_machine.py` |
| `BuilderBase/BuilderBaseReport.au3` | 201 | 2 | `mybot/village/builder_base/report.py` |
| `BuilderBase/Collect.au3` | 113 | 2 | `mybot/village/builder_base/collect.py` |
| `BuilderBase/StartClockTowerBoost.au3` | 112 | 2 | `mybot/village/builder_base/clock_tower.py` |
| `BuilderBase/CleanBBYard.au3` | 88 | 2 | `mybot/village/builder_base/clean_yard.py` |

### Phase 4 Deliverable

Python modules that can:
1. Verify bot is on main village screen
2. Detect and dismiss all obstacle popups
3. Search for enemy bases with loot filtering
4. Collect resources from mines/collectors
5. Donate troops to clan castle
6. Manage upgrades (buildings, walls, heroes, lab)
7. Switch between multiple accounts
8. Handle Builder Base operations

### Phase 4 Validation Checklist

- [ ] `checkMainScreen()` correctly identifies main village screen
- [ ] `checkObstacles()` handles all 20+ popup types
- [ ] Search loop finds bases matching loot criteria
- [ ] Resource collection clicks all available collectors
- [ ] Donation correctly identifies requested troops
- [ ] Multi-account switching works for 2+ accounts
- [ ] Builder Base detection and operations work

---

## 10. Phase 5: Army Training & Attack Systems

**Priority**: HIGH — the core "bot" functionality
**Source lines**: ~21,275 (CreateArmy 7,070 + Attack 13,561 + MOD 644)
**Target files**: ~35 Python modules
**Dependencies**: Phase 1-4 (all previous phases)

### 10.1 Army Training System

**Source directory**: `COCBot/functions/CreateArmy/` (7,070 lines, 110+ functions, 30+ files)

#### Core Training

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `TrainSystem.au3` | 1,607 | 39 | `mybot/army/train.py` | `TrainSystem()` — main orchestrator. Calls `CheckIfArmyIsReady()`, `QuickTrain()`/`TrainCustomArmy()`, `TrainSiege()`. 39 sub-functions for different training phases |
| `QuickTrain.au3` | 583 | 4 | `mybot/army/quick_train.py` | `QuickTrain()`, `CheckQuickTrainTroop()`, `TrainArmyNumber()` |
| `DoubleTrain.au3` | 353 | 7 | `mybot/army/double_train.py` | `DoubleTrain()` — train second army while first fights |
| `openArmyOverview.au3` | 314 | 10 | `mybot/army/army_overview.py` | `OpenArmyOverview()` — open army tab, navigate sub-tabs |
| `TrainSiege.au3` | 209 | 7 | `mybot/army/train_siege.py` | `TrainSiege()` — train siege machines |
| `TrainIt.au3` | 161 | 3 | `mybot/army/train_it.py` | `TrainIt()` — execute training clicks for specific troop |
| `checkArmyCamp.au3` | 139 | 3 | `mybot/army/check_camp.py` | `checkArmyCamp()` — verify army camp contents |
| `TrainClick.au3` | 77 | 2 | `mybot/army/train_click.py` | `TrainClick()` — click training buttons with quantity |
| `SmartWait4Train.au3` | 68 | 1 | `mybot/army/smart_wait.py` | `SmartWait4Train()` — calculate optimal wait time |
| `CheckFullArmy.au3` | 68 | 1 | `mybot/army/check_full.py` | `CheckFullArmy()` — determine if army is complete |

#### Army Reading (detect what's currently trained)

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `getArmyHeroes/getArmyHeroCount.au3` | 2,226 | 17 | `mybot/army/read_heroes.py` |
| `getArmyHeroes/getArmyHeroTime.au3` | 131 | 1 | `mybot/army/read_heroes.py` |
| `getArmyTroops/getArmyTroops.au3` | 93 | 1 | `mybot/army/read_troops.py` |
| `getArmyTroops/getArmyTroopCapacity.au3` | 141 | 1 | `mybot/army/read_troops.py` |
| `getArmyTroops/getArmyTroopTime.au3` | 47 | 1 | `mybot/army/read_troops.py` |
| `getArmySpells/getArmySpells.au3` | 74 | 1 | `mybot/army/read_spells.py` |
| `getArmySpells/getArmySpellCapacity.au3` | 79 | 1 | `mybot/army/read_spells.py` |
| `getArmySpells/getArmySpellCount.au3` | 25 | 1 | `mybot/army/read_spells.py` |
| `getArmySpells/getArmySpellTime.au3` | 40 | 1 | `mybot/army/read_spells.py` |
| `getArmySiegeMachines/getArmySiegeMachines.au3` | 127 | 1 | `mybot/army/read_siege.py` |
| `getArmyCCTroops/getArmyCCTroops.au3` | 101 | 1 | `mybot/army/read_cc.py` |
| `getArmyCCTroops/getArmyCCStatus.au3` | 56 | 1 | `mybot/army/read_cc.py` |
| `getArmyCCSpells/getArmyCCSpell.au3` | 134 | 2 | `mybot/army/read_cc.py` |
| `getArmyCCSpells/getArmyCCSpellCapacity.au3` | 72 | 1 | `mybot/army/read_cc.py` |
| `getArmyCCSiegeMachines/getArmyCCSiegeMachines.au3` | 145 | 3 | `mybot/army/read_cc.py` |

### 10.2 Attack System

**Source directory**: `COCBot/functions/Attack/` (13,561 lines, 150+ functions, 50+ files)

#### Attack Preparation & Execution

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `PrepareAttack.au3` | 463 | 5 | `mybot/attack/prepare.py` | `PrepareAttack()` — set up attack: read troop bar, select mode |
| `GetAttackBar.au3` | 513 | 9 | `mybot/attack/attack_bar.py` | `GetAttackBar()` — read troop slots from bottom bar during battle |
| `ReturnHome.au3` | 424 | 5 | `mybot/attack/return_home.py` | `ReturnHome()` — end battle, collect stars/loot |
| `AttackReport.au3` | 292 | 2 | `mybot/attack/report.py` | `AttackReport()` — log attack results |
| `AttackStats.au3` | 164 | 6 | `mybot/attack/stats.py` | Attack statistics tracking |
| `BuildingSide.au3` | 173 | 5 | `mybot/attack/building_side.py` | Determine which side buildings are on |
| `unbreakable.au3` | 151 | 1 | `mybot/attack/unbreakable.py` | Unbreakable defense achievement |
| `GoldElixirChangeEBO.au3` | 312 | 1 | `mybot/attack/resource_change.py` | Track resource changes during attack |
| `GoldElixirChangeThSnipes.au3` | 76 | 1 | `mybot/attack/resource_change.py` | TH snipe resource tracking |

#### Attack Algorithms

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `Attack Algorithms/SmartFarm.au3` | 950 | 10 | `mybot/attack/algorithms/smart_farm.py` | `SmartFarm()` — intelligent farming: target collectors, deploy troops near loot |
| `Attack Algorithms/AttackFromCSV.au3` | 949 | 6 | `mybot/attack/algorithms/csv_attack.py` | `Algorithm_AttackCSV()` — execute CSV-scripted attacks |
| `Attack Algorithms/algorithm_AllTroops.au3` | 559 | 4 | `mybot/attack/algorithms/all_troops.py` | `algorithm_AllTroops()` — deploy all troops on one or multiple sides |

#### CSV Attack Script Engine

| Source file | Lines | Funcs | Target file | Notes |
|-------------|-------|-------|-------------|-------|
| `AttackCSV/ParseAttackCSV.au3` | 1,075 | 4 | `mybot/attack/csv/parser.py` | **CRITICAL**: Uses `Assign()` and `Eval()` heavily for dynamic vector creation. Must replace with dict-based system |
| `AttackCSV/DropTroopFromINI.au3` | 312 | 1 | `mybot/attack/csv/drop.py` | Execute DROP command from CSV |
| `AttackCSV/MakeDropPoints.au3` | 303 | 2 | `mybot/attack/csv/drop_points.py` | Calculate drop point coordinates from MAKE vectors |
| `AttackCSV/MakeDropLine.au3` | 126 | 2 | `mybot/attack/csv/drop_line.py` | Calculate line-based drop points |
| `AttackCSV/AttackCSVDebugImage.au3` | 392 | 1 | `mybot/attack/csv/debug.py` | Debug visualization of CSV attacks |
| `AttackCSV/ParseAttackCSV_Settings_variables.au3` | 219 | 1 | `mybot/attack/csv/settings.py` | CSV script global settings |
| `AttackCSV/ParseAttackCSV_Read_SIDE_variables.au3` | 134 | 1 | `mybot/attack/csv/sides.py` | Parse SIDE/SIDEB commands |
| `AttackCSV/Slice8.au3` | 141 | 1 | `mybot/attack/csv/slice.py` | Divide edge into 8 segments |
| `AttackCSV/CheckCSVValues.au3` | 110 | 1 | `mybot/attack/csv/validate.py` | Validate CSV script syntax |
| `AttackCSV/GetListPixel3.au3` | 36 | 1 | `mybot/attack/csv/pixels.py` | Pixel list for CSV |
| `AttackCSV/IsInsideDiamondRedArea.au3` | 35 | 1 | `mybot/attack/csv/geometry.py` | Diamond boundary check |
| `AttackCSV/Line2Points.au3` | 20 | 1 | `mybot/attack/csv/geometry.py` | Line interpolation |
| `AttackCSV/CleanRedArea.au3` | 29 | 1 | `mybot/attack/csv/clean.py` | Clean cached red area |
| `AttackCSV/ChkAttackCSVConfig.au3` | 30 | 1 | `mybot/attack/csv/validate.py` | Check CSV config |
| `AttackCSV/DebugAttackCSV.au3` | 22 | 1 | `mybot/attack/csv/debug.py` | Debug toggle |

**CSV parser translation (CRITICAL — uses Assign/Eval):**
```python
# mybot/attack/csv/parser.py
@dataclass
class AttackVector:
    side: str
    points: list[tuple[int, int]]
    index_range: range

class CSVAttackScript:
    def __init__(self, path: Path):
        self.vectors: dict[str, AttackVector] = {}  # Replaces Assign("ATTACKVECTOR_X", ...)
        self.commands: list[CSVCommand] = []
        self._parse(path)

    def _parse(self, path: Path) -> None:
        for line in path.read_text().splitlines():
            parts = line.split("|")
            cmd = parts[0].strip()
            if cmd == "MAKE":
                self.vectors[parts[1].strip()] = AttackVector(...)
            elif cmd == "DROP":
                self.commands.append(DropCommand(...))
            # ... etc

    def execute(self, bot: BotState) -> None:
        for cmd in self.commands:
            cmd.execute(bot)
```

#### Red Area / Deployment Zone

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `RedArea/GetLocation.au3` | 473 | 12 | `mybot/attack/location.py` | `GetLocationTownHall()`, `GetLocationDarkElixirStorage()`, `GetLocationMineExtractor()`, etc. — all use DllCallMyBot for image search |
| `RedArea/_GetRedArea.au3` | 468 | 11 | `mybot/attack/red_area.py` | `_GetRedArea()` — detect valid troop deployment zone |
| `RedArea/PointInPoly.au3` | 341 | 5 | `mybot/attack/geometry.py` | `PointInPoly()` — point-in-polygon test for deployment validation |
| `RedArea/DropTroop.au3` | 197 | 2 | `mybot/attack/deploy.py` | `DropTroop()` — deploy troop at coordinates |
| `RedArea/DropOnPixel.au3` | 85 | 1 | `mybot/attack/deploy.py` | `DropOnPixel()` — deploy on specific pixel |
| `RedArea/_GetOffsetTroopFurther.au3` | 104 | 1 | `mybot/attack/geometry.py` | Offset troop position further from base |
| `RedArea/GetVectorPixelOnEachSide.au3` | 64 | 1 | `mybot/attack/geometry.py` | Get deployment pixels per side |
| `RedArea/GetPixelDropTroop.au3` | 59 | 1 | `mybot/attack/geometry.py` | Calculate pixel for troop drop |
| `RedArea/GetOffestPixelRedArea2.au3` | 54 | 1 | `mybot/attack/geometry.py` | Red area offset calculation |
| `RedArea/_GetVectorOutZone.au3` | 67 | 1 | `mybot/attack/geometry.py` | Vectors outside deployment zone |
| `RedArea/_FindPixelCloser.au3` | 63 | 1 | `mybot/attack/geometry.py` | Find closest valid pixel |
| `RedArea/GetPixelSide.au3` | 23 | 1 | `mybot/attack/geometry.py` | Get pixel side classification |
| `RedArea/DebugRedArea.au3` | 21 | 1 | `mybot/attack/debug.py` | Red area debug visualization |

#### Troop Management

| Source file | Lines | Funcs | Target file | Key functions |
|-------------|-------|-------|-------------|---------------|
| `Troops/CheckHeroesHealth.au3` | 269 | 1 | `mybot/attack/heroes.py` | `CheckHeroesHealth()` — monitor hero HP during battle, activate ability |
| `Troops/LaunchTroop.au3` | 269 | 2 | `mybot/attack/launch.py` | `LaunchTroop()` — deploy troop from bar to battlefield |
| `Troops/DropOrderTroops.au3` | 241 | 4 | `mybot/attack/drop_order.py` | `DropOrderTroops()` — custom troop deployment order |
| `Troops/dropHeroes.au3` | 173 | 7 | `mybot/attack/heroes.py` | `dropKing()`, `dropQueen()`, `dropWarden()`, `dropChampion()`, `dropPrince()` |
| `Troops/ReadTroopQuantity.au3` | 81 | 3 | `mybot/attack/troop_quantity.py` | Read troop counts from attack bar |
| `Troops/DropOnEdge.au3` | 75 | 1 | `mybot/attack/deploy.py` | Deploy troops on edge |
| `Troops/DropOnEdges.au3` | 55 | 1 | `mybot/attack/deploy.py` | Deploy on multiple edges |
| `Troops/dropCC.au3` | 58 | 1 | `mybot/attack/deploy.py` | Deploy clan castle troops |
| `Troops/SetSleep.au3` | 55 | 2 | `mybot/attack/timing.py` | Set deployment delays |
| `Troops/SelectDropTroop.au3` | 38 | 2 | `mybot/attack/select.py` | Select troop in attack bar |
| `Troops/OldDropTroop.au3` | 24 | 1 | _(deprecated, skip)_ | Legacy drop function |
| `Troops/GetSlotIndexFromXPos.au3` | 21 | 1 | `mybot/attack/attack_bar.py` | Map X position to troop slot |

#### Smart Zap (Dark Elixir stealing)

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `SmartZap/smartZap.au3` | 652 | 7 | `mybot/attack/smart_zap.py` |
| `SmartZap/drillSearch.au3` | 142 | 3 | `mybot/attack/drill_search.py` |
| `SmartZap/easyPreySearch.au3` | 89 | 1 | `mybot/attack/easy_prey.py` |

#### Builder Base Attack

| Source file | Lines | Funcs | Target file |
|-------------|-------|-------|-------------|
| `BuilderBase/AttackBB.au3` | 881 | 23 | `mybot/attack/builder_base/attack.py` |
| `BuilderBase/PrepareAttackBB.au3` | 249 | 9 | `mybot/attack/builder_base/prepare.py` |
| `BuilderBase/GetAttackBarBB.au3` | 160 | 1 | `mybot/attack/builder_base/attack_bar.py` |

### 10.3 MOD / Attack Modes

**Source directory**: `COCBot/functions/MOD/` (644 lines, 6 functions, 6 files)

| Source file | Lines | Funcs | Target file | Notes |
|-------------|-------|-------|-------------|-------|
| `AttackCycle.au3` | 154 | 1 | `mybot/attack/cycle.py` | Main attack loop coordinator — calls donate, upgrade, then attack |
| `BBSpam.au3` | 158 | 1 | `mybot/attack/modes/bb_spam.py` | Builder Base spam attack mode |
| `CCSpam.au3` | 82 | 1 | `mybot/attack/modes/cc_spam.py` | Clan Castle spam mode |
| `DirectAttack.au3` | 83 | 1 | `mybot/attack/modes/direct.py` | Direct attack without searching |
| `RankedBattle.au3` | 91 | 1 | `mybot/attack/modes/ranked.py` | Ranked battle mode |
| `RevengeBattle.au3` | 76 | 1 | `mybot/attack/modes/revenge.py` | Revenge attack mode |

### Phase 5 Deliverable

Python modules that can:
1. Read current army composition (troops, spells, heroes, siege, CC)
2. Train army via Quick Train or custom composition
3. Execute attacks using all algorithms (AllTroops, CSV, SmartFarm)
4. Parse and execute CSV attack scripts without `eval()`
5. Detect red deployment zone and calculate drop points
6. Deploy troops with proper timing and ordering
7. Monitor hero health and activate abilities
8. Handle Builder Base attacks

### Phase 5 Validation Checklist

- [ ] Army reading matches actual troop counts in all slots
- [ ] Quick Train correctly trains configured army
- [ ] CSV parser handles all 20+ existing CSV scripts
- [ ] CSV attack execution produces same troop drops as AutoIt version
- [ ] Red area detection matches expected deployment zone
- [ ] Hero ability activation fires at correct HP threshold
- [ ] SmartFarm targets correct collector positions
- [ ] Attack return home correctly reads loot gained

---

## 11. Phase 6: GUI & Application Shell

**Priority**: MEDIUM — bot can run headless during Phases 1-5
**Source lines**: ~35,000 (GUI/ 22,000 + top-level 10,800 + MBR GUI files)
**Target files**: ~35 Python modules
**Dependencies**: Phase 1-5 (all previous phases)

### 11.1 Main Entry Point

**Source files**: `MyBot.run.au3` (1,600 lines, 20 functions)

| Function | Lines | Target | Purpose |
|----------|-------|--------|---------|
| `InitializeBot()` | ~400 | `mybot/app.py: App.__init__()` | Parse CLI args, init subsystems, create GUI |
| `MainLoop()` | ~200 | `mybot/app.py: App.run()` | Event loop dispatching on `$g_iBotAction` |
| `runBot()` | ~500 | `mybot/bot.py: Bot.run()` | Main bot cycle — the infinite loop |
| `Initiate()` | ~100 | `mybot/bot.py: Bot.initiate()` | Check screen, zoom out, start main cycle |
| `FirstCheck()` | ~80 | `mybot/bot.py: Bot.first_check()` | One-time initialization checks |
| Plus 15 helper funcs | ~320 | Distributed | Various setup utilities |

**Target file**: `mybot/app.py` — Application entry point

```python
# mybot/app.py
class App:
    def __init__(self, args: argparse.Namespace):
        self.config = read_config(args.profile)
        self.state = BotState()
        self.bot = Bot(self.config, self.state)
        if not args.nogui:
            self.gui = MainWindow(self.config, self.state, self.bot)

    def run(self) -> None:
        if self.gui:
            self.gui.show()
        # Start bot in background thread
        self.bot_thread = threading.Thread(target=self.bot.run, daemon=True)
```

### 11.2 Bot Controller

**Source file**: `COCBot/MBR GUI Action.au3` (298 lines, 3 functions)

| Function | Target | Purpose |
|----------|--------|---------|
| `BotStart()` | `mybot/bot.py: Bot.start()` | Open Android, init, start main loop |
| `BotStop()` | `mybot/bot.py: Bot.stop()` | Cleanup, release resources |
| `BotSearchMode()` | `mybot/bot.py: Bot.search_mode()` | Search-only mode (no attack) |

### 11.3 GUI Design Files → PyQt6 Tabs

**Source directory**: `COCBot/GUI/` — Design files (layout creation)

| Source file | Lines | Controls | Target file | Tab/Section |
|-------------|-------|----------|-------------|-------------|
| `MBR GUI Design Bottom.au3` | 303 | ~50 | `mybot/gui/bottom_bar.py` | Status bar, Start/Stop/Pause buttons |
| `MBR GUI Design Log.au3` | 93 | ~5 | `mybot/gui/log_widget.py` | Log display (QTextEdit with colors) |
| `MBR GUI Design Splash.au3` | 113 | ~10 | `mybot/gui/splash.py` | Loading splash screen |
| `MBR GUI Design Village.au3` | 47 | ~5 | `mybot/gui/tabs/village.py` | Village tab container |
| `MBR GUI Design Bot.au3` | 66 | ~5 | `mybot/gui/tabs/bot.py` | Bot options tab container |
| `MBR GUI Design Attack.au3` | 143 | ~10 | `mybot/gui/tabs/attack.py` | Attack tab container |
| `MBR GUI Design About.au3` | 161 | ~15 | `mybot/gui/tabs/about.py` | About/info tab |
| **Village child tabs:** | | | |
| `Design Child Village - Donate.au3` | 3,966 | ~400 | `mybot/gui/tabs/village/donate.py` | Donation settings (LARGEST GUI file) |
| `Design Child Village - Misc.au3` | 1,030 | ~100 | `mybot/gui/tabs/village/misc.py` | Miscellaneous village settings |
| `Design Child Village - Upgrade.au3` | 975 | ~80 | `mybot/gui/tabs/village/upgrade.py` | Upgrade configuration |
| `Design Child Village - Notify.au3` | 212 | ~25 | `mybot/gui/tabs/village/notify.py` | Notification settings |
| `Design Child Village - Achievements.au3` | 105 | ~10 | `mybot/gui/tabs/village/achievements.py` | Achievement tracking |
| **Bot child tabs:** | | | |
| `Design Child Bot - Stats.au3` | 1,960 | ~150 | `mybot/gui/tabs/bot/stats.py` | Statistics display |
| `Design Child Bot - Options.au3` | 261 | ~25 | `mybot/gui/tabs/bot/options.py` | Bot options |
| `Design Child Bot - Debug.au3` | 201 | ~20 | `mybot/gui/tabs/bot/debug.py` | Debug settings |
| `Design Child Bot - Profiles.au3` | 193 | ~15 | `mybot/gui/tabs/bot/profiles.py` | Profile management |
| `Design Child Bot - Android.au3` | 188 | ~15 | `mybot/gui/tabs/bot/android.py` | Android emulator settings |
| **Attack child tabs:** | | | |
| `Design Child Attack - Troops.au3` | 1,760 | ~150 | `mybot/gui/tabs/attack/troops.py` | Troop selection & configuration |
| `Design Child Attack - Deadbase-Search.au3` | 346 | ~30 | `mybot/gui/tabs/attack/deadbase_search.py` | Dead base search settings |
| `Design Child Attack - Activebase-Search.au3` | 338 | ~30 | `mybot/gui/tabs/attack/activebase_search.py` | Active base search settings |
| `Design Child Attack - Options-Attack.au3` | 465 | ~40 | `mybot/gui/tabs/attack/options_attack.py` | Attack options |
| `Design Child Attack - Options-Search.au3` | 158 | ~15 | `mybot/gui/tabs/attack/options_search.py` | Search options |
| Plus ~20 more attack design files | ~2,000 | ~200 | `mybot/gui/tabs/attack/*.py` | Various attack subtabs |

### 11.4 GUI Control Files → PyQt6 Event Handlers

| Source file | Lines | Funcs | Target file | Purpose |
|-------------|-------|-------|-------------|---------|
| `MBR GUI Control.au3` | 2,276 | 71 | `mybot/gui/main_window.py` | Main window event handlers |
| `MBR GUI Control Variables.au3` | 352 | 1 | _(absorbed into widget refs)_ | GUI handle declarations |
| `Control Bottom.au3` | 503 | 27 | `mybot/gui/bottom_bar.py` | `Initiate()`, `InitiateLayout()` |
| `Control Child Army.au3` | 1,608 | 81 | `mybot/gui/handlers/army.py` | Army tab event handlers |
| `Control Child Misc.au3` | 1,585 | 98 | `mybot/gui/handlers/misc.py` | Misc tab handlers |
| `Control BOT Options.au3` | 1,226 | 68 | `mybot/gui/handlers/bot_options.py` | Bot options handlers |
| `Control Child Upgrade.au3` | 980 | 40 | `mybot/gui/handlers/upgrade.py` | Upgrade tab handlers |
| `Control Attack Scripted.au3` | 613 | 19 | `mybot/gui/handlers/attack_scripted.py` | Scripted attack handlers |
| `Control Child Attack.au3` | 464 | 32 | `mybot/gui/handlers/attack.py` | Attack tab handlers |
| `Control Tab Search.au3` | 402 | 38 | `mybot/gui/handlers/search.py` | Search settings handlers |
| `Control Donate.au3` | 292 | 20 | `mybot/gui/handlers/donate.py` | Donation handlers |
| `Control Android.au3` | 248 | 15 | `mybot/gui/handlers/android.py` | Android settings handlers |
| `Control Preset.au3` | 247 | 8 | `mybot/gui/handlers/preset.py` | Preset/strategy handlers |
| `Control Tab DropOrder.au3` | 233 | 9 | `mybot/gui/handlers/drop_order.py` | Drop order handlers |
| `Control Tab Village.au3` | 169 | 10 | `mybot/gui/handlers/village.py` | Village tab handlers |
| `Control Tab EndBattle.au3` | 145 | 10 | `mybot/gui/handlers/end_battle.py` | End battle handlers |
| `Control Tab General.au3` | 141 | 4 | `mybot/gui/handlers/general.py` | General tab handlers |
| `Control Notify.au3` | 114 | 6 | `mybot/gui/handlers/notify.py` | Notification handlers |
| `Control Tab Stats.au3` | 104 | 6 | `mybot/gui/handlers/stats.py` | Statistics handlers |
| `Control Splash.au3` | 70 | 4 | `mybot/gui/splash.py` | Splash screen handlers |
| `Control Tab SmartZap.au3` | 85 | 8 | `mybot/gui/handlers/smart_zap.py` | SmartZap handlers |
| `Control Achievements.au3` | 37 | 1 | `mybot/gui/handlers/achievements.py` | Achievement handlers |
| `Control Collectors.au3` | 33 | 3 | `mybot/gui/handlers/collectors.py` | Collector handlers |
| `Control Attack Standard.au3` | 43 | 2 | `mybot/gui/handlers/attack_standard.py` | Standard attack handlers |

### 11.5 Other Application Components

| Source file | Lines | Target file | Purpose |
|-------------|-------|-------------|---------|
| `MBR GUI Design.au3` | 681 | `mybot/gui/main_window.py` | Main window creation |
| `MBR GUI Design Mini.au3` | 537 | `mybot/gui/mini_window.py` | Mini GUI for multi-instance |
| `MyBot.run.MiniGui.au3` | 1,482 | `mybot/gui/mini_manager.py` | Multi-instance manager |
| `MyBot.run.Watchdog.au3` | 196 | `mybot/watchdog.py` | Watchdog process |
| `MyBot.run.Wmi.au3` | 136 | `mybot/system/wmi.py` | WMI process queries |
| `MultiBot.au3` | 1,324 | `mybot/multi_bot.py` | Multi-instance launcher |
| `MBR References.au3` | 530 | _(not needed)_ | AutoIt code stripping prevention |

### 11.6 API Server

**Source files**: `Other/Api.au3` (92 lines), `ApiClient.au3` (356 lines), `ApiHost.au3` (273 lines)

| Source | Target | Purpose |
|--------|--------|---------|
| `Api.au3` | `mybot/api/server.py` | FastAPI server for external control |
| `ApiClient.au3` | `mybot/api/client.py` | HTTP client for bot-to-bot communication |
| `ApiHost.au3` | `mybot/api/server.py` | API endpoint handlers |

### Phase 6 Deliverable

Complete Python application:
1. PyQt6 GUI matching AutoIt GUI layout and functionality
2. All event handlers wired to bot logic
3. Start/Stop/Pause controls
4. Real-time log display with colors
5. Statistics tracking and display
6. Multi-instance support
7. API server for external control
8. Watchdog process for crash recovery

### Phase 6 Validation Checklist

- [ ] GUI launches and shows all tabs
- [ ] All 3,775 controls have PyQt6 equivalents
- [ ] Start/Stop/Pause buttons work correctly
- [ ] Log widget displays colored messages in real-time
- [ ] Config changes in GUI save to INI on close
- [ ] Profile switching works in GUI
- [ ] Multi-instance launcher works
- [ ] API server responds to health/status endpoints
- [ ] Bot runs complete cycle via GUI (start → collect → train → attack → stop)

---

## 12. Risk Assessment

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **MBRBot.dll accuracy mismatch** | CRITICAL | HIGH | Prototype Phase 3 first. Capture test screenshots from AutoIt version, compare opencv-python results. Build accuracy benchmark. Accept ≥95% match rate |
| **OCR accuracy for game fonts** | HIGH | MEDIUM | Test pytesseract on game screenshots early. If insufficient, train Tesseract on game font or build custom matcher using existing `listSymbols_coc-*.xml` templates |
| **GUI complexity (3,775 controls)** | HIGH | MEDIUM | Start with headless/CLI mode. Build GUI incrementally. Consider auto-generating PyQt6 layout from AutoIt GUI definitions |
| **CSV attack script Assign/Eval** | HIGH | LOW | Dict-based replacement is well-understood. Test all 20+ scripts after translation |
| **Execute() dynamic dispatch** | HIGH | LOW | Strategy pattern replacement is straightforward. Test all 3 emulator types |
| **Windows API dependencies (251 calls)** | MEDIUM | LOW | pywin32 provides all needed functions. Test on Windows 10/11 |
| **ADB timing / race conditions** | MEDIUM | MEDIUM | Add proper retry logic, connection pooling, timeout handling |
| **Config INI compatibility** | LOW | LOW | configparser reads same format. Round-trip test validates |
| **Performance regression** | MEDIUM | MEDIUM | Python is slower than AutoIt+DLL for image matching. Mitigate with numpy vectorization, template caching, parallel matching |
| **Multi-account state isolation** | MEDIUM | MEDIUM | Careful BotState design with per-account containers |

---

## 13. Execution Order & Parallelism

```
Phase 1: Foundation ──────► Phase 2: Android ──────► Phase 3: Vision
   (2 weeks)                  (2 weeks)                (3 weeks)
   Config, logging,           ADB, emulators,          OpenCV, OCR,
   state, i18n                input, capture            templates
                                                            │
                              ┌─────────────────────────────┤
                              ▼                             ▼
                    Phase 4: Game Logic          Phase 5: Army & Attack
                    (3 weeks)                    (3 weeks)
                    Village, search,             Training, deployment,
                    collection                   CSV scripts
                              │         CAN RUN           │
                              │        IN PARALLEL        │
                              └──────────┬────────────────┘
                                         ▼
                              Phase 6: GUI & App Shell
                              (4 weeks)
                              PyQt6 GUI, API server,
                              entry point, watchdog
```

**Phases 4 and 5 can run in parallel** once Phases 1-3 are complete.

**Estimated total**: ~17 weeks for single developer, ~10 weeks with 2 developers working in parallel on Phase 4+5.

---

## 14. Python Project Structure (Final)

```
mybot-python/
├── pyproject.toml
├── README.md
├── TRANSLATION_PLAN.md              ← This file
├── mybot/
│   ├── __init__.py
│   ├── app.py                       ← Entry point (Phase 6)
│   ├── bot.py                       ← Bot controller (Phase 6)
│   ├── constants.py                 ← Game constants (Phase 1)
│   ├── enums.py                     ← All enumerations (Phase 1)
│   ├── state.py                     ← BotState dataclass hierarchy (Phase 1)
│   ├── i18n.py                      ← Translation system (Phase 1)
│   ├── watchdog.py                  ← Watchdog process (Phase 6)
│   ├── multi_bot.py                 ← Multi-instance launcher (Phase 6)
│   ├── notifications.py             ← Push notifications (Phase 6)
│   │
│   ├── config/                      ← Phase 1
│   │   ├── __init__.py
│   │   ├── models.py                ← Pydantic config models
│   │   ├── reader.py                ← INI → config
│   │   ├── writer.py                ← Config → INI
│   │   ├── applier.py               ← Config → GUI
│   │   ├── coordinates.py           ← Screen coordinates
│   │   ├── delays.py                ← Delay constants
│   │   ├── image_dirs.py            ← Image template paths
│   │   ├── profiles.py              ← Profile management
│   │   └── ini_table.py             ← INI batch operations
│   │
│   ├── android/                     ← Phase 2
│   │   ├── __init__.py
│   │   ├── adb.py                   ← ADB client
│   │   ├── base.py                  ← Abstract emulator interface
│   │   ├── bluestacks.py            ← BlueStacks5 implementation
│   │   ├── memu.py                  ← MEmu implementation
│   │   ├── nox.py                   ← Nox implementation
│   │   ├── manager.py               ← Emulator lifecycle
│   │   ├── embed.py                 ← Window embedding
│   │   ├── input.py                 ← Click/drag/touch
│   │   ├── capture.py               ← Screenshot capture
│   │   ├── app.py                   ← Open/close CoC
│   │   ├── health.py                ← Reboot/restart conditions
│   │   ├── position.py              ← Window position
│   │   ├── zoom.py                  ← Zoom control
│   │   ├── distributors.py          ← Game distributor detection
│   │   └── shortcuts.py             ← Menu shortcuts
│   │
│   ├── vision/                      ← Phase 3
│   │   ├── __init__.py
│   │   ├── matcher.py               ← OpenCV template matching
│   │   ├── templates.py             ← XML template loader
│   │   ├── pixel.py                 ← Pixel color operations
│   │   ├── geometry.py              ← Diamond bounds, point-in-poly
│   │   ├── ocr.py                   ← Text recognition
│   │   ├── building_info.py         ← Building info reader
│   │   ├── dead_base.py             ← Dead base detection
│   │   ├── tombs.py                 ← Tombstone detection
│   │   ├── townhall.py              ← TH detection
│   │   ├── walls.py                 ← Wall level detection
│   │   ├── window_detect.py         ← Game window detection
│   │   └── quick_search.py          ← Quick multi-image search
│   │
│   ├── game/                        ← Phase 4
│   │   ├── __init__.py
│   │   ├── main_screen.py           ← Main screen checks
│   │   └── obstacles.py             ← Popup detection/dismiss
│   │
│   ├── search/                      ← Phase 4
│   │   ├── __init__.py
│   │   ├── search.py                ← Village search loop
│   │   ├── multi.py                 ← Multi-criteria search
│   │   ├── resources.py             ← Loot reading & comparison
│   │   ├── filters.py               ← Search mode filters
│   │   ├── weak_base.py             ← Weak base detection
│   │   ├── clouds.py                ← Cloud waiting
│   │   ├── prepare.py               ← Pre-search setup
│   │   └── townhall.py              ← TH detection in search
│   │
│   ├── village/                     ← Phase 4
│   │   ├── __init__.py
│   │   ├── collect.py               ← Resource collection
│   │   ├── report.py                ← Village status report
│   │   ├── donate.py                ← CC donations
│   │   ├── request.py               ← CC requests
│   │   ├── laboratory.py            ← Lab upgrades
│   │   ├── upgrade_building.py      ← Building upgrades
│   │   ├── upgrade_wall.py          ← Wall upgrades
│   │   ├── upgrade_heroes.py        ← Hero upgrades
│   │   ├── auto_upgrade.py          ← Auto upgrade
│   │   ├── locate.py                ← Building location (7 buildings)
│   │   ├── locate_upgrade.py        ← Upgrade location
│   │   ├── switch_account.py        ← Multi-account switching
│   │   ├── switch_base.py           ← Home/Builder Base switching
│   │   ├── boost.py                 ← Barracks/heroes/structures
│   │   ├── boost_super_troop.py     ← Super troop activation
│   │   ├── helper_hut.py            ← Helper Hut management
│   │   ├── pet_house.py             ← Pet House management
│   │   ├── blacksmith.py            ← Blacksmith management
│   │   ├── clan_capital.py          ← Clan Capital
│   │   ├── clan_games.py            ← Clan Games
│   │   ├── daily_challenges.py      ← Daily challenges
│   │   ├── magic_items.py           ← Free magic items
│   │   ├── resources.py             ← Resource full checks
│   │   ├── treasury.py              ← Treasury collection
│   │   ├── achievements.py          ← Achievement collection
│   │   ├── shield.py                ← Shield status
│   │   ├── drop_trophy.py           ← Trophy dropping
│   │   ├── village_size.py          ← Village size detection
│   │   ├── townhall.py              ← TH level detection
│   │   ├── gain_cost.py             ← Gain/cost tracking
│   │   ├── profile_report.py        ← Profile statistics
│   │   ├── first_time.py            ← First-time detection
│   │   ├── time_convert.py          ← OCR time conversion
│   │   └── builder_base/            ← BB sub-module (10 files)
│   │
│   ├── army/                        ← Phase 5
│   │   ├── __init__.py
│   │   ├── train.py                 ← Training orchestrator
│   │   ├── quick_train.py           ← Quick train mode
│   │   ├── double_train.py          ← Double train mode
│   │   ├── army_overview.py         ← Open army overview
│   │   ├── train_siege.py           ← Siege training
│   │   ├── train_it.py              ← Execute training clicks
│   │   ├── train_click.py           ← Training button clicks
│   │   ├── check_camp.py            ← Army camp check
│   │   ├── check_full.py            ← Full army check
│   │   ├── smart_wait.py            ← Smart wait for training
│   │   ├── read_troops.py           ← Read troop composition
│   │   ├── read_spells.py           ← Read spell composition
│   │   ├── read_heroes.py           ← Read hero status
│   │   ├── read_siege.py            ← Read siege machines
│   │   └── read_cc.py               ← Read CC contents
│   │
│   ├── attack/                      ← Phase 5
│   │   ├── __init__.py
│   │   ├── cycle.py                 ← Attack cycle coordinator
│   │   ├── prepare.py               ← Pre-attack setup
│   │   ├── attack_bar.py            ← Read attack bar
│   │   ├── deploy.py                ← Troop deployment
│   │   ├── heroes.py                ← Hero deployment & health
│   │   ├── launch.py                ← Troop launching
│   │   ├── select.py                ← Troop selection
│   │   ├── drop_order.py            ← Custom drop order
│   │   ├── red_area.py              ← Red area detection
│   │   ├── location.py              ← Building location (attack)
│   │   ├── geometry.py              ← Attack geometry calculations
│   │   ├── return_home.py           ← End battle
│   │   ├── report.py                ← Attack report
│   │   ├── stats.py                 ← Attack statistics
│   │   ├── building_side.py         ← Building side detection
│   │   ├── resource_change.py       ← Resource tracking
│   │   ├── timing.py                ← Deployment timing
│   │   ├── smart_zap.py             ← Smart zap
│   │   ├── drill_search.py          ← DE drill search
│   │   ├── easy_prey.py             ← Easy prey search
│   │   ├── debug.py                 ← Attack debug visualization
│   │   ├── algorithms/              ← Attack algorithms
│   │   │   ├── all_troops.py
│   │   │   ├── csv_attack.py
│   │   │   └── smart_farm.py
│   │   ├── csv/                     ← CSV attack engine
│   │   │   ├── parser.py
│   │   │   ├── executor.py
│   │   │   ├── drop.py
│   │   │   ├── drop_points.py
│   │   │   ├── drop_line.py
│   │   │   ├── sides.py
│   │   │   ├── settings.py
│   │   │   ├── validate.py
│   │   │   ├── geometry.py
│   │   │   ├── slice.py
│   │   │   ├── debug.py
│   │   │   └── clean.py
│   │   ├── modes/                   ← Special attack modes
│   │   │   ├── bb_spam.py
│   │   │   ├── cc_spam.py
│   │   │   ├── direct.py
│   │   │   ├── ranked.py
│   │   │   └── revenge.py
│   │   └── builder_base/            ← BB attack
│   │       ├── attack.py
│   │       ├── prepare.py
│   │       └── attack_bar.py
│   │
│   ├── gui/                         ← Phase 6
│   │   ├── __init__.py
│   │   ├── main_window.py           ← Main window (QMainWindow)
│   │   ├── bottom_bar.py            ← Bottom control bar
│   │   ├── log_widget.py            ← Log display widget
│   │   ├── splash.py                ← Splash screen
│   │   ├── mini_window.py           ← Mini GUI
│   │   ├── mini_manager.py          ← Multi-instance manager
│   │   ├── tabs/                    ← Tab implementations
│   │   │   ├── village/             ← Village tab (5 subtabs)
│   │   │   ├── bot/                 ← Bot tab (5 subtabs)
│   │   │   ├── attack/              ← Attack tab (12+ subtabs)
│   │   │   └── about.py
│   │   └── handlers/                ← Event handlers (15 files)
│   │
│   ├── api/                         ← Phase 6
│   │   ├── __init__.py
│   │   ├── server.py                ← FastAPI server
│   │   ├── client.py                ← HTTP client
│   │   └── models.py                ← API models
│   │
│   ├── system/                      ← Phase 2/6
│   │   ├── tray.py                  ← Tray icon management
│   │   ├── dpi.py                   ← DPI detection
│   │   └── wmi.py                   ← WMI queries
│   │
│   ├── utils/                       ← Phase 1
│   │   ├── __init__.py
│   │   ├── sleep.py                 ← Cancellable sleep
│   │   ├── timer.py                 ← StopWatch, time formatting
│   │   ├── formatting.py            ← Number formatting
│   │   ├── version.py               ← Version checking
│   │   ├── prerequisites.py         ← System prerequisite checks
│   │   └── restart.py               ← Bot restart
│   │
│   └── log.py                       ← Phase 1
│
├── tests/                           ← All phases
│   ├── conftest.py                  ← Shared fixtures
│   ├── test_config/                 ← Phase 1 tests
│   ├── test_android/                ← Phase 2 tests
│   ├── test_vision/                 ← Phase 3 tests
│   ├── test_village/                ← Phase 4 tests
│   ├── test_army/                   ← Phase 5 tests
│   ├── test_attack/                 ← Phase 5 tests
│   ├── test_gui/                    ← Phase 6 tests
│   └── fixtures/                    ← Test screenshots, configs
│       ├── screenshots/             ← Reference game screenshots
│       ├── configs/                 ← Test INI files
│       └── templates/               ← Test XML templates
│
├── Languages/                       ← Reused from MyBot/ (unchanged)
├── CSV/Attack/                      ← Reused from MyBot/ (unchanged)
├── imgxml/                          ← Reused from MyBot/ (unchanged)
└── images/                          ← Reused from MyBot/ (unchanged)
```

**Total Python files**: ~160 modules + ~40 test files = ~200 files
