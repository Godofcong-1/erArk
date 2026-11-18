# -*- coding: UTF-8 -*-
"""全部无头回归测试套件共用的引导（不启动 Tk / Web）

各套件目录下的 `_bootstrap.py` 先把本目录（tools/tests）加进 sys.path，再 `from headless_base import *`，
然后补上本套件专属的导入与工具。测试文件开头统一写 `from _bootstrap import *` 即可拿到：
    已初始化的游戏配置与缓存、被屏蔽并可记录文本的绘制类（drawn_text）、
    check() / section() / finish() 三个断言工具、make_character() 角色 fixture 工厂、
    scene_str() / move_to() / set_time() / remove_character() 等环境工具，以及玩家 fixture `pl`。

铁律（详见 .github/skills/headless-game-test/SKILL.md）：
    1. 必须用 ./.conda/python.exe 跑，裸 python 是商店空壳
    2. 导入链会起非守护线程，脚本末尾必须 finish() → os._exit()
    3. 含中文的脚本一律写成文件跑，不要走 heredoc / stdin（GBK 会把中文喂坏）
    4. 只读：绝不调用 save_handle.establish_save()，不 inline 调用 init_character_behavior()
"""
import datetime
import os
import random  # noqa: F401  供测试 `from _bootstrap import *` 后直接用
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
""" 仓库根目录 """
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PASS = 0
""" 已通过的断言数 """
FAIL = []
""" 失败的断言名列表 """
KNOWN = []
""" 仍然存在的已知问题名列表（不算失败） """


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


def known_issue(name: str, cond, note: str = "", extra="") -> bool:
    """
    记录一条已知、暂不修的问题：写法与 check 相同，cond 写的是「问题修好后应当成立」的条件
    问题仍在（cond 不成立）时记为 [KNOWN]、不算失败，CI 照常通过；问题已经不在时按通过计，并提示把它改回 check
    只用于已确认是 BUG、但修法要由维护者拍板的情形，note 写明问题所在与待定的点
    Keyword arguments:
    name -- 断言名
    cond -- 问题修好后应当成立的条件
    note -- 问题说明
    extra -- 附带打印的实际值
    Return arguments:
    bool -- 条件是否成立
    """
    global PASS
    if cond:
        PASS += 1
        print(f"  [OK] {name}（已知问题已不再出现，把这条 known_issue 改回 check）")
        return True
    KNOWN.append(name)
    print(f"  [KNOWN] {name} —— {note} {extra}")
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
    print(f"PASS={PASS} FAIL={len(FAIL)} KNOWN={len(KNOWN)}")
    for name in FAIL:
        print("  -", name)
    for name in KNOWN:
        print("  ~", name)
    sys.stdout.flush()
    remove_test_map_cache()
    os._exit(0 if not FAIL else 1)


