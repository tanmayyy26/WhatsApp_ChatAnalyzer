@echo off
echo ========================================
echo   WhatsApp Analyzer - Professional
echo ========================================
echo.

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if activation worked
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo [2/3] Checking dependencies...
pip list | findstr streamlit >nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo [3/3] Starting application...
echo.
echo ========================================
echo   Application will open in browser
echo   Press Ctrl+C to stop
echo ========================================
echo.

streamlit run app.py --server.port 8504

pause
