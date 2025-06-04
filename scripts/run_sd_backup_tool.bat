@echo off
echo Starting SD Backup Tool...
echo.

REM Change to the project root directory (one level up from scripts)
cd /d "%~dp0\.."

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
    echo Make sure this batch file is in the project root folder
    pause
    exit /b 1
)

REM Check if requirements.txt exists and install dependencies
if exist "requirements.txt" (
    echo Checking and installing required dependencies...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Warning: Some dependencies may not have been installed properly
        echo The application may still work, continuing...
        echo.
    )
) else (
    echo Warning: requirements.txt not found, dependencies may not be installed
    echo.
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