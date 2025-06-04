# -*- coding: utf-8 -*-
"""
Create installer script
Uses Inno Setup to create a Windows installer
"""

import os
import sys
import subprocess
from pathlib import Path

def find_inno_setup():
    """Find Inno Setup compiler"""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def create_installer():
    """Create installer"""
    print("=== Creating SD Card Backup Tool Installer ===")
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    script_path = Path(__file__).parent / "installer.iss"
    exe_path = project_root / "dist" / "Photo Video Backup Tool.exe" # Photo Video Backup Tool.exe
    
    # Check if executable exists
    if not exe_path.exists():
        print("❌ Executable not found, please run build.py first.")
        print(f"   Expected location: {exe_path}")
        return False
    
    # Find Inno Setup
    iscc_path = find_inno_setup()
    if not iscc_path:
        print("❌ Inno Setup compiler not found.")
        print("💡 Please install Inno Setup first:")
        print("   1. Go to https://jrsoftware.org/isinfo.php")
        print("   2. Download and install Inno Setup")
        return False
    
    print(f"✅ Inno Setup found: {iscc_path}")
    print(f"📄 Using script: {script_path}")
    
    # Create output directory
    output_dir = project_root / "installer_output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Execute Inno Setup compiler
        command = [iscc_path, str(script_path)]
        print(f"🔧 Executing command: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding='utf-8' # Specify encoding for output
        )
        
        if result.returncode == 0:
            print("✅ Installer created successfully!")
            
            # Find the created installer file
            installer_files = list(output_dir.glob("*.exe"))
            if installer_files:
                installer_path = installer_files[0]
                print(f"📁 Installer location: {installer_path}")
                print(f"📏 File size: {installer_path.stat().st_size / (1024*1024):.1f} MB")
                
                # Display recommended testing steps
                print("\n🧪 Recommended testing steps:")
                print("1. Run the installer on a clean Windows system.")
                print("2. Verify that the program starts normally.")
                print("3. Test SD card detection functionality.")
                print("4. Test file scanning and backup functionality.")
                print("5. Test uninstallation functionality.")
                
                return True
            else:
                print("❌ Created installer file not found.")
                return False
        else:
            print(f"❌ Installer creation failed.")
            print(f"Standard output: {result.stdout}")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return False

def clean_installer_files():
    """Clean installer related files"""
    project_root = Path(__file__).parent.parent
    
    cleanup_dirs = [
        project_root / "installer_output"
    ]
    
    for dir_path in cleanup_dirs:
        if dir_path.exists():
            import shutil
            shutil.rmtree(dir_path)
            print(f"🗑️ Cleaned: {dir_path}")

def main():
    """Main program"""
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        print("Cleaning installer files...")
        clean_installer_files()
        print("✅ Cleanup complete.")
        return
    
    success = create_installer()
    
    if success:
        print("\n🎉 Installer created successfully!")
        print("📋 Release checklist:")
        print("✅ Executable: dist/Photo Video Backup Tool.exe") # Executable: dist/Photo Video Backup Tool.exe
        print("✅ Installer: installer_output/Photo Video Backup Tool_Installer_v1.0.0.exe") # Installer: installer_output/Photo Video Backup Tool_Installer_v1.0.0.exe
    else:
        print("\n❌ Installer creation failed.")

if __name__ == "__main__":
    main()