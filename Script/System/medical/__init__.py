"""Medical subsystem package - 医疗系统子模块

注意：此文件故意保持为空/最小化，以避免 PyInstaller 打包时的循环导入问题。
具体的模块导入在 game.py 中通过显式 import 语句完成。
"""
# 不在这里导入任何子模块，让 PyInstaller 能够正确分析
# 子模块会通过 game.py 中的显式导入或 hiddenimports 被包含
