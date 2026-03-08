# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Desktop\\Desktop\\proyects\\Stark\\build_temp\\Stark-Link.py'],
    pathex=['C:\\Users\\Desktop\\Desktop\\proyects\\Stark\\build_temp'],
    binaries=[],
    datas=[('C:\\Users\\Desktop\\Desktop\\proyects\\Stark\\build_temp\\system', 'system'), ('C:\\Users\\Desktop\\Desktop\\proyects\\Stark\\build_temp\\shared', 'shared')],
    hiddenimports=['configurations', 'datapackage', 'datavalue', 'importlib', 'inspect', 'platform', 'queue', 'random', 'shutil', 'socket', 'subprocess', 'threading', 'traceback', 'uuid', 'windows', 'winreg'],
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
    name='Stark-Link',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
