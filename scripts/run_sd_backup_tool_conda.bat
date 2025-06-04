@echo off
echo Starting SD Backup Tool (Conda Environment)...
echo.

REM Change to the project root directory (one level up from scripts)
cd /d "%~dp0\.."

REM Check if conda is available
conda --version >nul 2>&1
if errorlevel 1 (
    echo Error: Conda is not installed or not in PATH
    echo Please install Anaconda/Miniconda and try again
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

REM Check if there's an existing conda environment for this project
echo Checking for existing conda environment...
conda info --envs | findstr "sd_backup_tool" >nul 2>&1
if errorlevel 1 (
    echo Creating new conda environment 'sd_backup_tool'...
    echo.
    conda create -n sd_backup_tool python=3.9 -y
    if errorlevel 1 (
        echo Error: Failed to create conda environment
        pause
        exit /b 1
    )
)

REM Activate the conda environment and install/update dependencies
echo Activating conda environment and installing dependencies...
echo.
call conda activate sd_backup_tool
if errorlevel 1 (
    echo Error: Failed to activate conda environment
    pause
    exit /b 1
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing required dependencies...
    pip install -r requirements.txt
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

REM Deactivate conda environment
call conda deactivate

REM Keep the window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)