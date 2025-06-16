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
import subprocess
import re

try:
    import win32com.client
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    print("WARNING: win32com not available - MTP detection disabled")

class SDCardDetector(QObject):
    """Improved SD card detector"""
    
    sd_card_detected = pyqtSignal(dict)  # Emits dict: {'id': str, 'name': str, 'type': str, 'path': str}
    sd_card_removed = pyqtSignal(str)    # Emits the ID of the removed device
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.current_sd_drives = set()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_drives)
        self.last_drives = set()
        self.scan_cache = {}  # Cache scan results
        self.selected_source_device = None  # Track selected source
        self.selected_destination_drive = None  # Track selected destination
        self.smart_scanning_enabled = False  # Switch to smart mode after initial setup
    
    def start(self):
        """Start monitoring SD cards"""
        self.running = True
        self.timer.start(1000)  # Check every 1 second, more frequently
        self.check_drives()  # Check immediately once
    
    def stop(self):
        """Stop monitoring SD cards"""
        self.running = False
        self.timer.stop()
    
    def _is_potential_sd_card(self, drive):
        """Check if a drive is likely to be an SD card"""
        try:
            drive_type = win32file.GetDriveType(drive)
            if drive_type == win32file.DRIVE_REMOVABLE:
                # Get drive info
                total, used, free = shutil.disk_usage(drive)
                total_gb = total / (1024**3)
                
                # More strict size limits for SD cards (typically 2GB to 512GB)
                if total_gb > 512:  # Skip drives larger than 512GB
                    print(f"Skipping drive {drive} - too large ({total_gb:.2f}GB)")
                    return False
                    
                # Skip if drive is too small
                if total_gb < 2:  # Skip drives smaller than 2GB
                    print(f"Skipping drive {drive} - too small ({total_gb:.2f}GB)")
                    return False
                
                # Additional check for drive characteristics
                try:
                    volume_info = win32file.GetVolumeInformation(drive)
                    # Check if it has a filesystem type typical for SD cards
                    if volume_info[4] not in ['FAT32', 'FAT', 'exFAT']:
                        print(f"Skipping drive {drive} - not a typical SD card filesystem")
                        return False
                except Exception as e:
                    print(f"Error checking volume info for {drive}: {e}")
                    return False
                    
                return True
            return False
        except Exception as e:
            print(f"Error checking if drive is SD card: {e}")
            return False

    def check_drives(self):
        """Check for connected drives and emit signals for changes"""
        try:
            print("Starting drive detection...")
            current_drives = set()
            drives_info = {}
            
            # First check for MTP devices
            print("Checking for MTP devices using Windows COM...")
            if COM_AVAILABLE:
                try:
                    shell = win32com.client.Dispatch("Shell.Application")
                    computer = shell.NameSpace(17)  # Computer namespace
                    
                    if not computer:
                        print("Failed to get computer namespace")
                        return
                        
                    print("Successfully got computer namespace")
                    items = computer.Items()
                    print(f"Found {len(items)} items in computer namespace")
                    
                    for item in items:
                        try:
                            item_name = str(item.Name) if item.Name else ""
                            item_path = str(item.Path) if item.Path else ""
                            
                            print(f"Checking item - Name: '{item_name}', Path: '{item_path}'")
                            
                            # Check if this is a portable device
                            is_portable = False
                            
                            # Method 1: Check path for MTP or Portable
                            if "::" in item_path:
                                print(f"Item has '::' in path, checking for MTP/Portable indicators")
                                # Only consider it MTP if it has USB VID/PID in the path
                                if "usb#vid_" in item_path.lower() and "&pid_" in item_path.lower():
                                    is_portable = True
                                    print(f"Found MTP device with USB VID/PID in path")
                            
                            # Method 2: Try to get folder and check if it's a real MTP device
                            if not is_portable:
                                try:
                                    folder = item.GetFolder
                                    if folder:
                                        # Additional check to verify it's a real MTP device
                                        # Regular drives will have a simple path like "C:\"
                                        if "::" not in item_path and not any(x in item_path.upper() for x in ["MTP", "PORTABLE", "USB"]):
                                            print(f"Skipping regular drive: {item_name}")
                                            continue
                                        is_portable = True
                                except Exception as e:
                                    print(f"Error getting folder: {e}")
                            
                            if is_portable and item_name:
                                print(f"Found portable device: {item_name}")
                                device_id = f"MTP:{item_name}"
                                current_drives.add(device_id)
                                drives_info[device_id] = {
                                    'id': device_id,
                                    'drive': device_id,
                                    'name': item_name,
                                    'type': 'MTP',
                                    'path': device_id,
                                    'is_mtp': True,
                                    'com_item': item
                                }
                                print(f"Added MTP device to list: {device_id}")
                            
                        except Exception as e:
                            print(f"Error checking MTP device: {e}")
                            continue
                except Exception as e:
                    print(f"Error checking MTP devices: {e}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
            else:
                print("COM not available - MTP detection disabled")
            
            # Only check for SD cards if no MTP devices were found
            if not any(drives_info.get(d, {}).get('type') == 'MTP' for d in current_drives):
                # Get all drives
                drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:")]
                print(f"Found drives: {drives}")
                
                # Check each drive
                for drive in drives:
                    try:
                        print(f"Checking drive {drive}")
                        if self._is_potential_sd_card(drive):
                            total, used, free = shutil.disk_usage(drive)
                            print(f"Drive {drive} - Total: {total}, Used: {used}, Free: {free}")
                            
                            # Convert to GB for display
                            total_gb = total / (1024**3)
                            used_gb = used / (1024**3)
                            free_gb = free / (1024**3)
                            
                            print(f"Added drive {drive} to list (Free space: {free_gb:.1f}GB)")
                            current_drives.add(drive)
                            drives_info[drive] = {
                                'id': drive,
                                'drive': drive,
                                'name': '',
                                'type': 'SD',
                                'path': drive,
                                'total_gb': total_gb,
                                'free_gb': free_gb,
                                'used_gb': used_gb
                            }
                        else:
                            print(f"Drive {drive} is not a potential SD card")
                    except Exception as e:
                        print(f"Error checking drive {drive}: {e}")
            
            print(f"Final drives_info: {drives_info}")
            
            # Emit signals for changes
            for drive in current_drives - self.current_sd_drives:
                print(f"New device detected: {drive}")
                self.sd_card_detected.emit(drives_info[drive])
            
            for drive in self.current_sd_drives - current_drives:
                print(f"Device removed: {drive}")
                self.sd_card_removed.emit(drive)
            
            self.current_sd_drives = current_drives
            self.drives_info = drives_info
            
        except Exception as e:
            print(f"Error in check_drives: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
    
    def _is_device_still_connected(self, device_id):
        """Quick check if a specific device is still connected"""
        try:
            if device_id.startswith("MTP"):
                # Quick COM check for MTP devices
                if COM_AVAILABLE:
                    try:
                        shell = win32com.client.Dispatch("Shell.Application")
                        computer = shell.NameSpace(17)
                        for item in computer.Items():
                            if item.Name and (not item.Path or "::" in item.Path):
                                return True  # At least one MTP device found
                    except:
                        pass
                return False
            else:
                # Quick filesystem drive check
                return os.path.exists(device_id)
        except Exception as e:
            print(f"Error checking device connection for {device_id}: {e}")
            return False