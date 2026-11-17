# -*- coding: UTF-8 -*-
"""结算系统冒烟：全部一段 / 二段结算器与效果串里的综合数值结算(CVE)按可达方向逐个执行不抛异常，handle_settle_behavior 端到端跑通常用行为，抽查体力 / 气力 / 好感 / 信赖 / 状态通用结算的语义"""
import builtins
import faulthandler
import inspect
import pickle
import re
import time
import traceback

from _bootstrap import *  # noqa: F401,F403
from Script.Design import basement, character_behavior, character_move, update
from Script.Design import character as character_module
from Script.System.Cooking_System import cooking
from Script.System.Dormitory_System import common as dormitory_common
from Script.System.Field_Commission_System import field_commission_function
from Script.System.Instruct_System import handle_instruct
from Script.System.Medical_System import medical_service
from Script.UI.Panel import achievement_panel

T_BEGIN = time.time()
EFFECT = constant.settle_behavior_effect_data
""" 一段结算器注册表 效果id:结算器(character_id, add_time, change_data, now_time) """
SECOND = constant.settle_second_behavior_effect_data
""" 二段结算器注册表 效果id:结算器(character_id, change_data)，change_data 可能是 CharacterStatusChange 也可能是 TargetChange """
ADD_TIME = 10
""" 扫描用的结算分钟数：绝大多数结算器开头是 `if not add_time: return`，传 0 等于什么都没测 """
T_START = DEFAULT_TIME
""" 行为开始时间 """
T_END = DEFAULT_TIME + datetime.timedelta(minutes=ADD_TIME)
""" 行为结束时间 = 结算时间（真实流程是先把游戏时间推到行动结束点再结算） """
HANG_SECONDS = 60
""" 单个结算器超过这个秒数没返回就判为卡死：faulthandler 打出全部线程的栈后直接退出进程 """
CHILD_TALENT = (7, 101, 102, 103, 104)
""" 未成年 / 成长阶段素质：本文件的全部角色都不得带这些素质 """
TARGET_ADV = 148
""" 交互对象 NPC 的模板id（临光）：成年模板，不带任何未成年 / 成长阶段素质 """
DIRECTION_NAME = {"PL": "玩家对 NPC", "NPC": "NPC 对玩家", "PL_SELF": "玩家自身", "NPC_SELF": "NPC 自身（NPC 自己的行为）", "NPC_TC": "NPC 自身（玩家对 NPC 的行为，TargetChange）"}
""" 扫描方向 → 中文名 """
TRIGGER_DIRECTION = {"pl": ("PL",), "npc": ("NPC",), "both": ("PL", "NPC")}
""" Behavior_Data.csv 的 trigger 列 → 一段结算的可达方向（handle_npc_ai_in_h 等处以 trigger == "pl" 判「只能玩家使用」） """
TRIGGER_SECOND_MODE = {"pl": ("PL_SELF",), "npc": ("NPC_SELF", "NPC_TC"), "both": ("PL_SELF", "NPC_SELF", "NPC_TC")}
""" 二段行为的 trigger → 二段结算的可达方式：NPC 的二段行为既会在 NPC 自己的行为里结算，也会在玩家对她的行为里以 TargetChange 结算（second_behavior.check_second_effect） """

# ==== 排除规则（只有两条，均在下面写明理由） ====
# 规则一：养成 / 教育 / 性技实操课区域与未成年角色的专属内容整体不在本文件的覆盖范围内
#    （前者已由 tools/tests/education 覆盖、本套件不扩展它；后者是本套件的约定：fixture 一律成年，不与任何未成年相关的东西组合）。
#    判定：结算器实现位于 Script.System.Education_System 模块下，或其源码引用了 Education_System / child_growth / sex_class；
#    挂了这类结算器（或养成数值 CVE_..._Growth）的行为、以及模板带未成年 / 成长阶段素质的角色的专属事件（事件 adv_id）也视为该区域，
#    既不拿来当上下文，也不拿来做端到端；只被养成区域引用的结算器、只在这些行为 / 事件里出现的 CVE token 同样不扫
#    （只在未成年角色专属事件里出现的结算器是通用代码，照扫，只是不带事件上下文、作用在成年 NPC 身上）；
#    主体为这类角色的 CVE_A3|<adv> token 也不扫（成年世界里没有这个角色）。
EDU_SOURCE_PATTERN = re.compile(r"Education_System|child_growth|sex_class")
""" 规则一的源码特征 """
CHILD_ADV = {adv for adv, tem in character_config.character_tem_list.items() if any((tem.Talent or {}).get(talent_id) for talent_id in CHILD_TALENT)}
""" 规则一：模板带未成年 / 成长阶段素质的角色 adv_id """
# 规则二：未被任何行为 / 事件引用的死代码结算器（真实游戏走不到），若在某个方向上抛异常，在下面逐条登记为「潜在缺陷」，
#    只要它仍未被引用就汇成一条 known_issue（不算失败、但在 run_all 汇总里列出）；一旦数据里挂上了它，登记自动失效，照常断言。
LATENT_UNREFERENCED = {
    # 645 WEAR_CLOTH_OFF_MOST → clothing.get_cloth_wear_zero_except_need 没有其他换装函数都有的 `if character_id:` 守卫，
    #    对玩家调用时走进 chara_special_wear_cloth(0)，后者只在 character_id 非 0 时定义 return_list → UnboundLocalError（clothing.py:650）
    ("first", 645, "PL"): "未被引用；对玩家调用时 chara_special_wear_cloth(0) 的 return_list 未定义",
    # 293 ADD_LARGE_LEAD（增加大量先导，受虐补正）读 ability[25]，Ability.csv 里没有 25 号能力 → KeyError（Second_effect.py:1776）
    ("second", 293, "PL_SELF"): "未被引用；读取不存在的能力 ability[25]",
    ("second", 293, "NPC_SELF"): "未被引用；读取不存在的能力 ability[25]",
    ("second", 293, "NPC_TC"): "未被引用；读取不存在的能力 ability[25]",
}
""" (注册表名, 效果id, 方向) → 理由；注册表名为 first / second / cve """
LATENT_HITS = []
""" 扫描中实际撞上的已登记潜在缺陷，最后汇成一条 known_issue """
# 已确认、真实游戏可达的缺陷：按异常特征归组，每组单独一条断言（现在是失败的），扫描的总断言里不再重复计它们，
#    这样总断言继续守住其余结算器；缺陷修好后该组断言自然转绿
CONFIRMED_BUGS = (
    # 本表两条均由本文件首轮扫出，已于 2026-11-18 修好；保留为回归锁：再有用例撞上同样的异常特征就判失败
    # settle_behavior.handle_comprehensive_value_effect 的 A3 主体分支（CVE_A3|<adv>_...）只赋了 final_character_data，没赋 final_change_data；
    #    属性是状态 S / 能力 A / 经验 E 等要记录变化的类型时，数值已经加上去之后在记录这一步 UnboundLocalError。
    #    数据里白金（0204）的事件就有 CVE_A3|204_S|13_G_10000、CVE_A3|204_S|18_G_300 等，只要她已招募、事件一触发就崩
    ("CVE 的 A3 主体 token 结算不抛异常（A3 分支没给 final_change_data 赋值）", "'final_change_data'"),
    # 同一函数的通用分支把属性名映射到 change_data 上的同名字段记录变化，但 CharacterStatusChange / TargetChange 都没有 juel 字段，
    #    宝珠 J 一结算就 AttributeError。数据里星熊（0136）的事件就有 CVE_A2_J|0_G_1
    ("CVE 的宝珠 J token 结算不抛异常（变化记录对象没有 juel 字段）", "attribute 'juel'"),
)
""" (断言名, 异常描述里的特征串) """
BUG_HITS = {title: [] for title, _signature in CONFIRMED_BUGS}
""" 已确认缺陷 → 撞上它的用例 """
EXECUTED = set()
""" 实际执行过至少一次的 (注册表名, 键)，覆盖面断言用 """


