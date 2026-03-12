# CLAUDE.md — MyBot-translation Codebase Overview

## Project Summary

**MyBot (MyBot.run)** is a Clash of Clans automation bot written in **AutoIt 3**. It controls Android emulators (BlueStacks, MEmu, Nox) via ADB, uses OpenCV-based image recognition to detect game elements, and automates gameplay including resource collection, army training, attacks, upgrades, donations, and multi-account management.

- **Version**: v8.2.0 (November 2025)
- **License**: GNU GPL v3
- **Language**: AutoIt 3 (.au3 scripts)
- **Platform**: Windows (Vista/7/8/10+), requires .NET 4.5, VC++ 2010 Redistributable x86

---

## Repository Structure

```
MyBot-translation/
├── .gitignore
├── CLAUDE.md                          # This file
└── MyBot/
    ├── MyBot.run.au3                  # Main entry point (59 KB)
    ├── MyBot.run.MiniGui.au3          # Lightweight multi-instance GUI manager
    ├── MyBot.run.Wmi.au3              # WMI process query utility (console)
    ├── MultiBot.exe                   # Multi-instance launcher
    ├── README.md                      # Quick start guide
    ├── CHANGELOG                      # Detailed version history (164 KB)
    ├── COCBot/                        # Core bot logic (278+ .au3 files)
    │   ├── MBR Global Variables.au3   # All global variables & constants (187 KB)
    │   ├── MBR Functions.au3          # Master function include file (14 KB)
    │   ├── MBR GUI Design.au3         # GUI layout definitions (32 KB)
    │   ├── MBR GUI Control.au3        # GUI event handlers (92 KB)
    │   ├── MBR GUI Control Variables.au3  # GUI control handle declarations (27 KB)
    │   ├── MBR GUI Action.au3         # BotStart/BotStop/BotSearchMode (10 KB)
    │   ├── MBR GUI Design Mini.au3    # Minimal GUI layout (26 KB)
    │   ├── MBR References.au3         # Stub functions to prevent code stripping
    │   ├── GUI/                       # 63 GUI design & control files
    │   └── functions/                 # 13 subdirectories of bot logic
    ├── CSV/Attack/                    # 20+ pre-made CSV attack scripts
    ├── Languages/                     # 16 translation .ini files
    ├── Help/                          # RTF documentation files
    ├── images/                        # UI graphics, icons, button bitmaps
    ├── imgxml/                        # 2,140+ XML image templates for visual detection
    └── lib/                           # External libraries, DLLs, ADB tools
```

**Total files**: ~3,020 (excluding .git)

---

## Entry Points

### MyBot.run.au3 — Main Entry Point
1. **`InitializeBot()`** — Processes CLI args, sets up profiles, initializes GDI+/crypto/TCP, creates GUI, launches watchdog
2. **`MainLoop()`** — Infinite loop dispatching on `$g_iBotAction`:
   - `$eBotStart` → `BotStart()` → opens Android → `Initiate()` → `runBot()`
   - `$eBotStop` → `BotStop()` (cleanup, release resources)
   - `$eBotSearchMode` → `BotSearchMode()` (search-only, no attack)
   - `$eBotClose` → `BotClose()`

### MyBot.run.MiniGui.au3 — Lightweight Instance Manager
- Manages multiple bot instances with minimal UI
- Handles window positioning, docking, embedding
- Communicates with bot processes via window messages

### MyBot.run.Wmi.au3 — WMI Utility
- Console tool querying Win32_Process via WQL
- Outputs process data in XML format

---

## Core Architecture

### Boot Sequence
```
MyBot.run.au3
  └─ InitializeBot()
       ├─ Parse CLI args (restart, autostart, nowatchdog, dock, debug, minigui, nogui, console, profiles)
       ├─ Setup profile folders and logging
       ├─ Detect system language
       ├─ Load Android emulator config
       ├─ Initialize GDI+, cryptography, TCP, taskbar
       ├─ Create main GUI and splash screen
       ├─ Launch watchdog process
       └─ Load all GUI controls and configuration
  └─ MainLoop()
       └─ BotStart()
            ├─ Save/read/apply config
            ├─ Open Android emulator
            ├─ InitiateLayout() (check screen resolution)
            └─ Initiate() → checkMainScreen() → ZoomOut() → runBot()
```

