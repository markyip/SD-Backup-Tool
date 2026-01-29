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
from ..locales import LanguageManager

class DriveTile(QFrame):
    """Drive tile class"""
    
    def __init__(self, drive_info, drives_info, parent=None):
        super().__init__(parent)
        self.drive_info = drive_info
        self.drives_info = drives_info
        self.lang = LanguageManager()
        
        # Set colors based on drive letter hash to ensure stability
        # Use simple hash of the drive letter (e.g. "C:\") to pick a consistent color index
        colors = ['#e8f6f3', '#ebf5fb', '#fef9e7', '#f4ecf7']
        border_colors = ['#1abc9c', '#3498db', '#f1c40f', '#9b59b6']
        text_colors = ['#16a085', '#2980b9', '#d35400', '#8e44ad']
        
        # Use abs(hash()) to get consistent positive integer
        drive_hash = abs(hash(self.drive_info['drive']))
        index = drive_hash % len(colors)
        
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
        """Update drive list and store info for resizing"""
        self.current_drives_info = drives_info
        self.rebuild_grid()

    def rebuild_grid(self):
        """Rebuild the grid layout based on current width"""
        if not hasattr(self, 'tiles_layout'): return
            
        # Clear existing tiles
        for i in reversed(range(self.tiles_layout.count())):
            item = self.tiles_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        # Calculate columns based on width
        # Width of individual tiles is roughly 300-400px
        width = self.width()
        if width < 600:
            cols = 1
        elif width < 1000:
            cols = 2
        elif width < 1400:
            cols = 3
        else:
            cols = 4
            
        # Add new tiles
        row, col = 0, 0
        visible_drives = 0
        for drive, info in self.current_drives_info.items():
            # Filter by space if required
            if not self.check_drive_space(drive):
                continue
                
            visible_drives += 1
            tile = DriveTile(info, self.current_drives_info)
            # Re-select if it was selected
            if drive == self.selected_drive:
                tile.set_selected(True)
                
            self.tiles_layout.addWidget(tile, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        # If the selected drive is no longer visible, reset it
        if self.selected_drive and not self.check_drive_space(self.selected_drive):
            self.selected_drive = None
        
        # Add a stretch to the bottom to keep tiles at top
        # self.tiles_layout.setRowStretch(row + 1, 1)

    def resizeEvent(self, event):
        """Rebuild grid when widget is resized"""
        super().resizeEvent(event)
        # Use a small delay/throttle if needed, but for simple grid rebuild it's usually fine
        self.rebuild_grid()
    
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
        """Filter drives by required space and update layout"""
        self.required_space_gb = required_space_gb
        # We need to rebuild the grid to hide items properly and adjust layout
        self.rebuild_grid()

    def get_first_available_drive(self):
        """Get the first drive that meets space requirements"""
        for drive, info in self.current_drives_info.items():
            if self.check_drive_space(drive):
                return drive
        return None
    
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