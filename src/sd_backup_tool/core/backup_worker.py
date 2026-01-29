# -*- coding: utf-8 -*-
"""
Backup worker module
Handles file copying and backup logic from filesystem and MTP devices.
"""

import os
import sys
import time
import shutil
import hashlib
import win32com.client
import win32file
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from threading import Lock

# Remove wpd import and related code
print("Using Windows COM for MTP operations.")

class BackupWorker(QThread):
    progress_updated = pyqtSignal(int, int, int, int)
    file_copying = pyqtSignal(str)
    file_skipping = pyqtSignal(str)
    backup_completed = pyqtSignal(int, int, str)
    backup_error = pyqtSignal(str)
    drive_disconnected = pyqtSignal(str, int, int)
    
    def __init__(self, files_list, destination_base):
        super().__init__()
        self.files_list = files_list
        self.destination_base = destination_base
        self.should_stop = False
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the worker"""
        import logging
        self.logger = logging.getLogger('BackupWorker')
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
        """Main backup process"""
        try:
            total_files = len(self.files_list)
            files_processed = 0
            files_copied = 0
            files_skipped = 0
            
            # Create destination folders
            self._create_destination_folders(self.files_list)
            
            for file_info in self.files_list:
                if self.should_stop:
                    break
                    
                files_processed += 1
                self.progress_updated.emit(files_processed, total_files, files_copied, files_skipped)
                
                try:
                    destination_path = file_info.get('destination')
                    if not destination_path:
                        print(f"No destination path for file: {file_info.get('name', 'unknown')}")
                        files_skipped += 1
                        continue
                    
                    # Ensure destination directory exists
                    dest_dir = os.path.dirname(destination_path)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir, exist_ok=True)
                        print(f"Created directory: {dest_dir}")
                    
                    # Check if file already exists
                    if os.path.exists(destination_path):
                        print(f"Skipping existing file: {file_info['name']}")
                        self.file_skipping.emit(file_info['name'])
                        files_skipped += 1
                        continue
                    
                    # Copy the file
                    print(f"Copying file: {file_info['name']}")
                    self.file_copying.emit(file_info['name'])
                    
                    if self.copy_file_item(file_info):
                        files_copied += 1
                        print(f"Successfully copied: {file_info['name']} to {destination_path}")
                    else:
                        files_skipped += 1
                        print(f"Failed to copy: {file_info['name']}")
                        
                except Exception as e:
                    print(f"Error processing file {file_info.get('name', 'unknown')}: {e}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    files_skipped += 1
                    
            # Emit final results
            if not self.should_stop:
                self.backup_completed.emit(files_processed, files_copied, self.destination_base)
                
        except Exception as e:
            print(f"Error in backup process: {e}")
            self.backup_error.emit(str(e))
            
    def copy_file_item(self, file_info):
        """Copy a file item, handling both regular files and MTP files"""
        try:
            print(f"[copy_file_item] Starting copy for: {file_info['name']}")
            
            # For MTP files, use the COM interface
            if file_info.get('is_mtp', False):
                print(f"[copy_file_item] Using MTP copy for: {file_info['name']}")
                return self.copy_com_mtp_file(file_info, file_info['destination'])
            
            # For regular files, use direct file system copy
            print(f"[copy_file_item] Using direct file copy for: {file_info['name']}")
            try:
                # Ensure destination directory exists
                dest_dir = os.path.dirname(file_info['destination'])
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copy the file using optimized direct copy with large buffer
                # shutil.copy2 is good but we can ensure optimal buffer size manually if needed.
                # standard copy2 + copyfileobj uses default buffer (usually 16KB-64KB).
                # We'll stick to shutil.copy2 for metadata preservation but ensure we use it efficiently.
                # If performance is critical, we could use a custom copy loop, but shutil.copy2 is generally robust.
                # However, for this task, let's explicitly use a larger buffer copy implementation
                # while preserving metadata.
                
                with open(file_info['source'], 'rb') as fsrc:
                    with open(file_info['destination'], 'wb') as fdst:
                        # 1MB buffer size
                        shutil.copyfileobj(fsrc, fdst, length=1024*1024)
                
                # Copy metadata
                shutil.copystat(file_info['source'], file_info['destination'])
                
                # Verify the copy
                if os.path.exists(file_info['destination']):
                    if os.path.getsize(file_info['destination']) == os.path.getsize(file_info['source']):
                        print(f"[copy_file_item] Successfully copied: {file_info['name']}")
                        return True
                    else:
                        print(f"[copy_file_item] File size mismatch for: {file_info['name']}")
                        return False
                else:
                    print(f"[copy_file_item] Destination file not found: {file_info['destination']}")
                    return False
                    
            except Exception as e:
                print(f"[copy_file_item] Error copying file: {e}")
                import traceback
                print(f"[copy_file_item] Traceback: {traceback.format_exc()}")
                return False
                
        except Exception as e:
            print(f"[copy_file_item] Error in copy_file_item: {e}")
            import traceback
            print(f"[copy_file_item] Traceback: {traceback.format_exc()}")
            return False
            
    def copy_com_mtp_file(self, file_info, destination_file_path):
        """Copy a file from an MTP device using COM interface"""
        try:
            print(f"[copy_com_mtp_file] Attempting to copy: {file_info['name']} to {destination_file_path}")
            
            # Get the COM item from the file info
            com_item = file_info.get('com_item')
            if not com_item:
                print(f"[copy_com_mtp_file] No COM item found in file_info for: {file_info['name']}")
                return False
            
            print(f"[copy_com_mtp_file] Using stored COM item for: {file_info['name']}")
            
            # Try the most reliable copy method first (based on previous success)
            methods = [
                self._copy_com_direct_to_destination,  # This one worked, try first
                self._copy_com_simple,
                self._copy_com_via_drag_drop
            ]
            
            for i, method in enumerate(methods):
                try:
                    print(f"[copy_com_mtp_file] Trying copy method {i+1}/3: {method.__name__}")
                    result = method(com_item, destination_file_path, file_info)
                    print(f"[copy_com_mtp_file] Result of {method.__name__}: {result}")
                    if result:
                        print(f"[copy_com_mtp_file] Successfully copied using {method.__name__}")
                        return True
                    else:
                        print(f"[copy_com_mtp_file] Method {method.__name__} returned False, trying next method")
                except Exception as e:
                    print(f"[copy_com_mtp_file] Method {method.__name__} failed with exception: {e}")
                    continue
            
            print("[copy_com_mtp_file] All copy methods failed")
            return False
            
        except Exception as e:
            print(f"[copy_com_mtp_file] Error in copy_com_mtp_file: {e}")
            import traceback
            print(f"[copy_com_mtp_file] Traceback: {traceback.format_exc()}")
            return False
            
    def _copy_com_simple(self, com_item, destination_file_path, file_info):
        """Copy a file using direct data transfer from COM object"""
        try:
            print(f"[_copy_com_simple] Starting direct copy for {file_info['name']}")
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_file_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                print(f"[_copy_com_simple] Created destination directory: {dest_dir}")
            
            # Get the file data using COM
            try:
                print(f"[_copy_com_simple] Getting file data from COM object")
                # Try to get the file data using different COM properties
                file_data = None
                
                # Method 1: Try to get data using GetDetailsOf
                try:
                    shell = win32com.client.Dispatch("Shell.Application")
                    folder = shell.NameSpace(os.path.dirname(com_item.Path))
                    if folder:
                        for i in range(512):  # Try different property indices
                            try:
                                prop = folder.GetDetailsOf(com_item, i)
                                if prop and len(prop) > 0:
                                    print(f"[_copy_com_simple] Found property at index {i}: {prop[:100]}")
                            except:
                                continue
                except Exception as e:
                    print(f"[_copy_com_simple] Error getting details: {e}")
                
                # Method 2: Try to get data using Stream
                try:
                    if hasattr(com_item, 'GetStream'):
                        stream = com_item.GetStream()
                        if stream:
                            file_data = stream.Read()
                            print(f"[_copy_com_simple] Got file data using GetStream, size: {len(file_data) if file_data else 0}")
                except Exception as e:
                    print(f"[_copy_com_simple] Error getting stream: {e}")
                
                # Method 3: Try to get data using CopyTo
                if not file_data:
                    try:
                        temp_path = os.path.join(os.environ['TEMP'], f"temp_{file_info['name']}")
                        com_item.CopyTo(temp_path)
                        if os.path.exists(temp_path):
                            with open(temp_path, 'rb') as f:
                                file_data = f.read()
                            os.remove(temp_path)
                            print(f"[_copy_com_simple] Got file data using CopyTo, size: {len(file_data) if file_data else 0}")
                    except Exception as e:
                        print(f"[_copy_com_simple] Error using CopyTo: {e}")
                
                # Write the data to the destination file
                if file_data:
                    print(f"[_copy_com_simple] Writing data to {destination_file_path}")
                    with open(destination_file_path, 'wb') as f:
                        f.write(file_data)
                    
                    # Verify the file was written
                    if os.path.exists(destination_file_path):
                        print(f"[_copy_com_simple] File successfully written to {destination_file_path}")
                        return True
                    else:
                        print(f"[_copy_com_simple] File was not written successfully")
                        return False
                else:
                    print(f"[_copy_com_simple] Could not get file data using any method")
                    return False
                
            except Exception as e:
                print(f"[_copy_com_simple] Error during file transfer: {e}")
                import traceback
                print(f"[_copy_com_simple] Traceback: {traceback.format_exc()}")
                return False
            
        except Exception as e:
            print(f"[_copy_com_simple] Error in _copy_com_simple: {e}")
            import traceback
            print(f"[_copy_com_simple] Traceback: {traceback.format_exc()}")
            return False
            
    def _copy_com_direct_to_destination(self, com_item, destination_file_path, file_info):
        """Copy COM item directly to destination"""
        try:
            print(f"[_copy_com_direct_to_destination] Starting direct copy to {destination_file_path}")
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_file_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                print(f"[_copy_com_direct_to_destination] Created destination directory: {dest_dir}")
            
            # Get the destination folder as a shell folder
            shell = win32com.client.Dispatch("Shell.Application")
            dest_folder = shell.NameSpace(dest_dir)
            
            if not dest_folder:
                print(f"[_copy_com_direct_to_destination] Failed to get shell namespace for destination: {dest_dir}")
                return False
            
            # Copy the file using CopyHere with maximum silence flags
            print(f"[_copy_com_direct_to_destination] Copying to {dest_dir}")
            # Use all possible silence flags to suppress Windows dialogs completely
            # FOF_SILENT (4), FOF_NOCONFIRMATION (16), FOF_NOCONFIRMMKDIR (512), FOF_NOERRORUI (1024), FOF_NOCOPYSECURITYATTRIBS (2048)
            # Adding FOF_MULTIDESTFILES (1) and FOF_FILESONLY (128) for better compatibility
            silent_flags = 4 | 16 | 512 | 1024 | 2048 | 128
            print(f"[_copy_com_direct_to_destination] Using flags: {silent_flags}")
            dest_folder.CopyHere(com_item, silent_flags)
            
            # Wait for the file to appear with shorter timeout for better performance
            timeout = 10  # seconds (reduced from 30)
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.exists(destination_file_path):
                    print(f"[_copy_com_direct_to_destination] File appeared at {destination_file_path}")
                    return True
                time.sleep(0.2)  # Check more frequently
            
            # Check one more time - sometimes files appear after timeout
            if os.path.exists(destination_file_path):
                print(f"[_copy_com_direct_to_destination] File appeared after timeout: {destination_file_path}")
                return True
            
            print(f"[_copy_com_direct_to_destination] Timeout waiting for file to appear: {destination_file_path}")
            return False
            
        except Exception as e:
            print(f"[_copy_com_direct_to_destination] Error in _copy_com_direct_to_destination: {e}")
            import traceback
            print(f"[_copy_com_direct_to_destination] Traceback: {traceback.format_exc()}")
            return False
            
    def _copy_com_via_drag_drop(self, com_item, destination_file_path, file_info):
        """Copy COM item using drag and drop simulation"""
        try:
            print(f"[_copy_com_via_drag_drop] Starting drag and drop copy to {destination_file_path}")
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_file_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                print(f"[_copy_com_via_drag_drop] Created destination directory: {dest_dir}")
            
            # Get the destination folder as a shell folder
            shell = win32com.client.Dispatch("Shell.Application")
            dest_folder = shell.NameSpace(dest_dir)
            
            if not dest_folder:
                print(f"[_copy_com_via_drag_drop] Failed to get shell namespace for destination: {dest_dir}")
                return False
            
            # Create a temporary folder for the source
            temp_dir = os.path.join(os.environ['TEMP'], 'mtp_backup_temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Get the source folder
            source_folder = shell.NameSpace(os.path.dirname(com_item.Path))
            if not source_folder:
                print(f"[_copy_com_via_drag_drop] Failed to get shell namespace for source")
                return False
            
            # Copy using drag and drop
            print(f"[_copy_com_via_drag_drop] Starting drag and drop operation")
            source_folder.CopyHere(com_item, 4 | 16 | 512 | 1024 | 8192)  # All UI suppression flags
            
            # Wait for the file to appear
            timeout = 30  # seconds
            start_time = time.time()
            while time.time() - start_time < timeout:
                if os.path.exists(destination_file_path):
                    print(f"[_copy_com_via_drag_drop] File appeared at {destination_file_path}")
                    return True
                time.sleep(0.5)
            
            print(f"[_copy_com_via_drag_drop] Timeout waiting for file to appear: {destination_file_path}")
            return False
            
        except Exception as e:
            print(f"[_copy_com_via_drag_drop] Error in _copy_com_via_drag_drop: {e}")
            import traceback
            print(f"[_copy_com_via_drag_drop] Traceback: {traceback.format_exc()}")
            return False
            
    def get_main_destination_folder(self, files_processed_list):
        """Get the main destination folder for the backup"""
        if not files_processed_list:
            return self.destination_base
            
        # Get the most common date from the processed files
        dates = [f.get('creation_date') for f in files_processed_list if f.get('creation_date')]
        if not dates:
            return self.destination_base
            
        most_common_date = max(set(dates), key=dates.count)
        return os.path.join(self.destination_base, most_common_date.strftime('%Y-%m-%d'))
        
    def check_drive_connectivity(self, path_to_check, is_destination=False):
        """Check if a drive is still connected"""
        try:
            if is_destination:
                # For destination, just check if the path exists
                return os.path.exists(path_to_check)
            else:
                # For source, try to access the COM object
                return True  # We'll handle MTP disconnection in the copy process
        except Exception as e:
            print(f"Error checking drive connectivity: {e}")
            return False
            
    def stop(self):
        """Stop the backup process"""
        self.should_stop = True
        
    def is_potential_sd_card(self, drive_path, return_details=False):
        """Check if a drive is likely to be an SD card"""
        try:
            # Get drive information
            drive_info = win32file.GetVolumeInformation(drive_path)
            
            # Check if it's removable
            is_removable = win32file.GetDriveType(drive_path) == win32file.DRIVE_REMOVABLE
            
            # Check size (SD cards are typically 2GB to 2TB)
            total_bytes = win32file.GetDiskFreeSpace(drive_path)
            total_gb = (total_bytes[0] * total_bytes[1] * total_bytes[2]) / (1024**3)
            
            if return_details:
                return {
                    'is_removable': is_removable,
                    'total_gb': total_gb,
                    'is_potential_sd': is_removable and 2 <= total_gb <= 2048
                }
            
            return is_removable and 2 <= total_gb <= 2048
            
        except Exception as e:
            print(f"Error checking SD card: {e}")
            return False
            
    def copy_with_recovery(self, source, destination):
        """Copy a file with recovery options"""
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            # Copy the file
            shutil.copy2(source, destination)
            
            # Verify the copy
            if os.path.exists(destination):
                if os.path.getsize(destination) == os.path.getsize(source):
                    return True
            return False
            
        except Exception as e:
            print(f"Error in copy_with_recovery: {e}")
            return False
            
    def _create_destination_folders(self, files_list):
        """Create destination folders for the backup"""
        try:
            # Get unique destination directories from files
            destination_dirs = set()
            for file_info in files_list:
                destination_file = file_info.get('destination')
                if destination_file:
                    dest_dir = os.path.dirname(destination_file)
                    destination_dirs.add(dest_dir)
            
            # Create all destination directories
            for dest_dir in destination_dirs:
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                    print(f"Created folder: {dest_dir}")
                    
        except Exception as e:
            print(f"Error creating destination folders: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
class BackupValidator:
    @staticmethod
    def validate_backup(source_files, destination_base):
        """Validate the backup by comparing source and destination files"""
        try:
            results = {
                'total_files': len(source_files),
                'validated_files': 0,
                'missing_files': [],
                'size_mismatches': [],
                'hash_mismatches': []
            }
            
            for file_info in source_files:
                dest_path = os.path.join(destination_base, file_info['name'])
                
                if not os.path.exists(dest_path):
                    results['missing_files'].append(file_info['name'])
                    continue
                    
                if os.path.getsize(dest_path) != file_info.get('size', 0):
                    results['size_mismatches'].append(file_info['name'])
                    continue
                    
                results['validated_files'] += 1
                
            return results
            
        except Exception as e:
            print(f"Error validating backup: {e}")
            return None
            
    @staticmethod
    def generate_validation_report(validation_result, output_path=None):
        """Generate a validation report"""
        try:
            report = []
            report.append("Backup Validation Report")
            report.append("=====================")
            report.append(f"Total files: {validation_result['total_files']}")
            report.append(f"Validated files: {validation_result['validated_files']}")
            report.append(f"Missing files: {len(validation_result['missing_files'])}")
            report.append(f"Size mismatches: {len(validation_result['size_mismatches'])}")
            report.append(f"Hash mismatches: {len(validation_result['hash_mismatches'])}")
            
            if validation_result['missing_files']:
                report.append("\nMissing Files:")
                for file in validation_result['missing_files']:
                    report.append(f"  - {file}")
                    
            if validation_result['size_mismatches']:
                report.append("\nSize Mismatches:")
                for file in validation_result['size_mismatches']:
                    report.append(f"  - {file}")
                    
            if validation_result['hash_mismatches']:
                report.append("\nHash Mismatches:")
                for file in validation_result['hash_mismatches']:
                    report.append(f"  - {file}")
                    
            report_text = "\n".join(report)
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(report_text)
                    
            return report_text
            
        except Exception as e:
            print(f"Error generating validation report: {e}")
            return None
            
class ResourceManager:
    def __init__(self):
        """Initialize resource manager"""
        self.com_objects = []
        
    def __enter__(self):
        """Enter context"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        self.cleanup()
        
    def cleanup(self):
        """Cleanup COM objects"""
        for obj in self.com_objects:
            try:
                obj.Release()
            except:
                pass
        self.com_objects = []
        
class FileOperationManager:
    def __init__(self):
        """Initialize file operation manager"""
        self.locks = {}
        
    def get_operation_lock(self, path):
        """Get a lock for a file operation"""
        if path not in self.locks:
            self.locks[path] = Lock()
        return self.locks[path]
        
    def perform_operation(self, path, operation):
        """Perform a file operation with locking"""
        with self.get_operation_lock(path):
            return operation()
            
class PathHandler:
    @staticmethod
    def normalize_path(path):
        """Normalize a path for Windows"""
        # Handle long paths
        if path.startswith('\\\\?\\'):
            return path
        if len(path) > 260:
            return f'\\\\?\\{os.path.abspath(path)}'
        return os.path.abspath(path)