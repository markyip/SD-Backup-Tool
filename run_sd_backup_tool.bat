@echo off
echo Starting SD Backup Tool...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

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