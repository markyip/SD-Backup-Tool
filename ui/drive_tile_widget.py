# -*- coding: utf-8 -*-
"""
Drive tile widget module
Provides a visual drive selection interface
"""

import os
import win32api
import win32file
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QColor
from locales import LanguageManager

class DriveTile(QFrame):
    """Drive tile class"""
    
    def __init__(self, drive_info, drives_info, parent=None):
        super().__init__(parent)
        self.drive_info = drive_info
        self.drives_info = drives_info
        self.lang = LanguageManager()
        
        # Set colors based on index to match scanned files design
        index = list(self.drives_info.keys()).index(self.drive_info['drive'])
        colors = ['#e8f6f3', '#ebf5fb', '#fef9e7', '#f4ecf7']
        border_colors = ['#1abc9c', '#3498db', '#f1c40f', '#9b59b6']
        text_colors = ['#16a085', '#2980b9', '#d35400', '#8e44ad']
        
        self.background_color = colors[index % len(colors)]
        self.border_color = border_colors[index % len(border_colors)]
        self.text_color = text_colors[index % len(text_colors)]
        
        self.init_ui()
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.background_color};
                border: none;
                border-radius: 10px;
            }}
            QFrame:hover {{
                background-color: {self.background_color};
                border: 2px solid #34495e;
            }}
            QFrame[selected="true"] {{
                background-color: {self.background_color};
                border: 4px solid #2ecc71;
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.text_color};
                border: none;
            }}
        """)
    
    def init_ui(self):
        """Initialize UI to match scanned files tile design - single row layout"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(80)  # Match scanned files tile height
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Match scanned files padding
        layout.setSpacing(0)
        
        # Single row with drive letter and free space
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        
        # Drive letter
        self.drive_letter = QLabel(self.drive_info['drive'])
        self.drive_letter.setFont(QFont("Microsoft JhengHei", 20, QFont.Bold))  # Match scanned files font
        self.drive_letter.setStyleSheet(f"color: {self.text_color}; border: none;")
        self.drive_letter.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.drive_letter)
        
        # Free space info
        self.free_label = QLabel(self.lang.get_text('free_space', round(self.drive_info['free_gb'])))
        self.free_label.setFont(QFont("Microsoft JhengHei", 20, QFont.Bold))
        self.free_label.setStyleSheet(f"color: {self.text_color}; border: none;")
        self.free_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.free_label)
        
        layout.addLayout(main_layout)
    
    def set_selected(self, selected):
        """Set selected state with clear visual feedback"""
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        
        if selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.background_color};
                    border: 4px solid #2ecc71;
                    border-radius: 10px;
                }}
                QFrame:hover {{
                    background-color: {self.background_color};
                    border: 4px solid #2ecc71;
                }}
                QLabel {{
                    color: {self.text_color};
                    border: none;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.background_color};
                    border: none;
                    border-radius: 10px;
                }}
                QFrame:hover {{
                    background-color: {self.background_color};
                    border: 2px solid #34495e;
                }}
                QLabel {{
                    color: {self.text_color};
                    border: none;
                }}
            """)

    def mousePressEvent(self, event):
        """Handle mouse press event to select the drive"""
        if event.button() == Qt.LeftButton:
            # Find the DriveSelectionWidget parent
            widget = self.parent()
            while widget and not isinstance(widget, DriveSelectionWidget):
                widget = widget.parent()
            if widget:
                widget.on_drive_selected(self.drive_info['drive'])
            print(f"Drive tile clicked: {self.drive_info['drive']}")

class DriveSelectionWidget(QWidget):
    """Drive selection widget class"""
    
    drive_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = LanguageManager()
        self.current_drives_info = {}
        self.current_sd_drive = None
        self.selected_drive = None
        self.required_space_gb = 0
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Title
        title = QLabel(self.lang.get_text('select_destination'))
        title.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Scroll area for drive tiles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.tiles_container = QWidget()
        self.tiles_layout = QGridLayout(self.tiles_container)
        self.tiles_layout.setSpacing(15)
        self.tiles_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.tiles_container)
        layout.addWidget(scroll)
    
    def update_drives(self, drives_info):
        """Update drive list"""
        self.current_drives_info = drives_info
        
        # Clear existing tiles
        for i in reversed(range(self.tiles_layout.count())):
            item = self.tiles_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        # Add new tiles
        row, col = 0, 0
        for drive, info in drives_info.items():
            tile = DriveTile(info, drives_info)
            self.tiles_layout.addWidget(tile, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
    
    def on_drive_selected(self, drive):
        """Handle drive selection with improved logic"""
        print(f"Drive selection called for: {drive}")
        
        # Deselect all drives first
        for i in range(self.tiles_layout.count()):
            item = self.tiles_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), DriveTile):
                item.widget().set_selected(False)
        
        # Select the clicked drive
        for i in range(self.tiles_layout.count()):
            item = self.tiles_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), DriveTile):
                if item.widget().drive_info['drive'] == drive:
                    item.widget().set_selected(True)
                    self.selected_drive = drive
                    self.drive_selected.emit(drive)  # Emit signal to update backup destination
                    print(f"Drive selected and signal emitted: {drive}")
                    break
    
    def set_sd_card_drive(self, drive):
        """Set SD card drive"""
        self.current_sd_drive = drive
    
    def get_selected_drive(self):
        """Get selected drive"""
        return self.selected_drive
    
    def check_drive_space(self, drive):
        """Check if drive has enough space"""
        if drive in self.current_drives_info:
            return self.current_drives_info[drive]['free_gb'] >= self.required_space_gb
        return False
    
    def filter_drives_by_space(self, required_space_gb):
        """Filter drives by required space"""
        self.required_space_gb = required_space_gb
        
        for i in range(self.tiles_layout.count()):
            tile = self.tiles_layout.itemAt(i)
            if isinstance(tile.widget(), DriveTile):
                drive = tile.widget().drive_info['drive']
                has_space = self.check_drive_space(drive)
                tile.widget().setVisible(has_space)
    
    def show_all_drives(self):
        """Show all drives"""
        for i in range(self.tiles_layout.count()):
            tile = self.tiles_layout.itemAt(i)
            if isinstance(tile.widget(), DriveTile):
                tile.widget().setVisible(True)
    
    def set_selected_drive(self, drive):
        """Set the selected drive and update the UI"""
        if drive in self.current_drives_info:
            self.on_drive_selected(drive)