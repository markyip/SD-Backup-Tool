# Project Structure

```
sd_backup_tool/
├── .gitignore
├── LICENSE
├── README.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── main.py
├── build_config/
│   ├── build.py
│   ├── create_installer.py
│   ├── installer.iss
│   └── 相片影片備份工具.spec
├── scripts/
│   ├── build_sd_backup_tool.bat
│   ├── run_sd_backup_tool.bat
│   └── run_sd_backup_tool_conda.bat
├── core/
│   ├── __init__.py
│   ├── backup_worker.py
│   ├── file_scanner.py
│   └── sd_detector_fixed.py
├── ui/
│   ├── __init__.py
│   ├── main_window_enhanced.py
│   └── drive_tile_widget.py
├── assets/
│   └── icon.ico
├── locales/
│   ├── __init__.py
│   └── translations.py
└── dist/
    └── SD_Backup_Tool.exe
```

## Overview

This document describes the structure and organization of the SD Backup Tool project, including the purpose of each component and how they work together.

## Directory Structure

```
sd_backup_tool/
├── assets/              # Application assets
│   └── icon.ico        # Application icon
│
├── build_config/       # Build system files
│   ├── build.py        # Main build script for creating executable
│   ├── create_installer.py # Installer creation script
│   ├── installer.iss   # Inno Setup installer configuration
│   └── 相片影片備份工具.spec # PyInstaller spec file
│
├── scripts/            # Convenient batch files for different use cases
│   ├── build_sd_backup_tool.bat      # Build executable batch file
│   ├── run_sd_backup_tool.bat        # Run application (standard Python)
│   └── run_sd_backup_tool_conda.bat  # Run application (Conda environment)
│
├── core/               # Core functionality modules
│   ├── sd_detector_fixed.py    # SD card detection
│   ├── file_scanner.py         # File scanning logic
│   └── backup_worker.py        # Backup process handling
│
├── locales/            # Language support
│   ├── translations.py # Main translations file with English comments
│   └── __init__.py    # Language manager implementation
│
├── ui/                 # User interface modules
│   ├── main_window_enhanced.py # Main application window
│   └── drive_tile_widget.py    # Drive selection interface
│
├── main.py            # Application entry point
├── requirements.txt   # Python package dependencies
├── LICENSE            # MIT license file
└── README.md          # Project documentation
```

## Key Components

### Core Modules

- **sd_detector_fixed.py**: Handles SD card and MTP device detection and monitoring
  - SD card detection via Windows drive enumeration
  - MTP device detection via Windows COM interface
  - Real-time device monitoring and notifications
- **file_scanner.py**: Implements file scanning and categorization for both filesystem and MTP devices
  - Recursive file scanning with media type detection
  - MTP device scanning using Windows COM
  - Smart file type recognition (photos, videos, RAW, camera files)
  - Creation date extraction from file paths and metadata
- **backup_worker.py**: Manages the backup process and progress tracking for all device types
  - Multi-method MTP file copying with fallback strategies
  - Duplicate file detection and skipping
  - Organized folder structure creation (Photos_YYYY/MM/DD, Videos_YYYY/MM/DD, etc.)

### User Interface

- **main_window_enhanced.py**: Main application window with all UI components
- **drive_tile_widget.py**: Visual drive selection interface with space information

### Language Support

- **translations.py**: Single file containing all UI text with English comments
- **__init__.py**: Language manager for handling translations

### Build System

- **build_config/build.py**: Main build script that handles the creation of the executable
  - Installs required dependencies
  - Creates single-file executable using PyInstaller
  - Bundles assets and dependencies
  - Cleans up build artifacts

### Scripts

The `scripts/` folder contains convenient batch files for different use cases:

- **build_sd_backup_tool.bat**: User-friendly batch file for building
  - Validates Python installation
  - Checks for required files
  - Executes build script with error handling
  - Offers to run the application after building
- **run_sd_backup_tool.bat**: Development batch file for running the application
  - Runs application directly with Python
  - Automatically installs dependencies from requirements.txt
  - Includes error handling and validation
- **run_sd_backup_tool_conda.bat**: Conda environment batch file
  - Creates and manages isolated conda environment
  - Handles dependency installation within conda environment
  - Best for advanced users who prefer conda package management

## Workflow

1. **Application Launch**
   - `main.py` initializes the application
   - Creates main window and UI components
   - Initializes language manager

