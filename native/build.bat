@echo off
setlocal

:: ── Config ──────────────────────────────────────────────────────────────
set CC=gcc
set CFLAGS=-O2 -Wall -shared
set OUT=..\bin
set SRC=.

:: ── Check gcc is available ───────────────────────────────────────────────
where gcc >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] gcc not found. Install MinGW and add it to PATH.
    exit /b 1
)

:: ── Create output dir ────────────────────────────────────────────────────
if not exist %OUT% (
    mkdir %OUT%
    echo [INFO] Created %OUT%
)

:: ── Build pulse_loader.dll ───────────────────────────────────────────────
echo [BUILD] pulse_loader.dll ...
%CC% %CFLAGS% -o %OUT%\pulse_loader.dll %SRC%\pulse_loader.c
if %ERRORLEVEL% neq 0 (
    echo [FAILED] pulse_loader.dll
    exit /b 1
)
echo [OK] pulse_loader.dll

:: ── Build pulse_math.dll ─────────────────────────────────────────────────
echo [BUILD] pulse_math.dll ...
%CC% %CFLAGS% -o %OUT%\pulse_math.dll %SRC%\pulse_math.c -lm
if %ERRORLEVEL% neq 0 (
    echo [FAILED] pulse_math.dll
    exit /b 1
)
echo [OK] pulse_math.dll

:: ── Done ─────────────────────────────────────────────────────────────────
echo.
echo [DONE] All builds successful. Output: %OUT%
endlocal