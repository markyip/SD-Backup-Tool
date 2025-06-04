# SD Card Backup Tool - README
# SD卡備份工具 - 說明文件

一個易於使用的工具，用於將SD卡中的檔案備份到本地磁碟機
### 功能特點

- 簡單直觀的使用者介面
- 視覺化磁碟機選擇，顯示空間資訊
- 檔案類型偵測（照片、影片、RAW檔案）
- 可自訂語言支援

### 支援的檔案格式

#### 照片格式
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- HEIC (.heic)
- WebP (.webp)
- TIFF (.tiff, .tif)

#### RAW檔案格式
- Canon (.cr2, .cr3, .crw)
- Nikon (.nef)
- Sony (.arw, .sr2)
- Olympus (.orf)
- Panasonic (.rw2)
- Adobe (.dng)
- Fujifilm (.raf)
- Pentax (.pef)
- Generic (.raw)

#### 影片格式
- MP4 (.mp4)
- QuickTime (.mov)
- AVI (.avi)
- Matroska (.mkv)
- AVCHD (.mts, .m2ts)
- Windows Media (.wmv)
- Flash Video (.flv)
- 3GP (.3gp)
- iTunes Video (.m4v)
- MPEG (.mpg, .mpeg)

### 系統需求

#### 使用執行檔
- Windows 7 或更新版本

#### 從原始碼建置/執行
- Windows 7 或更新版本
- Python 3.8 或更新版本
- 必要的Python套件（由建置腳本自動安裝）：
  - PyQt5
  - pywin32
  - Pillow
  - pyinstaller（用於建置）

### 安裝方式

#### 選項1：使用執行檔

1. 從發布頁面下載最新版本
2. 執行 `SD_Backup_Tool.exe`

#### 選項2：從原始碼建置

1. **複製儲存庫：**
   ```bash
   git clone <repository-url>
   cd sd_backup_tool
   ```

2. **建立虛擬環境：**
   ```bash
   python -m venv venv
   ```

3. **啟用虛擬環境：**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **安裝依賴項目：**
   ```bash
   pip install -r requirements.txt
   ```

5. **使用批次檔建置執行檔：**
   ```bash
   # Windows（推薦 - 自動處理所有步驟）
   build_sd_backup_tool.bat
   
   # 或手動使用Python
   python build_config/build.py
   ```

6. **執行檔將在 `dist` 資料夾中建立**

#### 選項3：開發模式執行

用於開發或測試而不建置執行檔：

1. **依照上述步驟1-4設定環境**

2. **直接使用Python執行：**
   ```bash
   python main.py
   ```

3. **或使用開發批次檔：**
   ```bash
   
   run_sd_backup_tool.bat
   
   
   
   ```

### 使用方式

1. 啟動應用程式
2. 插入SD卡（應用程式會自動偵測並開始掃描檔案）
3. 選擇目標磁碟機
4. 點擊「開始備份」以開始備份程序

### 自訂語言

應用程式使用單一語言檔案進行翻譯。要修改語言：

1. 開啟 `locales/translations.py`
2. 每個翻譯都有英文註解作為參考
3. 修改每個冒號（:）後的文字
4. 儲存檔案並重新建置應用程式

### 專案結構

```
sd_backup_tool/
├── assets/              # 應用程式資源（圖示等）
├── core/               # 核心功能模組
├── locales/            # 語言檔案
│   ├── translations.py # 主要翻譯檔案
│   └── __init__.py    # 語言管理器
├── ui/                 # 使用者介面模組
├── build.py           # 建置腳本
├── main.py            # 應用程式進入點
└── requirements.txt   # Python依賴項目
```

### 開發者

本專案由以下開發者共同開發：
- **Mark Yip** - 主要開發者
- **Roo** - 協同開發者

### 參與貢獻

1. 複製儲存庫
2. 建立功能分支
3. 進行修改
4. 提交拉取請求

### 授權條款

本專案採用 MIT 授權條款 - 詳見 LICENSE 檔案。

---

A user-friendly tool for backing up files from SD cards to local drives, with a focus on ease of use and reliability.

### Features

- Simple and intuitive user interface
- Visual drive selection with space information
- File type detection (photos, videos, RAW files)
- Customizable language support

### Supported File Formats

#### Photo Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- HEIC (.heic)
- WebP (.webp)
- TIFF (.tiff, .tif)

#### RAW File Formats
- Canon (.cr2, .cr3, .crw)
- Nikon (.nef)
- Sony (.arw, .sr2)
- Olympus (.orf)
- Panasonic (.rw2)
- Adobe (.dng)
- Fujifilm (.raf)
- Pentax (.pef)
- Generic (.raw)

#### Video Formats
- MP4 (.mp4)
- QuickTime (.mov)
- AVI (.avi)
- Matroska (.mkv)
- AVCHD (.mts, .m2ts)
- Windows Media (.wmv)
- Flash Video (.flv)
- 3GP (.3gp)
- iTunes Video (.m4v)
- MPEG (.mpg, .mpeg)

### Requirements

#### Using the Executable
- Windows 7 or later

#### Building/Running from Source
- Windows 7 or later
- Python 3.8 or later
- Required Python packages (automatically installed by build script):
  - PyQt5
  - pywin32
  - Pillow
  - pyinstaller (for building)

### Installation

#### Option 1: Using the Executable

1. Download the latest release from the releases page
2. Run `SD_Backup_Tool.exe`

#### Option 2: Building from Source

To build the executable from source, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sd_backup_tool
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Build the executable using the batch file:**
   ```bash
   # Windows (recommended - handles all steps automatically)
   build_sd_backup_tool.bat
   
   # Or manually using Python
   python build_config/build.py
   ```

6. **Run the executable:**
   - The executable will be located in the `dist` directory.
   - Run `dist/SD_Backup_Tool.exe` to start the application.

#### Option 3: Running in Development Mode

For development or testing without building:

1. **Follow steps 1-4 above to set up the environment**

2. **Run directly with Python:**
   ```bash
   python main.py
   ```

3. **Or use the development batch files:**
   ```bash
   
   run_sd_backup_tool.bat
   
   
   
   ```

### Usage

1. Launch the application
2. Insert your SD card (the application will automatically detect and scan files)
3. Select a destination drive
4. Click "Start Backup" to begin the backup process

### Customizing Language

The application uses a single language file for translations. To modify the language:

1. Open `locales/translations.py`
2. Each translation has an English comment for reference
3. Modify the text after the colon (:) in each line
4. Save the file and rebuild the application

### Project Structure

```
sd_backup_tool/
├── assets/              # Application assets (icons, etc.)
├── core/               # Core functionality modules
├── locales/            # Language files
│   ├── translations.py # Main translations file
│   └── __init__.py    # Language manager
├── ui/                 # User interface modules
├── build.py           # Build script
├── main.py            # Application entry point
└── requirements.txt   # Python dependencies
```

### Developers

This project was developed by:
- **Mark Yip** - Lead Developer
- **Roo** - Co-Developer

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### License

This project is licensed under the MIT License - see the LICENSE file for details.
