# -*- coding: utf-8 -*-
"""
Improved SD card detection module
SD card monitoring optimized for Windows 11
"""

import os
import time
import shutil
import threading
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import win32file
import win32api
import win32con

class SDCardDetector(QObject):
    """Improved SD card detector"""
    
    sd_card_detected = pyqtSignal(str)  # Signal emitted when SD card is detected, parameter is drive letter
    sd_card_removed = pyqtSignal()      # Signal emitted when SD card is removed
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.current_sd_drives = set()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_drives)
        self.last_drives = set()
    
    def start(self):
        """Start monitoring SD cards"""
        self.running = True
        self.timer.start(1000)  # Check every 1 second, more frequently
        self.check_drives()  # Check immediately once
    
    def stop(self):
        """Stop monitoring SD cards"""
        self.running = False
        self.timer.stop()
    
    def check_drives(self):
        """Check for drive changes"""
        if not self.running:
            return
        
        current_drives = self.get_all_potential_sd_drives()
        
        # Check for newly inserted SD cards
        new_drives = current_drives - self.current_sd_drives
        for drive in new_drives:
            print(f"New drive detected: {drive}")
            self.sd_card_detected.emit(drive)
        
        # Check for removed SD cards
        removed_drives = self.current_sd_drives - current_drives
        if removed_drives:
            print(f"Drive removed: {removed_drives}")
            self.sd_card_removed.emit()
        
        self.current_sd_drives = current_drives
    
    def get_all_potential_sd_drives(self):
        """Get all potential SD card drives"""
        potential_drives = set()
        
        try:
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            
            for drive in drives:
                if self.is_potential_sd_card(drive):
                    potential_drives.add(drive)
                    
        except Exception as e:
            print(f"Error getting drives: {e}")
        
        return potential_drives
    
    def is_potential_sd_card(self, drive_path):
        """Determine if it might be an SD card (improved version)"""
        try:
            # Check if the drive is accessible
            if not os.path.exists(drive_path):
                return False
            
            drive_type = win32file.GetDriveType(drive_path)
            
            # 1. Removable drive - very likely an SD card
            if drive_type == win32file.DRIVE_REMOVABLE:
                print(f"{drive_path} identified as removable drive")
                return True
            
            # 2. Fixed drive - needs further checking (some card readers identify this way)
            if drive_type == win32file.DRIVE_FIXED:
                return self.is_fixed_drive_sd_card(drive_path)
            
            return False
            
        except Exception as e:
            print(f"Error checking drive {drive_path}: {e}")
            return False
    
    def is_fixed_drive_sd_card(self, drive_path):
        """Check if a fixed drive is an SD card"""
        try:
            # Check drive size
            total, used, free = shutil.disk_usage(drive_path)
            total_gb = total / (1024**3)
            
            print(f"{drive_path} size: {total_gb:.2f} GB")
            
            # Rule 1: External HDDs are typically much larger than SD cards
            # Most external HDDs are >1TB, while most SD cards are <1TB
            if total_gb > 2000:  # 2TB threshold for very large external HDDs
                print(f"{drive_path} too large ({total_gb:.2f}GB), likely external HDD")
                return False
            
            # Rule 2: SD cards are typically between 128MB and 1TB
            if not (0.1 < total_gb < 1024):
                print(f"{drive_path} size outside SD card range")
                return False
            
            # Rule 3: Check for external storage indicators (HDD/SSD/external drive software/folders)
            storage_device_indicators = [
                'Seagate',           # Seagate software
                'WD Discovery',      # Western Digital software
                'Backup Plus',       # Seagate backup software
                'My Passport',       # WD Passport software
                'Toshiba',          # Toshiba software
                'Samsung',          # Samsung software
                'Kingston',         # Kingston software
                'SanDisk',          # SanDisk software (careful - also makes SD cards)
                'Crucial',          # Crucial SSD software
                'Intel',            # Intel SSD software
                'System Volume Information', # Present on both, so we'll handle this separately
                'autorun.inf',      # Auto-run files common on external storage
                'Setup.exe',        # Setup executables
                'Backup',           # Generic backup folders
                'TimeMachine',      # Mac Time Machine backups
                '$RECYCLE.BIN',     # Windows recycle bin (more common on external drives)
                'Documents',        # User folders common on external drives
                'Downloads',        # User folders common on external drives
                'Music',           # User folders common on external drives
                'Pictures',        # User folders common on external drives
                'Videos',          # User folders common on external drives
                'Program Files',   # Program installation folders
                'Windows'          # Windows system folder
            ]
            
            # Rule 4: Check for typical camera file structure
            camera_indicators = [
                'DCIM',       # Standard digital camera folder (strongest indicator)
                'MISC',       # Other camera files
                'PRIVATE'     # Private camera files
            ]
            
            found_storage_indicators = 0
            found_camera_indicators = 0
            
            try:
                items = os.listdir(drive_path)
                total_items = len(items)
                
                # Check for storage device indicators
                for indicator in storage_device_indicators:
                    if indicator in items:
                        found_storage_indicators += 1
                        print(f"{drive_path} found storage device indicator: {indicator}")
                
                # Special handling for SanDisk - they make both SD cards and SSDs
                if 'SanDisk' in items and found_storage_indicators == 1:
                    # If only SanDisk folder found, check for camera structure
                    pass  # Will be handled by camera indicator check below
                elif found_storage_indicators >= 2:
                    print(f"{drive_path} multiple storage device indicators found, likely external storage")
                    return False
                elif found_storage_indicators >= 1 and total_gb > 128:
                    print(f"{drive_path} storage indicator + large size, likely external storage")
                    return False
                
                # Check for camera indicators
                for indicator in camera_indicators:
                    if indicator in items:
                        found_camera_indicators += 1
                        print(f"{drive_path} found camera indicator: {indicator}")
                
                # Rule 5: Strong camera structure indicates SD card
                if found_camera_indicators >= 1:
                    print(f"{drive_path} has camera structure, likely SD card")
                    return True
                
                # Rule 6: Check file structure complexity
                # SD cards typically have simpler structure, HDDs have more complex folder hierarchies
                if total_items > 50 and total_gb > 64:
                    print(f"{drive_path} too many root items ({total_items}) for SD card size")
                    return False
                
                # Rule 7: Check for media files (but be more restrictive)
                media_extensions = {'.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi', '.cr2', '.nef', '.dng'}
                media_files_found = 0
                
                # Only check first 10 items to avoid false positives from large photo libraries
                for item in items[:10]:
                    if any(item.lower().endswith(ext) for ext in media_extensions):
                        media_files_found += 1
                        print(f"{drive_path} found media file: {item}")
                
                # If small drive with media files, likely SD card
                if media_files_found > 0 and total_gb < 128 and total_items < 30:
                    print(f"{drive_path} small drive with media files, likely SD card")
                    return True
                
                # Rule 8: Empty small drives might be empty SD cards
                if total_gb < 32 and total_items < 5:
                    print(f"{drive_path} small empty drive, might be empty SD card")
                    return True
                
            except PermissionError:
                # Rule 9: Permission denied - only consider if very small
                if total_gb < 64:
                    print(f"{drive_path} permission denied but very small, might be SD card")
                    return True
                else:
                    print(f"{drive_path} permission denied and large, likely external HDD")
                    return False
            except Exception as e:
                print(f"Error listing {drive_path}: {e}")
                return False
            
            # If none of the above criteria are met, it's probably not an SD card
            print(f"{drive_path} doesn't match SD card criteria")
            return False
            
        except Exception as e:
            print(f"Error checking fixed drive {drive_path}: {e}")
            return False
    
    def get_drive_info(self, drive_path):
        """Get detailed drive information"""
        try:
            volume_info = win32api.GetVolumeInformation(drive_path)
            total, used, free = shutil.disk_usage(drive_path)
            
            return {
                'label': volume_info[0] or 'Unnamed',
                'serial': volume_info[1],
                'filesystem': volume_info[4],
                'total_gb': total / (1024**3),
                'free_gb': free / (1024**3)
            }
        except Exception as e:
            print(f"Error getting drive info for {drive_path}: {e}")
            return {
                'label': 'Unknown',
                'serial': 0,
                'filesystem': 'Unknown',
                'total_gb': 0,
                'free_gb': 0
            }

    def get_removable_drives(self):
        """Return a list of removable drive letters (e.g., ['E:\\', 'F:\\'])"""
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        removable_drives = []
        for drive in drives:
            try:
                drive_type = win32file.GetDriveType(drive)
                if drive_type == win32file.DRIVE_REMOVABLE:
                    removable_drives.append(drive)
            except Exception:
                continue
        return removable_drives