2. **Device Detection**
   - `SDDetector` monitors for both SD card and MTP device insertion
   - Uses Windows COM interface for MTP device detection
   - Updates UI when devices are detected/removed
   - Supports phones, cameras, and other MTP-compatible devices

3. **File Scanning**
   - User selects destination drive
   - `FileScanner` scans for supported file types on selected source device
   - For MTP devices: Uses COM interface for recursive scanning
   - For SD cards: Uses standard filesystem scanning
   - Smart detection of camera files (Sony DSC files, etc.)
   - Updates UI with file statistics and type breakdown

4. **Backup Process**
   - `BackupWorker` handles file copying with device-specific methods
   - For MTP devices: Multiple copy strategies with fallback methods
   - For SD cards: Direct filesystem copying
   - Automatic folder organization by date and file type
   - Duplicate file detection and skipping
   - Real-time progress updates in UI

5. **Language Support**
   - All UI text is loaded from `translations.py`
   - English comments help with translation
   - Easy to modify or add new translations

## Building the Application

### Option 1: Using the Batch File (Recommended)

1. Run the build batch file:
   ```bash
   scripts\build_sd_backup_tool.bat
   ```

2. The batch file will:
   - Validate Python installation
   - Check for required project files
   - Execute the build script automatically
   - Offer to run the application after building

### Option 2: Manual Build

1. Run the build script directly:
   ```bash
   python build_config/build.py
   ```

2. Both methods will:
   - Install required dependencies automatically
   - Create executable in `dist` folder as `SD_Backup_Tool.exe`
   - Clean up build artifacts and temporary files

3. The resulting executable:
   - Contains all necessary components
   - Bundles required assets and dependencies
   - Supports language customization
   - Runs independently without Python installation

## Development Workflow

### Setting up Development Environment

1. **Clone the repository and create virtual environment:**
   ```bash
   git clone <repository-url>
   cd sd_backup_tool
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Run in development mode:**
   ```bash
   # Using batch file (recommended for standard Python)
   scripts\run_sd_backup_tool.bat
   
   # Using conda environment (recommended for advanced users)
   scripts\run_sd_backup_tool_conda.bat
   
   # Or directly with Python
   python main.py
   ```

3. **Build for distribution:**
   ```bash
   scripts\build_sd_backup_tool.bat
   ```

## Development Guidelines

1. **Adding New Features**
   - Place core functionality in `core/`
   - Add UI components to `ui/`
   - Update translations in `translations.py`

2. **Modifying Language**
   - Edit text in `translations.py`
   - Keep English comments for reference
   - Maintain formatting placeholders

3. **Building Changes**
   - Use `scripts\build_sd_backup_tool.bat` to create new executable
   - Test changes in the built version
   - Verify all features work as expected

## Script Usage Guide

### For New Users
- Use `scripts\build_sd_backup_tool.bat` to create a standalone executable
- The executable will be created in the `dist/` folder and can be run independently

### For Developers
- Use `scripts\run_sd_backup_tool.bat` for quick development and testing
- Automatically handles dependency installation
- Runs directly from source code

### For Advanced Users
- Use `scripts\run_sd_backup_tool_conda.bat` for isolated environment management
- Creates and manages a dedicated conda environment
- Handles all dependencies within the conda environment

## Technical Requirements & Dependencies

### Core Dependencies
- **PyQt5**: GUI framework for the user interface
- **pywin32**: Windows COM interface for MTP device communication
- **Pillow**: Image processing and EXIF data extraction
- **win32com.client**: Windows Shell integration for device detection

### MTP Support Requirements
- **Windows 10/11 recommended**: Optimal MTP driver support
- **COM interface**: Required for MTP device communication
- **USB drivers**: Proper MTP device drivers must be installed
- **Administrator privileges**: May be required for some MTP operations

### Development Environment
- **Python 3.8+**: Minimum Python version requirement
- **Virtual environment**: Isolated development environment recommended
- **Windows development**: Primary target platform
- The `venv/` folder is excluded from git (see `.gitignore`)
- Each developer should create their own virtual environment

### Performance Considerations
- **Memory usage**: MTP operations can be memory-intensive for large files
- **USB connection quality**: High-quality USB 3.0 cables recommended
- **Antivirus interference**: May need temporary disabling during file operations
- **Device power management**: Keep devices from entering sleep mode during backup