@echo off
setlocal enabledelayedexpansion
set "DIR=%~dp0"
pushd "%DIR%"
set "AUTOIT_DIR=%DIR%AutoIt"
set "ERROR_COUNT=0"
set "TOTAL_FILES=4"
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "RESET=[0m"

echo !YELLOW!========================================!RESET!
echo !YELLOW! MyBot.run Build Tool!RESET!
echo !YELLOW! Started at %DATE% %TIME%!RESET!
echo !YELLOW!========================================!RESET!
echo.

echo !YELLOW![PHASE 1] Cleanup!RESET!
echo.

echo Deleting old executables...
if exist "MyBot.run.exe" (del /F /Q "MyBot.run.exe" && echo !GREEN![OK]!RESET! Deleted MyBot.run.exe) else (echo !YELLOW![INFO]!RESET! MyBot.run.exe not found.)
if exist "MyBot.run.Watchdog.exe" (del /F /Q "MyBot.run.Watchdog.exe" && echo !GREEN![OK]!RESET! Deleted MyBot.run.Watchdog.exe) else (echo !YELLOW![INFO]!RESET! MyBot.run.Watchdog.exe not found.)
if exist "MyBot.run.Wmi.exe" (del /F /Q "MyBot.run.Wmi.exe" && echo !GREEN![OK]!RESET! Deleted MyBot.run.Wmi.exe) else (echo !YELLOW![INFO]!RESET! MyBot.run.Wmi.exe not found.)
if exist "MyBot.run.MiniGui.exe" (del /F /Q "MyBot.run.MiniGui.exe" && echo !GREEN![OK]!RESET! Deleted MyBot.run.MiniGui.exe) else (echo !YELLOW![INFO]!RESET! MyBot.run.MiniGui.exe not found.)

echo.
echo !YELLOW![PHASE 2] Syntax Check!RESET!
echo.

echo [1/%TOTAL_FILES%] Checking MyBot.run.au3...
"%AUTOIT_DIR%\Au3Check.exe" "MyBot.run.au3"
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Syntax errors found in MyBot.run.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! No syntax errors in MyBot.run.au3.
)

echo.
echo [2/%TOTAL_FILES%] Checking MyBot.run.Watchdog.au3...
"%AUTOIT_DIR%\Au3Check.exe" "MyBot.run.Watchdog.au3"
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Syntax errors found in MyBot.run.Watchdog.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! No syntax errors in MyBot.run.Watchdog.au3.
)

echo.
echo [3/%TOTAL_FILES%] Checking MyBot.run.Wmi.au3...
"%AUTOIT_DIR%\Au3Check.exe" "MyBot.run.Wmi.au3"
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Syntax errors found in MyBot.run.Wmi.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! No syntax errors in MyBot.run.Wmi.au3.
)

echo.
echo [4/%TOTAL_FILES%] Checking MyBot.run.MiniGui.au3...
"%AUTOIT_DIR%\Au3Check.exe" "MyBot.run.MiniGui.au3"
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Syntax errors found in MyBot.run.MiniGui.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! No syntax errors in MyBot.run.MiniGui.au3.
)

echo.
if !ERROR_COUNT! neq 0 (
    echo !RED![FAILURE]!RESET! Syntax check failed. Compilation aborted.
    goto :end
)

echo !GREEN![SUCCESS]!RESET! All files passed syntax check. Proceeding to compilation.
echo.
echo !YELLOW![PHASE 3] Compilation!RESET!
echo.

echo [1/%TOTAL_FILES%] Compiling MyBot.run.au3...
"%AUTOIT_DIR%\Aut2Exe\Aut2exe.exe" /in "MyBot.run.au3" /out "MyBot.run.exe" /comp 4 /pack
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Failed to compile MyBot.run.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! MyBot.run.au3 compiled successfully.
)

echo.
echo [2/%TOTAL_FILES%] Compiling MyBot.run.Watchdog.au3...
"%AUTOIT_DIR%\Aut2Exe\Aut2exe.exe" /in "MyBot.run.Watchdog.au3" /out "MyBot.run.Watchdog.exe" /comp 4 /pack
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Failed to compile MyBot.run.Watchdog.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! MyBot.run.Watchdog.au3 compiled successfully.
)

echo.
echo [3/%TOTAL_FILES%] Compiling MyBot.run.Wmi.au3...
"%AUTOIT_DIR%\Aut2Exe\Aut2exe.exe" /in "MyBot.run.Wmi.au3" /out "MyBot.run.Wmi.exe" /comp 4 /pack
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Failed to compile MyBot.run.Wmi.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! MyBot.run.Wmi.au3 compiled successfully.
)

echo.
echo [4/%TOTAL_FILES%] Compiling MyBot.run.MiniGui.au3...
"%AUTOIT_DIR%\Aut2Exe\Aut2exe.exe" /in "MyBot.run.MiniGui.au3" /out "MyBot.run.MiniGui.exe" /comp 4 /pack
if %errorlevel% neq 0 (
    echo !RED![ERROR]!RESET! Failed to compile MyBot.run.MiniGui.au3.
    set /a ERROR_COUNT+=1
) else (
    echo !GREEN![OK]!RESET! MyBot.run.MiniGui.au3 compiled successfully.
)

echo.
echo !YELLOW!========================================!RESET!
if !ERROR_COUNT! equ 0 (
    echo !GREEN![SUCCESS]!RESET! All files compiled successfully
) else (
    echo !RED![FAILURE]!RESET! !ERROR_COUNT! files failed to compile
)
echo !YELLOW! Completed at %DATE% %TIME%!RESET!
echo !YELLOW!========================================!RESET!
goto :end

:end
pause