def remove_test_map_cache():
    """
    删掉指定语言启动时建在临时目录里的地图预处理文件（没有指定语言时什么都不做）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    cache_dir = globals().get("_TEST_MAP_CACHE_DIR", "")
    if cache_dir and os.path.isdir(cache_dir):
        import shutil

        shutil.rmtree(cache_dir, ignore_errors=True)


# ==== 1. 初始化链（照 game.py 的顺序，顺序不能乱） ====
import auto_build_config  # noqa: F401,E402  增量构建游戏数据
from Script.Config import normal_config  # noqa: E402
from Script.Core import game_type, cache_control  # noqa: E402

cache_control.cache = game_type.Cache()  # 必须在 game_config.init() 之前
normal_config.init_normal_config()
TEST_LANGUAGE = os.environ.get("ERARK_TEST_LANGUAGE", "")
""" 让本进程的游戏在指定语言下启动（en_US / ko_KR），空串表示照 config.ini。
    测试文件在 `from _bootstrap import *` 之前写 `os.environ["ERARK_TEST_LANGUAGE"] = "en_US"`；
    必须在导入 get_text 之前生效（它在导入时就按这个语言建好翻译链，配置表的名字随后在载入时被翻译） """
if TEST_LANGUAGE:
    normal_config.config_normal.language = TEST_LANGUAGE
from Script.Config import game_config, character_config  # noqa: E402

game_config.init()
character_config.init_character_tem_data()
from Script.Config import map_config  # noqa: E402

_TEST_MAP_CACHE_DIR = ""
""" 指定语言启动时地图预处理文件所在的临时目录，进程结束前删掉 """
if TEST_LANGUAGE:
    # 地图预处理文件（场景名、地图名）是按构建时的语言翻译好再存盘的：换语言启动时改到临时目录里重建，
    #    既能得到这种语言下真实的场景数据，也不会改写仓库 data/ 下按当前语言建好的那几份
    import tempfile  # noqa: E402
    from Script.Design import map_handle as _map_handle_for_cache  # noqa: E402

    _TEST_MAP_CACHE_DIR = tempfile.mkdtemp(prefix="erArk_test_map_")
    for _path_name in ("scene_path_edge_path", "all_scene_data_path", "all_place_data_path", "all_map_data_path"):
        setattr(map_config, _path_name, os.path.join(_TEST_MAP_CACHE_DIR, os.path.basename(getattr(map_config, _path_name))))
    _map_handle_for_cache.scene_path_edge_path = map_config.scene_path_edge_path
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
# 罗德岛设施：全部设施 Lv1；facility_open 默认空
for _facility_cid in game_config.config_facility:
    cache.rhodes_island.facility_level.setdefault(_facility_cid, 1)
# 书库：全部书籍在架、没被借走（与 basement 初始化一致）
for _book_cid in game_config.config_book:
    cache.rhodes_island.book_borrow_dict.setdefault(_book_cid, -1)

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

# ==== 3.1 可点击的按钮（按需开启：enable_clickable_buttons） ====
# 上面默认的 askfor_all 桩只返回选项、不执行按钮的响应函数；而真实流程里 askfor_all 选中后会执行按钮绑定的函数（flow_handle._cmd_deal），
#    靠按钮回调改状态、退出循环的面板在默认桩下会死循环。驱动这类面板时调 enable_clickable_buttons()，再用 run_panel() 按选择序列跑。
button_map = {}
""" 本轮已绘制的按钮：返回值 → (响应函数, 参数)，每次 askfor_all 选完后清空 """
ask_log = []
""" 每次 askfor_all 的 (可选项列表, 选中项, 当时的按钮表快照) """
plan = []
""" 待依次执行的选择：字符串（与返回值等值匹配）或谓词函数（参数为返回值） """
missed = []
""" 计划里没能在可选项中找到的选择 """
ASK_LIMIT = 60
""" 单次面板运行允许的最多 askfor_all 次数，超过视为按钮循环退不出 """


def _record_and_bind(self, *args, **kwargs):
    """
    可点击按钮用的绘制桩：与 _record_draw 一样记录文本，按钮还登记返回值对应的响应函数
    Keyword arguments:
    self -- 绘制对象
    Return arguments:
    无
    """
    text = getattr(self, "text", None) or getattr(self, "title", None)
    if text:
        drawn_text.append(str(text))
    return_text = getattr(self, "return_text", None)
    if return_text is not None and hasattr(self, "cmd_func"):
        button_map[return_text] = (self.cmd_func, getattr(self, "args", ()))


def scripted_askfor(return_list, *args, **kwargs):
    """
    脚本化的 askfor_all：按 plan 依次选择，选不到或 plan 用完则选[返回]；选中后执行该按钮的响应函数（同真实的 _cmd_deal）
    Keyword arguments:
    return_list -- 可选项列表
    Return arguments:
    str -- 选中的返回值
    """
    if len(ask_log) >= ASK_LIMIT:
        raise RuntimeError("askfor_all 调用次数超过上限，面板的按钮循环可能退不出")
    pick = None
    if plan:
        want = plan.pop(0)
        for option in return_list:
            if want(option) if callable(want) else option == want:
                pick = option
                break
        if pick is None:
            missed.append(want)
    if pick is None:
        pick = _("返回") if _("返回") in return_list else (return_list[-1] if return_list else "")
    ask_log.append((list(return_list), pick, dict(button_map)))
    bound = button_map.get(pick)
    button_map.clear()
    if bound and bound[0] is not None:
        func, arg = bound
        if not isinstance(arg, tuple):
            arg = (arg,)
        func(*arg)
    return pick


def enable_clickable_buttons():
    """
    换上可点击按钮的绘制桩与脚本化的 askfor_all
    Keyword arguments:
    无
    Return arguments:
    无
    """
    for cls_name in dir(draw):
        cls = getattr(draw, cls_name)
        if isinstance(cls, type) and hasattr(cls, "draw"):
            try:
                cls.draw = _record_and_bind
            except Exception:
                pass
    flow_handle.askfor_all = scripted_askfor


def run_panel(func, choices: list):
    """
    清空记录后按选择序列跑一段面板流程，异常不外抛而是返回给调用方做断言（需先 enable_clickable_buttons）
    Keyword arguments:
    func -- 无参的面板入口
    choices -- 选择序列，每项为返回值字符串或谓词函数
    Return arguments:
    Exception | None -- 流程中抛出的异常
    """
    drawn_text.clear()
    ask_log.clear()
    missed.clear()
    button_map.clear()
    plan[:] = list(choices)
    try:
        func()
    except Exception as err:  # noqa: BLE001  旧代码的报错要变成失败的断言，而不是让整个测试崩掉
        return err
    finally:
        plan.clear()
    return None

# ==== 4. 环境工具 ====
DEFAULT_TIME = datetime.datetime(2026, 9, 7, 9, 0)
""" 默认游戏时间：2026-09-07 周一 09:00 """
SCENE_DORM = ["宿舍", "1区", "101"]
""" 一间真实宿舍 """
assert map_handle.get_map_system_path_str_for_list(SCENE_DORM) in cache.scene_data


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
    Keyword arguments:
    scene_path_str -- 场景路径字符串
    character_id -- 角色id
    Return arguments:
    无
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
    Keyword arguments:
    scene_path_str -- 场景路径字符串
    character_id -- 角色id
    Return arguments:
    无
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
    get_class_period 等函数读的是 behavior.start_time（默认是公元1年），不同步会永远算成不在节次内
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
    stage -- 成长阶段素质id（101 婴儿 / 102 幼女 / 103 萝莉 / 104 少女），0 为成年干员；婴儿不进 npc_id_got（Plan 28）
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
    # 婴儿不进 npc_id_got，与真实婴儿一致（Plan 28 §3.9）：character_handle.born_new_character 不加，
    #    要到长成幼女、get_new_character 上线时才加。此前夹具把婴儿也放进去，婴儿期事件派不出来的 BUG 一直测不出
    if cid and stage != 101:
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


set_time(DEFAULT_TIME)
pl = make_character(0, "博士")
""" 玩家 """


def _exit_on_exception(exc_type, exc_value, exc_traceback):
    """
    未捕获异常时打印回溯并强制退出
    导入链起的非守护线程会让崩溃的测试进程挂住，直到 run_all 的超时才被杀掉
    Keyword arguments:
    exc_type -- 异常类型
    exc_value -- 异常对象
    exc_traceback -- 回溯对象
    Return arguments:
    无
    """
    import traceback

    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("\nPASS={0} FAIL={1} (crashed)".format(PASS, len(FAIL) + 1))
    sys.stdout.flush()
    remove_test_map_cache()
    os._exit(2)


sys.excepthook = _exit_on_exception

# `from headless_base import *` 默认不导出下划线开头的名字，而翻译函数 `_` 正是测试里最常用的一个
__all__ = [_name for _name in list(globals()) if not _name.startswith("__")]
