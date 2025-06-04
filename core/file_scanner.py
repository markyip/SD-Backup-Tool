# -*- coding: utf-8 -*-
"""
File scanning module
Scans and classifies media files
"""

import os
import hashlib
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import mimetypes

class FileScanner(QObject):
    """File scanner"""
    
    scan_completed = pyqtSignal(dict)  # Scan completed signal
    
    # Supported file formats (all lowercase for consistent matching)
    PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.heic', '.webp', '.tiff', '.tif'}
    RAW_EXTENSIONS = {'.cr2', '.nef', '.arw', '.orf', '.rw2', '.dng', '.raf', '.sr2', '.pef', '.raw', '.crw', '.cr3'}
    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.mts', '.m2ts', '.wmv', '.flv', '.3gp', '.m4v', '.mpg', '.mpeg'}
    
    def __init__(self):
        super().__init__()
        self.scan_thread = None
    
    def scan_directory(self, directory):
        """Scan the specified directory"""
        if self.scan_thread and self.scan_thread.isRunning():
            return
        
        self.scan_thread = ScanWorkerThread(directory)
        self.scan_thread.scan_completed.connect(self.scan_completed.emit)
        self.scan_thread.start()

class ScanWorkerThread(QThread):
    """Scan worker thread"""
    
    scan_completed = pyqtSignal(dict)
    
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
    
    def run(self):
        """Execute scan"""
        try:
            result = self.scan_files(self.directory)
            self.scan_completed.emit(result)
        except Exception as e:
            print(f"Scan error: {e}")
            self.scan_completed.emit({
                'total_files': 0,
                'photos': 0,
                'videos': 0,
                'raw_files': 0,
                'total_size_gb': 0,
                'files': [],
                'error': str(e)
            })
    
    def scan_files(self, directory):
        """Scan files and classify them"""
        files_info = {
            'total_files': 0,
            'photos': 0,
            'videos': 0,
            'raw_files': 0,
            'total_size_gb': 0,
            'files': []
        }
        
        total_size = 0
        
        # Recursively scan all files
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Check if it's a supported media format
                file_type = self.get_file_type(file_ext)
                if file_type == 'unknown':
                    continue
                
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    # Get file creation date
                    creation_date = self.get_file_creation_date(file_path, file_type)
                    
                    file_info = {
                        'path': file_path,
                        'name': file,
                        'size': file_size,
                        'type': file_type,
                        'creation_date': creation_date,
                        'relative_path': os.path.relpath(file_path, directory)
                    }
                    
                    files_info['files'].append(file_info)
                    files_info['total_files'] += 1
                    
                    # Count files of each type
                    if file_type == 'photo':
                        files_info['photos'] += 1
                    elif file_type == 'video':
                        files_info['videos'] += 1
                    elif file_type == 'raw':
                        files_info['raw_files'] += 1
                
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    continue
        
        files_info['total_size_gb'] = total_size / (1024**3)
        return files_info
    
    def get_file_type(self, extension):
        """Determine file type based on extension"""
        ext_lower = extension.lower() # Ensure the extension is lowercase for comparison
        if ext_lower in FileScanner.PHOTO_EXTENSIONS: # PHOTO_EXTENSIONS are already lowercase
            return 'photo'
        elif ext_lower in FileScanner.RAW_EXTENSIONS: # RAW_EXTENSIONS are already lowercase
            return 'raw'
        elif ext_lower in FileScanner.VIDEO_EXTENSIONS: # VIDEO_EXTENSIONS are already lowercase
            return 'video'
        else:
            return 'unknown'
    
    def get_file_creation_date(self, file_path, file_type):
        """Get file creation date"""
        try:
            # For photos, try to get shooting date from EXIF data
            if file_type == 'photo':
                exif_date = self.get_exif_date(file_path)
                if exif_date:
                    return exif_date
            
            # For videos or photos where EXIF cannot be obtained, use file modification time
            timestamp = os.path.getmtime(file_path)
            return datetime.fromtimestamp(timestamp)
            
        except Exception as e:
            print(f"Error getting creation date for {file_path}: {e}")
            # If an error occurs, use the current date
            return datetime.now()
    
    def get_exif_date(self, image_path):
        """Get shooting date from image EXIF data"""
        try:
            with Image.open(image_path) as image:
                exif_data = image._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'DateTime' or tag == 'DateTimeOriginal':
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
            return None
        except Exception as e:
            print(f"Error reading EXIF from {image_path}: {e}")
            return None

class FileDeduplicator:
    """File deduplicator"""
    
    @staticmethod
    def get_file_hash(file_path, chunk_size=8192):
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    @staticmethod
    def is_duplicate(source_file, destination_path):
        """Check if a file is a duplicate"""
        destination_file = os.path.join(destination_path, os.path.basename(source_file))
        
        # Check if destination file exists
        if not os.path.exists(destination_file):
            return False
        
        try:
            # Compare file sizes
            source_size = os.path.getsize(source_file)
            dest_size = os.path.getsize(destination_file)
            
            if source_size != dest_size:
                return False
            
            # If sizes are the same, compare file hashes
            source_hash = FileDeduplicator.get_file_hash(source_file)
            dest_hash = FileDeduplicator.get_file_hash(destination_file)
            
            return source_hash == dest_hash and source_hash is not None
            
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False
    
    @staticmethod
    def find_duplicates_in_destination(files_list, destination_base):
        """Find duplicate files in the destination directory"""
        duplicates = []
        new_files = []
        
        for file_info in files_list:
            # Construct destination path
            creation_date = file_info['creation_date']
            folder_name = FileDeduplicator.get_folder_name(file_info['type'], creation_date)
            destination_dir = os.path.join(destination_base, folder_name)
            
            if FileDeduplicator.is_duplicate(file_info['path'], destination_dir):
                duplicates.append(file_info)
            else:
                new_files.append(file_info)
        
        return new_files, duplicates
    
    @staticmethod
    def get_folder_name(file_type, creation_date):
        """Generate folder name based on file type and creation date"""
        date_str = creation_date.strftime('%Y/%m/%d')
        
        if file_type in ['photo', 'raw']:
            return f"Photos_{date_str}" # Photos_
        elif file_type == 'video':
            return f"Videos_{date_str}" # Videos_
        else:
            return f"Others_{date_str}" # Others_