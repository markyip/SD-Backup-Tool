# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Development\\sd_backup_tool\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('../assets', 'assets')],
    hiddenimports=['win32timezone', 'PyQt5.sip', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='相片影片備份工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['..\\assets\\icon.ico'],
)
