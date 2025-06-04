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
        """Refresh drives"""
        print("Refreshing drives...")
        self.update_destination_drives()
        if hasattr(self, 'sd_detector'):
            self.sd_detector.check_drives()
    
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
    
    def on_sd_card_detected(self, drive_path):
        """Handle SD card detection"""
        self.sd_status_label.setText(self.lang.get_text('sd_detected', drive_path))
        self.sd_status_label.setStyleSheet("padding: 15px; background-color: #d5edda; border-radius: 8px; color: #155724;")
        self.status_label.setText("")
        self.current_sd_drive = drive_path
        
        self.drive_selector.set_sd_card_drive(drive_path)
        self.start_scan()
    
    def on_sd_card_removed(self):
        """Handle SD card removal"""
        self.sd_status_label.setText(self.lang.get_text('searching_sd'))
        self.sd_status_label.setStyleSheet("padding: 15px; background-color: #f8f9fa; border-radius: 8px;")
        self.scanned_files = []
        self.photo_result.hide()
        self.video_result.hide()
        # Ensure the file scan tile remains visible
        self.photo_result.show()
        self.video_result.show()
        self.backup_button.setEnabled(False)
        self.status_label.setText(self.lang.get_text('sd_removed'))
        self.current_sd_drive = None
        
        self.drive_selector.set_sd_card_drive(None)
        
        self.photo_result.setText(self.lang.get_text('photos', 0))
        self.video_result.setText(self.lang.get_text('videos', 0))
        self.raw_result.setText(self.lang.get_text('raw_files', 0))
        self.total_result.setText(self.lang.get_text('total_size', 0))
        
        self.drive_selector.show_all_drives()
    
    def start_scan(self):
        """Start file scan"""
        if not hasattr(self, 'current_sd_drive') or not self.current_sd_drive:
            QMessageBox.warning(self, self.lang.get_text('warning_title'), 
                              self.lang.get_text('insert_sd_first'))
            return
        
        self.photo_result.show()
        self.video_result.show()
        self.raw_result.show()
        self.total_result.show()
        
        self.status_label.setText(self.lang.get_text('scanning'))
        
        self.file_scanner.scan_directory(self.current_sd_drive)
    
    def on_scan_completed(self, result):
        """Handle scan completion"""
        if 'error' in result:
            self.status_label.setText(f"Scan error: {result['error']}")
            return
            
        self.scanned_files = result['files']
        self.status_label.setText(self.lang.get_text('scan_complete'))
        self.backup_button.setEnabled(True)
        
        photo_count = result['photos']
        video_count = result['videos']
        raw_count = result['raw_files']
        total_size = result['total_size_gb']
        
        self.last_scan_result_size = total_size
        
        self.photo_result.setText(self.lang.get_text('photos', photo_count))
        self.video_result.setText(self.lang.get_text('videos', video_count))
        self.raw_result.setText(self.lang.get_text('raw_files', raw_count))
        self.total_result.setText(self.lang.get_text('total_size', f"{round(total_size)} GB"))
        
        # Store required space but don't filter drives automatically
        self.drive_selector.required_space_gb = total_size
    
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
            
            self.backup_worker = BackupWorker(self.scanned_files, destination_path)
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
        self.backup_button.setEnabled(True)
        self.backup_button.setText(self.lang.get_text('start_backup'))
        self.progress_bar.setValue(100)
        self.current_file_label.setText("")
        
        total_processed = copied_count + skipped_count
        if skipped_count > 0:
            self.status_label.setText(f"備份完成！已複製 {copied_count} 個檔案，跳過 {skipped_count} 個重複檔案")
        else:
            self.status_label.setText(f"備份完成！已複製 {copied_count} 個檔案")
        
        self.eject_sd_card()
        
        # Create improved completion message
        if skipped_count > 0:
            completion_message = f"備份任務已完成！\n\n已成功複製 {copied_count} 個新檔案\n跳過 {skipped_count} 個已存在的重複檔案\n總計處理 {total_processed} 個檔案\n\n目標位置: {destination_path}"
        else:
            completion_message = f"備份任務已完成！\n\n已成功複製 {copied_count} 個檔案\n\n目標位置: {destination_path}"
        
        self.show_custom_completion_dialog(
            "✅ 備份完成",
            completion_message,
            destination_path
        )
    
    def eject_sd_card(self):
        """Eject SD card"""
        if hasattr(self, 'current_sd_drive') and self.current_sd_drive:
            try:
                import win32file
                import win32api
                import win32con
                
                # Get the drive letter without the colon
                drive_letter = self.current_sd_drive[0]
                
                # Create a handle to the drive
                handle = win32file.CreateFile(
                    f"\\\\.\\{drive_letter}:",
                    win32con.GENERIC_READ,
                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                    None,
                    win32con.OPEN_EXISTING,
                    0,
                    None
                )
                
                # Define the IOCTL constant for ejecting media
                IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808
                
                # Eject the media
                win32file.DeviceIoControl(
                    handle,
                    IOCTL_STORAGE_EJECT_MEDIA,
                    None,
                    0,
                    None
                )
                
                # Close the handle
                win32file.CloseHandle(handle)
                
                # Use custom dialog
                dialog = QDialog(self)
                dialog.setFixedSize(600, 250)
                dialog.setModal(True)
                dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
                
                # Set dialog style
                dialog.setStyleSheet("""
                    QDialog {
                        background-color: #ffffff;
                        border: 2px solid #27ae60;
                        border-radius: 15px;
                    }
                    QLabel {
                        color: #2c3e50;
                    }
                    QPushButton {
                        min-width: 120px;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                """)
                
                layout = QVBoxLayout(dialog)
                layout.setSpacing(25)
                layout.setContentsMargins(40, 40, 40, 40)
                
                # Title label
                title_label = QLabel("✅ SD卡已安全退出")
                title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
                title_label.setAlignment(Qt.AlignCenter)
                title_label.setStyleSheet("color: #27ae60; margin-bottom: 15px;")
                layout.addWidget(title_label)
                
                # Message label
                message_label = QLabel("您現在可以安全地移除SD卡。")
                message_label.setFont(QFont("Microsoft JhengHei", 14))
                message_label.setAlignment(Qt.AlignCenter)
                message_label.setStyleSheet("color: #34495e; margin-bottom: 25px;")
                message_label.setWordWrap(True)
                layout.addWidget(message_label)
                
                # Button container
                button_layout = QHBoxLayout()
                button_layout.setSpacing(20)
                button_layout.setContentsMargins(0, 10, 0, 0)
                
                # OK button
                ok_button = QPushButton("確定")
                ok_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
                ok_button.setMinimumHeight(50)
                ok_button.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2ecc71;
                    }
                    QPushButton:pressed {
                        background-color: #1e8449;
                    }
                """)
                ok_button.clicked.connect(dialog.accept)
                
                # Button container
                button_layout.addStretch()
                button_layout.addWidget(ok_button)
                button_layout.addStretch()
                
                layout.addLayout(button_layout)
                
                dialog.exec_()
                
            except Exception as e:
                # Use custom error dialog
                self.show_custom_error_dialog(
                    "⚠️ 無法自動退出SD卡",
                    f"請手動移除SD卡：\n{str(e)}"
                )
    
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
    
    def show_custom_confirmation_dialog(self, title, message):
        """Show custom styled confirmation dialog"""
        dialog = QDialog(self)
        dialog.setFixedSize(600, 250)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                min-width: 120px;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
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
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        cancel_button = QPushButton(self.lang.get_text('cancel'))
        cancel_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        cancel_button.setMinimumHeight(50)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c757d;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        confirm_button = QPushButton(self.lang.get_text('confirm'))
        confirm_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        confirm_button.setMinimumHeight(50)
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        confirm_button.clicked.connect(dialog.accept)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        
        return dialog.exec_() == QDialog.Accepted

    def show_custom_completion_dialog(self, title, message, destination_path):
        """Show custom styled completion dialog"""
        dialog = QDialog(self)
        dialog.setFixedSize(700, 300)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #27ae60;
                border-radius: 15px;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                min-width: 120px;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft JhengHei", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #27ae60; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Microsoft JhengHei", 14))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #34495e; margin-bottom: 25px;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        open_folder_button = QPushButton(self.lang.get_text('open_folder'))
        open_folder_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        open_folder_button.setMinimumHeight(50)
        open_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f5582;
            }
        """)
        def open_folder():
            os.startfile(destination_path)
            dialog.accept()
        open_folder_button.clicked.connect(open_folder)
        button_layout.addWidget(open_folder_button)
        
        ok_button = QPushButton(self.lang.get_text('ok'))
        ok_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        ok_button.setMinimumHeight(50)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
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
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #e74c3c;
                border-radius: 15px;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                min-width: 120px;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
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
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        ok_button = QPushButton(self.lang.get_text('ok'))
        ok_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        ok_button.setMinimumHeight(50)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def show_drive_disconnection_dialog(self, error_type, copied_count, total_files, remaining_files):
        """Show drive disconnection dialog"""
        dialog = QDialog(self)
        dialog.setFixedSize(800, 400)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #f39c12;
                border-radius: 15px;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                min-width: 120px;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
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
                                   copied_count,
                                   remaining_files)
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Microsoft JhengHei", 12))
        message_label.setAlignment(Qt.AlignLeft)
        message_label.setStyleSheet("color: #34495e; margin-bottom: 25px; line-height: 1.6;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        restart_button = QPushButton(self.lang.get_text('restart'))
        restart_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        restart_button.setMinimumHeight(50)
        restart_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        def restart_backup():
            dialog.accept()
            if hasattr(self, 'current_sd_drive') and self.current_sd_drive:
                self.start_scan()
        restart_button.clicked.connect(restart_backup)
        button_layout.addWidget(restart_button)
        
        ok_button = QPushButton(self.lang.get_text('handle_later'))
        ok_button.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        ok_button.setMinimumHeight(50)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c757d;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        
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