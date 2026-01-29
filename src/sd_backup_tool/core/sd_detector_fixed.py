# -*- coding: utf-8 -*-
"""
Improved SD card detection module
SD card monitoring optimized for Windows 11
"""

import os
import time
import shutil
import threading
from PyQt5.QtCore import QThread, pyqtSignal
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

class SDCardDetector(QThread):
    """Improved SD card detector running on background thread"""
    
    sd_card_detected = pyqtSignal(dict)  # Emits dict: {'id': str, 'name': str, 'type': str, 'path': str}
    sd_card_removed = pyqtSignal(str)    # Emits the ID of the removed device
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.current_sd_drives = set()
        # QTimer removal: Self-contained thread loop
        self.last_drives = set()
        self.scan_cache = {}  # Cache scan results
        self.selected_source_device = None  # Track selected source
        self.selected_destination_drive = None  # Track selected destination
        self.smart_scanning_enabled = False  # Switch to smart mode after initial setup
    
    def run(self):
        """Main thread loop"""
        self.running = True
        print("SD Card Detector thread started")
        while self.running:
            self.check_drives()
            # Sleep for 1 second between checks
            for _ in range(10): 
                if not self.running: break
                time.sleep(0.1)
                
    def stop(self):
        """Stop monitoring SD cards"""
        self.running = False
        self.wait()  # Wait for thread to finish
    
    def _is_potential_sd_card(self, drive):
        """Check if a drive is likely to be an SD card"""
        try:
            # Skip C:\ drive as it's almost certainly the system drive
            if drive.upper() == "C:\\":
                return False

            drive_type = win32file.GetDriveType(drive)
            
            # Get drive info
            try:
                total, used, free = shutil.disk_usage(drive)
                total_gb = total / (1024**3)
            except:
                return False

            # SD cards are typically 2GB to 2TB
            if total_gb < 1 or total_gb > 2048:
                return False

            # Case 1: Standard Removable Drive
            if drive_type == win32file.DRIVE_REMOVABLE:
                return True
            
            # Case 2: Fixed Drive that looks like an SD card (Large cards with high-speed readers)
            if drive_type == win32file.DRIVE_FIXED:
                # Check for characteristic media folders
                media_folders = ['DCIM', 'PRIVATE', 'GOPRO', 'AVCHD', 'DOWNLOAD', 'PICTURES']
                for folder in media_folders:
                    if os.path.exists(os.path.join(drive, folder)):
                        print(f"Drive {drive} detected as SD card because of folder: {folder}")
                        return True
                
                # Check volume label
                try:
                    volume_info = win32file.GetVolumeInformation(drive)
                    label = volume_info[0].upper()
                    if any(x in label for x in ["SD", "CANON", "SONY", "NIKON", "DJI", "GOPRO", "EOS"]):
                        print(f"Drive {drive} detected as SD card by label: {label}")
                        return True
                except:
                    pass
                    
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
                    print(f"Found {len(items)} items in computer namespace:")
                    for idx, itm in enumerate(items):
                        try:
                            print(f"  {idx}: Name='{itm.Name}', Path='{itm.Path}'")
                        except: pass
                    
                    for item in items:
                        try:
                            item_name = str(item.Name) if item.Name else ""
                            item_path = str(item.Path) if item.Path else ""
                            item_type = ""
                            try:
                                item_type = str(item.Type) if hasattr(item, 'Type') else ""
                            except: pass
                            
                            print(f"Checking item - Name: '{item_name}', Type: '{item_type}', Path: '{item_path}'")
                            
                            # Check if this is a portable device
                            is_portable = False
                            
                            # Method 1: Check Type property for common indicators
                            if any(x in item_type.upper() for x in ["PORTABLE", "MTP", "MEDIA", "手機", "行動裝置"]):
                                is_portable = True
                                print(f"Found portable device by Type indicator: {item_type}")
                            
                            # Method 2: Check path for MTP or Portable indicators
                            if not is_portable:
                                if "::" in item_path:
                                    # If it has the GUID prefix, it's very likely a shell namespace device (MTP/Network/etc)
                                    is_portable = True
                                    print(f"Found shell namespace item (potential MTP): {item_path}")
                                elif "usb#vid_" in item_path.lower() and "&pid_" in item_path.lower():
                                    is_portable = True
                                    print(f"Found MTP device with USB VID/PID in path")
                            
                            # Method 3: Check if it's a folder but NOT a standard drive letter
                            if not is_portable:
                                try:
                                    folder = item.GetFolder
                                    if folder:
                                        # If it's not a standard drive (e.g. "C:\") it might be an MTP device
                                        # Regular drives are handled separately
                                        if len(item_path) >= 2 and item_path[1:3] == ":\\":
                                            print(f"Skipping regular drive: {item_name} ({item_path})")
                                            continue
                                            
                                        # If path is empty but name exists and it's a folder, it's likely a portable device
                                        if not item_path and item_name:
                                            is_portable = True
                                            print(f"Found potential portable device with empty path: {item_name}")
                                        elif any(x in item_path.upper() for x in ["MTP", "PORTABLE", "USB"]):
                                            is_portable = True
                                            print(f"Found portable device by path keyword: {item_path}")
                                except Exception as e:
                                    pass
                            
                            if is_portable and item_name:
                                # Final check: Ensure it has some content or is a folder
                                try:
                                    folder = item.GetFolder
                                    # Even if we don't explore deeper here, the presence of GetFolder 
                                    # for a portable device is a good sign.
                                except:
                                    print(f"Item {item_name} reported as portable but has no folder access")
                                    # Don't skip yet, older phones might behave differently
                                
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
            
            # Check for SD cards (Mass Storage) even if MTP devices detected
            # This allows supporting devices that might appear as both or user having multiple devices
            
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