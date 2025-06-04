@echo off
echo Starting SD Backup Tool with Conda...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Initialize conda for batch scripts
call conda activate base

REM Check if main.py exists
if not exist "main.py" (
    echo Error: main.py not found in current directory
    echo Make sure this batch file is in the same folder as main.py
    pause
    exit /b 1
)

REM Run the application
echo Running SD Backup Tool...
echo.
python main.py

REM Keep the window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)

echo.
echo Application finished. Press any key to close.
pause >nul