def is_edu_function(func) -> bool:
    """
    判断结算器是否属于养成 / 教育 / 性技实操课区域（排除规则一）
    Keyword arguments:
    func -- 注册表里的结算器（装饰器包装过的函数）
    Return arguments:
    bool -- 是否属于该区域
    """
    real_func = inspect.unwrap(func)
    if real_func.__module__.startswith("Script.System.Education_System"):
        return True
    return bool(EDU_SOURCE_PATTERN.search(inspect.getsource(real_func)))


def is_second_behavior(behavior_id: str) -> bool:
    """
    判断行为是否为二段行为（二段行为的效果串走二段结算器注册表）
    Keyword arguments:
    behavior_id -- 行为id
    Return arguments:
    bool -- 是否为二段行为
    """
    return _("二段结算") in game_config.config_behavior[behavior_id].tag


def is_h_behavior(behavior_id: str) -> bool:
    """
    判断行为是否为性爱类（真实游戏里只在 H 中执行，扫描时先按游戏自己的流程进入 H）
    Keyword arguments:
    behavior_id -- 行为id
    Return arguments:
    bool -- 是否为性爱类行为
    """
    return behavior_id in game_config.config_behavior and _("性爱") in game_config.config_behavior[behavior_id].tag.split("|")


def event_directions(event_data) -> tuple:
    """
    事件的可达方向：前提里的 sys_0 / sys_1 指明玩家 / NPC 触发，都没有时按事件所属行为的 trigger
    Keyword arguments:
    event_data -- 事件配置
    Return arguments:
    tuple -- 方向元组
    """
    premise = event_data.premise
    if "sys_0" in premise:
        return ("PL",)
    if "sys_1" in premise:
        return ("NPC",)
    behavior_data = game_config.config_behavior.get(event_data.behavior_id)
    return TRIGGER_DIRECTION.get(behavior_data.trigger if behavior_data else "both", ("PL", "NPC"))


section("世界：照开新局的流程（creator_character_flow 去掉界面）实例化成年干员模板")
# creator_character_flow 本身会导入 io_init 的 Tk 主窗体，这里照它的 creator_character_panel → first_bonus_and_setting_updata → game_start 逐步复刻
for _scene in cache.scene_data.values():
    _scene.character_list.clear()
cache.character_data.clear()
cache.npc_id_got.clear()
character_handle.init_character_tem()
# 只保留成年模板：不带任何未成年 / 成长阶段素质（本套件的约定：fixture 一律成年，不与任何未成年相关的东西组合）
cache.npc_tem_data = {adv: tem for adv, tem in cache.npc_tem_data.items() if not any((tem.Talent or {}).get(talent_id) for talent_id in CHILD_TALENT)}
cache.character_data[0] = game_type.Character()
character_handle.init_character_list()
cache.character_data[0].name = "博士"
character_module.init_attr(0)
cache.rhodes_island = basement.get_base_zero()
for _cid in game_config.config_first_bonus:
    cache.first_bonus[_cid] = False
for _cid in game_config.config_world_setting:
    cache.world_setting[_cid] = 0
cache.all_system_setting = attr_calculation.get_system_setting_zero()
cache.rhodes_island.materials_resouce[1] = 20000
cache.rhodes_island.materials_resouce[11] = 20
cache.rhodes_island.materials_resouce[15] = 1000
cache.rhodes_island.materials_resouce[21] = 10
cache.rhodes_island.physical_examination_setting = attr_calculation.get_physical_exam_setting_zero()
cache.rhodes_island.confinement_training_setting = attr_calculation.get_confinement_training_setting_zero()
character_handle.first_NPC_work()
dormitory_common.init_character_dormitory()
character_handle.init_character_position()
character_handle.init_character_facility_open()
character_handle.handle_character_setting()
cooking.init_recipes()
cooking.init_food_shop_data(new_day_flag=True)
_talk_setting = cache.all_system_setting.character_text_version
cache.all_system_setting = attr_calculation.get_system_setting_zero()
cache.all_system_setting.character_text_version = _talk_setting
cache.country = attr_calculation.get_country_reset(cache.country)
basement.get_base_updata()
character_handle.init_character_entertainment()
medical_service.init_medical_department_data(reset_runtime=True)
achievement_panel.achievement_flow(_("周目"))
# 交互对象：走真实的招募上线链（宿舍分配、移到博士办公室、娱乐安排），玩家再走到她身边
NPC = TARGET_ADV if TARGET_ADV in cache.character_data else min(cid for cid in cache.character_data if cid and cid not in cache.npc_id_got)
""" 交互对象的角色id（模板数据若改得临光不再是成年模板，就退回任意一个未招募的成年干员） """
character_handle.get_new_character(NPC)
pl = cache.character_data[0]
npc = cache.character_data[NPC]
map_handle.character_move_scene(pl.position, npc.position, 0)
check("世界里全部角色都是成年模板（不带未成年 / 成长阶段素质）", not [cid for cid, cd in cache.character_data.items() if any(cd.talent.get(t) for t in CHILD_TALENT)],
      [cid for cid, cd in cache.character_data.items() if any(cd.talent.get(t) for t in CHILD_TALENT)][:10])
check("玩家与交互对象同处一个真实场景，交互对象已招募", pl.position == npc.position and scene_str(pl.position) in cache.scene_data
      and {0, NPC} <= set(cache.scene_data[scene_str(pl.position)].character_list) and NPC in cache.npc_id_got, (pl.position, npc.position))

# ==== fixture 补全（每条都是真实游戏里该字段在结算前必然已有的样子） ====
_recipe_id = min(rid for rid, recipe in cache.recipe_data.items() if recipe.type == 0)
_gift_id = next((gid for gid, gift in sorted(game_config.config_gift_items.items()) if gift.type == 3), min(game_config.config_gift_items))
for _cid in (0, NPC):
    _cd = cache.character_data[_cid]
    # 「前提结算用」的行为子字段：真实游戏里由对应指令 / 状态机在行为开始前填好（桌游类型、食物、书、礼物），默认值 0 / 空食物不是合法 id
    _cd.behavior.board_game_type = min(game_config.config_board_game)
    _cd.behavior.board_game_ai_difficulty = 1
    _food = cooking.cook({}, _recipe_id, 1, _cd.name)
    _cd.food_bag[_food.uid] = _food
    _cd.behavior.target_food = _food
    if _cd.behavior.book_id not in game_config.config_book:
        _cd.behavior.book_id = min(game_config.config_book)
    _cd.behavior.gift_id = _gift_id
    _cd.item[game_config.config_gift_items[_gift_id].item_id] = 1
for _cd in cache.character_data.values():
    # 衣柜精液数据：init_attr 用的 get_dirty_reset 不填它；任何一次读档（old_chara_to_new 按服装类型数补齐）
    #    或第一次「衣服放进浴场衣柜」（default_cloth 里 setdefault）之后都会是满的，「从衣柜穿回」的结算一定在那之后
    if len(_cd.dirty.cloth_locker_semen) != len(game_config.config_clothing_type):
        _cd.dirty.cloth_locker_semen = attr_calculation.get_zero_dirty().cloth_locker_semen

