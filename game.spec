# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# SPECPATH 是 PyInstaller 提供的内置变量，指向 spec 文件所在目录
# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(SPECPATH))

# 将项目根目录添加到 sys.path，确保模块可被分析
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 显式列出 Script.System.Medical 的所有模块
# 不使用 collect_submodules 因为它会在分析时尝试导入模块，触发未初始化的配置错误
hiddenimports = [
    'engineio.async_drivers.threading',
    'Script.System',
    'Script.System.Medical',
    'Script.System.Medical.medical_constant',
    'Script.System.Medical.medical_core',
    'Script.System.Medical.log_system',
    'Script.System.Medical.medical_service',
    'Script.System.Medical.clinic_patient_management',
    'Script.System.Medical.clinic_doctor_service',
    'Script.System.Medical.hospital_patient_management',
    'Script.System.Medical.hospital_doctor_service',
    'Script.System.Medical.medical_department_panel',
    'Script.System.Medical.medical_player_diagnose_function',
    'Script.System.Medical.medical_player_diagnose_panel',
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
