# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# SPECPATH 是 PyInstaller 提供的内置变量，指向 spec 文件所在目录
# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(SPECPATH))

# 将项目根目录添加到 sys.path，确保模块可被分析
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# hiddenimports - 仅包含第三方库的隐藏依赖
# Script.System.Medical 子模块已在 game.py 中显式导入，PyInstaller 会自动分析
hiddenimports = [
    'engineio.async_drivers.threading',
]

a = Analysis(
    ['game.py'],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=['.'],
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
    name='game',
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
    icon=['image\\logo.png'],
)
