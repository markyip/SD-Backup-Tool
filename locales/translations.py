# -*- coding: utf-8 -*-
"""
Language translations file for SD Backup Tool
Each translation includes an English comment for reference
To change the language, modify the text after the colon (:) in each line
"""

UI_TEXT = {
    # Main window
    'window_title': 'SD卡備份工具',  # SD Backup Tool
    'sd_card_status': 'SD卡狀態',  # SD Card Status
    'backup_destination': '備份目標',  # Backup Destination
    'file_scan': '檔案掃描',  # File Scan
    'backup_progress': '備份進度',  # Backup Progress
    
    # File types
    'photos': '照片: {}張',  # Photos: {} files
    'videos': '影片: {}個',  # Videos: {} files
    'raw_files': 'RAW檔案: {}個',  # RAW Files: {} files
    'total_size': '總大小: {}',  # Total Size: {}
    
    # Buttons
    'refresh': '重新整理',  # Refresh
    'start_scan': '開始掃描',  # Start Scan
    'start_backup': '開始備份',  # Start Backup
    'backing_up': '備份中...',  # Backing up...
    'select': '選擇',  # Select
    'selected': '已選擇',  # Selected
    'confirm': '確認',  # Confirm
    'cancel': '取消',  # Cancel
    'ok': '確定',  # OK
    'open_folder': '開啟資料夾',  # Open Folder
    'restart': '重新開始',  # Restart
    'handle_later': '稍後處理',  # Handle Later
    
    # Messages
    'searching_sd': '正在搜尋SD卡...',  # Searching for SD card...
    'sd_detected': '已偵測到SD卡: {}',  # SD card detected: {}
    'sd_removed': 'SD卡已移除',  # SD card removed
    'scan_complete': '掃描完成',  # Scan complete
    'backup_complete': '備份完成！已複製 {} 個檔案',  # Backup complete! Copied {} files
    'backup_interrupted': '備份中斷 - 磁碟機已斷開連接',  # Backup interrupted - Drive disconnected
    'backup_failed': '備份失敗',  # Backup failed
    'total_space': '總空間: {}GB',  # Total space: {}GB
    'used_space': '已使用: {}GB',  # Used space: {}GB
    'free_space': '可用空間: {}GB',  # Free space: {}GB
    'select_destination': '選擇備份目標',  # Select backup destination
    
    # Dialogs
    'warning_title': '警告',  # Warning
    'error_title': '備份錯誤',  # Backup Error
    'confirm_backup': '確認備份',  # Confirm Backup
    'confirm_backup_message': '確定要將 {} 個檔案備份到 {} 嗎？',  # Are you sure you want to backup {} files to {}?
    'backup_complete_title': '✅ 備份完成',  # ✅ Backup Complete
    'backup_complete_message': '已成功複製 {} 個檔案到：\n{}',  # Successfully copied {} files to:\n{}
    'drive_disconnected': '⚠️ 備份中斷 - 磁碟機連接異常',  # ⚠️ Backup Interrupted - Drive Connection Issue
    'drive_disconnected_message': '備份過程中偵測到磁碟機連接問題：\n\n'
                                 '🔸 問題類型：{}\n'  # 🔸 Issue Type: {}
                                 '🔸 備份進度：{}/{} 個檔案 ({}%)\n'  # 🔸 Backup Progress: {}/{} files ({}%)
                                 '🔸 已成功備份：{} 個檔案\n'  # 🔸 Successfully backed up: {} files
                                 '🔸 剩餘檔案：{} 個檔案\n\n'  # 🔸 Remaining files: {} files
                                 '請檢查以下項目：\n'  # Please check the following:
                                 '• SD卡是否正確插入？\n'  # • Is the SD card properly inserted?
                                 '• 目標磁碟機是否正確連接？\n'  # • Is the target drive properly connected?
                                 '• USB線是否穩固？\n\n'  # • Is the USB cable secure?
                                 '建議重新連接磁碟機並重新開始備份程序，以確保所有檔案都能正確備份。',  # It is recommended to reconnect the drive and restart the backup process to ensure all files are properly backed up.
    
    # Error messages
    'insert_sd_first': '請先插入SD卡',  # Please insert SD card first
    'select_destination': '請選擇具有足夠空間的備份目標',  # Please select a backup destination with sufficient space
    'invalid_destination': '無效的目標位置',  # Invalid destination
    'cannot_backup_to_self': '無法將SD卡備份到自身！\n\n請選擇其他磁碟機作為備份目標。',  # Cannot backup SD card to itself!\n\nPlease select another drive as the backup destination.
    'insufficient_space': '所選磁碟機空間不足！\n\n'
                         '📊 所需空間：{:.2f} GB\n'  # 📊 Required space: {:.2f} GB
                         '💾 可用空間：{:.2f} GB\n'  # 💾 Available space: {:.2f} GB
                         '⚠️ 需要額外空間：{:.2f} GB\n\n'  # ⚠️ Additional space needed: {:.2f} GB
                         '請選擇具有足夠空間的其他磁碟機。',  # Please select another drive with sufficient space.
    'drive_disconnected': '磁碟機已斷開連接',  # Drive disconnected
    'backup_error': '備份過程中發生錯誤',  # Error occurred during backup
    
    # Status messages
    'scanning': '正在掃描...',  # Scanning...
    'backup_progress': '備份進度：{}/{} ({}%)',  # Backup Progress: {}/{} ({}%)
    'backup_progress_detailed': '進度: {}/{} ({}%) - 已複製: {}, 已跳過: {}',  # Progress: {}/{} ({}%) - Copied: {}, Skipped: {}
    'copying': '正在複製：{}',  # Copying: {}
    'skipping_duplicate': '跳過重複檔案：{}',  # Skipping duplicate: {}
    'backup_complete_with_skipped': '備份完成！已複製 {} 個檔案，跳過 {} 個重複檔案',  # Backup complete! Copied {} files, skipped {} duplicates
}