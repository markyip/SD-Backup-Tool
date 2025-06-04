# Project Structure

```
sd_backup_tool/
├── .gitignore
├── README.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── main.py
├── build_config/
│   └── build.py
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
│   ├── icon.ico
│   └── other_assets/
├── locales/
│   ├── __init__.py
│   └── language_manager.py
└── dist/
    └── Photo Video Backup Tool.exe
```

## Overview

This document describes the structure and organization of the SD Backup Tool project, including the purpose of each component and how they work together.

## Directory Structure

```
sd_backup_tool/
├── assets/              # Application assets
│   └── icon.ico        # Application icon
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
├── build.py           # Build script for creating executable
├── main.py            # Application entry point
└── requirements.txt   # Python package dependencies
```

## Key Components

### Core Modules

- **sd_detector_fixed.py**: Handles SD card detection and monitoring
- **file_scanner.py**: Implements file scanning and categorization
- **backup_worker.py**: Manages the backup process and progress tracking

### User Interface

- **main_window_enhanced.py**: Main application window with all UI components
- **drive_tile_widget.py**: Visual drive selection interface with space information

### Language Support

- **translations.py**: Single file containing all UI text with English comments
- **__init__.py**: Language manager for handling translations

### Build System

- **build.py**: Handles the creation of the executable
  - Installs required dependencies
  - Creates single-file executable
  - Bundles assets
  - Cleans up build artifacts

## Workflow

1. **Application Launch**
   - `main.py` initializes the application
   - Creates main window and UI components
   - Initializes language manager

2. **SD Card Detection**
   - `SDDetector` monitors for SD card insertion
   - Updates UI when SD card is detected/removed

3. **File Scanning**
   - User selects destination drive
   - `FileScanner` scans for supported file types
   - Updates UI with file statistics

4. **Backup Process**
   - `BackupWorker` handles file copying
   - Updates progress in UI
   - Handles errors and interruptions

5. **Language Support**
   - All UI text is loaded from `translations.py`
   - English comments help with translation
   - Easy to modify or add new translations

## Building the Application

1. Run `build.py`:
   ```bash
   python build.py
   ```

2. The script will:
   - Install required dependencies
   - Create executable in `dist` folder
   - Clean up build artifacts

3. The resulting executable:
   - Contains all necessary components
   - Bundles required assets
   - Supports language customization

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
   - Run `build.py` to create new executable
   - Test changes in the built version
   - Verify all features work as expected