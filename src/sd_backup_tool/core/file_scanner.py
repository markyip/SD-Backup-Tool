# -*- coding: utf-8 -*-
"""
File scanning module
Scans and classifies media files from filesystem and MTP devices.
"""

import os
import hashlib
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import mimetypes # Not actively used, but kept for potential future use
import shutil
import re
import sys
import time
import win32com.client
import win32file
from threading import Lock

try:
    import win32com.client
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    print("WARNING: win32com not available - MTP scanning disabled")

class FileScanner(QObject):
    """File scanner - dispatches scan requests."""
    
    scan_completed = pyqtSignal(dict)  # Scan completed signal
    scan_error = pyqtSignal(str)
    scan_progress = pyqtSignal(int, int)
    
    PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.heic', '.webp', '.tiff', '.tif'}
    RAW_EXTENSIONS = {'.cr2', '.nef', '.arw', '.orf', '.rw2', '.dng', '.raf', '.sr2', '.pef', '.raw', '.crw', '.cr3'}
    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.mts', '.m2ts', '.wmv', '.flv', '.3gp', '.m4v', '.mpg', '.mpeg'}
    
    def __init__(self):
        super().__init__()
        self.scan_thread = None
        self.scan_cache = {}
        self.cache_lock = Lock()
        self.cache_timeout = 300  # Cache results for 5 minutes
    
    def start_scan(self, target_path_or_id):
        """Start a new scan"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
            
        self.scan_thread = ScanWorkerThread(target_path_or_id, is_mtp=target_path_or_id.startswith("MTP"))
        self.scan_thread.scan_completed.connect(self._handle_scan_completion)
        self.scan_thread.scan_error.connect(self.scan_error.emit)
        self.scan_thread.progress_updated.connect(self.scan_progress.emit)
        self.scan_thread.start()
    
    def _handle_scan_completion(self, result):
        """Handle scan completion and cache the result"""
        if self.scan_thread:
            target_id = self.scan_thread.path
            
            # Calculate file counts and total size from the result
            photo_count = 0
            video_count = 0
            raw_count = 0
            total_size_bytes = 0
            
            for file_info in result:
                file_type = file_info.get('type', 'unknown')
                
                if file_type == 'photo' or file_type == 'camera':
                    photo_count += 1
                elif file_type == 'video':
                    video_count += 1
                elif file_type == 'raw':
                    raw_count += 1
                
                total_size_bytes += file_info.get('size', 0)
            
            print(f"[_handle_scan_completion] Final counts - Photos: {photo_count}, Videos: {video_count}, RAW: {raw_count}")
            
            # Convert bytes to GB
            total_size_gb = total_size_bytes / (1024**3)
            
            # Convert list result to dict for caching with summary information
            result_dict = {
                'files': result,
                'photos': photo_count,
                'videos': video_count,
                'raw_files': raw_count,
                'total_size_gb': total_size_gb,
                'total_files': len(result),
                'error': None
            }
            with self.cache_lock:
                self.scan_cache[target_id] = result_dict
            self.scan_completed.emit(result_dict)
    
    def clear_cache(self, target_id=None):
        """Clear scan cache for a specific target or all targets"""
        with self.cache_lock:
            if target_id:
                if target_id in self.scan_cache:
                    del self.scan_cache[target_id]
                    print(f"Cleared cache for: {target_id}")
            else:
                self.scan_cache.clear()
                print("Cleared all scan cache")

    def _is_media_file(self, filename):
        """Check if a file is a media file"""
        try:
            # Convert to lowercase for case-insensitive comparison
            filename_lower = filename.lower()
            
            # Check for known extensions
            ext = os.path.splitext(filename_lower)[1]
            if ext in self.PHOTO_EXTENSIONS or ext in self.RAW_EXTENSIONS or ext in self.VIDEO_EXTENSIONS:
                return True
                
            # Special handling for camera files that might not have extensions
            # Sony cameras often use DSC prefix
            if filename_lower.startswith('dsc'):
                return True
                
            return False
        except Exception as e:
            print(f"Error checking if file is media: {e}")
            return False

    def _get_file_type(self, filename):
        """Get the type of a file"""
        try:
            filename_lower = filename.lower()
            ext = os.path.splitext(filename_lower)[1]
            
            if ext in self.PHOTO_EXTENSIONS:
                return 'photo'
            elif ext in self.RAW_EXTENSIONS:
                return 'raw'
            elif ext in self.VIDEO_EXTENSIONS:
                return 'video'
            elif filename_lower.startswith('dsc'):
                return 'camera'  # Special type for camera files
            else:
                return 'unknown'
        except Exception as e:
            print(f"Error getting file type: {e}")
            return 'unknown'

    def _get_creation_date(self, item):
        """Get creation date from COM item"""
        try:
            # Try different methods to get the date
            try:
                # Method 1: Direct property
                return item.DateCreated
            except:
                try:
                    # Method 2: Extended property
                    return item.ExtendedProperty("System.DateCreated")
                except:
                    # Method 3: Fallback to current date
                    return datetime.now()
        except Exception as e:
            print(f"Error getting creation date: {e}")
            return datetime.now()

    def scan_target(self, target_id, force_rescan=False):
        """Start a scan for a specific target"""
        self.start_scan(target_id)

class ScanWorkerThread(QThread):
    progress_updated = pyqtSignal(int, int)
    scan_completed = pyqtSignal(list)
    scan_error = pyqtSignal(str)
    
    def __init__(self, path, is_mtp=False):
        super().__init__()
        self.path = path
        self.is_mtp = is_mtp
        self.should_stop = False
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the worker"""
        import logging
        self.logger = logging.getLogger('ScanWorker')
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(ch)
        
    def run(self):
        """Main scanning process"""
        try:
            if self.is_mtp:
                self._scan_mtp_device()
            else:
                self._scan_filesystem()
                
        except Exception as e:
            print(f"Error in scan process: {e}")
            self.scan_error.emit(str(e))
            
    def _scan_mtp_device(self):
        """Scan an MTP device using COM"""
        try:
            print(f"[_scan_mtp_device] Starting MTP scan for: {self.path}")
            
            # Get the device using COM
            shell = win32com.client.Dispatch("Shell.Application")
            computer = shell.NameSpace(17)  # Computer namespace
            
            # Find the MTP device
            device = None
            device_name = self.path.replace("MTP:", "")  # Remove the prefix if present
            print(f"[_scan_mtp_device] Looking for device: {device_name}")
            
            for item in computer.Items():
                try:
                    if item.Name and item.Path and "::" in item.Path:
                        print(f"[_scan_mtp_device] Checking item: {item.Name}")
                        if item.Name == device_name:
                            device = item
                            print(f"[_scan_mtp_device] Found matching device: {item.Name}")
                            break
                except Exception as e:
                    print(f"[_scan_mtp_device] Error checking item: {e}")
                    continue
            
            if not device:
                print(f"[_scan_mtp_device] Device not found: {device_name}")
                self.scan_error.emit(f"Device not found: {device_name}")
                return
            
            print(f"[_scan_mtp_device] Found device: {device.Name}")
            
            # Get the device folder
            try:
                device_folder = device.GetFolder
                if not device_folder:
                    print(f"[_scan_mtp_device] Could not get device folder")
                    self.scan_error.emit("Could not access device folder")
                    return
                
                # Try to get the root folder items
                try:
                    items = device_folder.Items()
                    print(f"[_scan_mtp_device] Successfully got root folder items")
                except Exception as e:
                    print(f"[_scan_mtp_device] Error getting root folder items: {e}")
                    self.scan_error.emit(f"Error accessing device contents: {e}")
                    return
                
            except Exception as e:
                print(f"[_scan_mtp_device] Error getting device folder: {e}")
                self.scan_error.emit(f"Error accessing device folder: {e}")
                return
            
            # Scan the device recursively
            media_files = []
            total_size_bytes = 0
            
            def scan_folder(folder, current_path=""):
                nonlocal media_files, total_size_bytes
                
                if self.should_stop:
                    return
                
                try:
                    items = folder.Items()
                    print(f"[_scan_mtp_device] Scanning folder: {current_path}, found {len(items)} items")
                    
                    for item in items:
                        if self.should_stop:
                            return
                        
                        try:
                            item_path = os.path.join(current_path, item.Name)
                            print(f"[_scan_mtp_device] Processing item: {item_path}")
                            
                            # Check if it's a folder
                            try:
                                is_folder = item.IsFolder
                            except:
                                # Some MTP devices might not support IsFolder property
                                try:
                                    subfolder = item.GetFolder
                                    is_folder = True
                                except:
                                    is_folder = False
                            
                            if is_folder:
                                print(f"[_scan_mtp_device] Found folder: {item_path}")
                                # Recursively scan subfolder
                                try:
                                    subfolder = item.GetFolder
                                    if subfolder:
                                        scan_folder(subfolder, item_path)
                                except Exception as e:
                                    print(f"[_scan_mtp_device] Error accessing subfolder {item_path}: {e}")
                            else:
                                # Check if it's a media file
                                if self._is_media_file(item.Name):
                                    print(f"[_scan_mtp_device] Found media file: {item_path}")
                                    try:
                                        # Get file size
                                        try:
                                            size = item.Size
                                        except:
                                            # Some MTP devices might not support Size property
                                            size = 0
                                        
                                        # Get creation date - try from path first, then COM
                                        try:
                                            creation_date = self._extract_date_from_path(item_path)
                                            if creation_date is None:
                                                creation_date = self._get_creation_date(item)
                                                if creation_date is None:
                                                    creation_date = datetime.now()
                                                    print(f"[_scan_mtp_device] No creation date found for {item.Name}, using current date")
                                        except Exception as e:
                                            print(f"[_scan_mtp_device] Error getting creation date for {item.Name}: {e}")
                                            creation_date = datetime.now()
                                        
                                        # For MTP files, try to get the real file name with extension
                                        real_name = item.Name
                                        try:
                                            # Try to get extended property for real file name
                                            # Some MTP devices hide extensions in Name but have them in other properties
                                            if hasattr(item, 'ExtendedProperty'):
                                                try:
                                                    real_filename = item.ExtendedProperty("System.FileName")
                                                    if real_filename and '.' in real_filename:
                                                        real_name = real_filename
                                                        print(f"[_scan_mtp_device] Got real filename: {real_filename}")
                                                except:
                                                    pass
                                        except:
                                            pass
                                        
                                        # If still no extension and it's a DSC file, assume it's ARW
                                        if real_name.startswith('DSC') and '.' not in real_name:
                                            real_name = real_name + '.ARW'
                                            print(f"[_scan_mtp_device] Sony camera file detected, assuming ARW extension: {real_name}")
                                        
                                        # Get file type and add debug logging
                                        detected_type = self._get_file_type(real_name)
                                        print(f"[_scan_mtp_device] File {item.Name} -> {real_name} detected as type: {detected_type}")
                                        
                                        file_info = {
                                            'name': real_name,  # Use real name with extension
                                            'original_name': item.Name,  # Keep original for reference
                                            'path': item_path,
                                            'size': size,
                                            'type': detected_type,
                                            'creation_date': creation_date,
                                            'is_mtp': True,
                                            'com_item': item
                                        }
                                        media_files.append(file_info)
                                        total_size_bytes += size
                                        
                                        # Emit progress
                                        self.progress_updated.emit(len(media_files), total_size_bytes)
                                    except Exception as e:
                                        print(f"[_scan_mtp_device] Error processing media file {item_path}: {e}")
                                    
                        except Exception as e:
                            print(f"[_scan_mtp_device] Error processing item {item.Name}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"[_scan_mtp_device] Error scanning folder {current_path}: {e}")
                    return
            
            # Start scanning from root
            scan_folder(device_folder)
            
            if not self.should_stop:
                print(f"[_scan_mtp_device] Scan complete. Found {len(media_files)} media files")
                self.scan_completed.emit(media_files)
                
        except Exception as e:
            print(f"[_scan_mtp_device] Error in MTP scan: {e}")
            import traceback
            print(f"[_scan_mtp_device] Traceback: {traceback.format_exc()}")
            self.scan_error.emit(str(e))
            
    def _scan_filesystem(self):
        """Scan a filesystem path"""
        try:
            print(f"[_scan_filesystem] Starting filesystem scan for: {self.path}")
            
            media_files = []
            total_size_bytes = 0
            
            for root, dirs, files in os.walk(self.path):
                if self.should_stop:
                    break
                    
                for file in files:
                    if self.should_stop:
                        break
                        
                    try:
                        if self._is_media_file(file):
                            file_path = os.path.join(root, file)
                            file_info = {
                                'name': file,
                                'path': file_path,
                                'size': os.path.getsize(file_path),
                                'type': self._get_file_type(file),
                                'creation_date': datetime.fromtimestamp(os.path.getctime(file_path)),
                                'is_mtp': False
                            }
                            media_files.append(file_info)
                            total_size_bytes += file_info['size']
                            
                            # Emit progress
                            self.progress_updated.emit(len(media_files), total_size_bytes)
                            
                    except Exception as e:
                        print(f"[_scan_filesystem] Error processing file {file}: {e}")
                        continue
                        
            if not self.should_stop:
                print(f"[_scan_filesystem] Scan complete. Found {len(media_files)} media files")
                self.scan_completed.emit(media_files)
                
        except Exception as e:
            print(f"[_scan_filesystem] Error in filesystem scan: {e}")
            import traceback
            print(f"[_scan_filesystem] Traceback: {traceback.format_exc()}")
            self.scan_error.emit(str(e))
            
    def stop(self):
        """Stop the scanning process"""
        self.should_stop = True

    def _is_media_file(self, name):
        """Check if a file is a media file based on name and extension"""
        # Convert to lowercase for case-insensitive comparison
        name_lower = name.lower()
        
        # Check for Sony camera files (DSC prefix)
        if name.startswith('DSC'):
            return True
            
        # Check for common media extensions
        media_extensions = {
            # Photos
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            # Raw formats
            '.raw', '.arw', '.cr2', '.nef', '.dng',
            # Videos
            '.mp4', '.mov', '.avi', '.wmv', '.mkv'
        }
        
        return any(name_lower.endswith(ext) for ext in media_extensions)

    def _get_file_type(self, name):
        """Determine the type of file based on name and extension"""
        name_lower = name.lower()
        
        # Check extensions first (more specific)
        if any(name_lower.endswith(ext) for ext in ['.raw', '.arw', '.cr2', '.nef', '.dng']):
            return 'raw'
        elif any(name_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']):
            return 'photo'
        elif any(name_lower.endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.wmv', '.mkv']):
            return 'video'
        # Sony camera files without extension or with unrecognized extension
        elif name.startswith('DSC'):
            return 'camera'
            
        return 'unknown'

    def _get_creation_date(self, com_item):
        """Get creation date from COM item using multiple methods"""
        try:
            # Method 1: Try direct DateCreated property
            try:
                date_created = com_item.DateCreated
                if date_created:
                    print(f"[_get_creation_date] Got DateCreated: {date_created}")
                    return date_created
            except Exception as e:
                print(f"[_get_creation_date] DateCreated failed: {e}")
            
            # Method 2: Try getting date from properties
            try:
                props = com_item.Properties
                for i in range(min(props.Count, 50)):  # Limit iterations for performance
                    try:
                        prop = props.Item(i)
                        if 'Date' in prop.Name or 'Created' in prop.Name:
                            if prop.Value:
                                print(f"[_get_creation_date] Got from property {prop.Name}: {prop.Value}")
                                return prop.Value
                    except:
                        continue
            except Exception as e:
                print(f"[_get_creation_date] Properties method failed: {e}")
                    
            # Method 3: Try ModifyDate
            try:
                modify_date = com_item.ModifyDate
                if modify_date:
                    # Check if it's a valid date (not the COM default 1899-12-30)
                    if modify_date.year > 1900:
                        print(f"[_get_creation_date] Got valid ModifyDate: {modify_date}")
                        return modify_date
                    else:
                        print(f"[_get_creation_date] Invalid ModifyDate (COM default): {modify_date}")
            except Exception as e:
                print(f"[_get_creation_date] ModifyDate failed: {e}")
            
            print(f"[_get_creation_date] No date found for {com_item.Name}")
            return None
            
        except Exception as e:
            print(f"[_get_creation_date] All methods failed for {com_item.Name}: {e}")
            return None

    def _extract_date_from_path(self, file_path):
        """Extract date from file path like 'Storage Media\\2025-06-03\\DSC00519'"""
        try:
            import re
            # Look for date pattern YYYY-MM-DD in the path
            date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
            match = re.search(date_pattern, file_path)
            if match:
                year, month, day = match.groups()
                extracted_date = datetime(int(year), int(month), int(day))
                print(f"[_extract_date_from_path] Extracted date from path '{file_path}': {extracted_date}")
                return extracted_date
            else:
                print(f"[_extract_date_from_path] No date pattern found in path: {file_path}")
                return None
        except Exception as e:
            print(f"[_extract_date_from_path] Error extracting date from path '{file_path}': {e}")
            return None

class FileDeduplicator:
    @staticmethod
    def get_file_hash(source_info, chunk_size=8192):
        """
        Calculate MD5 hash of a file from a filesystem path.
        For MTP files, we skip hashing because it's too slow (requires downloading the file).
        """
        if source_info.get('is_mtp', False):
            return None
            
        path = source_info.get('path')
        if not path or not os.path.exists(path):
            return None

        hash_md5 = hashlib.md5()
        try:
            with open(path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {path}: {e}")
            return None
    
    @staticmethod
    def is_duplicate(source_file_info, destination_path_base):
        source_path_or_id = source_file_info['path']
        source_size = source_file_info['size']
        
        # CRITICAL: Skip duplicate checking for unknown file types
        # Unknown files will be skipped during backup anyway
        # But allow camera files to be checked (they'll be processed)
        if source_file_info['type'] == 'unknown':
            return False  # Never consider unknown files as duplicates
        elif source_file_info['type'] == 'camera':
            # Camera files should be processed, but use 'photo' for duplicate checking temporarily
            # since the actual type will be determined during copy
            return False  # Don't check duplicates for camera files - let them be processed
        
        creation_date = source_file_info['creation_date']
        folder_name_suffix = FileDeduplicator.get_folder_name_suffix(source_file_info['type'], creation_date)
        
        # Construct the full potential destination path
        # This assumes the backup worker uses a similar logic to build the final path.
        # For robustness, the backup worker should ideally create the year/month/day subfolders.
        # Here, we construct it for checking.
        year_str = creation_date.strftime('%Y')
        month_str = creation_date.strftime('%m')
        day_str = creation_date.strftime('%d')
        
        # Base folder for type (Photos_YYYY, Videos_YYYY etc.)
        type_folder_base = folder_name_suffix.split('_')[0] + "_" + year_str 
        
        destination_dir = os.path.join(destination_path_base, type_folder_base, month_str, day_str)
        destination_file = os.path.join(destination_dir, source_file_info['name'])
        
        if not os.path.exists(destination_file):
            return False
        
        try:
            dest_size = os.path.getsize(destination_file)
            if source_size != dest_size:
                return False
            
            # For MTP files, size match + date match is sufficient deduplication
            # to avoid the massive performance hit of downloading for MD5.
            if source_file_info.get('is_mtp', False):
                try:
                    dest_mtime = datetime.fromtimestamp(os.path.getmtime(destination_file))
                    # Allow 2 second difference for filesystem precision issues
                    if abs((creation_date - dest_mtime).total_seconds()) < 2:
                        return True
                except:
                    pass
                return False # If we can't verify date, assume not duplicate to be safe
                
            # For regular files, we use hashes for 100% certainty
            source_hash = FileDeduplicator.get_file_hash(source_file_info) 
            dest_hash_info = {'path': destination_file, 'is_mtp': False}
            dest_hash = FileDeduplicator.get_file_hash(dest_hash_info)
            
            return source_hash == dest_hash and source_hash is not None
            
        except Exception as e:
            print(f"Error checking duplicate for {source_file_info.get('name', 'N/A')}: {e}")
            return False 
    
    @staticmethod
    def find_duplicates_in_destination(files_list, destination_base):
        duplicates = []
        new_files = []
        
        # This part is called by BackupWorker before starting the copy.
        # The files_list here is the full list from the scanner.
        for file_info in files_list:
            if FileDeduplicator.is_duplicate(file_info, destination_base):
                duplicates.append(file_info)
            else:
                new_files.append(file_info)
        
        return new_files, duplicates
    
    @staticmethod
    def get_folder_name_suffix(file_type, creation_date):
        # This now returns the full Photos_YYYY/MM/DD structure part
        date_str_path = creation_date.strftime('%Y/%m/%d') # YYYY/MM/DD
        
        if file_type == 'photo':
            return f"Photos_{date_str_path}"
        elif file_type == 'raw':
            return f"Raw_{date_str_path}"  # RAW files get their own folder structure
        elif file_type == 'video':
            return f"Videos_{date_str_path}"
        elif file_type == 'camera':
            # Camera files default to Photos folder initially - will be moved if needed
            return f"Photos_{date_str_path}"
        else:
            # CRITICAL: Should never reach here for media backup tool
            # Only supported media types should be processed
            raise ValueError(f"Unsupported file type '{file_type}' should not be copied")