# ==== 打桩：结算器里通向真实主循环 / 写盘的出口（打在调用方实际取用的模块属性上） ====
STUB_CALLS = []
""" 被拦下的调用 (桩名, 当前用例) """
CURRENT_CASE = [""]
""" 当前正在跑的用例名，桩与写盘拦截记录用 """


def make_stub(stub_name: str):
    """
    生成一个只记录、不执行的桩
    Keyword arguments:
    stub_name -- 桩名
    Return arguments:
    function -- 桩函数
    """

    def stub(*args, **kwargs):
        """
        记录型桩：记下是哪个用例走到了这里
        Keyword arguments:
        args -- 原调用的位置参数
        kwargs -- 原调用的关键字参数
        Return arguments:
        无
        """
        STUB_CALLS.append((stub_name, CURRENT_CASE[0]))

    return stub


# 1228 TARGET_HYPNOSIS_ACTIVE_H_SWITCH_CHANGE 等：chara_handle_instruct_common_settle 最终会调 init_character_behavior（真实主循环）
handle_instruct.chara_handle_instruct_common_settle = make_stub("chara_handle_instruct_common_settle")
# 1701 WAIT_UNITL_TRAGET_ACTION_END：函数内 `from Script.Design import update` 后调 game_update_flow → 主循环
update.game_update_flow = make_stub("game_update_flow")
# 兜底：主循环本体与存档（sleep_settle.update_save 会调 establish_save 写 save/auto）
character_behavior.init_character_behavior = make_stub("init_character_behavior")
save_handle.establish_save = make_stub("establish_save")
# 3003 OFFICIAL_EVENT_TEMP_COMMISSION：create_temp_commission 会把新委托追加写进 data/csv/Commission.csv，还会改 game_config.config_commission
field_commission_function.create_temp_commission = make_stub("create_temp_commission")
# CVE_A1_Move_寻路（玩家寻路移动）：own_charcter_move 每走一段都调 game_update_flow 推进主循环，主循环被上面钉死后它会原地死循环
character_move.own_charcter_move = make_stub("own_charcter_move")

# 写盘拦截：扫描期间任何以写模式打开文件都直接拒绝并记录，最后断言一次都没有发生
WRITE_ATTEMPTS = []
""" 被拒绝的写盘 (路径, 模式, 当前用例) """
_real_open = builtins.open


def guarded_open(file, mode="r", *args, **kwargs):
    """
    写模式一律拒绝的 open 替身
    Keyword arguments:
    file -- 文件路径
    mode -- 打开模式
    Return arguments:
    file object -- 只读模式时返回真实文件对象
    """
    if any(flag in str(mode) for flag in "wax+"):
        WRITE_ATTEMPTS.append((str(file), str(mode), CURRENT_CASE[0]))
        raise PermissionError(f"test_settle_smoke 拒绝写盘：{file}")
    return _real_open(file, mode, *args, **kwargs)


builtins.open = guarded_open
_real_os_func = {name: getattr(os, name) for name in ("makedirs", "mkdir", "remove", "unlink", "rename", "replace", "rmdir")}
""" 被替换掉的 os 写盘函数原件（导入机制写 __pycache__ 走的是 nt 模块，不受影响） """


def make_os_guard(func_name: str):
    """
    生成一个拒绝执行并记录的 os 写盘函数替身（如 save_handle 读 save_info 时会先 os.makedirs("save")）
    Keyword arguments:
    func_name -- os 函数名
    Return arguments:
    function -- 替身函数
    """

    def guard(*args, **kwargs):
        """
        记录后拒绝
        Keyword arguments:
        args -- 原调用的位置参数
        kwargs -- 原调用的关键字参数
        Return arguments:
        无
        """
        WRITE_ATTEMPTS.append((str(args[0]) if args else "", func_name, CURRENT_CASE[0]))
        raise PermissionError(f"test_settle_smoke 拒绝 os.{func_name}：{args}")

    return guard


for _name in _real_os_func:
    setattr(os, _name, make_os_guard(_name))

# ==== 快照与还原：每个用例前把世界还原成基线，结算器之间互不串味 ====
SKIP_CACHE_FIELDS = {"map_data", "character_data"}
""" 不进快照的 cache 字段：map_data 为静态地图数据；character_data 按角色单独快照 """
TOUCHED = set()
""" 本用例经 cache.character_data 取用过的角色id """
TOUCHED_ALL = [False]
""" 本用例是否整批取用过角色对象（values / items / copy），是则还原时逐个比对 """
AUDIT_EVERY = 25
""" 每隔这么多次还原做一次全量比对，核查「只换回取用过的角色」没有漏网 """
ISOLATION_LEAKS = []
""" 全量比对时发现的、没被记为取用却被改过的角色 (角色id, 用例名) """


class TrackingCharacterDict(dict):
    """记录本用例取用过哪些角色的角色字典：还原时只需换回取用过的角色（全量重新 pickle 比对一次要 10ms，是隔离开销的大头）"""

    def __getitem__(self, key):
        """
        下标取用：记下角色id
        Keyword arguments:
        key -- 角色id
        Return arguments:
        game_type.Character -- 角色对象
        """
        TOUCHED.add(key)
        return dict.__getitem__(self, key)

    def get(self, key, default=None):
        """
        get 取用：记下角色id
        Keyword arguments:
        key -- 角色id
        default -- 缺省值
        Return arguments:
        game_type.Character -- 角色对象或缺省值
        """
        TOUCHED.add(key)
        return dict.get(self, key, default)

    def pop(self, key, *args):
        """
        pop 取用：记下角色id
        Keyword arguments:
        key -- 角色id
        args -- 缺省值
        Return arguments:
        game_type.Character -- 角色对象或缺省值
        """
        TOUCHED.add(key)
        return dict.pop(self, key, *args)

    def setdefault(self, key, default=None):
        """
        setdefault 取用：记下角色id
        Keyword arguments:
        key -- 角色id
        default -- 缺省值
        Return arguments:
        game_type.Character -- 角色对象
        """
        TOUCHED.add(key)
        return dict.setdefault(self, key, default)

    def values(self):
        """
        整批取用角色对象：还原时改为逐个比对
        Keyword arguments:
        无
        Return arguments:
        dict_values -- 角色对象视图
        """
        TOUCHED_ALL[0] = True
        return dict.values(self)

    def items(self):
        """
        整批取用角色对象：还原时改为逐个比对
        Keyword arguments:
        无
        Return arguments:
        dict_items -- (角色id, 角色对象) 视图
        """
        TOUCHED_ALL[0] = True
        return dict.items(self)

    def copy(self):
        """
        整批取用角色对象：还原时改为逐个比对
        Keyword arguments:
        无
        Return arguments:
        dict -- 浅拷贝
        """
        TOUCHED_ALL[0] = True
        return dict(dict.items(self))


cache.character_data = TrackingCharacterDict(cache.character_data)


def take_snapshot() -> tuple:
    """
    给当前世界拍快照
    Keyword arguments:
    无
    Return arguments:
    tuple -- (cache 其余字段的 pickle, 各角色的 pickle 字典)
    """
    field_blob = pickle.dumps({k: v for k, v in cache.__dict__.items() if k not in SKIP_CACHE_FIELDS}, protocol=pickle.HIGHEST_PROTOCOL)
    character_blob = {cid: pickle.dumps(cd, protocol=pickle.HIGHEST_PROTOCOL) for cid, cd in dict.items(cache.character_data)}
    return field_blob, character_blob


