# Release Notes

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

| Script | Purpose | Best For |
|--------|---------|----------|
| `scripts\build_sd_backup_tool.bat` | Creates standalone executable | New users, distribution |
| `scripts\run_sd_backup_tool.bat` | Runs from Python source | Developers, quick testing |
| `scripts\run_sd_backup_tool_conda.bat` | Uses Conda environment | Advanced users, environment isolation |

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