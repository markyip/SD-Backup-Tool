# Release Notes

## v1.4.0 - Multi-Source support & MTP Optimization (2026-01-29)

### 🎉 New Features & Major Improvements

**🎛️ Advanced Source Selection**

- **Manual Folder Selection** - The "Scan Device" button now allows manual folder selection as a fallback if a device isn't automatically detected.
- **Multi-Source Support** - A new dynamic dropdown menu appears when multiple SD cards or phones are connected, allowing explicit selection.
- **Detailed Device Info** - The status bar now explicitly shows device type (SD/MTP/Manual), name, and path/ID for 100% clarity.

**⚡ MTP (Phone) Performance & Stability**

- **Optimized Deduplication** - MTP devices now use Size+Date comparison for deduplication, eliminating the slow MD5 hashing that required downloading files over USB.
- **Fixed MTP Crashes** - Resolved critical bugs in the deduplication logic that caused crashes when processing specific phone file types.
- **Improved Connection Stability** - Better handling of mobile device connection states.

**🌐 Localization & UI**

- **Full Chinese Support** - All new UI elements, including MTP-specific buttons and status messages, are fully localized (繁體中文).
- **Dynamic Action Button** - The scan button now identifies its mode (e.g., "開始 MTP 掃描") based on the selected source.

### 🛠️ Technical Improvements

- **Robust Build System** - Updated PyInstaller configuration to ensure all submodules and win32com components are correctly bundled into the standalone executable.
- **Cleaned Codebase** - Removed legacy/broken MTP hashing functions in favor of high-performance alternatives.

---

## v1.3.0 - Performance, Stability & Large SD Support (2026-01-29)

### 🎉 New Features & Major Improvements

**🚀 Performance & UI Responsiveness**

- **Non-blocking UI Architecture** - Device detection now runs on a background `QThread`. No more UI freezes or stutters during drive polling.
- **Optimized File Transfer** - Increased copy buffer size to 1MB, significantly improving transfer speeds for large video files.
- **Large SD Card Support** - Increased supported SD card size limit to 2048GB (2TB) to accommodate modern action cameras (GoPro, DJI, etc.).

**🎨 UI/UX Enhancements**

- **Stable Drive Coloring** - Drive tiles now use hash-based colors. Your `D:` drive will always be the same color, improving visual recognition.
- **Improved MTP Workflow** - Enhanced MTP detection with "Ready to Scan" auto-status and clearer feedback.
- **Dual-Mode Detection** - Simultaneous monitoring for both MTP devices and Mass Storage drives.

### 🐛 Bug Fixes

- Fixed a critical issue where MTP detection could block Mass Storage drive recognition.
- Resolved UI "micro-freezes" caused by synchronous COM object polling on the main thread.
- Unified SD card size limits across detector and backup worker modules.

---

## v1.2.0 - MTP Device Support & Advanced Features (2025-06-16)

### 🎉 Major New Features

**🔥 MTP Device Support**

- **Full MTP device integration** - Direct backup from phones, cameras, and other MTP devices
- **Automatic device detection** - Uses Windows COM interface for seamless device recognition
- **Multi-method file transfer** - Robust copying with multiple fallback strategies for reliability
- **Smart file type recognition** - Intelligent detection of camera files (Sony DSC, etc.) without extensions

**📁 Enhanced File Organization**

- **Automatic folder structure** - Files organized as Photos_YYYY/MM/DD, Videos_YYYY/MM/DD, Raw_YYYY/MM/DD
- **Duplicate file detection** - Smart skipping of already backed up files
- **Path-based date extraction** - Extracts creation dates from MTP folder structures like "Storage Media\\2025-06-03"
- **Camera file support** - Special handling for manufacturer-specific file formats

### 🛠️ Technical Improvements

**Core Engine Enhancements**

- **Unified scanning engine** - Single [`FileScanner`](core/file_scanner.py:29) handles both filesystem and MTP devices
- **Advanced MTP integration** - Windows COM-based implementation for maximum compatibility
- **Robust error handling** - Multiple retry mechanisms and graceful degradation
- **Performance optimizations** - Efficient scanning with progress tracking

**Device Detection**

- **Real-time monitoring** - Automatic detection of device connection/disconnection
- **Smart filtering** - Distinguishes between storage devices and MTP devices
- **Resource management** - Proper COM object lifecycle management

### 📱 Supported MTP Devices

- **Android phones** - Direct access to internal storage and SD cards
- **iOS devices** - Support via iTunes MTP interface
- **Digital cameras** - Sony, Canon, Nikon, and other major brands
- **Portable media devices** - Any MTP-compatible storage device

### 🎯 User Experience Improvements

- **Seamless workflow** - No difference in user experience between SD cards and MTP devices
- **Clear device identification** - Visual distinction between device types in UI
- **Enhanced progress tracking** - Real-time file copying progress with detailed status
- **Better error messaging** - Clear feedback for device-specific issues

---

## v1.1.0 - Enhanced Build Scripts & Organization (2025-01-06)

### 🎉 What's New

**Improved Project Organization**

- Moved all batch files to dedicated `scripts/` folder for better organization
- Enhanced project structure for easier navigation and maintenance

**Enhanced Build & Run Scripts**

- **Fixed path navigation issues** - Scripts now properly locate project files regardless of execution location
- **Automatic dependency management** - `run_sd_backup_tool.bat` now automatically installs required packages
- **New Conda support** - Added `run_sd_backup_tool_conda.bat` for isolated environment management

### 📁 Available Scripts

| Script                                 | Purpose                       | Best For                              |
| -------------------------------------- | ----------------------------- | ------------------------------------- |
| `scripts\build_sd_backup_tool.bat`     | Creates standalone executable | New users, distribution               |
| `scripts\run_sd_backup_tool.bat`       | Runs from Python source       | Developers, quick testing             |
| `scripts\run_sd_backup_tool_conda.bat` | Uses Conda environment        | Advanced users, environment isolation |

### 🔧 Improvements

- **Better error handling** - All scripts now provide clear error messages and validation
- **Enhanced documentation** - Updated README.md and PROJECT_STRUCTURE.md with comprehensive usage guides
- **User-friendly approach** - Different scripts for different user types (beginners, developers, advanced)

### 🐛 Fixes

- Fixed batch files not finding project root when executed from scripts folder
- Improved dependency installation process
- Better validation of Python and project file requirements

### 📚 Documentation Updates

- Complete project structure documentation
- Step-by-step usage guides for each script
- Troubleshooting section for common issues
- Clear examples for different use cases

---

**Full Changelog**: [View on GitHub](https://github.com/markyip/SD-Backup-Tool/compare/49bd685...HEAD)

**Download**: Use any of the scripts in the `scripts/` folder to build or run the application according to your needs.

### 🔧 Migration Notes

**For Users Upgrading from v1.1.0:**

- No action required - MTP support is automatically available
- Connect your phone or camera and it will be detected automatically
- Existing SD card workflows remain unchanged

**For Developers:**

- New dependency: `win32com.client` (included in pywin32)
- Enhanced [`core/file_scanner.py`](core/file_scanner.py:1) with MTP scanning capabilities
- Updated [`core/backup_worker.py`](core/backup_worker.py:1) with MTP file transfer methods
- Modified [`core/sd_detector_fixed.py`](core/sd_detector_fixed.py:1) for unified device detection

---

**Full Changelog**: [View on GitHub](https://github.com/markyip/SD-Backup-Tool/compare/0404f91...49bd685)

**Download**: Use any of the scripts in the `scripts/` folder to build or run the application according to your needs.