def restore_snapshot(snapshot: tuple):
    """
    把世界还原成快照：cache 其余字段整体换回；角色只换回本用例取用过的（整批取用过时逐个重新 pickle 比对），
    每 AUDIT_EVERY 次再全量比对一次，核查没被记为取用的角色确实没被改过
    Keyword arguments:
    snapshot -- take_snapshot() 的返回值
    Return arguments:
    无
    """
    start = time.perf_counter()
    field_blob, character_blob = snapshot
    field_dict = pickle.loads(field_blob)
    for key in list(cache.__dict__):
        if key not in SKIP_CACHE_FIELDS and key not in field_dict:
            delattr(cache, key)
    for key, value in field_dict.items():
        setattr(cache, key, value)
    character_dict = cache.character_data
    for cid in list(dict.keys(character_dict)):
        if cid not in character_blob:
            dict.__delitem__(character_dict, cid)
    audit = RESTORE_COST[0] % AUDIT_EVERY == 0
    for cid, blob in character_blob.items():
        now_data = dict.get(character_dict, cid)
        if now_data is None or cid in TOUCHED or cid in (0, NPC):
            dict.__setitem__(character_dict, cid, pickle.loads(blob))
        elif (TOUCHED_ALL[0] or audit) and pickle.dumps(now_data, protocol=pickle.HIGHEST_PROTOCOL) != blob:
            if not TOUCHED_ALL[0]:
                ISOLATION_LEAKS.append((cid, CURRENT_CASE[0]))
            dict.__setitem__(character_dict, cid, pickle.loads(blob))
    TOUCHED.clear()
    TOUCHED_ALL[0] = False
    drawn_text.clear()
    RESTORE_COST[0] += 1
    RESTORE_COST[1] += time.perf_counter() - start


RESTORE_COST = [0, 0.0]
""" 隔离开销统计：[还原次数, 还原总秒数] """


def enter_h_mode():
    """
    按游戏自己的流程进入 H：以玩家为发起者、NPC 为交互对象执行行为 h 的整条效果串
    Keyword arguments:
    无
    Return arguments:
    无
    """
    cache.character_data[0].target_character_id = NPC
    for effect_id in game_config.config_behavior_effect_data[constant.Behavior.H]:
        EFFECT[effect_id](0, 1, game_type.CharacterStatusChange(), T_START)


def set_context(actor_id: int, other_id: int, behavior_id: str = "", event_id: str = ""):
    """
    把发起者与对象摆成「某个行为 / 事件正在结算」的样子：互为交互对象、行为开始于 T_START、持续 ADD_TIME、游戏时间推到 T_END
    Keyword arguments:
    actor_id -- 发起者id
    other_id -- 对象id
    behavior_id -- 上下文行为id，空为无行动
    event_id -- 上下文事件id
    Return arguments:
    无
    """
    if is_h_behavior(behavior_id):
        enter_h_mode()
    actor = cache.character_data[actor_id]
    other = cache.character_data[other_id]
    actor.target_character_id = other_id
    other.target_character_id = actor_id
    actor.behavior.behavior_id = behavior_id or constant.Behavior.SHARE_BLANKLY
    actor.behavior.start_time = T_START
    actor.behavior.duration = ADD_TIME
    other.behavior.start_time = T_START
    actor.event.event_id = event_id
    cache.game_time = T_END


def format_exception(exc: BaseException) -> str:
    """
    把异常压成一行：类型、消息、最内层的游戏代码位置
    Keyword arguments:
    exc -- 异常对象
    Return arguments:
    str -- 一行描述
    """
    frame_list = traceback.extract_tb(exc.__traceback__)
    game_frame_list = [frame for frame in frame_list if "Script" in frame.filename.replace("\\", "/").split("/")]
    frame = (game_frame_list or frame_list)[-1]
    location = os.path.relpath(frame.filename, ROOT).replace("\\", "/") + f":{frame.lineno}"
    return f"{type(exc).__name__}: {str(exc)[:80]} @{location}"


def run_case(case_name: str, call, actor_id: int, other_id: int, behavior_id: str = "", event_id: str = ""):
    """
    跑一个隔离用例：还原世界 → 摆上下文 → 固定随机种子 → 带卡死看门狗执行
    Keyword arguments:
    case_name -- 用例名（随机种子与记录用）
    call -- 无参可调用对象，真正执行结算
    actor_id -- 发起者id
    other_id -- 对象id
    behavior_id -- 上下文行为id
    event_id -- 上下文事件id
    Return arguments:
    str -- 抛异常时的一行描述，未抛为空串
    """
    CURRENT_CASE[0] = case_name
    restore_snapshot(BASELINE)
    error_text = ""
    faulthandler.dump_traceback_later(HANG_SECONDS, exit=True)
    try:
        random.seed(case_name)
        set_context(actor_id, other_id, behavior_id, event_id)
        call()
    except (Exception, SystemExit) as exc:
        error_text = format_exception(exc)
    finally:
        faulthandler.cancel_dump_traceback_later()
    return error_text


BASELINE = take_snapshot()
""" 基线快照 """
# 隔离本身先验一次：改动交互对象、一个旁人与罗德岛资源，还原后都要回到基线
_bystander = next(cid for cid in sorted(cache.character_data) if cid not in (0, NPC))
cache.character_data[NPC].hit_point -= 7
cache.character_data[_bystander].favorability[0] = 123
cache.rhodes_island.materials_resouce[1] += 1
cache.character_data[99999] = game_type.Character()
restore_snapshot(BASELINE)
check("快照还原：交互对象、旁人、罗德岛资源被改动、新增的角色都回到基线",
      pickle.dumps(cache.character_data[NPC], protocol=pickle.HIGHEST_PROTOCOL) == BASELINE[1][NPC]
      and pickle.dumps(cache.character_data[_bystander], protocol=pickle.HIGHEST_PROTOCOL) == BASELINE[1][_bystander]
      and cache.rhodes_island.materials_resouce[1] == pickle.loads(BASELINE[0])["rhodes_island"].materials_resouce[1] and 99999 not in cache.character_data)
print(f"  （世界：{len(cache.character_data)} 个角色，已招募 {len(cache.npc_id_got)} 人；构建 {time.time() - T_BEGIN:.1f}s）")

section("注册表与效果串的一致性")
EDU_FIRST = {eid for eid, func in EFFECT.items() if is_edu_function(func)}
""" 规则一排除的一段结算器 """
EDU_SECOND = {eid for eid, func in SECOND.items() if is_edu_function(func)}
""" 规则一排除的二段结算器 """
EDU_BEHAVIORS = set()
""" 规则一排除的行为（挂了养成区域结算器或养成数值 CVE 的行为） """
for _bid, _effect_list in game_config.config_behavior_effect_data.items():
    _edu_ids = EDU_SECOND if _bid in game_config.config_behavior and is_second_behavior(_bid) else EDU_FIRST
    if any((isinstance(e, int) and e in _edu_ids) or (isinstance(e, str) and "_Growth|" in e) for e in _effect_list):
        EDU_BEHAVIORS.add(_bid)
