# -*- coding: UTF-8 -*-
"""生长养成系统回归测试的公共引导（Plan 22 收尾轮）

每个 test_*.py 开头 `from _bootstrap import *` 即可拿到：
    已初始化的游戏配置与缓存（不启动 Tk / Web）、被屏蔽并可记录文本的绘制类、
    check() / section() / finish() 三个断言工具、make_character() 角色 fixture 工厂、
    set_time() / move_to() / open_all_classroom() / clear_schedules() 等环境工具。

⚠️ 铁律（详见 .claude/skills/headless-game-test/SKILL.md）：
    1. 必须用 ./.conda/python.exe 跑，裸 python 是商店空壳
    2. 导入链会起非守护线程，脚本末尾必须 finish() → os._exit()
    3. 含中文的脚本一律写成文件跑，不要走 heredoc / stdin（GBK 会把中文喂坏）
    4. 只读：绝不调用 save_handle.establish_save()，不 inline 调用 init_character_behavior()
"""
import datetime
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PASS = 0
""" 已通过的断言数 """
FAIL = []
""" 失败的断言名列表 """


def check(name: str, cond, extra="") -> bool:
    """
    记录一条断言结果
    Keyword arguments:
    name -- 断言名
    cond -- 断言条件
    extra -- 失败时附带打印的实际值
    Return arguments:
    bool -- 断言是否通过
    """
    global PASS
    if cond:
        PASS += 1
        print(f"  [OK] {name}")
        return True
    FAIL.append(name)
    print(f"  [FAIL] {name} {extra}")
    return False


def section(title: str):
    """
    打印一个分节标题
    Keyword arguments:
    title -- 标题
    Return arguments:
    无
    """
    print(f"\n==== {title} ====")


