# -*- coding: utf-8 -*-
"""
Main window module - Enhanced version
Provides a simple and easy-to-use interface, suitable for elderly users
Includes a visual drive selector and pie chart display, removes automatic eject function
"""

import os
import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QGroupBox, QGridLayout,
    QSizePolicy, QMessageBox, QFileDialog, QScrollArea, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize, QSettings
from PyQt5.QtGui import QFont, QIcon
from core.sd_detector_fixed import SDCardDetector
from core.file_scanner import FileScanner
from core.backup_worker import BackupWorker
from ui.drive_tile_widget import DriveSelectionWidget
from locales import LanguageManager
import shutil

class MainWindow(QMainWindow):
    """Main window class"""
    
    def __init__(self):
        super().__init__()
        self.sd_detector = SDCardDetector()
        self.file_scanner = FileScanner()
        self.backup_worker = None
        self.scanned_files = []
        self.settings = QSettings('SDBackupTool', 'PhotoVideoBackupTool')
        
        # Initialize language manager
        self.lang = LanguageManager()
        
        # Set application icon
        icon_path_source = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico')
        icon_path_bundled = os.path.join(getattr(sys, '_MEIPASS', '.'), 'assets', 'icon.ico')

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            final_icon_path = icon_path_bundled
        else:
            final_icon_path = icon_path_source
            
        if os.path.exists(final_icon_path):
            self.setWindowIcon(QIcon(final_icon_path))
        else:
            print(f"Warning: Window icon not found at {final_icon_path}")
        
        self.init_ui()
        self.init_connections()
        self.init_sd_detection()
        self.load_settings()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle(self.lang.get_text('window_title'))
        self.setMinimumSize(1000, 700)
        
        # Set to full screen display
        self.showMaximized()
        
        # Set font
        font = QFont("Microsoft JhengHei", 12)
        self.setFont(font)
        
        # Create main window
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("📱 " + self.lang.get_text('window_title') + " - 檔案備份")
        title_font = QFont("Microsoft JhengHei", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title_label)
        
        # SD card status area
        self.create_sd_status_group(layout)
        
        # Destination selection area
        self.create_destination_group_enhanced(layout)
        
        # File scan area
        self.create_scan_group(layout)
        
        # Backup progress area
        self.create_backup_group(layout)
        
        # Status bar and buttons
        self.create_bottom_section(layout)
        
        # Update drive list immediately
        print("Initializing drive list...")
        QTimer.singleShot(100, self.refresh_drives)
    
    def create_sd_status_group(self, layout):
        """Create SD card status group"""
        status_container = QHBoxLayout()
        status_container.setSpacing(20)
        
        group = QGroupBox(self.lang.get_text('sd_card_status'))
        group.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        group.setMaximumWidth(600)
        group_layout = QVBoxLayout()
        
        status_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton(self.lang.get_text('refresh'))
        self.refresh_button.setFont(QFont("Microsoft JhengHei", 12))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_drives)
        status_layout.addWidget(self.refresh_button)
        
        # Add manual scan button for MTP devices
        self.scan_button = QPushButton("Scan Device")
        self.scan_button.setFont(QFont("Microsoft JhengHei", 12))
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.scan_button.clicked.connect(self.manual_scan)
        self.scan_button.setEnabled(False)
        status_layout.addWidget(self.scan_button)
        
        self.sd_status_label = QLabel(self.lang.get_text('searching_sd'))
        self.sd_status_label.setFont(QFont("Microsoft JhengHei", 13))
        self.sd_status_label.setStyleSheet("padding: 15px; background-color: #f8f9fa; border-radius: 8px;")
        self.sd_status_label.setMinimumWidth(260)
        self.sd_status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        status_layout.addWidget(self.sd_status_label)
        
        group_layout.addLayout(status_layout)
        group.setLayout(group_layout)
        
        status_container.addWidget(group)
        status_container.addStretch()
        layout.addLayout(status_container)
    
    def create_destination_group_enhanced(self, layout):
        """Create enhanced destination selection group"""
        group = QGroupBox(self.lang.get_text('backup_destination'))
        group.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(20, 20, 20, 20)
        group_layout.setSpacing(15)
        
        self.drive_selector = DriveSelectionWidget()
        self.drive_selector.drive_selected.connect(self.on_drive_selected)
        self.drive_selector.setMinimumHeight(80)
        group_layout.addWidget(self.drive_selector)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_scan_group(self, layout):
        """Create file scan group"""
        group = QGroupBox(self.lang.get_text('file_scan'))
        group.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        group_layout = QVBoxLayout()
        
        self.scan_result_grid = QGridLayout()
        self.scan_result_grid.setSpacing(15)
        
        # Photo results
        self.photo_result = QLabel(self.lang.get_text('photos', 0))
        self.photo_result.setFont(QFont("Microsoft JhengHei", 20, QFont.Bold))
        self.photo_result.setStyleSheet("""
            QLabel {
                background-color: #e8f6f3;
                border: 2px solid #1abc9c;
                border-radius: 10px;
                padding: 20px;
                color: #16a085;
            }
        """)
        self.photo_result.setAlignment(Qt.AlignCenter)
        self.photo_result.setMinimumHeight(80)
        self.scan_result_grid.addWidget(self.photo_result, 0, 0)
        
        # Video results
        self.video_result = QLabel(self.lang.get_text('videos', 0))
        self.video_result.setFont(QFont("Microsoft JhengHei", 20, QFont.Bold))
        self.video_result.setStyleSheet("""
            QLabel {
                background-color: #ebf5fb;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 20px;
                color: #2980b9;
            }
        """)
        self.video_result.setAlignment(Qt.AlignCenter)
        self.video_result.setMinimumHeight(80)
        self.scan_result_grid.addWidget(self.video_result, 0, 1)
        
        # RAW file results
        self.raw_result = QLabel(self.lang.get_text('raw_files', 0))
        self.raw_result.setFont(QFont("Microsoft JhengHei", 20, QFont.Bold))
        self.raw_result.setStyleSheet("""
            QLabel {
                background-color: #fef9e7;
                border: 2px solid #f1c40f;
                border-radius: 10px;
                padding: 20px;
                color: #d35400;
            }
        """)
        self.raw_result.setAlignment(Qt.AlignCenter)
        self.raw_result.setMinimumHeight(80)
        self.scan_result_grid.addWidget(self.raw_result, 1, 0)
        
        # Total size results
        self.total_result = QLabel(self.lang.get_text('total_size', 0))
        self.total_result.setFont(QFont("Microsoft JhengHei", 20, QFont.Bold))
        self.total_result.setStyleSheet("""
            QLabel {
                background-color: #f4ecf7;
                border: 2px solid #9b59b6;
                border-radius: 10px;
                padding: 20px;
                color: #8e44ad;
            }
        """)
        self.total_result.setAlignment(Qt.AlignCenter)
        self.total_result.setMinimumHeight(80)
        self.scan_result_grid.addWidget(self.total_result, 1, 1)
        
        group_layout.addLayout(self.scan_result_grid)
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_backup_group(self, layout):
        """Create backup group"""
        group = QGroupBox("檔案備份")
        group.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        group_layout = QVBoxLayout()
        
        self.backup_button = QPushButton(self.lang.get_text('start_backup'))
        self.backup_button.setFont(QFont("Microsoft JhengHei", 20, QFont.Bold))
        self.backup_button.setMinimumHeight(60)
        self.backup_button.setEnabled(False)
        self.backup_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.backup_button.clicked.connect(self.start_backup)
        group_layout.addWidget(self.backup_button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        group_layout.addWidget(self.progress_bar)
        
        self.current_file_label = QLabel("")
        self.current_file_label.setFont(QFont("Microsoft JhengHei", 10))
        self.current_file_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        group_layout.addWidget(self.current_file_label)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_bottom_section(self, layout):
        """Create bottom section"""
        bottom_layout = QHBoxLayout()
        
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Microsoft JhengHei", 11))
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        bottom_layout.addWidget(self.status_label)
        
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)
    
    def init_connections(self):
        """Initialize signal connections"""
        self.sd_detector.sd_card_detected.connect(self.on_sd_card_detected)
        self.sd_detector.sd_card_removed.connect(self.on_sd_card_removed)
        self.file_scanner.scan_completed.connect(self.on_scan_completed)
    
    def init_sd_detection(self):
        """Initialize SD card detection"""
        self.sd_detector.start()
        self.update_destination_drives()
    
    def load_settings(self):
        """Load settings"""
        last_destination = self.settings.value('last_destination', '')
        if last_destination:
            self.drive_selector.set_selected_drive(last_destination)
    
    def save_settings(self):
        """Save settings"""
        selected_drive = self.drive_selector.get_selected_drive()
        if selected_drive:
            self.settings.setValue('last_destination', selected_drive)
    
    def refresh_drives(self):
        """Refresh the list of available drives"""
        try:
            self.sd_detector.check_drives()  # Use check_drives instead of force_refresh
        except Exception as e:
            print(f"Error refreshing drives: {e}")
    
    def update_destination_drives(self):
        """Update destination drive list"""
        print("Starting drive detection...")
        drives_info = {}
        
        try:
            import win32api
            import win32file
            
            # Get all drives
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            print(f"Found drives: {drives}")
            
            for drive in drives:
                try:
                    # Check if drive is ready
                    if win32file.GetDriveType(drive) == win32file.DRIVE_FIXED:
                        print(f"Checking drive {drive}")
                        total, used, free = shutil.disk_usage(drive)
                        print(f"Drive {drive} - Total: {total}, Used: {used}, Free: {free}")
                        
                        # Convert to GB
                        total_gb = total / (1024**3)
                        free_gb = free / (1024**3)
                        used_gb = used / (1024**3)
                        
                        # Only show drives with at least 10GB free
                        if free >= 10 * (1024**3):  # 10GB in bytes
                            drives_info[drive] = {
                                'drive': drive,
                                'name': '',  # Default empty name
                                'total_gb': total_gb,
                                'free_gb': free_gb,
                                'used_gb': used_gb
                            }
                            print(f"Added drive {drive} to list (Free space: {free_gb:.1f}GB)")
                        else:
                            print(f"Drive {drive} has insufficient space (Free space: {free_gb:.1f}GB)")
                    else:
                        print(f"Drive {drive} is not a fixed drive")
                        
                except Exception as e:
                    print(f"Error getting info for drive {drive}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error updating drives: {e}")
        
        print(f"Final drives_info: {drives_info}")
        
        # Update drive selector
        if hasattr(self, 'drive_selector'):
            print("Updating drive selector...")
            self.drive_selector.update_drives(drives_info)
            print("Drive selector updated")
        else:
            print("Drive selector not found!")
    
    def on_drive_selected(self, drive_path):
        """Handle drive selection event"""
        self.save_settings()
        self.status_label.setText(f"Destination selected: {drive_path}")
        self._update_smart_scanning()
    
    def _update_smart_scanning(self):
        """Update smart scanning when both source and destination are selected"""
        if hasattr(self, 'current_sd_drive') and self.current_sd_drive and hasattr(self, 'drive_selector'):
            source_device_id = self.current_sd_drive.get('id')
            destination_drive = self.drive_selector.get_selected_drive()
            
            if source_device_id and destination_drive:
                print(f"Both devices selected - enabling smart scanning")
                # Check if smart scanning method exists (for backward compatibility)
                if hasattr(self.sd_detector, 'set_selected_devices'):
                    try:
                        self.sd_detector.set_selected_devices(source_device_id, destination_drive)
                    except Exception as e:
                        print(f"Error enabling smart scanning: {e}")
                else:
                    print("Smart scanning not available - using regular scanning")
    
    def on_sd_card_detected(self, device_info: dict):
        """Handle SD card/MTP device detection.
        device_info: {'id': str, 'name': str, 'type': str, 'path': str}
        """
        # Use device_info['name'] for display, device_info['id'] for processing
        display_name = device_info.get('name', 'Unknown Device')
        device_id = device_info.get('id') # This is what scanner and backup worker use

        self.sd_status_label.setText(self.lang.get_text('device_detected', display_name)) # New lang string
        self.sd_status_label.setStyleSheet("padding: 15px; background-color: #d5edda; border-radius: 8px; color: #155724;")
        self.status_label.setText("")
        self.current_sd_drive = device_info # Store the whole dict
        
        # Enable scan button for MTP devices
        if device_info.get('type') == 'MTP':
            self.scan_button.setEnabled(True)
        
        # Pass the device_id (e.g., "D:\" or "MTP:XYZ") to drive_selector and scanner
        self.drive_selector.set_sd_card_drive(device_id)
        self._update_smart_scanning()  # Check if we can enable smart scanning
        self.start_scan() # start_scan will use self.current_sd_drive['id']
    
    def on_sd_card_removed(self, removed_device_id: str):
        """Handle SD card/MTP device removal."""
        # Check if the removed device is the one currently being processed
        current_processing_id = None
        if hasattr(self, 'current_sd_drive') and self.current_sd_drive:
            current_processing_id = self.current_sd_drive.get('id')

        if current_processing_id == removed_device_id or not self.sd_detector.current_sd_drives:
            # If the active device was removed, or no devices are left, reset UI
            self.sd_status_label.setText(self.lang.get_text('searching_sd'))
            self.sd_status_label.setStyleSheet("padding: 15px; background-color: #f8f9fa; border-radius: 8px;")
            self.scanned_files = []
            self.reset_scan_ui() # Use the new reset method
            self.backup_button.setEnabled(False)
            self.scan_button.setEnabled(False)  # Disable scan button
            self.status_label.setText(self.lang.get_text('device_removed_status', removed_device_id)) # New lang string
            self.current_sd_drive = None
            self.drive_selector.set_sd_card_drive(None)
            self.drive_selector.show_all_drives()
        else:
            # Another device might still be connected, or this was not the active one.
            # UI might not need a full reset if another device is auto-selected or user selects another.
            # For now, we assume if a device is removed, and it wasn't the active one, the UI
            # for the active one (if any) remains. The sd_status_label might need an update
            # if the list of available devices changes.
            print(f"Device {removed_device_id} removed, but it was not the active source or other sources exist.")
            # Potentially refresh sd_status_label if no device is active now
            if not self.current_sd_drive and not self.sd_detector.current_sd_drives:
                 self.sd_status_label.setText(self.lang.get_text('searching_sd'))


    def start_scan(self):
        """Start scanning the selected source device"""
        if not self.current_sd_drive:
            print("No source device selected")
            return
            
        source_id_to_scan = self.current_sd_drive['id']
        print(f"Starting scan for source: {source_id_to_scan}")
        
        # Clear cache to ensure fresh scan results
        self.file_scanner.clear_cache(source_id_to_scan)
        print(f"Cleared cache for: {source_id_to_scan}")
        
        self.file_scanner.start_scan(source_id_to_scan)  # Updated method name
    
    def manual_scan(self):
        """Manually trigger scan for MTP device"""
        print("=== MANUAL SCAN TRIGGERED ===")
        if hasattr(self, 'current_sd_drive') and self.current_sd_drive:
            device_id = self.current_sd_drive.get('id')
            device_name = self.current_sd_drive.get('name', 'Unknown Device')
            print(f"Manual scan for device: {device_name} (ID: {device_id})")
            
            # Reset scan UI first
            self.reset_scan_ui()
            
            # Show scanning status
            self.status_label.setText(f"Manually scanning {device_name}...")
            
            # Trigger scan
            self.file_scanner.start_scan(device_id)
        else:
            print("No current device available for manual scan")
    
    def on_scan_completed(self, result):
        """Handle scan completion"""
        device_name_for_status = "the device"
        if hasattr(self, 'current_sd_drive') and self.current_sd_drive:
            device_name_for_status = self.current_sd_drive.get('name', 'the device')

        if 'error' in result and result['error']:
            error_msg = result['error']
            self.status_label.setText(self.lang.get_text('scan_error_status', device_name_for_status, error_msg))
            QMessageBox.warning(self, self.lang.get_text('scan_error_title'),
                                self.lang.get_text('scan_error_message', error_msg))
            self.reset_scan_ui()
            return
            
        self.scanned_files = result.get('files', [])
        if not self.scanned_files:
            self.status_label.setText(self.lang.get_text('no_media_found_on_device_status', device_name_for_status))
            self.reset_scan_ui()
            # Optionally, inform user more directly if no files found, e.g.:
            # QMessageBox.information(self, self.lang.get_text('scan_complete_title'), self.lang.get_text('no_media_found_message', device_name_for_status))
            return

        self.status_label.setText(self.lang.get_text('scan_complete_on_device_status', device_name_for_status))
        self.backup_button.setEnabled(True)
        
        photo_count = result.get('photos', 0)
        video_count = result.get('videos', 0) # Assuming these keys exist if no error
        raw_count = result.get('raw_files', 0)
        total_size = result.get('total_size_gb', 0)
        
        self.last_scan_result_size = total_size
        
        self.photo_result.setText(self.lang.get_text('photos', photo_count))
        self.video_result.setText(self.lang.get_text('videos', video_count))
        self.raw_result.setText(self.lang.get_text('raw_files', raw_count))
        self.total_result.setText(self.lang.get_text('total_size', f"{round(total_size)} GB"))
        
        self.drive_selector.required_space_gb = total_size

    def reset_scan_ui(self):
        """Resets the scan related UI elements to initial state."""
        self.scanned_files = []
        self.photo_result.setText(self.lang.get_text('photos', 0))
        self.video_result.setText(self.lang.get_text('videos', 0))
        self.raw_result.setText(self.lang.get_text('raw_files', 0))
        self.total_result.setText(self.lang.get_text('total_size', 0))
        self.backup_button.setEnabled(False)
        # self.status_label is typically set by the caller after reset_scan_ui
        self.progress_bar.setValue(0)
        self.current_file_label.setText("")
    
    def _prepare_files_for_backup(self, files_list, destination_base):
        """Prepare files for backup by setting destination paths"""
        prepared_files = []
        
        for file_info in files_list:
            # Create a copy of the file info
            prepared_file = file_info.copy()
            
            # Get file details
            creation_date = file_info.get('creation_date')
            if creation_date is None:
                creation_date = datetime.now()
                print(f"Warning: No creation date found for {file_info.get('name', 'unknown')}, using current date")
            
            file_type = file_info.get('type', 'unknown')
            file_name = file_info.get('name', 'unknown_file')
            
            # Determine folder structure based on file type and date
            year_str = creation_date.strftime('%Y')
            month_str = creation_date.strftime('%m')
            day_str = creation_date.strftime('%d')
            
            # Create type-specific folder
            if file_type == 'photo' or file_type == 'camera':
                type_folder = f"Photos_{year_str}"
            elif file_type == 'video':
                type_folder = f"Videos_{year_str}"
            elif file_type == 'raw':
                type_folder = f"Raw_{year_str}"
            else:
                type_folder = f"Other_{year_str}"
            
            # Build the full destination path
            destination_dir = os.path.join(destination_base, type_folder, month_str, day_str)
            destination_file = os.path.join(destination_dir, file_name)
            
            # Set the destination and source paths
            prepared_file['destination'] = destination_file
            if file_info.get('is_mtp', False):
                # For MTP files, the source is the file info itself (contains COM object)
                prepared_file['source'] = file_info.get('path', '')
            else:
                # For filesystem files, use the path directly
                prepared_file['source'] = file_info.get('path', '')
            
            prepared_files.append(prepared_file)
            
        return prepared_files
    
    def _find_actual_backup_folder(self, destination_base):
        """Find the actual backup folder that was created"""
        try:
            from datetime import datetime
            import glob
            
            # Look for folders created today with pattern like Photos_2025, Raw_2025, Videos_2025
            current_year = datetime.now().strftime('%Y')
            possible_patterns = [
                f"Photos_{current_year}",
                f"Raw_{current_year}",
                f"Videos_{current_year}",
                f"Other_{current_year}"
            ]
            
            for pattern in possible_patterns:
                folder_path = os.path.join(destination_base, pattern)
                if os.path.exists(folder_path):
                    print(f"Found backup folder: {folder_path}")
                    return folder_path
            
            # If no specific folder found, return the base destination
            print(f"No specific backup folder found, returning base: {destination_base}")
            return destination_base
            
        except Exception as e:
            print(f"Error finding actual backup folder: {e}")
            return destination_base
    
    def start_backup(self):
        """Start backup"""
        if not self.scanned_files:
            QMessageBox.warning(self, self.lang.get_text('warning_title'), 
                              self.lang.get_text('insert_sd_first'))
            return
        
        selected_drive = self.drive_selector.get_selected_drive()
        destination_path = selected_drive
        
        if hasattr(self, 'custom_destination'):
            destination_path = self.custom_destination
        
        if not destination_path:
            self.show_custom_error_dialog(
                self.lang.get_text('select_destination'),
                self.lang.get_text('select_destination')
            )
            return
        
        if hasattr(self, 'current_sd_drive') and self.current_sd_drive and destination_path == self.current_sd_drive:
            self.show_custom_error_dialog(
                self.lang.get_text('invalid_destination'),
                self.lang.get_text('cannot_backup_to_self')
            )
            return
        
        if not self.drive_selector.check_drive_space(destination_path):
            drives_info = getattr(self.drive_selector, 'current_drives_info', {})
            if destination_path in drives_info:
                drive_info = drives_info[destination_path]
                required_space = getattr(self.drive_selector, 'required_space_gb', 0)
                
                self.show_custom_error_dialog(
                    self.lang.get_text('insufficient_space'),
                    self.lang.get_text('insufficient_space', 
                                     required_space,
                                     drive_info['free_gb'],
                                     required_space - drive_info['free_gb'])
                )
                return
        
        reply = self.show_custom_confirmation_dialog(
            self.lang.get_text('confirm_backup'),
            self.lang.get_text('confirm_backup_message', len(self.scanned_files), destination_path)
        )
        
        if reply:
            self.backup_button.setEnabled(False)
            self.backup_button.setText(self.lang.get_text('backing_up'))
            self.progress_bar.setValue(0)
            
            # Prepare files with destination paths
            prepared_files = self._prepare_files_for_backup(self.scanned_files, destination_path)
            
            self.backup_worker = BackupWorker(prepared_files, destination_path)
            self.backup_worker.progress_updated.connect(self.on_backup_progress)
            self.backup_worker.file_copying.connect(self.on_file_copying)
            self.backup_worker.file_skipping.connect(self.on_file_skipping)
            self.backup_worker.backup_completed.connect(self.on_backup_completed)
            self.backup_worker.backup_error.connect(self.on_backup_error)
            self.backup_worker.drive_disconnected.connect(self.on_drive_disconnected)
            self.backup_worker.start()
    
    def on_backup_progress(self, current, total, copied, skipped):
        """Backup progress update"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"進度: {current}/{total} ({progress}%) - 已複製: {copied}, 已跳過: {skipped}")
    
    def on_file_copying(self, filename):
        """Copying file"""
        self.current_file_label.setText(f"正在複製: {filename}")
        self.current_file_label.setStyleSheet("color: #2980b9; padding: 5px; font-weight: bold;")
    
    def on_file_skipping(self, filename):
        """Skipping duplicate file"""
        self.current_file_label.setText(f"跳過重複檔案: {filename}")
        self.current_file_label.setStyleSheet("color: #f39c12; padding: 5px; font-weight: bold;")
    
    def on_backup_completed(self, copied_count, skipped_count, destination_path):
        """Backup complete"""
        self.backup_button.setEnabled(True) # Re-enable backup button for another operation
        self.backup_button.setText(self.lang.get_text('start_backup'))
        self.progress_bar.setValue(100)
        self.current_file_label.setText("") # Clear current file label
        
        total_processed = copied_count + skipped_count
        if skipped_count > 0:
            self.status_label.setText(self.lang.get_text('backup_complete_skipped_status', copied_count, skipped_count))
        else:
            self.status_label.setText(self.lang.get_text('backup_complete_status', copied_count))
        
        # Find the actual backup folder that was created
        actual_backup_folder = self._find_actual_backup_folder(destination_path)
        
        # This method now handles MTP vs ejectable drives
        self.handle_post_backup_device_action()
        
        if skipped_count > 0:
            completion_message = self.lang.get_text('backup_summary_skipped_message',
                                                  copied_count, skipped_count,
                                                  total_processed, actual_backup_folder)
        else:
            completion_message = self.lang.get_text('backup_summary_message',
                                                  copied_count, actual_backup_folder)
        
        self.show_custom_completion_dialog(
            self.lang.get_text('backup_complete_title'), # Should be a generic "Backup Complete" title
            completion_message,
            actual_backup_folder
        )
    
    def handle_post_backup_device_action(self):
        """Handle actions after backup, like ejecting SD card or notifying MTP disconnect."""
        current_device_info = getattr(self, 'current_sd_drive', None)
        if not current_device_info:
            return

        device_type = current_device_info.get('type')
        device_name = current_device_info.get('name', 'Device')
        device_path = current_device_info.get('path') # This is the drive letter for ejectable drives

        if device_type == "MTP":
            self.show_custom_info_dialog(
                self.lang.get_text('mtp_backup_complete_title'),
                self.lang.get_text('mtp_can_disconnect_message', device_name)
            )
        elif device_type in ["DRIVE_REMOVABLE", "DRIVE_FIXED_SD"] and device_path:
            try:
                import win32file
                GENERIC_READ = 0x80000000
                FILE_SHARE_READ = 0x00000001
                FILE_SHARE_WRITE = 0x00000002
                OPEN_EXISTING = 3
                IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808
                
                wp_path = f"\\\\.\\{device_path[0]}:"
                
                handle = win32file.CreateFile(
                    wp_path, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
                    None, OPEN_EXISTING, 0, None
                )
                win32file.DeviceIoControl(handle, IOCTL_STORAGE_EJECT_MEDIA, None, 0, None)
                win32file.CloseHandle(handle)
                
                dialog = QDialog(self)
                dialog.setFixedSize(600, 250); dialog.setModal(True)
                dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
                dialog.setStyleSheet(self.get_dialog_style("#27ae60"))
                
                layout = QVBoxLayout(dialog)
                layout.setSpacing(25); layout.setContentsMargins(40, 40, 40, 40)
                
                title_label = QLabel(self.lang.get_text('device_ejected_title', device_name))
                title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
                title_label.setAlignment(Qt.AlignCenter)
                title_label.setStyleSheet("color: #27ae60; margin-bottom: 15px;")
                layout.addWidget(title_label)
                
                message_label = QLabel(self.lang.get_text('can_remove_device_message', device_name))
                message_label.setFont(QFont("Microsoft JhengHei", 14))
                message_label.setAlignment(Qt.AlignCenter)
                message_label.setStyleSheet("color: #34495e; margin-bottom: 25px;")
                message_label.setWordWrap(True)
                layout.addWidget(message_label)
                
                ok_button = QPushButton(self.lang.get_text('ok'))
                self.style_dialog_button(ok_button, "#27ae60", "#2ecc71", "#1e8449")
                ok_button.clicked.connect(dialog.accept)
                
                button_layout = QHBoxLayout()
                button_layout.addStretch(); button_layout.addWidget(ok_button); button_layout.addStretch()
                layout.addLayout(button_layout)
                dialog.exec_()
                
            except Exception as e:
                print(f"Error ejecting drive {device_path}: {e}")
                self.show_custom_error_dialog(
                    self.lang.get_text('eject_failed_title', device_name),
                    self.lang.get_text('eject_failed_message', device_name, str(e))
                )
        else:
            print(f"Post-backup: Device type '{device_type}' not ejectable or path missing for {device_name}.")

    def on_drive_disconnected(self, error_type, copied_count, total_files):
        """Handle drive disconnection error"""
        self.backup_button.setEnabled(True)
        self.backup_button.setText(self.lang.get_text('start_backup'))
        self.current_file_label.setText("")
        self.status_label.setText(self.lang.get_text('backup_interrupted'))
        
        remaining_files = total_files - copied_count
        self.show_drive_disconnection_dialog(error_type, copied_count, total_files, remaining_files)

    def on_backup_error(self, error_message):
        """Handle backup error"""
        self.backup_button.setEnabled(True)
        self.backup_button.setText(self.lang.get_text('start_backup'))
        self.status_label.setText(self.lang.get_text('backup_failed'))
        self.current_file_label.setText("")
        
        self.show_custom_error_dialog(self.lang.get_text('error_title'), error_message)
    
    def get_dialog_style(self, border_color="#3498db"):
        """Returns a standard stylesheet string for custom dialogs."""
        return f"""
            QDialog {{
                background-color: #ffffff;
                border: 2px solid {border_color};
                border-radius: 15px;
            }}
            QLabel {{
                color: #2c3e50;
            }}
            QPushButton {{
                min-width: 120px;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
        """

    def style_dialog_button(self, button: QPushButton, bg_color, hover_color, pressed_color):
        """Applies consistent styling to a dialog button."""
        button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        button.setMinimumHeight(50)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)

    def show_custom_confirmation_dialog(self, title, message):
        """Show custom styled confirmation dialog"""
        dialog = QDialog(self)
        dialog.setFixedSize(600, 250)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setStyleSheet(self.get_dialog_style("#3498db")) # Blue border for confirmation
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25); layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Microsoft JhengHei", 14))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #34495e; margin-bottom: 25px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20); button_layout.setContentsMargins(0, 10, 0, 0)
        
        cancel_button = QPushButton(self.lang.get_text('cancel'))
        self.style_dialog_button(cancel_button, "#95a5a6", "#7f8c8d", "#6c757d") # Grey
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        confirm_button = QPushButton(self.lang.get_text('confirm'))
        self.style_dialog_button(confirm_button, "#27ae60", "#2ecc71", "#1e8449") # Green
        confirm_button.clicked.connect(dialog.accept)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        return dialog.exec_() == QDialog.Accepted

    def show_custom_completion_dialog(self, title, message, destination_path):
        """Show custom styled completion dialog"""
        dialog = QDialog(self)
        dialog.setFixedSize(700, 300) # Adjusted size for potentially longer messages
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setStyleSheet(self.get_dialog_style("#27ae60")) # Green border for completion
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25); layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #27ae60; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Microsoft JhengHei", 14))
        message_label.setAlignment(Qt.AlignCenter) # Keep centered for general message
        message_label.setStyleSheet("color: #34495e; margin-bottom: 25px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20); button_layout.setContentsMargins(0, 10, 0, 0)
        
        open_folder_button = QPushButton(self.lang.get_text('open_folder'))
        self.style_dialog_button(open_folder_button, "#3498db", "#2980b9", "#1f5582") # Blue
        def open_folder():
            try:
                os.startfile(destination_path)
            except Exception as e:
                print(f"Error opening folder {destination_path}: {e}")
                # Optionally show a small error to user if os.startfile fails
                QMessageBox.warning(self, "Error", f"Could not open folder: {destination_path}")
            dialog.accept()
        open_folder_button.clicked.connect(open_folder)
        button_layout.addWidget(open_folder_button)
        
        ok_button = QPushButton(self.lang.get_text('ok'))
        self.style_dialog_button(ok_button, "#27ae60", "#2ecc71", "#1e8449") # Green
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        dialog.exec_()

    def show_custom_error_dialog(self, title, message):
        """Show custom styled error dialog"""
        dialog = QDialog(self)
        dialog.setFixedSize(600, 250)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setStyleSheet(self.get_dialog_style("#e74c3c")) # Red border for error
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25); layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #e74c3c; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Microsoft JhengHei", 14))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #34495e; margin-bottom: 25px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        ok_button = QPushButton(self.lang.get_text('ok'))
        self.style_dialog_button(ok_button, "#e74c3c", "#c0392b", "#a93226") # Red
        ok_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch(); button_layout.addWidget(ok_button); button_layout.addStretch()
        layout.addLayout(button_layout)
        dialog.exec_()

    def show_custom_info_dialog(self, title, message):
        """Show custom styled informational dialog (similar to error but with info styling)."""
        dialog = QDialog(self)
        dialog.setFixedSize(600, 250)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setStyleSheet(self.get_dialog_style("#3498db")) # Blue border for info
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25); layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2980b9; margin-bottom: 15px;") # Blue title
        layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Microsoft JhengHei", 14))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #34495e; margin-bottom: 25px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        ok_button = QPushButton(self.lang.get_text('ok'))
        self.style_dialog_button(ok_button, "#3498db", "#2980b9", "#1f5582") # Blue
        ok_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch(); button_layout.addWidget(ok_button); button_layout.addStretch()
        layout.addLayout(button_layout)
        dialog.exec_()


    def show_drive_disconnection_dialog(self, error_type, copied_count, total_files, remaining_files):
        """Show drive disconnection dialog"""
        dialog = QDialog(self)
        dialog.setFixedSize(800, 400) # Kept larger size for this detailed message
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setStyleSheet(self.get_dialog_style("#f39c12")) # Orange border for warning/disconnection
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25); layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(self.lang.get_text('drive_disconnected'))
        title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #f39c12; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        progress_percentage = int((copied_count / total_files) * 100) if total_files > 0 else 0
        
        message = self.lang.get_text('drive_disconnected_message',
                                   error_type,
                                   copied_count,
                                   total_files,
                                   progress_percentage,
                                   copied_count, # This seems redundant with the other copied_count
                                   remaining_files)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Microsoft JhengHei", 12))
        message_label.setAlignment(Qt.AlignLeft) # Align left for better readability of multi-line info
        message_label.setStyleSheet("color: #34495e; margin-bottom: 25px; line-height: 1.6;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20); button_layout.setContentsMargins(0, 10, 0, 0)
        
        restart_button = QPushButton(self.lang.get_text('restart'))
        self.style_dialog_button(restart_button, "#27ae60", "#2ecc71", "#1e8449") # Green for restart
        def restart_backup():
            dialog.accept()
            # Re-trigger scan if a source device was active, assuming it might be reconnected
            if hasattr(self, 'current_sd_drive') and self.current_sd_drive:
                self.on_sd_card_detected(self.current_sd_drive) # Re-process the current device
            else: # Or if no device was active, just refresh general state
                self.refresh_drives()
        restart_button.clicked.connect(restart_backup)
        button_layout.addWidget(restart_button)
        
        handle_later_button = QPushButton(self.lang.get_text('handle_later')) # Renamed from 'ok_button'
        self.style_dialog_button(handle_later_button, "#95a5a6", "#7f8c8d", "#6c757d") # Grey
        handle_later_button.clicked.connect(dialog.accept)
        button_layout.addWidget(handle_later_button)
        
        layout.addLayout(button_layout)
        dialog.exec_()

    def closeEvent(self, event):
        """Close event handler"""
        self.save_settings()
        self.sd_detector.stop()
        if self.backup_worker and self.backup_worker.isRunning():
            self.backup_worker.stop()
            self.backup_worker.wait()
        event.accept()