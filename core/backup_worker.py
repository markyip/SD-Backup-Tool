# -*- coding: utf-8 -*-
"""
Backup worker module
Handles file copying and backup logic
"""

import os
import shutil
import logging
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from .file_scanner import FileDeduplicator

class BackupWorker(QThread):
    """Backup worker thread"""
    
    progress_updated = pyqtSignal(int, int)  # current progress, total count
    file_copying = pyqtSignal(str)           # name of the file being copied
    backup_completed = pyqtSignal(int, str)  # number of files copied, destination path
    backup_error = pyqtSignal(str)           # error message
    drive_disconnected = pyqtSignal(str, int, int)  # error type, number of files copied, total files
    
    def __init__(self, files_list, destination_base):
        super().__init__()
        self.files_list = files_list
        self.destination_base = destination_base
        self.should_stop = False
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging"""
        log_dir = os.path.join(os.path.expanduser("~"), "Documents", "SDBackupToolLogs") # SD Backup Tool Logs
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting backup process")
    
    def run(self):
        """Execute backup process"""
        try:
            self.logger.info(f"Starting backup of {len(self.files_list)} files to {self.destination_base}")
            
            # Check and filter duplicate files
            new_files, duplicates = FileDeduplicator.find_duplicates_in_destination(
                self.files_list, self.destination_base
            )
            
            if duplicates:
                self.logger.info(f"Skipping {len(duplicates)} duplicate files")
            
            if not new_files:
                self.logger.info("No new files to backup")
                self.backup_completed.emit(0, self.destination_base)
                return
            
            copied_count = 0
            total_files = len(new_files)
            
            for i, file_info in enumerate(new_files):
                if self.should_stop:
                    self.logger.info("Backup process aborted by user")
                    break
                
                try:
                    # Check source drive connectivity (SD card)
                    source_drive = os.path.splitdrive(file_info['path'])[0] + '\\'
                    if not self.check_drive_connectivity(source_drive):
                        error_msg = f"SD card disconnected: Cannot access {source_drive}"
                        self.logger.error(error_msg)
                        self.drive_disconnected.emit("SD card disconnected", copied_count, total_files) # SD card disconnected
                        return
                    
                    # Check destination drive connectivity
                    if not self.check_drive_connectivity(self.destination_base):
                        error_msg = f"Destination drive disconnected: Cannot access {self.destination_base}"
                        self.logger.error(error_msg)
                        self.drive_disconnected.emit("Destination drive disconnected", copied_count, total_files) # Destination drive disconnected
                        return
                    
                    # Send progress update
                    self.progress_updated.emit(i, total_files)
                    self.file_copying.emit(file_info['name'])
                    
                    # Copy file
                    success = self.copy_file(file_info)
                    if success:
                        copied_count += 1
                        self.logger.info(f"Successfully copied: {file_info['name']}")
                    else:
                        self.logger.error(f"Copy failed: {file_info['name']}")
                
                except Exception as e:
                    # Check if it's a drive disconnection error
                    if self.is_drive_disconnection_error(e):
                        # Re-check drive status
                        source_drive = os.path.splitdrive(file_info['path'])[0] + '\\'
                        if not self.check_drive_connectivity(source_drive):
                            self.logger.error(f"SD card disconnected: {str(e)}")
                            self.drive_disconnected.emit("SD card disconnected", copied_count, total_files) # SD card disconnected
                        elif not self.check_drive_connectivity(self.destination_base):
                            self.logger.error(f"Destination drive disconnected: {str(e)}")
                            self.drive_disconnected.emit("Destination drive disconnected", copied_count, total_files) # Destination drive disconnected
                        else:
                            self.logger.error(f"Unknown drive error: {str(e)}")
                            self.drive_disconnected.emit("Drive connection anomaly", copied_count, total_files) # Drive connection anomaly
                        return
                    else:
                        error_msg = f"Error copying file: {file_info['name']} - {str(e)}"
                        self.logger.error(error_msg)
                        self.backup_error.emit(error_msg)
                        continue
            
            # Send completion signal
            self.progress_updated.emit(total_files, total_files)
            
            # Find the main destination folder (most used)
            main_destination = self.get_main_destination_folder()
            
            self.logger.info(f"Backup complete, copied {copied_count} files, skipped {len(duplicates)} duplicate files")
            self.backup_completed.emit(copied_count, main_destination)
            
        except Exception as e:
            error_msg = f"Serious error in backup process: {str(e)}"
            self.logger.error(error_msg)
            self.backup_error.emit(error_msg)
    
    def copy_file(self, file_info):
        """Copy a single file"""
        try:
            source_path = file_info['path']
            
            # Generate destination folder path
            creation_date = file_info['creation_date']
            folder_name = FileDeduplicator.get_folder_name(file_info['type'], creation_date)
            destination_dir = os.path.join(self.destination_base, folder_name)
            
            # Ensure destination folder exists
            os.makedirs(destination_dir, exist_ok=True)
            
            # Generate destination file path
            destination_path = os.path.join(destination_dir, file_info['name'])
            
            # Handle filename conflicts (different files with the same name)
            destination_path = self.handle_filename_conflict(destination_path, source_path)
            
            # Re-check if source file exists before copying
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            # Copy file
            shutil.copy2(source_path, destination_path)
            
            # Verify if copy was successful
            if os.path.exists(destination_path):
                source_size = os.path.getsize(source_path)
                dest_size = os.path.getsize(destination_path)
                if source_size == dest_size:
                    return True
                else:
                    self.logger.error(f"File size mismatch: {file_info['name']}")
                    return False
            else:
                self.logger.error(f"Destination file not found: {destination_path}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to copy file: {file_info['name']} - {str(e)}")
            return False
    
    def handle_filename_conflict(self, destination_path, source_path):
        """Handle filename conflicts"""
        if not os.path.exists(destination_path):
            return destination_path
        
        # Check if it's the same file (avoid duplicate copying)
        if FileDeduplicator.is_duplicate(source_path, os.path.dirname(destination_path)):
            return destination_path
        
        # Filename conflict, generate new filename
        base_name, extension = os.path.splitext(destination_path)
        counter = 1
        
        while os.path.exists(destination_path):
            new_name = f"{base_name}_{counter}{extension}"
            destination_path = new_name
            counter += 1
            
            # Avoid infinite loop
            if counter > 1000:
                raise Exception("Cannot generate unique filename")
        
        return destination_path
    
    def get_main_destination_folder(self):
        """Get the main destination folder path"""
        if not self.files_list:
            return self.destination_base
        
        # Count files in each folder
        folder_counts = {}
        
        for file_info in self.files_list:
            creation_date = file_info['creation_date']
            folder_name = FileDeduplicator.get_folder_name(file_info['type'], creation_date)
            folder_path = os.path.join(self.destination_base, folder_name)
            
            folder_counts[folder_path] = folder_counts.get(folder_path, 0) + 1
        
        # Return the folder with the most files
        if folder_counts:
            main_folder = max(folder_counts.keys(), key=lambda k: folder_counts[k])
            return main_folder
        
        return self.destination_base
    
    def check_drive_connectivity(self, path):
        """Check drive connectivity status"""
        try:
            # Check if path exists and is accessible
            return os.path.exists(path) and os.access(path, os.R_OK | os.W_OK)
        except Exception:
            return False
    
    def is_drive_disconnection_error(self, error):
        """Determine if it's a drive disconnection error"""
        error_str = str(error).lower()
        disconnection_indicators = [
            'device not ready',
            'the system cannot find the path',
            'no such file or directory',
            'access is denied',
            'the network path was not found',
            'device is not ready',
            'the specified path is invalid',
            'drive not ready',
            'device not found'
        ]
        return any(indicator in error_str for indicator in disconnection_indicators)

    def stop(self):
        """Stop backup process"""
        self.should_stop = True