### Main Bot Cycle (`runBot()`)
```
runBot()
  ├─ InitiateSwitchAcc()          # Multi-account switching
  ├─ VillageReport()              # Display village status
  ├─ Initial checks (Lab, Heroes, Buildings, Achievements)
  ├─ FirstCheck()                 # One-time initialization
  └─ MAIN LOOP (infinite):
       ├─ Check restart conditions (timer-based)
       ├─ PrepareDonateCC()       # Clan Castle donation
       ├─ checkMainScreen()       # Verify we're in-game
       ├─ checkObstacles()        # Check for error dialogs
       ├─ CheckAndroidReboot() / CheckBotRestart()
       ├─ VillageReport()         # Update village info
       ├─ BotCommand()            # Execute pending commands
       ├─ Collections (RANDOMIZED ORDER):
       │   ├─ LabCheck, Collect, CollectCCGold, CheckTombs
       │   ├─ CleanYard, CollectAchievements, CollectFreeMagicItems
       │   └─ DailyChallenge, PetCheck
       ├─ AddIdleTime()           # Idle collection time
       ├─ Donation/Training/Request cycle (randomized)
       ├─ AttackCycle(False)      # Execute attacks if army ready
       ├─ BoostEverything()       # Apply training potions
       └─ BuilderBase operations (if enabled)
```

### Attack Flow
```
AttackCycle()
  ├─ PrepareSearch()
  ├─ VillageSearch()              # Loop until matching base found
  │   ├─ multiSearch()
  │   ├─ FindTownHall()
  │   ├─ GetResources()
  │   └─ CompareResources()       # Filter by loot thresholds
  └─ PrepareAttack()
       ├─ GetRedArea()            # Detect valid deployment zone
       ├─ SelectDropTroop()
       ├─ LaunchTroop() / DropTroop()
       └─ GetAttackBar()          # Monitor battle progress
```

### Training Flow
```
TrainSystem()
  ├─ CheckFullArmy()
  ├─ QuickTrain() OR TrainCustomArmy()
  │   ├─ openArmyOverview()
  │   ├─ TrainClick()
  │   └─ TrainIt()
  ├─ TrainSiege()
  └─ EndGainCost("Train")
```

---

## COCBot/functions/ Directory (13 Subdirectories)

### Android/ (15 files)
Emulator abstraction layer: BlueStacks5, MEmu, Nox support. Handles open/close/reboot, zoom, screen capture, embed mode, distributor detection.

Key files:
- `Android.au3` — Core emulator management
- `AndroidBluestacks5.au3`, `AndroidMEmu.au3`, `AndroidNox.au3` — Emulator-specific implementations
- `AndroidEmbed.au3` — Dock/embed emulator into bot window
- `CheckAndroidRebootCondition.au3`, `CheckBotRestartCondition.au3` — Recovery logic

### Attack/ (50+ files across subdirs)
Battle execution: preparation, deployment algorithms, troop management, red area detection.