_missing_behavior = sorted(bid for bid in game_config.config_behavior_effect_data if bid not in game_config.config_behavior)
check("效果串里的行为id都在行为表里（不在表里的行为没有 trigger / tag，结算方向无从判断）", not _missing_behavior, _missing_behavior[:20])
_bad_ref = []
for _bid, _effect_list in game_config.config_behavior_effect_data.items():
    if _bid not in game_config.config_behavior:
        continue
    _registry = SECOND if is_second_behavior(_bid) else EFFECT
    _bad_ref.extend(f"{_bid}:{e}" for e in _effect_list if isinstance(e, int) and e not in _registry)
for _uid, _event in game_config.config_event.items():
    _bad_ref.extend(f"事件{_uid[:8]}:{e}" for e in _event.effect if e.isdigit() and int(e) not in EFFECT)
check("行为 / 事件效果串引用的结算器id全部已注册（未注册的会被派发器打印一行 error 后静默跳过）", not _bad_ref, _bad_ref[:20])

# ==== 扫描计划：每个结算器在哪些方向上可达、用哪个行为 / 事件当上下文 ====
FIRST_REFS = {eid: {"PL": [], "NPC": []} for eid in EFFECT}
""" 一段结算器 → 方向 → [(行为id, 事件id)]，只收非养成区域的引用 """
FIRST_REF_ANY = set()
""" 被任意行为 / 事件（含养成区域）引用过的一段结算器 """
SECOND_REFS = {eid: {"PL_SELF": [], "NPC_SELF": [], "NPC_TC": []} for eid in SECOND}
""" 二段结算器 → 方式 → [(二段行为id, "")] """
SECOND_REF_ANY = set()
""" 被任意二段行为引用过的二段结算器 """
CVE_REFS = {}
""" CVE token → 方式 → [(行为id, 事件id)]；方式取 PL / NPC / NPC_SELF / NPC_TC / PL_SELF """
for _bid in sorted(game_config.config_behavior_effect_data):
    if _bid not in game_config.config_behavior:
        continue
    _effect_list = game_config.config_behavior_effect_data[_bid]
    _trigger = game_config.config_behavior[_bid].trigger
    _second = is_second_behavior(_bid)
    _mode_list = TRIGGER_SECOND_MODE.get(_trigger, TRIGGER_SECOND_MODE["both"]) if _second else TRIGGER_DIRECTION.get(_trigger, ("PL", "NPC"))
    for _e in _effect_list:
        if isinstance(_e, int):
            (SECOND_REF_ANY if _second else FIRST_REF_ANY).add(_e)
        if _bid in EDU_BEHAVIORS:
            continue
        for _mode in _mode_list:
            if isinstance(_e, int):
                (SECOND_REFS if _second else FIRST_REFS)[_e][_mode].append((_bid, ""))
            elif "CVE" in _e:
                CVE_REFS.setdefault(_e, {}).setdefault(_mode, []).append((_bid, ""))
_first_ref_not_child = set(FIRST_REF_ANY)
for _uid in sorted(game_config.config_event):
    _event = game_config.config_event[_uid]
    _event_child = int(_event.adv_id or 0) in CHILD_ADV
    _event_edu = _event.behavior_id in EDU_BEHAVIORS or any((e.isdigit() and int(e) in EDU_FIRST) or "_Growth|" in e for e in _event.effect)
    for _e in _event.effect:
        if _e.isdigit():
            FIRST_REF_ANY.add(int(_e))
            if not _event_child:
                _first_ref_not_child.add(int(_e))
        if _event_edu or _event_child:
            continue
        for _mode in event_directions(_event):
            if _e.isdigit():
                FIRST_REFS[int(_e)][_mode].append((_event.behavior_id, _uid))
            elif _e.startswith("CVE"):
                CVE_REFS.setdefault(_e, {}).setdefault(_mode, []).append((_event.behavior_id, _uid))
FIRST_REF_CHILD_ONLY = {eid for eid in FIRST_REF_ANY if eid not in _first_ref_not_child}
""" 只在未成年角色专属事件里出现过的一段结算器（结算器本身是通用代码：不带事件上下文、对成年 NPC 两个方向都扫） """

# 只被养成区域引用的结算器同样归入规则一
EDU_FIRST |= {eid for eid in _first_ref_not_child if eid in EFFECT and not any(FIRST_REFS[eid].values())}
EDU_SECOND |= {eid for eid in SECOND_REF_ANY if eid in SECOND and not any(SECOND_REFS[eid].values())}
UNREF_FIRST = sorted(eid for eid in EFFECT if eid not in FIRST_REF_ANY)
""" 未被任何行为 / 事件引用的一段结算器（死代码，方向不可知，两个方向都扫） """
UNREF_SECOND = sorted(eid for eid in SECOND if eid not in SECOND_REF_ANY)
""" 未被任何二段行为引用的二段结算器（三种方式都扫） """
print(f"  （规则一排除：一段 {sorted(EDU_FIRST)}，二段 {sorted(EDU_SECOND)}，行为 {len(EDU_BEHAVIORS)} 个，"
      f"未成年角色专属事件 {sum(1 for ev in game_config.config_event.values() if int(ev.adv_id or 0) in CHILD_ADV)} 个）")
print(f"  （未被引用的一段结算器 {len(UNREF_FIRST)} 个、二段 {len(UNREF_SECOND)} 个，只在未成年角色专属事件里出现的一段结算器 {sorted(FIRST_REF_CHILD_ONLY)}，"
      f"都不带上下文、所有方向都扫）")


def sweep(registry_name: str, plan: dict, mode_list: tuple, make_call) -> dict:
    """
    按计划扫一张注册表
    Keyword arguments:
    registry_name -- 注册表名（first / second / cve），用于用例名与潜在缺陷登记
    plan -- 键 → 方式 → [(行为id, 事件id)]；某方式列表为空表示该方向不可达；值为 None 表示未被引用、所有方式都扫且无上下文
    mode_list -- 本注册表的全部方式
    make_call -- (键, 方式) → (发起者id, 对象id, 无参调用)
    Return arguments:
    dict -- 方式 → [失败描述]
    """
    fail_dict = {mode: [] for mode in mode_list}
    for key in sorted(plan, key=str):
        ref_dict = plan[key]
        for mode in mode_list:
            if ref_dict is None:
                context = ("", "")
            elif ref_dict.get(mode):
                context = ref_dict[mode][0]
            else:
                continue
            actor_id, other_id, call = make_call(key, mode)
            error_text = run_case(f"{registry_name}:{key}:{mode}", call, actor_id, other_id, *context)
            EXECUTED.add((registry_name, key))
            if not error_text:
                continue
            line = f"{key} {error_text}"
            if ref_dict is None and (registry_name, key, mode) in LATENT_UNREFERENCED:
                LATENT_HITS.append(f"{registry_name}/{mode} {line}")
                continue
            bug_title = next((title for title, signature in CONFIRMED_BUGS if signature in error_text), "")
            if bug_title:
                BUG_HITS[bug_title].append(f"{registry_name}/{mode} {line}")
                continue
            fail_dict[mode].append(line)
    return fail_dict


def first_call(effect_id: int, mode: str) -> tuple:
    """
    一段结算器的调用方式
    Keyword arguments:
    effect_id -- 效果id
    mode -- 方向 PL / NPC
    Return arguments:
    tuple -- (发起者id, 对象id, 无参调用)
    """
    actor_id, other_id = (0, NPC) if mode == "PL" else (NPC, 0)
    return actor_id, other_id, lambda: EFFECT[effect_id](actor_id, ADD_TIME, game_type.CharacterStatusChange(), T_END)


