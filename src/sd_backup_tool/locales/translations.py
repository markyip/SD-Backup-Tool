# -*- coding: utf-8 -*-
"""
Language translations file for SD Backup Tool
Each translation includes an English comment for reference
To change the language, modify the text after the colon (:) in each line
"""

UI_TEXT = {
    # Main window
    'window_title': '相片影片備份工具',  # Photo & Video Backup Tool (Updated comment)
    'sd_card_status': '來源裝置狀態',  # Source Device Status (Updated comment)
    'backup_destination': '備份目的地',  # Backup Destination
    'file_scan': '檔案掃描結果',  # File Scan Results (Updated comment)
    # 'backup_progress': '備份進度',  # Backup Progress (Superseded by backup_progress_detailed)
    
    # File types
    'photos': '相片: {}',  # Photos: {} (Generalised)
    'videos': '影片: {}',  # Videos: {} (Generalised)
    'raw_files': 'RAW檔案: {}',  # RAW Files: {} (Generalised)
    'total_size': '總大小: {}',  # Total Size: {}
    
    # Buttons
    'refresh': '重新整理',  # Refresh
    # 'start_scan': '開始掃描',  # Start Scan (Scanning is automatic on device detection in new UI)
    'start_backup': '開始備份',  # Start Backup
    'scan_device': '掃描裝置',  # Scan Device
    'backing_up': '備份中...',  # Backing up...
    'select': '選擇',  # Select
    'selected': '已選擇',  # Selected
    'confirm': '確認',  # Confirm
    'cancel': '取消',  # Cancel
    'ok': '確定',  # OK
    'open_folder': '開啟資料夾',  # Open Folder
    'restart': '立即重試',  # Retry Now (Updated from 重新掃描)
    'handle_later': '稍後再說',  # Dismiss (Updated from 稍後處理)
    
    # Messages (Status messages are now grouped below)
    'searching_sd': '正在搜尋裝置...',  # Searching for device... (Updated from SD卡...)
    'refreshing_devices': '正在重新整理裝置清單...',  # Refreshing device list...
    # 'sd_detected': '已偵測到SD卡: {}',  # SD card detected: {} (Superseded by device_detected)
    # 'sd_removed': 'SD卡已移除',  # SD card removed (Superseded by device_removed_status)
    # 'scan_complete': '掃描完成',  # Scan complete (Superseded by scan_complete_on_device_status)
    # 'backup_complete': '備份完成！已複製 {} 個檔案',  # Backup complete! Copied {} files (Superseded by backup_complete_status/skipped_status)
    # 'backup_interrupted': '備份中斷 - 磁碟機已斷開連接',  # Backup interrupted - Drive disconnected (More specific messages exist)
    # 'backup_failed': '備份失敗',  # Backup failed (More specific messages exist)
    'total_space': '總空間: {}GB',  # Total space: {}GB (Used by Drive Tile)
    'used_space': '已使用: {}GB',  # Used space: {}GB (Used by Drive Tile)
    'free_space': '可用空間: {}GB',  # Free space: {}GB (Used by Drive Tile)
    'select_destination': '選擇備份目標',  # Select backup destination (Used in UI)
    
    # Dialogs (Titles and messages are now grouped below more clearly)
    'warning_title': '警告',  # Warning
    'error_title': '錯誤',  # Error (Generic error dialog title)
    'confirm_backup_title': '確認備份',  # Confirm Backup (Used as Dialog Title)
    'confirm_backup_message': '確定要將 {} 個檔案備份到 {} 嗎？',  # Are you sure you want to backup {} files to {}?
    'backup_complete_title': '✅ 備份完成',  # ✅ Backup Complete (Used as Dialog Title)
    # 'backup_complete_message': '已成功複製 {} 個檔案到：\n{}',  # Successfully copied {} files to:\n{} (Superseded by backup_summary_message/skipped_message)
    # 'drive_disconnected': '⚠️ 備份中斷 - 磁碟機連接異常',  # ⚠️ Backup Interrupted - Drive Connection Issue (Superseded by drive_disconnected_title/message)
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
    'insert_sd_first': '請連接裝置並確保其已被偵測後再掃描。',  # Please connect a device and ensure it's detected before scanning.
    'scan_error_message': '掃描裝置時發生錯誤: {}',  # An error occurred while scanning the device: {}
    'device_id_missing_for_scan': '裝置資訊不完整，無法開始掃描。', # Device information is incomplete. Cannot start scan.
    'select_destination_message': '請選擇一個備份目標磁碟機。', # Please select a backup destination drive.
    'invalid_destination_title': '無效的目的地', # Invalid Destination (Title for invalid destination dialog)
    'cannot_backup_to_self_message': '無法將來源裝置備份到其自身。', # Cannot backup the source device to itself.
    'insufficient_space_title': '空間不足', # Insufficient Space (Title for insufficient space dialog)
    'insufficient_space_message': '{} 上空間不足。\n需要 {:.1f} GB，但僅有 {:.1f} GB 可用。\n請釋放 {:.1f} GB 或選擇其他磁碟機。', # Not enough space on {}.\nRequires {:.1f} GB, but only {:.1f} GB available.\nPlease free up {:.1f} GB or choose another drive.
    'insufficient_space_unknown_drive_message': "無法驗證 {} 上的空間。空間可能已滿或無法存取。", # Could not verify space on {}. It might be too full or inaccessible.
    # 'select_destination': '請選擇具有足夠空間的備份目標',  # Please select a backup destination with sufficient space (This was a duplicate/older version)
    # 'invalid_destination': '無效的目標位置',  # Invalid destination (Superseded by invalid_destination_title)
    # 'cannot_backup_to_self': '無法將SD卡備份到自身！\n\n請選擇其他磁碟機作為備份目標。',  # Cannot backup SD card to itself! (Superseded by cannot_backup_to_self_message)
    # 'insufficient_space': '所選磁碟機空間不足！\n\n' # (Superseded by insufficient_space_title and insufficient_space_message)
    #                      '📊 所需空間：{:.2f} GB\n'
    #                      '💾 可用空間：{:.2f} GB\n'
    #                      '⚠️ 需要額外空間：{:.2f} GB\n\n'
    #                      '請選擇具有足夠空間的其他磁碟機。',
    # 'drive_disconnected': '磁碟機已斷開連接',  # Drive disconnected (Superseded by drive_disconnected_title/message)
    # 'backup_error': '備份過程中發生錯誤',  # Error occurred during backup (Generic, error_title is used for dialogs)
    
    # Status messages (Consolidated and reviewed)
    'device_detected': '已偵測到裝置: {}',  # Device Detected: {}
    'device_ready': '已準備好裝置: {name} ({path})', # Device ready: {name} ({path})
    'device_ready_simple': '已準備好裝置: {name}', # Device ready (Simple): {name}
    'device_removed_status': '裝置 {} 已移除。',  # Device {} has been removed.
    'scanning_device': '正在掃描 {}...',  # Scanning {}...
    'scan_error_status': '掃描 {} 時發生錯誤: {}',  # Scan Error on {}: {}
    'scan_complete_on_device_status': '{} 掃描完成。',  # Scan complete for {}.
    'no_media_found_on_device_status': '掃描完成。在 {} 上找不到任何媒體檔案。',  # Scan complete. No media files found on {}.
    'scan_failed_status': '掃描失敗或找不到任何媒體檔案。', # Scan failed or no media files found.
    'backup_complete_status': '備份完成！已複製 {} 個檔案。',  # Backup complete! {} files copied.
    'backup_complete_skipped_status': '備份完成！已複製 {} 個檔案，已跳過 {} 個重複檔案。',  # Backup complete! {} files copied, {} duplicates skipped.
    'copying_file': '正在複製: {}', # Copying: {}
    'skipping_file': '跳過重複檔案: {}', # Skipping duplicate: {}
    'backup_interrupted': '備份已中斷。',  # Backup interrupted.
    'backup_failed': '備份失敗。',  # Backup failed.
    'destination_selected': '目的地已選擇: {}', # Destination selected: {} (Status label)
    'scanning': '正在掃描裝置...',  # Scanning device... (More specific than just 'Scanning...')
    # 'backup_progress': '備份進度：{}/{} ({}%)',  # Backup Progress: {}/{} ({}%) (Superseded by backup_progress_detailed)
    'backup_progress_detailed': '進度: {}/{} ({}%) - 已複製: {}, 已跳過: {}',  # Progress: {}/{} ({}%) - Copied: {}, Skipped: {}
    # Commented out lines for 'copying', 'skipping_duplicate', 'backup_complete_with_skipped' are fine as they denote replacements.

    # Dialog Titles (Consolidated and reviewed)
    'scan_error_title': '掃描錯誤', # Scan Error
    'select_destination_title': '選擇目的地', # Select Destination
    'mtp_backup_complete_title': '備份完成', # MTP Backup Complete Title
    'device_ejected_title': '✅ {} 已安全退出', # ✅ {} Safely Ejected
    'eject_failed_title': '⚠️ 無法退出 {}', # ⚠️ Could Not Eject {}
    'drive_disconnected_title': '磁碟機已中斷連線', # Drive Disconnected Title from main_window
    'no_destination_space_title': '⚠️ 沒有足夠空間的磁碟機', # No Drives with Enough Space
    'no_destination_space_message': '找不到可容納 {:.1f} GB 備份資料的磁碟機。\n請連接其他硬碟或釋放空間後再試。', # No drive found to hold ... GB...
    'select_source_folder': '選擇來源資料夾', # Select source folder
    'start_mtp_scan': '開始 MTP 掃描', # Start MTP Scan
    'mtp_ready': 'MTP 裝置 {} 已就緒', # MTP Device {} ready
    'select_source': '選擇來源裝置', # Select Source Device

    # Dialog Messages (New Section for clarity)
    'backup_summary_message': '備份任務已完成！\n\n已成功複製 {} 個檔案。\n\n目標位置: {}',
    'backup_summary_skipped_message': '備份任務已完成！\n\n已成功複製 {} 個新檔案。\n已跳過 {} 個已存在的重複檔案。\n總計處理 {} 個檔案。\n\n目標位置: {}',
    'mtp_can_disconnect_message': '{} 的備份已完成。\n您現在可以安全地中斷裝置連線。',
    'can_remove_device_message': '您現在可以安全地移除 {}。',
    'eject_failed_message': '無法自動退出 {}。\n請手動移除。\n錯誤: {}',
}