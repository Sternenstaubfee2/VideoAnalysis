@echo off
REM Poker Video Analyzer - Quick Run Script
REM This script runs the poker video analyzer on the Spin & Go video

echo ========================================
echo    Poker Video Analyzer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK!
echo.

REM Run the analyzer
echo Starting video analysis...
echo.
python main_poker_analyzer.py

echo.
echo ========================================
echo Analysis Complete!
echo ========================================
echo.
echo Check the following files:
echo   - poker_data.db (SQLite database)
echo   - poker_analysis_report.txt (text report)
echo   - poker_hands.json (JSON export)
echo.
pause