def second_call(effect_id: int, mode: str) -> tuple:
    """
    二段结算器的调用方式：PL_SELF 玩家自身、NPC_SELF NPC 自身、NPC_TC 玩家对 NPC 行为时以 TargetChange 结算 NPC 的二段行为
    Keyword arguments:
    effect_id -- 效果id
    mode -- 方式
    Return arguments:
    tuple -- (发起者id, 对象id, 无参调用)
    """
    if mode == "PL_SELF":
        return 0, NPC, lambda: SECOND[effect_id](0, game_type.CharacterStatusChange())
    if mode == "NPC_SELF":
        return NPC, 0, lambda: SECOND[effect_id](NPC, game_type.CharacterStatusChange())
    return 0, NPC, lambda: SECOND[effect_id](NPC, game_type.TargetChange())


def cve_a3_subject(token: str) -> int:
    """
    取 CVE_A3|<adv> token 的主体 adv_id
    Keyword arguments:
    token -- CVE token
    Return arguments:
    int -- 主体 adv_id，不是 A3 主体时为 -1
    """
    subject = token.split("_")[1]
    return int(subject[3:]) if subject.startswith("A3|") else -1


def cve_call(token: str, mode: str) -> tuple:
    """
    综合数值结算 token 的调用方式（与派发器一样把 CVE_ 之后按 _ 切开）
    A3 主体的 token 只在该角色已招募时才结算（未招募直接返回 0）；角色专属事件只有她在场时才会触发，所以先把她登记为已招募
    Keyword arguments:
    token -- CVE token
    mode -- 方式
    Return arguments:
    tuple -- (发起者id, 对象id, 无参调用)
    """
    value_list = token.split("_")[1:]
    subject_adv = cve_a3_subject(token)
    if mode in ("PL", "PL_SELF"):
        actor_id, other_id, change = 0, NPC, game_type.CharacterStatusChange()
    elif mode == "NPC_TC":
        actor_id, other_id, change = NPC, 0, game_type.TargetChange()
    else:
        actor_id, other_id, change = NPC, 0, game_type.CharacterStatusChange()

    def call():
        """
        登记 A3 主体后执行综合数值结算
        Keyword arguments:
        无
        Return arguments:
        无
        """
        if subject_adv > 0:
            cache.npc_id_got.add(subject_adv)
        settle_behavior.handle_comprehensive_value_effect(actor_id, value_list, change)

    # NPC_TC：玩家对 NPC 的行为里结算 NPC 的二段行为，发起者在上下文里是玩家
    return (0, NPC, call) if mode == "NPC_TC" else (actor_id, other_id, call)


section("一段结算器：按可达方向逐个执行（add_time > 0）")
_t = time.time()
FIRST_PLAN = {}
""" 一段结算器扫描计划 """
for _eid in EFFECT:
    if _eid in EDU_FIRST:
        continue
    FIRST_PLAN[_eid] = None if _eid in UNREF_FIRST or _eid in FIRST_REF_CHILD_ONLY else FIRST_REFS[_eid]
FIRST_FAIL = sweep("first", FIRST_PLAN, ("PL", "NPC"), first_call)
for _mode in ("PL", "NPC"):
    _count = sum(1 for v in FIRST_PLAN.values() if v is None or v.get(_mode))
    check(f"一段结算器（{DIRECTION_NAME[_mode]}）：{_count} 个可达结算器执行不抛异常", not FIRST_FAIL[_mode], f"失败 {len(FIRST_FAIL[_mode])} 个：" + " | ".join(FIRST_FAIL[_mode][:20]))
print(f"  （一段扫描 {time.time() - _t:.1f}s）")

section("二段结算器：按二段行为的 trigger 逐个执行")
_t = time.time()
SECOND_PLAN = {}
""" 二段结算器扫描计划 """
for _eid in SECOND:
    if _eid in EDU_SECOND:
        continue
    SECOND_PLAN[_eid] = None if _eid in UNREF_SECOND else SECOND_REFS[_eid]
SECOND_FAIL = sweep("second", SECOND_PLAN, ("PL_SELF", "NPC_SELF", "NPC_TC"), second_call)
for _mode in ("PL_SELF", "NPC_SELF", "NPC_TC"):
    _count = sum(1 for v in SECOND_PLAN.values() if v is None or v.get(_mode))
    check(f"二段结算器（{DIRECTION_NAME[_mode]}）：{_count} 个可达结算器执行不抛异常", not SECOND_FAIL[_mode], f"失败 {len(SECOND_FAIL[_mode])} 个：" + " | ".join(SECOND_FAIL[_mode][:20]))
print(f"  （二段扫描 {time.time() - _t:.1f}s）")

section("综合数值结算 CVE：行为与事件效果串里出现过的每个 token")
_t = time.time()
CVE_PLAN = {token: ref for token, ref in CVE_REFS.items() if "_Growth|" not in token and cve_a3_subject(token) not in CHILD_ADV
            and (cve_a3_subject(token) < 0 or cve_a3_subject(token) in cache.character_data)}
""" CVE 扫描计划（规则一：去掉养成数值与主体为未成年角色的 A3 token） """
CVE_FAIL = sweep("cve", CVE_PLAN, ("PL", "NPC", "PL_SELF", "NPC_SELF", "NPC_TC"), cve_call)
for _mode in ("PL", "NPC", "PL_SELF", "NPC_SELF", "NPC_TC"):
    _count = sum(1 for v in CVE_PLAN.values() if v.get(_mode))
    if _count:
        check(f"综合数值结算 CVE（{DIRECTION_NAME[_mode]}）：{_count} 个 token 执行不抛异常", not CVE_FAIL[_mode], f"失败 {len(CVE_FAIL[_mode])} 个：" + " | ".join(CVE_FAIL[_mode][:20]))
print(f"  （CVE 扫描 {time.time() - _t:.1f}s）")

section("已确认的游戏缺陷与死代码里的潜在缺陷")
for _title, _signature in CONFIRMED_BUGS:
    check(_title, not BUG_HITS[_title], f"撞上 {len(BUG_HITS[_title])} 次：" + " | ".join(BUG_HITS[_title][:20]))
_latent_expected = sorted(f"{name}/{mode} {key}" for name, key, mode in LATENT_UNREFERENCED)
known_issue("未被引用的死代码结算器在全部方向上都不抛异常", not LATENT_HITS,
            "645 WEAR_CLOTH_OFF_MOST 对玩家调用时 chara_special_wear_cloth(0) 的 return_list 未定义；二段 293 ADD_LARGE_LEAD 读不存在的 ability[25]；"
            "两者都没有任何行为 / 事件引用，修（补守卫 / 改能力id）还是删由维护者定", " | ".join(LATENT_HITS))
for _stale in [line for line in _latent_expected if not any(hit.startswith(line.split(" ")[0] + " " + line.split(" ")[1] + " ") for hit in LATENT_HITS)]:
    print(f"  （登记的潜在缺陷 {_stale} 已不再复现：把它从 LATENT_UNREFERENCED 里删掉，免得掩盖别的问题）")

section("扫描覆盖面")
_uncovered = (sorted(eid for eid in EFFECT if ("first", eid) not in EXECUTED and eid not in EDU_FIRST)
              + sorted(f"二段{eid}" for eid in SECOND if ("second", eid) not in EXECUTED and eid not in EDU_SECOND))
check(f"每个已注册的结算器要么至少实际执行过一次（一段 {len(EFFECT) - len(EDU_FIRST)} 个、二段 {len(SECOND) - len(EDU_SECOND)} 个），要么归入排除规则一",
      not _uncovered, _uncovered[:20])
