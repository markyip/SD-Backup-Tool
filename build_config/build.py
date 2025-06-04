# -*- coding: utf-8 -*-
"""
Build script for SD Backup Tool
Creates a single executable with customizable language support
"""

import os
import sys
import shutil
import subprocess
import pkg_resources

def check_dependencies():
    """Check and install required dependencies"""
    required = {
        'pyinstaller',
        'PyQt5',
        'pywin32',
        'Pillow'  # For image handling
    }
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print("Installing required packages:", missing)
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

def cleanup_build_folders():
    """Clean up build folders and spec file"""
    # Clean up build folder
    if os.path.exists('build'):
        print("Cleaning up build folder...")
        shutil.rmtree('build')
    
    # Clean up spec file
    spec_file = 'SD_Backup_Tool.spec'
    if os.path.exists(spec_file):
        print(f"Removing {spec_file}...")
        os.remove(spec_file)
    
    # Clean up __pycache__ folders
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            print(f"Cleaning up {cache_dir}...")
            shutil.rmtree(cache_dir)

def build_executable():
    """Build executable"""
    print("Building SD Backup Tool...")
    
    # Check and install dependencies
    check_dependencies()
    
    # Build command
    build_cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--name=SD_Backup_Tool',
        '--onefile',  # Create single file executable
        '--windowed',
        '--icon=assets/icon.ico',
        '--add-data=assets;assets',
        '--clean',
        '--noconfirm',  # Replace existing build without asking
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=win32api',
        '--hidden-import=win32file',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ExifTags',
        'main.py'
    ]
    
    try:
        # Run build command
        subprocess.run(build_cmd, check=True)
        print("SD Backup Tool built successfully!")
        print("Executable location: dist/SD_Backup_Tool.exe")
        
        # Clean up build folders and spec file
        cleanup_build_folders()
        print("Build cleanup completed.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_executable() 