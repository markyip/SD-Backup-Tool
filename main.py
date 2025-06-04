#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SD Card Media Backup Tool
Main program entry point
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTranslator, QLocale
from PyQt5.QtGui import QFont
from ui.main_window_enhanced import MainWindow  # Updated to use enhanced version
from locales import LanguageManager

# Add this for better exception handling in bundled app
def excepthook_handler(exc_type, exc_value, exc_tb):
    import traceback
    import time
    import sys
    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    tb_text = "".join(tb_lines)
    log_filename = "error_log.txt"
    # Log to a file
    try:
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(tb_text)
            f.write("-" * 80 + "\n")
        print(f"Unhandled exception logged to {log_filename}", file=sys.stderr)
    except Exception as log_exc:
        print(f"Error writing to log file {log_filename}: {log_exc}", file=sys.stderr)
    
    # Also print to stderr (especially useful if file logging fails or for console apps)
    print("Unhandled exception caught by custom excepthook:", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb) # Call the original excepthook too

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Get language from command line argument or environment variable
    language = 'zh_TW'  # Default to Traditional Chinese
    if len(sys.argv) > 1:
        language = sys.argv[1]
    elif 'SD_BACKUP_LANG' in os.environ:
        language = os.environ['SD_BACKUP_LANG']
    
    # Set application attributes
    app.setApplicationName("Photo Video Backup Tool") # Photo Video Backup Tool
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SD Backup Tool") # SD Backup Tool
    
    # Set font - Large font suitable for elderly users
    font = QFont("Microsoft JhengHei", 12)  # Microsoft JhengHei (Traditional Chinese font)
    app.setFont(font)
    
    # Set High DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create main window with specified language
    window = MainWindow()
    window.lang.set_language(language)
    window.show()
    
    sys.excepthook = excepthook_handler # Set the custom excepthook
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())