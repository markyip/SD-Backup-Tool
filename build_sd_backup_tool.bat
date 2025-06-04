@echo off
echo Building SD Backup Tool...
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

REM Check if build_config/build.py exists
if not exist "build_config\build.py" (
    echo Error: build_config\build.py not found
    echo Make sure this batch file is in the same folder as the project
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

REM Run the build script
echo Running build script...
echo.
python build_config\build.py

REM Check if build was successful
if errorlevel 1 (
    echo.
    echo Build failed! Please check the error messages above.
    pause
    exit /b 1
)

REM Check if executable was created
if exist "dist\SD_Backup_Tool.exe" (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Executable location: dist\SD_Backup_Tool.exe
    echo.
    echo You can now:
    echo 1. Run the executable directly from dist\SD_Backup_Tool.exe
    echo 2. Copy the executable to any location
    echo 3. Create a shortcut on your desktop
    echo.
    
    REM Ask if user wants to run the application
    set /p choice="Do you want to run the application now? (y/n): "
    if /i "%choice%"=="y" (
        echo.
        echo Starting SD Backup Tool...
        start "" "dist\SD_Backup_Tool.exe"
    )
) else (
    echo.
    echo Error: Executable was not created successfully
    echo Please check the build output for errors
    pause
    exit /b 1
)

echo.
echo Press any key to close this window...
pause >nul