restore_snapshot(BASELINE)
set_context(0, NPC, "normal_sex")
check("性爱类行为的上下文按游戏流程进入了 H（玩家与交互对象都处于 H 状态）", cache.character_data[0].sp_flag.is_h and cache.character_data[NPC].sp_flag.is_h,
      (cache.character_data[0].sp_flag.is_h, cache.character_data[NPC].sp_flag.is_h))
_stub_hit = {}
for _name, _case in STUB_CALLS:
    _stub_hit.setdefault(_name, set()).add(_case.split(":")[0] + ":" + _case.split(":")[1] if ":" in _case else _case)
for _name, _case_set in sorted(_stub_hit.items()):
    print(f"  （桩 {_name} 被这些用例走到：{sorted(_case_set)[:10]}）")

section("派发器：handle_settle_behavior 端到端跑常用行为")
DISPATCH_BEHAVIORS = ["chat", "stroke", "rest", "make_coffee", "official_work", "embrace", "kiss", "read_book", "eat", "give_gift", "handjob", "normal_sex", "masturebate"]
""" 端到端行为：日常 / 工作 / 猥亵 / 性爱各取几个最常见的（性爱类会先按游戏流程进入 H） """
_absent = [bid for bid in DISPATCH_BEHAVIORS if bid not in game_config.config_behavior or bid not in game_config.config_behavior_effect_data or bid in EDU_BEHAVIORS]
check("选定的常用行为都在行为表与效果表里、且不属于养成区域", not _absent, _absent)
_dispatch_fail = []
_dispatch_count = 0
for _bid in DISPATCH_BEHAVIORS:
    if _bid in _absent:
        continue
    for _mode in TRIGGER_DIRECTION.get(game_config.config_behavior[_bid].trigger, ("PL", "NPC")):
        _actor, _other = (0, NPC) if _mode == "PL" else (NPC, 0)
        _err = run_case(f"dispatch:{_bid}:{_mode}", lambda actor=_actor: settle_behavior.handle_settle_behavior(actor, T_END), _actor, _other, _bid)
        _dispatch_count += 1
        if _err:
            _dispatch_fail.append(f"{_bid}/{_mode} {_err}")
check(f"{_dispatch_count} 个（行为, 方向）组合经 handle_settle_behavior 结算不抛异常", not _dispatch_fail, " | ".join(_dispatch_fail[:20]))
# 聊天（效果串 21 好感 / 12 双方少量气力 / CVE 双方经验80+1 / 53 / 55 / 501）的结算真的落到了数值上
_panel_box = []
_err = run_case("dispatch:chat:check", lambda: _panel_box.append(settle_behavior.handle_settle_behavior(0, T_END)), 0, NPC, "chat")
pl = cache.character_data[0]
npc = cache.character_data[NPC]
_base_pl = pickle.loads(BASELINE[1][0])
_base_npc = pickle.loads(BASELINE[1][NPC])
check("玩家聊天：交互对象好感上升、双方经验80各+1、双方气力下降、返回了结算面板",
      not _err and npc.favorability[0] > _base_npc.favorability[0] and pl.experience[80] == _base_pl.experience[80] + 1 and npc.experience[80] == _base_npc.experience[80] + 1
      and pl.mana_point < _base_pl.mana_point and npc.mana_point < _base_npc.mana_point and _panel_box and _panel_box[0] is not None,
      (_err, npc.favorability[0], pl.experience[80], npc.experience[80], pl.mana_point, npc.mana_point, _panel_box))
_panel_box.clear()
_err = run_case("dispatch:chat:npc", lambda: _panel_box.append(settle_behavior.handle_settle_behavior(NPC, T_END)), NPC, 0, "chat")
npc = cache.character_data[NPC]
check("NPC 找玩家聊天：NPC 对玩家的好感上升，玩家同场时输出互换后仍返回结算面板",
      not _err and npc.favorability[0] > _base_npc.favorability[0] and _panel_box and _panel_box[0] is not None, (_err, npc.favorability[0], _panel_box))
# add_time=0：按分钟计的结算（21 好感、12 气力）不生效；CVE 是按次的固定值、不看 add_time，这里不断言经验
_err = run_case("dispatch:chat:zero", lambda: _panel_box.append(settle_behavior.handle_settle_behavior(0, T_START)), 0, NPC, "chat")
check("结算时间等于开始时间（add_time=0）：按分钟计的好感与气力结算不生效",
      not _err and pickle.dumps(cache.character_data[NPC].favorability) == pickle.dumps(_base_npc.favorability)
      and cache.character_data[0].mana_point == _base_pl.mana_point and cache.character_data[NPC].mana_point == _base_npc.mana_point,
      (_err, cache.character_data[NPC].favorability, cache.character_data[0].mana_point - _base_pl.mana_point, cache.character_data[NPC].mana_point - _base_npc.mana_point))

section("抽查：引用最多的通用结算器的语义")
BE = constant_effect.BehaviorEffect
SE = constant_effect.SecondEffect


def run_effect(effect_id: int, actor_id: int, other_id: int, add_time: int = ADD_TIME, prepare=None) -> game_type.CharacterStatusChange:
    """
    还原世界后在「无行动」上下文里直接调一个一段结算器
    Keyword arguments:
    effect_id -- 效果id
    actor_id -- 发起者id
    other_id -- 对象id
    add_time -- 结算分钟数
    prepare -- 调用前对世界再做的调整（无参可调用对象）
    Return arguments:
    game_type.CharacterStatusChange -- 结算记录对象
    """
    restore_snapshot(BASELINE)
    set_context(actor_id, other_id)
    if prepare is not None:
        prepare()
    change = game_type.CharacterStatusChange()
    EFFECT[effect_id](actor_id, add_time, change, T_END)
    return change


def target_change_of(change, character_id: int) -> game_type.TargetChange:
    """
    取结算记录里某个交互对象的变化，没有时给一个空的
    Keyword arguments:
    change -- 结算记录对象
    character_id -- 交互对象id
    Return arguments:
    game_type.TargetChange -- 交互对象的变化
    """
    return change.target_change.get(character_id, game_type.TargetChange())


# 双方体力 / 气力消耗：common_default.base_chara_hp_mp_common_settle 的程度表 少[1,3] 中[3,6] 大[5,10]（体力, 气力）每分钟
_hp_pl0, _hp_npc0 = _base_pl.hit_point, _base_npc.hit_point
_hp_ok = True
_hp_detail = []
for _eid, _per_min in ((BE.DOWN_BOTH_SMALL_HIT_POINT, 1), (BE.DOWN_BOTH_MEDIUM_HIT_POINT, 3), (BE.DOWN_BOTH_LARGE_HIT_POINT, 5)):
    _change = run_effect(_eid, 0, NPC)
    _expect = -ADD_TIME * _per_min
    _row = (_eid, cache.character_data[0].hit_point - _hp_pl0, cache.character_data[NPC].hit_point - _hp_npc0, _change.hit_point, target_change_of(_change, NPC).hit_point)
    _hp_detail.append(_row)
    _hp_ok = _hp_ok and _row[1:] == (_expect, _expect, _expect, _expect)
