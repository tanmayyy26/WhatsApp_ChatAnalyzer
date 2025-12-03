@echo off
REM WhatsApp Analyzer - Theme Switcher for Windows
REM This script makes it easy to change themes

setlocal enabledelayedexpansion

echo.
echo ========================================================
echo   WhatsApp Analyzer - Theme Switcher
echo ========================================================
echo.

REM Check if .streamlit/config.toml exists
if not exist ".streamlit\config.toml" (
    echo Error: config.toml not found!
    pause
    exit /b 1
)

REM Show menu
echo Available themes:
echo   1. Light theme (default)
echo   2. Dark theme
echo   3. Show current theme
echo   4. Exit
echo.

set /p choice="Enter your choice (1/2/3/4): "

if "%choice%"=="1" (
    echo Switching to light theme...
    python switch_theme.py light
    if !errorlevel! equ 0 (
        echo.
        echo Success! Restart the app to see changes:
        echo   streamlit run app.py
    )
) else if "%choice%"=="2" (
    echo Switching to dark theme...
    python switch_theme.py dark
    if !errorlevel! equ 0 (
        echo.
        echo Success! Restart the app to see changes:
        echo   streamlit run app.py
    )
) else if "%choice%"=="3" (
    python -c "
import sys
with open('.streamlit/config.toml', 'r') as f:
    for line in f:
        if line.startswith('base ='):
            theme = line.split('\"')[1]
            print(f'Current theme: {theme}')
            break
"
) else if "%choice%"=="4" (
    echo Cancelled.
    exit /b 0
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
pause
