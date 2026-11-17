# -*- coding: UTF-8 -*-
"""生长养成系统回归测试的公共引导（Plan 22 收尾轮）

通用部分（初始化链、绘制屏蔽、断言工具、角色 fixture、环境工具、玩家 `pl`）在上一级的
tools/tests/headless_base.py，本文件只补养成系统专属的导入与工具。
每个 test_*.py 开头 `from _bootstrap import *` 即可拿到：
    已初始化的游戏配置与缓存（不启动 Tk / Web）、被屏蔽并可记录文本的绘制类、
    check() / section() / finish() 三个断言工具、make_character() 角色 fixture 工厂、
    set_time() / move_to() / open_all_classroom() / clear_schedules() 等环境工具。

铁律（详见 .github/skills/headless-game-test/SKILL.md）：
    1. 必须用 ./.conda/python.exe 跑，裸 python 是商店空壳
    2. 导入链会起非守护线程，脚本末尾必须 finish() → os._exit()
    3. 含中文的脚本一律写成文件跑，不要走 heredoc / stdin（GBK 会把中文喂坏）
    4. 只读：绝不调用 save_handle.establish_save()，不 inline 调用 init_character_behavior()
"""
import datetime
import os
import sys

# 先把 tools/tests 加进 sys.path，才能导入各套件共用的 headless_base
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from headless_base import *  # noqa: F401,F403,E402
from headless_base import cache, game_config, game_time, map_handle  # noqa: E402

from Script.System.Education_System import (  # noqa: E402,F401
    auto_schedule,
    baby_growth_handle,
    class_ai,
    education_constant,
    growth_event_handle,
    growth_handle,
    schedule_handle,
    schedule_template_handle,
    semester_handle,
    sex_class_handle,
)

# ==== 养成系统专属的环境工具 ====
SCENE_EDU_ENTRY = ["教", "0"]
""" 教育区入口 """
SCENE_NURSERY = ["教", "育儿"]
""" 育儿室 """
assert map_handle.get_map_system_path_str_for_list(SCENE_EDU_ENTRY) in cache.scene_data


def open_all_classroom():
    """
    把 Facility_open.csv 里的全部房间置为已开放（10 间教室全开）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    for open_cid in game_config.config_facility_open:
        cache.rhodes_island.facility_open[open_cid] = True


def clear_schedules():
    """
    清空课表、临时实操课、日程模板与公务事件队列，供各组用例之间隔离
    Keyword arguments:
    无
    Return arguments:
    无
    """
    cache.rhodes_island.class_schedule = {}
    cache.rhodes_island.temp_sex_class = {}
    cache.rhodes_island.child_schedule_template = {}
    cache.rhodes_island.official_event_queue = []
    cache.rhodes_island.official_event_history = {}
    cache.sex_class_mode = False
    cache.group_sex_mode = False


def classroom_path(classroom: str) -> list:
    """
    教室场景名 → 场景路径
    Keyword arguments:
    classroom -- 教室场景名
    Return arguments:
    list -- 场景路径
    """
    return schedule_handle.get_classroom_position(classroom)


def period_time(period: int, day: datetime.date = None) -> datetime.datetime:
    """
    取某天某节次的开始时刻
    Keyword arguments:
    period -- 节次0~8
    day -- 日期，默认 DEFAULT_TIME 那天
    Return arguments:
    datetime.datetime -- 开始时刻
    """
    if day is None:
        day = DEFAULT_TIME.date()  # noqa: F405
    hour, minute = game_time.CLASS_PERIOD_START[period]
    return datetime.datetime(day.year, day.month, day.day, hour, minute)


# `from _bootstrap import *` 默认不导出下划线开头的名字，而翻译函数 `_` 正是测试里最常用的一个
__all__ = [_name for _name in list(globals()) if not _name.startswith("__")]
