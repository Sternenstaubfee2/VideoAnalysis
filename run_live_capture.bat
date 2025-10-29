@echo off
REM Live Poker Capture - Quick Launch Script

echo ========================================
echo    Live Poker Capture
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Check if live dependencies are installed
echo Checking dependencies...
python -c "import mss" >nul 2>&1
if errorlevel 1 (
    echo Installing live capture dependencies...
    pip install mss pyautogui pywin32
)

echo.
echo SELECT CAPTURE MODE:
echo ========================================
echo 1. Screen Capture (Recommended - Simple)
echo 2. OBS Virtual Camera (Advanced)
echo 3. Quick 10-second Test
echo 4. Exit
echo ========================================
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto screen
if "%choice%"=="2" goto obs
if "%choice%"=="3" goto test
if "%choice%"=="4" goto end

:screen
echo.
echo Starting Screen Capture Mode...
echo Make sure GG Poker is visible on your screen!
echo.
echo Press Ctrl+C to stop at any time.
echo.
pause
python live_capture_analyzer.py --method screen --interval 2.0
goto end

:obs
echo.
echo Starting OBS Virtual Camera Mode...
echo.
echo Prerequisites:
echo  1. OBS Studio installed
echo  2. Poker game capture source added
echo  3. Virtual Camera started (Tools - Start Virtual Camera)
echo.
pause
python live_capture_analyzer.py --method obs --interval 2.0
goto end

:test
echo.
echo Running 10-second test...
echo.
python test_live_capture.py quick
pause
goto end

:end
echo.
echo Check live_poker_data.db for captured data!
echo.
pause
