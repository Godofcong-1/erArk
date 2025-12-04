# 用于解决 Script.System 及其子模块的隐藏导入问题

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('Script.System')
hiddenimports += collect_submodules('Script.System.Medical')
