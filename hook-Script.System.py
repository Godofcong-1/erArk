# PyInstaller hook for Script.System package
# This hook ensures all Script.System submodules are collected

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('Script.System')