check("双方减少少量 / 中量 / 大量体力：双方体力按每分钟 1 / 3 / 5 下降，并分别记进 change_data 与 target_change", _hp_ok, _hp_detail)
_mp_ok = True
_mp_detail = []
for _eid, _per_min in ((BE.DOWN_BOTH_SMALL_MANA_POINT, 3), (BE.DOWN_BOTH_MEDIUM_MANA_POINT, 6), (BE.DOWN_BOTH_LARGE_MANA_POINT, 10)):
    _change = run_effect(_eid, 0, NPC)
    _expect = -ADD_TIME * _per_min
    _row = (_eid, cache.character_data[0].mana_point - _base_pl.mana_point, cache.character_data[NPC].mana_point - _base_npc.mana_point, _change.mana_point, target_change_of(_change, NPC).mana_point)
    _mp_detail.append(_row)
    _mp_ok = _mp_ok and _row[1:] == (_expect, _expect, _expect, _expect)
check("双方减少少量 / 中量 / 大量气力：双方气力按每分钟 3 / 6 / 10 下降，并分别记进 change_data 与 target_change", _mp_ok, _mp_detail)
_change = run_effect(BE.DOWN_BOTH_SMALL_HIT_POINT, 0, NPC, prepare=lambda: setattr(cache.character_data[0], "mana_point", 0))
check("气力为 0 时体力消耗变 3 倍（只影响气力为 0 的一方）", cache.character_data[0].hit_point - _hp_pl0 == -3 * ADD_TIME and cache.character_data[NPC].hit_point - _hp_npc0 == -ADD_TIME
      and _change.hit_point == -3 * ADD_TIME, (cache.character_data[0].hit_point - _hp_pl0, cache.character_data[NPC].hit_point - _hp_npc0, _change.hit_point))
_change = run_effect(BE.DOWN_SELF_SMALL_HIT_POINT, 0, NPC)
check("减少自己少量体力：只扣发起者，交互对象体力不变、也不记 target_change", cache.character_data[0].hit_point - _hp_pl0 == -ADD_TIME and cache.character_data[NPC].hit_point == _hp_npc0
      and _change.hit_point == -ADD_TIME and NPC not in _change.target_change, (cache.character_data[0].hit_point - _hp_pl0, cache.character_data[NPC].hit_point - _hp_npc0, _change.target_change))
# 好感 / 信赖：common_default.base_chara_favorability_and_trust_common_settle → character_handle.add_favorability
_change = run_effect(BE.ADD_INTERACTION_FAVORABILITY, 0, NPC)
_gain = cache.character_data[NPC].favorability[0] - _base_npc.favorability[0]
check("增加基础互动好感（玩家对 NPC）：NPC 对玩家的好感上升，增量与 target_change.favorability 一致，玩家自己的好感表不变",
      _gain > 0 and target_change_of(_change, NPC).favorability == _gain and cache.character_data[0].favorability.get(0, 0) == _base_pl.favorability.get(0, 0),
      (_gain, target_change_of(_change, NPC).favorability))
_change = run_effect(BE.ADD_INTERACTION_FAVORABILITY, NPC, 0)
_gain = cache.character_data[NPC].favorability[0] - _base_npc.favorability[0]
check("增加基础互动好感（NPC 对玩家）：NPC 对玩家的好感上升，记在 NPC 自己的 change_data.favorability", _gain > 0 and _change.favorability == _gain, (_gain, _change.favorability))
_change = run_effect(BE.ADD_SMALL_TRUST, 0, NPC)
_gain = cache.character_data[NPC].trust - _base_npc.trust
check("增加基础互动信赖（玩家对 NPC）：NPC 的信赖上升，增量与 target_change.trust 一致", _gain > 0 and abs(target_change_of(_change, NPC).trust - _gain) < 1e-9, (_gain, target_change_of(_change, NPC).trust))
# 交互对象状态：62 反感（状态20）/ 58 羞耻（状态16），走 base_chara_state_common_settle(change_data_to_target_change=...)
_state_ok = True
_state_detail = []
for _eid, _state_id in ((BE.TARGET_ADD_SMALL_DISGUST, 20), (BE.TARGET_ADD_SMALL_SHY, 16)):
    _change = run_effect(_eid, 0, NPC)
    _gain = cache.character_data[NPC].status_data[_state_id] - _base_npc.status_data[_state_id]
    _row = (_eid, _state_id, _gain, target_change_of(_change, NPC).status_data.get(_state_id))
    _state_detail.append(_row)
    _state_ok = _state_ok and _gain > 0 and _row[3] == _gain and cache.character_data[0].status_data[_state_id] == _base_pl.status_data[_state_id]
check("交互对象增加少量反感 / 羞耻：只加在交互对象身上，增量记进 target_change.status_data", _state_ok, _state_detail)
# add_time=0：上面这些结算器都不得改动任何人的数值，也不得往记录里写东西
_zero_bad = []
for _eid in (BE.DOWN_BOTH_SMALL_HIT_POINT, BE.DOWN_BOTH_SMALL_MANA_POINT, BE.DOWN_SELF_SMALL_HIT_POINT, BE.ADD_INTERACTION_FAVORABILITY, BE.ADD_SMALL_TRUST,
             BE.TARGET_ADD_SMALL_DISGUST, BE.TARGET_ADD_SMALL_SHY):
    _change = run_effect(_eid, 0, NPC, add_time=0)
    _same = all(pickle.dumps(getattr(cache.character_data[cid], attr)) == pickle.dumps(getattr(base, attr))
                for cid, base in ((0, _base_pl), (NPC, _base_npc)) for attr in ("hit_point", "mana_point", "favorability", "trust", "status_data"))
    _empty = pickle.dumps(_change.__dict__) == pickle.dumps(game_type.CharacterStatusChange().__dict__)
    if not (_same and _empty):
        _zero_bad.append((_eid, _same, _empty))
check("add_time=0 时上述结算器不改任何数值、也不往 change_data 里写记录", not _zero_bad, _zero_bad)
# 二段：玩家对 NPC 行为时，NPC 的二段「减少少量体力 / 气力」以 TargetChange 结算（固定 10 分钟 / 20 分钟的少量消耗）
restore_snapshot(BASELINE)
set_context(0, NPC)
_tc = game_type.TargetChange()
SECOND[SE.DOWN_SMALL_HIT_POINT](NPC, _tc)
SECOND[SE.DOWN_SMALL_MANA_POINT](NPC, _tc)
check("二段 减少少量体力 / 气力（TargetChange）：NPC 体力 -10、气力 -60，并记进 TargetChange",
      cache.character_data[NPC].hit_point - _hp_npc0 == -10 and cache.character_data[NPC].mana_point - _base_npc.mana_point == -60 and _tc.hit_point == -10 and _tc.mana_point == -60,
      (cache.character_data[NPC].hit_point - _hp_npc0, cache.character_data[NPC].mana_point - _base_npc.mana_point, _tc.hit_point, _tc.mana_point))

section("副作用")
check("全程没有任何写盘（写模式 open 与 os 的建 / 删 / 改名一律被拒绝并记录）", not WRITE_ATTEMPTS, WRITE_ATTEMPTS[:5])
check(f"隔离没有漏网：每 {AUDIT_EVERY} 次还原的全量比对里，没发现未经 cache.character_data 取用却被改过的角色", not ISOLATION_LEAKS,
      f"（角色id, 发现时的用例；改动发生在它之前 {AUDIT_EVERY} 个用例之内）{ISOLATION_LEAKS[:10]}")
builtins.open = _real_open
for _name, _func in _real_os_func.items():
    setattr(os, _name, _func)
print(f"\n  （总耗时 {time.time() - T_BEGIN:.1f}s；隔离：快照还原 {RESTORE_COST[0]} 次，共 {RESTORE_COST[1]:.1f}s）")
finish()