class BackupValidator:
    """Backup validator"""
    
    @staticmethod
    def validate_backup(source_files, destination_base):
        """Validate backup integrity"""
        validation_result = {
            'total_checked': 0,
            'successful': 0,
            'failed': 0,
            'missing': 0,
            'size_mismatch': 0,
            'failed_files': []
        }
        
        for file_info in source_files:
            validation_result['total_checked'] += 1
            
            try:
                # Calculate destination file path
                creation_date = file_info['creation_date']
                folder_name = FileDeduplicator.get_folder_name(file_info['type'], creation_date)
                destination_dir = os.path.join(destination_base, folder_name)
                destination_path = os.path.join(destination_dir, file_info['name'])
                
                # Check if file exists
                if not os.path.exists(destination_path):
                    validation_result['missing'] += 1
                    validation_result['failed_files'].append({
                        'file': file_info['name'],
                        'error': 'File not found' # File not found
                    })
                    continue
                
                # Check file size
                source_size = os.path.getsize(file_info['path'])
                dest_size = os.path.getsize(destination_path)
                
                if source_size != dest_size:
                    validation_result['size_mismatch'] += 1
                    validation_result['failed_files'].append({
                        'file': file_info['name'],
                        'error': f'File size mismatch (source: {source_size}, destination: {dest_size})' # File size mismatch (source: {source_size}, destination: {dest_size})
                    })
                    continue
                
                validation_result['successful'] += 1
                
            except Exception as e:
                validation_result['failed'] += 1
                validation_result['failed_files'].append({
                    'file': file_info['name'],
                    'error': str(e)
                })
        
        return validation_result
    
    @staticmethod
    def generate_validation_report(validation_result, output_path=None):
        """Generate validation report"""
        report_lines = [
            "=== Backup Validation Report ===", # Backup Validation Report
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", # Generated at:
            "",
            f"Total files checked: {validation_result['total_checked']}", # Total files checked:
            f"Successfully backed up: {validation_result['successful']}", # Successfully backed up:
            f"Files missing: {validation_result['missing']}", # Files missing:
            f"Size mismatch: {validation_result['size_mismatch']}", # Size mismatch:
            f"Other errors: {validation_result['failed']}", # Other errors:
            ""
        ]
        
        if validation_result['failed_files']:
            report_lines.append("=== Failed File Details ===") # Failed File Details
            for failed_file in validation_result['failed_files']:
                report_lines.append(f"File: {failed_file['file']}") # File:
                report_lines.append(f"Error: {failed_file['error']}") # Error:
                report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            except Exception as e:
                print(f"Could not write validation report: {e}") # Could not write validation report:
        
        return report_content