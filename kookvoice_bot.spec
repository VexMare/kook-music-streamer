# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['kookvoice_bot.py'],
    pathex=[],
    binaries=[],
    datas=[('ffmpeg/bin', 'ffmpeg/bin'), ('config.py', '.'), ('kookvoice', './kookvoice')],
    hiddenimports=['kookvoice.kookvoice', 'kookvoice.requestor'],
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
    [],
    exclude_binaries=True,
    name='kookvoice_bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['myicon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='kookvoice_bot',
)
