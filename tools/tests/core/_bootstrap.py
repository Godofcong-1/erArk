# -*- coding: UTF-8 -*-
"""基础系统回归测试的公共引导

通用部分（初始化链、绘制屏蔽、断言工具、角色 fixture、环境工具、玩家 `pl`）全部来自上一级的
tools/tests/headless_base.py；基础系统套件暂无专属工具，各测试文件按需自行导入要测的模块。
每个 test_*.py 开头 `from _bootstrap import *` 即可。

铁律（详见 .github/skills/headless-game-test/SKILL.md）：
    1. 必须用 ./.conda/python.exe 跑，裸 python 是商店空壳
    2. 导入链会起非守护线程，脚本末尾必须 finish() → os._exit()
    3. 含中文的脚本一律写成文件跑，不要走 heredoc / stdin（GBK 会把中文喂坏）
    4. 只读：绝不调用 save_handle.establish_save()，不 inline 调用 init_character_behavior()
"""
import os
import sys

# 先把 tools/tests 加进 sys.path，才能导入各套件共用的 headless_base
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from headless_base import *  # noqa: F401,F403,E402

# `from _bootstrap import *` 默认不导出下划线开头的名字，而翻译函数 `_` 正是测试里最常用的一个
__all__ = [_name for _name in list(globals()) if not _name.startswith("__")]
