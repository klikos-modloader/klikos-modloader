# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["C:\\Projects\\ROBLOX\\Kliko's modloader - dev\\v1.8.0 - Copy\\build\\temp\\source\\main.py"],
    pathex=["C:\\Projects\\ROBLOX\\Kliko's modloader - dev\\v1.8.0 - Copy\\build\\temp\\source\\libraries"],
    binaries=[],
    datas=[("C:\\Projects\\ROBLOX\\Kliko's modloader - dev\\v1.8.0 - Copy\\build\\temp\\source\\modules", 'modules'), ("C:\\Projects\\ROBLOX\\Kliko's modloader - dev\\v1.8.0 - Copy\\build\\temp\\source\\config", 'config')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    "C:\\Projects\\ROBLOX\\Kliko's modloader - dev\\v1.8.0 - Copy\\build\\splash.png",
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name="Kliko's modloader.exe",
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
    icon=["C:\\Projects\\ROBLOX\\Kliko's modloader - dev\\v1.8.0 - Copy\\build\\favicon.ico"],
)
