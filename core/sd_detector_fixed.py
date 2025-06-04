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
            
            # SD cards are typically between 128MB and 1TB
            if not (0.1 < total_gb < 1024):
                return False
            
            print(f"{drive_path} size: {total_gb:.2f} GB")
            
            # Check for typical camera file structure
            camera_indicators = [
                'DCIM',       # Standard digital camera folder
                'MISC',       # Other files
                'PRIVATE',    # Private files
                'System Volume Information'  # System folder
            ]
            
            found_indicators = 0
            try:
                items = os.listdir(drive_path)
                for indicator in camera_indicators:
                    if indicator in items:
                        found_indicators += 1
                        print(f"{drive_path} found camera indicator: {indicator}")
                
                # If camera indicators are found, it's likely an SD card
                if found_indicators > 0:
                    return True
                
                # Check for media files
                media_extensions = {'.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi', '.cr2', '.nef', '.dng'}
                for item in items[:20]:  # Only check the first 20 files
                    if any(item.lower().endswith(ext) for ext in media_extensions):
                        print(f"{drive_path} found media file: {item}")
                        return True
                
                # If the drive is small and has no system files, it might be an empty SD card
                if total_gb < 64 and len(items) < 10:
                    print(f"{drive_path} might be an empty low-capacity SD card")
                    return True
                
            except PermissionError:
                # If permission is denied but the size is reasonable, it might be an SD card
                if total_gb < 128:
                    print(f"{drive_path} permission denied but size reasonable, might be SD card")
                    return True
            except Exception as e:
                print(f"Error listing {drive_path}: {e}")
            
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