def finish():
    """
    打印汇总并强制退出进程（导入链里的非守护线程会让进程不自行结束）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    print()
    print("=" * 50)
    print(f"PASS={PASS} FAIL={len(FAIL)}")
    for name in FAIL:
        print("  -", name)
    sys.stdout.flush()
    os._exit(0 if not FAIL else 1)


# ==== 1. 初始化链（照 game.py 的顺序，顺序不能乱） ====
import auto_build_config  # noqa: F401,E402  增量构建游戏数据
from Script.Config import normal_config  # noqa: E402
from Script.Core import game_type, cache_control  # noqa: E402

cache_control.cache = game_type.Cache()  # 必须在 game_config.init() 之前
normal_config.init_normal_config()
from Script.Config import game_config, character_config  # noqa: E402

game_config.init()
character_config.init_character_tem_data()
from Script.Config import map_config  # noqa: E402

map_config.init_map_data()
from Script.Design import (  # noqa: E402
    attr_calculation,
    character_handle,
    game_time,
    handle_premise,
    map_handle,
    settle_behavior,
)
import Script.Settle  # noqa: F401,E402  注册全部结算器
import Script.StateMachine  # noqa: F401,E402  注册全部状态机
from Script.Core import constant, constant_effect, constant_promise, flow_handle, get_text, save_handle  # noqa: F401,E402
from Script.UI.Moudle import draw  # noqa: E402

_ = get_text._
""" 翻译api：配置里的名字都过了翻译，测试里比对名字一律包 _() """

character_handle.init_character_tem()
game_time.init_time()
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

# ==== 2. 全局前置 ====
cache.all_system_setting = attr_calculation.get_system_setting_zero()
# 罗德岛设施：全部设施 Lv1，教育区另由测试按需调；facility_open 默认空（只开放三间基础教室）
for _facility_cid in game_config.config_facility:
    cache.rhodes_island.facility_level.setdefault(_facility_cid, 1)

# ==== 3. 屏蔽 UI，并把绘制文本收进 drawn_text ====
drawn_text = []
""" 全部绘制类 draw() 时的文本记录，断言「某段提示是否被画出」时用；测试可自行 clear() """


def _record_draw(self, *args, **kwargs):
    """
    记录型绘制桩
    Keyword arguments:
    self -- 绘制对象
    Return arguments:
    无
    """
    # 标题线类（TitleLineDraw / LittleTitleLineDraw）的文字在 title 属性上
    text = getattr(self, "text", None) or getattr(self, "title", None)
    if text:
        drawn_text.append(str(text))


for _cls_name in dir(draw):
    _cls = getattr(draw, _cls_name)
    if isinstance(_cls, type) and hasattr(_cls, "draw"):
        try:
            _cls.draw = _record_draw
        except Exception:
            pass
# askfor_all 默认返回第一个可选项，面板的按钮循环才退得出去；测试可自行替换
flow_handle.askfor_all = lambda return_list, *a, **k: return_list[0] if return_list else ""
flow_handle.askfor_wait = lambda *a, **k: None

from Script.System.Education_System import (  # noqa: E402
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

# ==== 4. 环境工具 ====
DEFAULT_TIME = datetime.datetime(2026, 9, 7, 9, 0)
""" 默认游戏时间：2026-09-07 周一 09:00，秋季学期（9月）第一节课的开始时刻 """
SCENE_DORM = ["宿舍", "1区", "101"]
""" 一间真实宿舍 """
SCENE_EDU_ENTRY = ["教", "0"]
""" 教育区入口 """
SCENE_NURSERY = ["教", "育儿室"]
""" 育儿室 """
assert map_handle.get_map_system_path_str_for_list(SCENE_DORM) in cache.scene_data
assert map_handle.get_map_system_path_str_for_list(SCENE_EDU_ENTRY) in cache.scene_data


def scene_str(path: list) -> str:
    """
    场景路径列表 → 场景路径字符串
    Keyword arguments:
    path -- 场景路径列表
    Return arguments:
    str -- 场景路径字符串
    """
    return map_handle.get_map_system_path_str_for_list(path)


def _scene_list_add(scene_path_str: str, character_id: int):
    """
    把角色登记进场景的角色名单（兼容 set 与 list 两种容器）
    """
    if scene_path_str not in cache.scene_data:
        return
    char_list = cache.scene_data[scene_path_str].character_list
    if isinstance(char_list, set):
        char_list.add(character_id)
    elif character_id not in char_list:
        char_list.append(character_id)


def _scene_list_remove(scene_path_str: str, character_id: int):
    """
    把角色从场景的角色名单里移除
    """
    if scene_path_str not in cache.scene_data:
        return
    char_list = cache.scene_data[scene_path_str].character_list
    if isinstance(char_list, set):
        char_list.discard(character_id)
    elif character_id in char_list:
        char_list.remove(character_id)


def move_to(character_id: int, path: list):
    """
    把角色直接放到某个场景（同步 position 与两边的场景名单，不走寻路）
    Keyword arguments:
    character_id -- 角色id
    path -- 目标场景路径列表
    Return arguments:
    无
    """
    character_data: game_type.Character = cache.character_data[character_id]
    _scene_list_remove(scene_str(character_data.position), character_id)
    character_data.position = list(path)
    _scene_list_add(scene_str(path), character_id)


def set_time(now_time: datetime.datetime):
    """
    设置游戏时间，并把全部角色的行为起始时间同步过去
    ⚠️ get_class_period 等函数读的是 behavior.start_time（默认是公元1年），不同步会永远算成不在节次内
    Keyword arguments:
    now_time -- 新的游戏时间
    Return arguments:
    无
    """
    cache.game_time = now_time
    for character_data in cache.character_data.values():
        character_data.behavior.start_time = now_time


def make_character(cid: int, name: str, work_type: int = 0, daughter: bool = False, stage: int = 0,
                   mother_id: int = -1, position=None, born_days: int = 30) -> game_type.Character:
    """
    造一个能跑通结算 / 前提 / 面板链路的最小角色 fixture，并登记进 cache
    Keyword arguments:
    cid -- 角色id（0 为玩家）
    name -- 角色名
    work_type -- 岗位id（151 教师 / 152 学生 / 153 保育员）
    daughter -- 是否为玩家的女儿（father_id = 0）
    stage -- 成长阶段素质id（101 婴儿 / 102 幼女 / 103 萝莉 / 104 少女），0 为成年干员
    mother_id -- 母亲的角色id
    position -- 初始场景路径，默认宿舍
    born_days -- 出生距今的日历天数（成长天数用）
    Return arguments:
    game_type.Character -- 角色对象
    """
    cd = game_type.Character()
    cd.cid = cid
    cd.name = name
    cd.adv = 0
    cd.sex = 1
    cd.race = 0
    cd.cloth = attr_calculation.get_cloth_zero()
    cd.cloth.cloth_locker_in_dormitory = attr_calculation.get_cloth_locker_in_dormitory_zero()
    cd.cloth.cloth_locker_in_shower = attr_calculation.get_shower_cloth_locker_zero()
    cd.dirty = attr_calculation.get_zero_dirty()
    cd.talent = attr_calculation.get_talent_zero({})
    cd.ability = attr_calculation.get_ability_zero({})
    cd.status_data = attr_calculation.get_status_zero({})
    cd.juel = attr_calculation.get_juel_zero({})
    cd.experience = attr_calculation.get_experience_zero({})
    cd.second_behavior = attr_calculation.get_second_behavior_zero({})
    cd.h_state = attr_calculation.get_h_state_reset(cd.h_state)
    cd.body_manage = attr_calculation.get_body_manage_zero()
    cd.favorability = {0: 0}
    cd.social_contact = {}
    cd.social_contact_data = {}
    cd.assistant_services = attr_calculation.get_assistant_services_zero()  # 实行值计算会读助理服务[8]
    cd.talent[121] = 1
    cd.hit_point_max = 100
    cd.hit_point = 100
    cd.mana_point_max = 100
    cd.mana_point = 100
    cd.work.work_type = work_type
    cd.dormitory = scene_str(SCENE_DORM)
    cd.behavior.start_time = cache.game_time
    if stage:
        cd.talent[stage] = 1
        if stage != 104:
            cd.talent[7] = 1  # 未成年
    if daughter:
        cd.relationship.father_id = 0
        cd.relationship.mother_id = mother_id
        cd.pregnancy.born_time = cache.game_time - datetime.timedelta(days=born_days)
        if mother_id in cache.character_data:
            mother_data = cache.character_data[mother_id]
            if cid not in mother_data.relationship.child_id_list:
                mother_data.relationship.child_id_list.append(cid)
    cd.position = list(position if position is not None else SCENE_DORM)
    cache.character_data[cid] = cd
    if cid:
        cache.npc_id_got.add(cid)
    _scene_list_add(scene_str(cd.position), cid)
    return cd


def remove_character(cid: int):
    """
    把一个 fixture 角色从缓存里撤掉
    Keyword arguments:
    cid -- 角色id
    Return arguments:
    无
    """
    if cid in cache.character_data:
        _scene_list_remove(scene_str(cache.character_data[cid].position), cid)
        del cache.character_data[cid]
    cache.npc_id_got.discard(cid)


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
        day = DEFAULT_TIME.date()
    hour, minute = game_time.CLASS_PERIOD_START[period]
    return datetime.datetime(day.year, day.month, day.day, hour, minute)


set_time(DEFAULT_TIME)
pl = make_character(0, "博士")
""" 玩家 """


def _exit_on_exception(exc_type, exc_value, exc_traceback):
    """
    未捕获异常时打印回溯并强制退出
    ⚠️ 导入链起的非守护线程会让崩溃的测试进程挂住，直到 run_all 的超时才被杀掉
    """
    import traceback

    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("\nPASS={0} FAIL={1} (crashed)".format(PASS, len(FAIL) + 1))
    sys.stdout.flush()
    os._exit(2)


sys.excepthook = _exit_on_exception

# ⚠️ `from _bootstrap import *` 默认不导出下划线开头的名字，而翻译函数 `_` 正是测试里最常用的一个
__all__ = [_name for _name in list(globals()) if not _name.startswith("__")]