Subdirectories:
- **Attack Algorithms/** — `AttackFromCSV.au3`, `SmartFarm.au3`, `algorithm_AllTroops.au3`
- **AttackCSV/** — CSV-scripted attacks: `ParseAttackCSV`, `DropTroopFromINI`, `MakeDropPoints`, etc.
- **RedArea/** — Deployment zone detection: `GetRedArea`, `DropOnPixel`, `DropTroop`, `PointInPoly`
- **Troops/** — `DropOrderTroops`, `LaunchTroop`, `ReadTroopQuantity`, `CheckHeroesHealth`, `dropHeroes`, `dropCC`
- **SmartZap/** — Dark elixir zapping: `smartZap.au3`, `drillSearch.au3`
- **BuilderBase/** — `AttackBB.au3`, `PrepareAttackBB.au3`

### CreateArmy/ (30+ files)
Army composition and training management.

- `TrainSystem.au3` — Main training orchestrator
- `QuickTrain.au3`, `DoubleTrain.au3` — Quick/double training modes
- `CheckFullArmy.au3`, `checkArmyCamp.au3` — Army readiness checks
- Subdirs: `getArmyTroops/`, `getArmyHeroes/`, `getArmySpells/`, `getArmySiegeMachines/`, `getArmyCCTroops/`, `getArmyCCSpells/`, `getArmyCCSiegeMachines/`

### Config/ (8 files)
Settings persistence using INI files.

- `readConfig.au3` — Read settings from profile INI
- `saveConfig.au3` — Save settings to profile INI
- `applyConfig.au3` — Apply loaded config to globals
- `ScreenCoordinates.au3` — Game screen coordinate constants
- `ImageDirectories.au3` — Paths to imgxml template directories
- `DelayTimes.au3` — Configurable delay constants
- `profileFunctions.au3` — Profile management utilities

### Image Search/ (7 files)
OpenCV/ImgLoc-based image matching.

- `imglocTHSearch.au3` — Town Hall image search
- `imglocCheckWall.au3` — Wall level detection
- `checkDeadBase.au3` — Dead base identification
- `QuickMIS.au3` — Quick multi-image search
- `IsWindowOpen.au3` — Game window state detection

### Main Screen/ (9 files)
Game state verification and error recovery.

- `checkMainScreen.au3` — Verify bot is on main village screen
- `waitMainScreen.au3` — Wait for main screen to load
- `checkObstacles.au3` — Detect and dismiss error popups/obstacles
- `isOnBuilderBase.au3` — Detect if on Builder Base

### MOD/ (6 files)
Special attack modes beyond normal flow.

- `AttackCycle.au3` — Main attack routine coordinator
- `BBSpam.au3` — Builder Base spam attacks
- `CCSpam.au3` — Clan Castle spam attacks
- `DirectAttack.au3` — Direct attack without searching
- `RankedBattle.au3` — Ranked battle mode
- `RevengeBattle.au3` — Revenge battle mode

### Other/ (60 files)
Utilities, API, helpers, system calls.

Notable files:
- `ADB.au3` — Android Debug Bridge communication
- `Click.au3`, `ClickDrag.au3` — Mouse/touch simulation
- `MakeScreenshot.au3` — Screenshot capture
- `Multilanguage.au3` — Translation system (`GetTranslatedFileIni()`)
- `SetLog.au3` — Logging framework
- `Time.au3`, `StopWatch.au3` — Timer utilities
- `_Sleep.au3` — Sleep with pause/restart checking
- `Api.au3`, `ApiClient.au3`, `ApiHost.au3` — HTTP API for external control
- `Base64.au3`, `Json.au3` — Data encoding utilities
- `KillProcess.au3`, `RestartBot.au3` — Process management
- `Notify.au3` — Push notification support

### Pixels/ (8 files)
Low-level pixel scanning and color detection.

- `_CaptureRegion.au3` — Screen region capture
- `_PixelSearch.au3`, `_MultiPixelSearch.au3` — Pixel color scanning
- `_GetPixelColor.au3`, `_CheckPixel.au3`, `_ColorCheck.au3` — Color comparison
- `isInsideDiamond.au3` — Diamond-shaped boundary checks

### Read Text/ (4 files)
OCR and text recognition from game screenshots.

- `getOcr.au3` — Main OCR caller
- `BuildingInfo.au3` — Extract building upgrade information
- `getBuilderCount.au3` — Count available builders
- `getShieldInfo.au3` — Extract shield/guard status

### Search/ (11 files)
Enemy village discovery and filtering.

- `VillageSearch.au3` — Main search loop
- `multiSearch.au3` — Multi-criteria search
- `FindTownHall.au3` — TH detection via image search
- `GetResources.au3`, `CompareResources.au3` — Loot evaluation
- `WeakBase.au3` — Weak base detection
- `WaitForClouds.au3` — Cloud waiting during search
- `PrepareSearch.au3` — Pre-search setup

### Village/ (53 files + subdirs)
Village management, upgrades, resource collection, donations.

Key files:
- `Collect.au3` — Resource collection from mines/collectors
- `VillageReport.au3` — Village status summary
- `DonateCC.au3`, `RequestCC.au3` — Clan Castle donation/request
- `Laboratory.au3` — Lab upgrade management
- `UpgradeBuilding.au3`, `UpgradeWall.au3`, `UpgradeHeroes.au3` — Upgrade automation
- `Auto Upgrade.au3` — Automatic upgrade selection
- `SwitchAccount.au3` — Multi-account switching
- `BoostSuperTroop.au3`, `BoostBarracks.au3`, `BoostStructure.au3` — Boosting
- `FreeMagicItems.au3` — Trader/free item collection
- `ClanCapital.au3` — Clan Capital management
- `Blacksmith.au3`, `PetHouse.au3`, `HelperHut.au3` — Special buildings

Subdirectories:
- **BuilderBase/** — BB upgrades, collection, Star Laboratory, Clock Tower boost
- **Clan Games/** — `ClanGames.au3`
- **Personal Challenges/** — `DailyChallenges.au3`

---

## COCBot/GUI/ Directory (63 files)

### Design Files (UI Layout Creation)
Create the visual layout of each tab and section:
- `MBR GUI Design Bottom.au3` — Bottom status bar and control buttons
- `MBR GUI Design Log.au3` — Log display area
- `MBR GUI Design Splash.au3` — Loading splash screen
- `MBR GUI Design Village.au3` — Village management tab
- `MBR GUI Design Bot.au3` — Bot options tab
- `MBR GUI Design Attack.au3` — Attack configuration tab
- `MBR GUI Design About.au3` — About/info tab
- `MBR GUI Design Strategies.au3` — Attack strategy selection

### Child Design Files (Nested Tabs)
- **Child Village**: Achievements, Donate, Misc, Notify, Upgrade
- **Child Bot**: Android, Debug, Options, Profiles, Stats
- **Child Attack**: Activebase, Deadbase, Bully, Options, Search, Strategies, Troops, EndBattle, SmartZap
  - Sub-variants for Scripted/Standard/Smart Farm attacks

### Control Files (Event Handlers)
- `MBR GUI Control Bottom.au3` — `Initiate()` and `InitiateLayout()` functions
- `MBR GUI Control Tab [General|Village|Search|DropOrder|EndBattle|SmartZap|Stats].au3`
- `MBR GUI Control Child [Army|Attack|Misc|Upgrade].au3`
- Various specialized control files for Donate, Notify, Android, Preset, etc.

---

## Key Global Variables (MBR Global Variables.au3)

### Game Dimensions
```autoit
$g_iGAME_WIDTH = 860
$g_iGAME_HEIGHT = 732
$g_iDEFAULT_HEIGHT = 780
$g_iDEFAULT_WIDTH = 860
```

### Bot State
```autoit
$g_bRunState          ; Bot currently running
$g_bSearchMode        ; Search-only mode active
$g_bRestart           ; Restart flag (checked frequently via _Sleep)
$g_iBotAction         ; Current action: Start, Stop, SearchMode, Close
$g_bFirstStart        ; First execution flag
$g_bFullArmy          ; Army trained and ready
```

### Android Emulator
```autoit
$g_sAndroidEmulator   ; Emulator name (BlueStacks, MEmu, Nox)
$g_hAndroidWindow     ; Window handle of Android emulator
$g_bAndroidEmbedded   ; Embedded/docked mode flag
```

### Resources & Loot
```autoit
$g_aiCurrentLoot[]    ; Current resources array [Gold, Elixir, DarkElixir, Trophies]
$eLootGold, $eLootElixir, $eLootDarkElixir, $eLootTrophy  ; Loot index enums
$g_abFullStorage[]    ; Storage full flags per resource type
```

### Troops & Heroes
```autoit
$eTroopBarbarian, $eTroopArcher, ...   ; Troop type enums
$eSpellLightning, $eSpellHeal, ...     ; Spell type enums
$eKing, $eQueen, $ePrince, $eWarden, $eChampion  ; Hero enums
$g_abDropKing, $g_abDropQueen, ...     ; Hero deployment flags
```

### Attack
```autoit
$g_aiAttackAlgorithm[]  ; Attack algorithm per mode (AllTroops, CSV, SmartFarm)
$DB, $LB, $TS           ; Match mode constants (DeadBase, LiveBase, TroopSearching)
$g_sImglocRedline       ; Cached red line image data
```

### Configuration & Profiles
```autoit
$g_sProfileCurrentName  ; Current profile name
$g_sProfileConfigPath   ; Path to profile config INI
$g_iCurAccount          ; Current account index (multi-account)
```

### Debug Flags
```autoit
$g_bDebugSetLog         ; Verbose logging
$g_bDebugClick          ; Click debugging
$g_bDebugImageSave      ; Save debug screenshots
$g_bDebugRedArea        ; Red area detection debug
$g_bDebugAttackCSV      ; CSV attack script debug
```

### Log Colors
```autoit
$COLOR_ERROR, $COLOR_WARNING, $COLOR_INFO, $COLOR_SUCCESS, $COLOR_DEBUG, $COLOR_ACTION
```

---

## Image Recognition System (imgxml/)

### How It Works
1. Bot captures a screenshot of the Android emulator via ADB
2. Calls `findMultiple()` with a path to an imgxml template folder
3. OpenCV (via MBRBot.dll) compares the screenshot region against base64-encoded reference images
4. Returns array of matches: `[ObjectName, X_Coordinate, Y_Coordinate]`
5. Bot uses coordinates to click buttons, read info, or verify game state

### XML Template Format
- Each `.xml` file contains a single base64-encoded image template
- **Naming convention**: `ElementName_Scale_Rotation.xml`
  - Example: `Barb_100_91.xml` = Barbarian at 100% scale, 91° rotation
  - Example: `TownHall_14_89.xml` = Town Hall level 14, 89° rotation
- Rotation values typically 85-96° (slight rotation for better screen matching)
- **Total**: 2,140+ XML template files across 227 subdirectories

### Directory Organization (by game function)
| Directory | Purpose |
|-----------|---------|
| `ArmyOverview/` | Troops, Spells, Heroes, Siege Machines in army camps |
| `Train/` | Training window UI elements |
| `DonateCC/` | Clan Castle donation troop/spell/siege detection |
| `Buildings/` | Defense and infrastructure detection (TH, Infernos, X-Bow, Eagle, etc.) |
| `Storages/` | Resource storage building detection (Gold, Elixir, Drills) |
| `Resources/` | Collectibles, GemBox, LootCart, Obstacles, Clan Games |
| `Attack/` | Attack search, resource targeting, Builder Base attacks |
| `imglocbuttons/` | Game UI buttons (main, train, attack, upgrade windows) |
| `SuperTroops/` | Super troop detection and activation |
| `SwitchAccounts/` | Supercell ID account switching |
| `Research/` | Laboratory and Blacksmith research |
| `deadbase/` | Dead/abandoned base detection |
| `village/` | Village scene and page detection |
| `Walls/` | Wall upgrade level detection |
| `Windows/` | Window close button detection |

### OCR System (lib/)
- `listSymbols_coc-*.xml` files (150+) — Character recognition templates
- Language bundles: `chinese-bundle.imglocdat`, `korean-bundle.imglocdat`, `persian-bundle.imglocdat`
- Used to read upgrade times, troop costs, resource amounts from screenshots

---

## External Libraries (lib/)

| Library | Purpose | Size |
|---------|---------|------|
| `MBRBot.dll` | Main bot engine & image processing | 27.4 MB |
| `MyBot.run.dll` | Bot runtime library | 2.76 MB |
| `opencv_core220.dll` | OpenCV image processing core | 2.0 MB |
| `opencv_imgproc220.dll` | OpenCV image filtering/transform | 1.24 MB |
| `libcurl.dll` | HTTP/HTTPS for push notifications | 1.7 MB |
| `sqlite3.dll` | Local database storage | 846 KB |
| `Newtonsoft.Json.dll` | JSON processing (.NET) | 554 KB |
| `adb/adb.exe` | Android Debug Bridge | 1.87 MB |
| `curl/curl.exe` | CLI data transfer tool | 637 KB |
| `adb.scripts/minitouch` | Touch event simulator for emulators | 34 KB |

---

## Translation / Language System

### File Format
Location: `MyBot/Languages/*.ini` (16 languages)

Supported: English, Arabic, Azerbaijani, Bahasa Indonesian, Chinese (Simplified & Traditional), French, German, Italian, Korean, Persian, Portuguese, Russian, Spanish, Turkish, Vietnamese

```ini
[Language]
DisplayName=English

[SectionName]
Key=Translated text here
Key_02=Text with %s placeholder for variables
Key_03=Multiline text with \r\n for line breaks
```

### Translation Function
`GetTranslatedFileIni($section, $key, $default, $var1, $var2, $var3)` in `Multilanguage.au3`:
1. Checks static array cache (keyed by `SectionName§KeyName`)
2. If cached, returns translation
3. If not cached, reads from `Languages\[LanguageName].ini`
4. Falls back to `English.ini` if translation missing
5. Auto-detects new strings and writes them to `English.ini`
6. Supports `%s` variable substitution and `\r\n` line breaks

### Section Categories (30+)
- `MBR Distributors` — Game distributor selection
- `MBR Popups` — Dialog messages
- `MBR Func_*` — Function-specific UI text
- `MBR GUI Control *` — Button labels, UI controls
- `MBR Global GUI Design` — Time units, day names, constants
- `MBR GUI Design Child *` — Tab-specific UI (Attack, Village, Bot)
- `MBR Global GUI Design Names` — Troop and spell names

---

## CSV Attack Script Format

Location: `MyBot/CSV/Attack/` (20+ scripts)

### Structure (tab/pipe-separated)
```
NOTE  | Description of army composition and TH levels
SIDE  | Extractor locations (GOLD/ELIXIR/DARK), forced sides, red line usage
SIDEB | Defensive building priorities with detection radii
MAKE  | Vector definitions (A-Z): side, drop points, offsets, direction
DROP  | Troop deployment: vector, index range, quantity, troop name, delays
WAIT  | Millisecond delays between phases
```

### Troop Names in CSV
`Barb`, `Arch`, `Ball`, `EDrag`, `King`, `Queen`, `Warden`, `WallW` (Wall Wrecker), `Castle`, `RSpell`, `FSpell`, etc.

---

## Configuration System

### Profile-Based INI Config
- Default path: `%USERPROFILE%\MyBot\Profiles\[ProfileName]\`
- Customizable via CLI: `/profiles=C:\CustomPath\`
- Per-profile settings stored in `config.ini`
- Global profile in `profile.ini` with `defaultprofile` key

### Config Lifecycle
1. `readConfig()` — Load from INI to global variables
2. `applyConfig()` — Apply globals to GUI controls
3. `saveConfig()` — Save GUI state back to INI

### Android Emulator Config
- 2D array: `$g_avAndroidAppConfig[$index][n]`
- Stores: emulator type, instance names, window titles, class names, dimensions, ADB paths

---

## Design Patterns

1. **Module-per-function** — Each game operation in its own .au3 file
2. **Event-driven GUI** — `GUISetOnEvent` mode with main loop dispatching actions
3. **Restart/Recovery** — `$g_bRestart` flag checked via `_Sleep()` between every operation
4. **Randomization** — Collection/training order shuffled via `_ArrayShuffle()` to appear human-like
5. **Multi-account** — Profile switching with account-specific timers and mutex locks
6. **INI persistence** — All config via INI files with save/load/apply cycle
7. **Emulator abstraction** — Android operations abstracted from game logic
8. **Image-based detection** — All game state read via OpenCV template matching + pixel scanning
9. **Comprehensive logging** — `SetLog()` calls at every decision point
10. **Sleep guards** — `_Sleep()` wraps all waits, checking for pause/restart/stop

---

## Key Files Quick Reference

| File | Purpose |
|------|---------|
| `MyBot/MyBot.run.au3` | Main entry point, `InitializeBot()` + `MainLoop()` |
| `COCBot/MBR Global Variables.au3` | All global variables, constants, enums (187 KB) |
| `COCBot/MBR Functions.au3` | Master include file for all function modules |
| `COCBot/MBR GUI Design.au3` | Main GUI layout creation |
| `COCBot/MBR GUI Control.au3` | All GUI event handlers |
| `COCBot/MBR GUI Action.au3` | `BotStart()`, `BotStop()`, `BotSearchMode()` |
| `COCBot/functions/Config/readConfig.au3` | Read settings from INI |
| `COCBot/functions/Config/saveConfig.au3` | Save settings to INI |
| `COCBot/functions/Config/ScreenCoordinates.au3` | Game screen coordinate constants |
| `COCBot/functions/Config/ImageDirectories.au3` | Paths to imgxml templates |
| `COCBot/functions/Other/Multilanguage.au3` | Translation system |
| `COCBot/functions/Other/_Sleep.au3` | Sleep with restart/pause checking |
| `COCBot/functions/Other/SetLog.au3` | Logging framework |
| `COCBot/functions/Other/Click.au3` | Touch/click simulation |
| `COCBot/functions/Other/MakeScreenshot.au3` | Screenshot capture |
| `COCBot/functions/MOD/AttackCycle.au3` | Main attack routine coordinator |
| `COCBot/functions/Village/Collect.au3` | Resource collection |
| `COCBot/functions/Village/DonateCC.au3` | Clan Castle donations |
| `COCBot/functions/Village/SwitchAccount.au3` | Multi-account switching |
| `COCBot/functions/Attack/Attack Algorithms/AttackFromCSV.au3` | CSV attack executor |
| `COCBot/functions/CreateArmy/TrainSystem.au3` | Army training orchestrator |
| `COCBot/functions/Search/VillageSearch.au3` | Enemy base search loop |
| `COCBot/functions/Android/Android.au3` | Core emulator management |
| `COCBot/functions/Pixels/_CaptureRegion.au3` | Screen capture |
| `COCBot/functions/Read Text/getOcr.au3` | OCR text recognition |

---

## Editing Guidelines

- **AutoIt 3 syntax**: Variables prefixed with `$`, functions use `Func`/`EndFunc`, includes via `#include`
- **Naming convention**: Global variables use `$g_` prefix (e.g., `$g_bRunState`), GUI controls use `$g_h` prefix
- **Variable declaration**: `Opt("MustDeclareVars", 1)` enforced — all variables must be declared with `Local`/`Global`
- **File encoding**: Most .au3 files use UTF-8 with BOM
- **Include order matters**: `MBR Global Variables.au3` must load before `MBR Functions.au3`
- **Sleep discipline**: Always use `_Sleep()` wrapper (not `Sleep()`) to allow restart/pause checking
- **Translation strings**: Use `GetTranslatedFileIni()` for all user-facing text
- **Image templates**: Add new XML templates to appropriate `imgxml/` subdirectory for visual detection
- **Config changes**: Must update `readConfig.au3`, `saveConfig.au3`, and `applyConfig.au3` together
