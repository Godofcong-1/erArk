# -*- coding: UTF-8 -*-
"""前提系统冒烟与抽查：全部已注册前提在日常 / H中 / 深夜睡眠猥亵三种世界状态的玩家与NPC主体-对象组合、一周全时段与全部场景下可求值且返回合法权重；注册表与装饰器一一对应；权重、主体、交互对象、同场景、在场有意识者、时段、好感阈值、能力阈值、H状态、指令门槛等核心前提的语义翻转"""
import ast
import glob
import inspect
import math
import numbers
import time

from _bootstrap import *  # noqa: F401,F403

from Script.Design import basement, character, character_behavior, clothing  # noqa: E402

# ==== 范围说明 ====
# 1. 扫描对象是 constant.handle_premise_data 里注册的全部前提；CVP 综合数值前提不在注册表里，不扫
# 2. 排除规则（唯一的一条）：实现函数位于 Script.System.Education_System 下的前提，以及前提id含 "sex_class" 的性技实操课前提。
#    养成系统由 tools/tests/education 覆盖，本套件不扩展它的覆盖面；除此之外不排除任何前提，已知会抛异常的也照扫照报
# 3. 全部 fixture 都是成年角色（make_character 默认 stage=0、daughter=False），不给任何 fixture 成长阶段素质
# 4. 已确认的前提 BUG（KNOWN_BROKEN_PREMISE）照样每次都扫，但各自只记一条专门的断言（第 6 节），逐组合的扫描断言里不再重复计入：
#    这样逐组合断言只对「新出现」的问题报失败，不会被同一批老问题一直染红而失去回归作用。BUG 修好后专门断言自动转为通过，届时把条目从字典里删掉

P = constant_promise.Premise
""" 前提id常量 """
HP = handle_premise.handle_premise
""" 前提分发入口：游戏里口上 / AI / 指令都经它按id取处理函数 """
NPC_A = 3
""" NPC甲的角色id（取一个成年角色模板的id，get_npc_cloth 才能按模板给她穿衣） """
NPC_B = 10
""" NPC乙的角色id（同上） """
RANDOM_SEED = 20260907
""" init_attr / 换衣会用随机数，固定种子保证每次构建的世界一致 """
OFFICE = ["中枢", "博士办公室"]
""" 一间真实的办公室，与宿舍不同场景 """
CHILD_TALENT_ID_LIST = [7, 101, 102, 103, 104]
""" 未成年与成长阶段素质：fixture 一个都不能有 """
EDUCATION_MODULE_PREFIX = "Script.System.Education_System"
""" 养成系统模块前缀：实现函数在其下的前提不扫 """
WEIGHT_PREMISE = {P.HIGH_1: 1, P.HIGH_2: 2, P.HIGH_5: 5, P.HIGH_10: 10, P.HIGH_999: 999}
""" 权重前提 → 应返回的权重 """
KNOWN_BROKEN_PREMISE = {}
""" 已确认的前提 BUG：前提id → 问题说明（证据见各自专门断言的附带信息）。
本文件首轮扫出的 t_not_wear_hat（自己调自己无限递归）、t_turn_m_orgasm_g_3（读了不存在的 orgasm_count[8]）、
ask_hands_flexibility_exercises（Body_Manage_Requirement.csv 手部一行误写成 cid 35）已于 2026-11-18 修好并移出 """
KNOWN_DUPLICATE_PREMISE = {"kiss_0", "t_kiss_0"}
""" 已知的重复注册前提id：KISS_0 与 NO_FIRST_KISS、TARGET_KISS_0 与 TARGET_NO_FIRST_KISS 取了同一个id，含义相反，待维护者定 """
assert scene_str(OFFICE) in cache.scene_data


def is_out_of_scope(premise_id: str, func) -> bool:
    """
    判断一个前提是否落在排除规则里
    Keyword arguments:
    premise_id -- 前提id
    func -- 前提处理函数
    Return arguments:
    bool -- 属于养成系统（含性技实操课）时为 True
    """
    return getattr(func, "__module__", "").startswith(EDUCATION_MODULE_PREFIX) or "sex_class" in premise_id


SWEEP_ITEM_LIST = [(premise_id, func) for premise_id, func in constant.handle_premise_data.items() if not is_out_of_scope(premise_id, func)]
""" 扫描清单：(前提id, 处理函数)，按注册顺序 """
OUT_OF_SCOPE_LIST = sorted(premise_id for premise_id, func in constant.handle_premise_data.items() if is_out_of_scope(premise_id, func))
""" 被排除规则命中的前提id """


def flag(value) -> int:
    """
    把前提返回值归一成 0 / 1（布尔前提可能返回 bool、1 或 999 之类的权重）
    Keyword arguments:
    value -- 前提返回值
    Return arguments:
    int -- 成立为 1，不成立为 0
    """
    return 1 if value else 0


def is_valid_weight(value) -> bool:
    """
    判断前提返回值是否是调用方能消费的权重
    口上走 get_weight_from_premise_dict（真值判断后累加），AI 走 max(值, 0) 后累加并作 random.choices 的权重，指令只做真值判断：
       所以合法值是非负实数（bool / int / float 都行，hunger_ge_80 这类前提本就返回按饥饿值折算的浮点权重），None、负数、NaN、非数值都不合法
    Keyword arguments:
    value -- 前提返回值
    Return arguments:
    bool -- 合法时为 True
    """
    if isinstance(value, bool):
        return True
    if not isinstance(value, numbers.Real):
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    return value >= 0


def describe_exception(exc: BaseException) -> str:
    """
    把异常压成一行：类型、信息、最内层的文件与行号
    Keyword arguments:
    exc -- 异常对象
    Return arguments:
    str -- 一行描述
    """
    trace = exc.__traceback__
    while trace is not None and trace.tb_next is not None:
        trace = trace.tb_next
    where = ""
    if trace is not None:
        where = f" @ {os.path.basename(trace.tb_frame.f_code.co_filename)}:{trace.tb_lineno}"
    return f"{type(exc).__name__}: {str(exc)[:80]}{where}"


def sweep(subject_id: int) -> dict:
    """
    以某角色为主体求值扫描清单里的全部前提
    Keyword arguments:
    subject_id -- 主体角色id（前提的 character_id 参数）
    Return arguments:
    dict -- 有问题的前提：前提id → 问题描述（抛异常或返回值不合法）
    """
    problem_dict = {}
    for premise_id, func in SWEEP_ITEM_LIST:
        try:
            value = func(subject_id)
        except Exception as exc:  # 扫描就是要接住一切异常（含 RecursionError），逐个记下来
            problem_dict[premise_id] = describe_exception(exc)
            continue
        if not is_valid_weight(value):
            problem_dict[premise_id] = f"返回值不是非负实数权重：{value!r}"
    return problem_dict


known_broken_problem = {}
""" 已确认 BUG 的前提在扫描中实际出的问题：前提id → 首次出现的问题描述（含出现的状态） """


def split_known(problem_dict: dict, where: str) -> dict:
    """
    把已确认 BUG 的问题转记到 known_broken_problem，返回其余（新出现的）问题
    Keyword arguments:
    problem_dict -- 一次扫描的问题：前提id → 问题描述
    where -- 这次扫描所在的状态，记进首次出现的位置
    Return arguments:
    dict -- 不属于已确认 BUG 的问题
    """
    rest_dict = {}
    for premise_id, text in problem_dict.items():
        if premise_id in KNOWN_BROKEN_PREMISE:
            known_broken_problem.setdefault(premise_id, f"{text}（首见于 {where}）")
        else:
            rest_dict[premise_id] = text
    return rest_dict


def format_problem(problem_dict: dict, count: int = 20) -> str:
    """
    把问题字典格式化成断言失败时的附带信息
    Keyword arguments:
    problem_dict -- 前提id → 问题描述
    count -- 最多列出的条数
    Return arguments:
    str -- 附带信息
    """
    line_list = [f"{premise_id}: {text}" for premise_id, text in sorted(problem_dict.items())[:count]]
    more = f"\n      ……共 {len(problem_dict)} 个" if len(problem_dict) > count else ""
    return "\n      " + "\n      ".join(line_list) + more


def set_targets(target_map: dict):
    """
    按映射设置各角色的交互对象
    Keyword arguments:
    target_map -- 角色id → 交互对象id
    Return arguments:
    无
    """
    for character_id, target_id in target_map.items():
        cache.character_data[character_id].target_character_id = target_id


def forbidden_call(*args, **kwargs):
    """
    护栏桩：前提求值绝不该走到存档或主循环，真走到了就抛异常，由扫描记成该前提的问题
    Keyword arguments:
    args -- 任意位置参数
    kwargs -- 任意关键字参数
    Return arguments:
    无（总是抛 RuntimeError）
    """
    raise RuntimeError("前提求值触及了测试里禁止调用的函数（存档 / 主循环）")


# ==== 只读护栏：打在函数所在模块上（前提包里没有 from-import 这两个函数） ====
save_handle.establish_save = forbidden_call
character_behavior.init_character_behavior = forbidden_call

# ==== 全局前置：照新开游戏的流程补齐罗德岛与系统设置 ====
# 与 creator_character_flow.creator_character_panel 一致：先 basement.get_base_zero()，再做 first_bonus_and_setting_updata() 的同样几件事。
#    不直接导入那个 UI 流程模块：它经 io_init 会触发整套立绘预加载。
#    get_base_zero 补齐了 physical_examination_setting 以外的全部罗德岛字段（访客邀请、设施开放、当前位置等），缺了的话体检 / 访客 / 大地图类前提都会 KeyError
cache.rhodes_island = basement.get_base_zero()
for _first_bonus_cid in game_config.config_first_bonus:
    cache.first_bonus[_first_bonus_cid] = False
for _world_setting_cid in game_config.config_world_setting:
    cache.world_setting[_world_setting_cid] = 0
cache.all_system_setting = attr_calculation.get_system_setting_zero()
cache.rhodes_island.materials_resouce[1] = 20000
cache.rhodes_island.materials_resouce[11] = 20
cache.rhodes_island.materials_resouce[15] = 1000
cache.rhodes_island.materials_resouce[21] = 10
cache.rhodes_island.physical_examination_setting = attr_calculation.get_physical_exam_setting_zero()
cache.rhodes_island.confinement_training_setting = attr_calculation.get_confinement_training_setting_zero()
# 指令类型过滤：与 see_instruct_panel.SeeInstructPanel 首次打开时的初始化一致（面板类前提直接下标取它）
for _instruct_type in range(5):
    cache.instruct_type_filter[_instruct_type] = True
for _instruct_type in game_config.config_instruct_type:
    cache.instruct_type_filter.setdefault(_instruct_type, False)
cache.instruct_type_filter[6] = True


def build_world(now_time: datetime.datetime = DEFAULT_TIME):
    """
    重建日常世界：玩家与 NPC甲、NPC乙 同在一间宿舍、各自空闲，清掉上一个世界状态留下的全部痕迹
    角色属性走游戏自己的 character.init_attr（开局与 init_character 都调它，补齐道具、初次记录、行动信息、工作、娱乐、怀孕、角色设置等字段），
       NPC 再按角色模板穿衣、补上新角色模板都有的处女 / 无接吻经验素质
    Keyword arguments:
    now_time -- 游戏时间
    Return arguments:
    无
    """
    random.seed(RANDOM_SEED)
    set_time(now_time)
    # 玩家刚下过一条普通指令：最近输入为空时 last_cmd 类前提会落空返回 None，真实游戏里开局输入过名字后就不会再空
    cache.input_cache = [str(constant.Instruct.CHAT)]
    character.init_attr(0)
    move_to(0, SCENE_DORM)
    for cid in (NPC_A, NPC_B):
        remove_character(cid)
        npc_data = make_character(cid, cache.npc_tem_data[cid].Name)
        character.init_attr(cid)
        npc_data.adv = cid  # 真实角色的 adv 与角色id相同（init_character 按 adv 建角色）
        for talent_id in (0, 1, 2, 3, 4):
            npc_data.talent[talent_id] = 1  # 阴道 / 肛门 / 尿道 / 子宫处女与无接吻经验，新角色模板都带
        clothing.get_npc_cloth(cid)
    # init_attr 会按当前时间重设行为起始时间，再统一同步一次；交互对象复位成「没有交互对象」（指向自己）
    set_time(now_time)
    set_targets({0: 0, NPC_A: NPC_A, NPC_B: NPC_B})


def build_h_world():
    """
    H中世界：玩家与 NPC甲 在宿舍里正常位插入中，NPC乙 在旁边；NPC甲 是好感、信赖、能力、经验都已养成的恋人
    各项标记与游戏里对应结算写的相同：H_FLAG_TO_1 / T_H_FLAG_TO_1（is_h、see_pl_h）、PENIS_IN_T_VAGINA（insert_position=6）、DR_POSITION_NORMAL（current_sex_position=1）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    build_world()
    npc_a = cache.character_data[NPC_A]
    npc_a.favorability[0] = 50000
    npc_a.trust = 200
    for ability_id in npc_a.ability:
        npc_a.ability[ability_id] = 5
    for experience_id in npc_a.experience:
        npc_a.experience[experience_id] = 50
    for state_id in npc_a.status_data:
        npc_a.status_data[state_id] = 1000
    npc_a.talent[0] = 0  # 已非处女
    npc_a.talent[4] = 0  # 已有接吻经验
    npc_a.talent[203] = 1  # 恋人
    for character_data in (pl, npc_a):
        character_data.sp_flag.is_h = True
        character_data.sp_flag.see_pl_h = True
    npc_a.h_state.insert_position = 6
    pl.h_state.current_sex_position = 1
    pl.behavior.behavior_id = constant.Behavior.NORMAL_SEX
    clothing.get_all_cloth_off(NPC_A)
    cache.input_cache = [str(constant.Instruct.NORMAL_SEX)]
    set_targets({0: NPC_A, NPC_A: 0, NPC_B: NPC_A})


def build_night_world():
    """
    深夜世界：周二凌晨两点，NPC甲、NPC乙 在宿舍里睡着，玩家夜访并对 NPC甲 发起了睡眠猥亵
    入睡走游戏自己的两个状态机（START_SLEEP 置 sleep 标记并结算异常位，SLEEP 设睡眠行为与状态）；
       睡眠猥亵只照 handle_instruct.handle_sleep_obscenity 设同样的标记（unconscious_h=1 并结算异常位 5、6），不调用指令处理函数
    Keyword arguments:
    无
    Return arguments:
    无
    """
    build_world(datetime.datetime(2026, 9, 8, 2, 0))
    for cid in (NPC_A, NPC_B):
        constant.handle_state_machine_data[constant.StateMachine.START_SLEEP](cid)
        constant.handle_state_machine_data[constant.StateMachine.SLEEP](cid)
    cache.character_data[NPC_A].sp_flag.unconscious_h = 1
    handle_premise.settle_chara_unnormal_flag(NPC_A, 5)
    handle_premise.settle_chara_unnormal_flag(NPC_A, 6)
    set_targets({0: NPC_A})


# ==== 1. fixture 自检 ====
section("fixture")
build_world()
child_talent_list = [(cid, talent_id) for cid in (0, NPC_A, NPC_B) for talent_id in CHILD_TALENT_ID_LIST if cache.character_data[cid].talent.get(talent_id)]
check("三名 fixture 都是成年角色：没有未成年素质（7）与成长阶段素质（101~104）", not child_talent_list, child_talent_list)
dressed = all(any(cache.character_data[cid].cloth.cloth_wear.values()) for cid in (NPC_A, NPC_B))
same_room = all(cache.character_data[cid].position == SCENE_DORM for cid in (0, NPC_A, NPC_B))
check("两名 NPC 已按角色模板穿好衣服，三人同处一间真实宿舍", dressed and same_room)
# 世界构建自检：构建函数若因游戏改动不再设出预期状态，下面的扫描会悄悄退化成日常世界，先在这里拦住
build_h_world()
h_npc_data = cache.character_data[NPC_A]
h_state_text = (pl.sp_flag.is_h, h_npc_data.sp_flag.is_h, h_npc_data.h_state.insert_position, pl.h_state.current_sex_position, h_npc_data.favorability[0], pl.target_character_id)
check("H中世界已生效：玩家与NPC甲都在H中、正常位插入、NPC甲好感已养成、玩家对着NPC甲", h_state_text == (True, True, 6, 1, 50000, NPC_A), h_state_text)
build_night_world()
night_state_text = [(cid, cache.character_data[cid].sp_flag.sleep, cache.character_data[cid].state, cache.character_data[cid].behavior.behavior_id) for cid in (NPC_A, NPC_B)]
night_ready = all(row[1:] == (True, constant.CharacterStatus.STATUS_SLEEP, constant.Behavior.SLEEP) for row in night_state_text)
night_ready = night_ready and cache.character_data[NPC_A].sp_flag.unconscious_h == 1 and cache.game_time.hour == 2 and pl.target_character_id == NPC_A
check("深夜世界已生效：凌晨两点两名NPC经状态机入睡，NPC甲处于睡眠无意识，玩家对着NPC甲", night_ready, night_state_text)
print(f"  扫描 {len(SWEEP_ITEM_LIST)} 个前提；排除规则命中 {len(OUT_OF_SCOPE_LIST)} 个：{OUT_OF_SCOPE_LIST}")

# ==== 2. 注册表本身 ====
section("前提注册表")


def scan_decorated_premise() -> tuple:
    """
    用 AST 扫前提包里全部 @add_premise(...) 装饰器，取每个装饰器注册的前提id
    只认真正生效的装饰器：注释掉的、写在字符串里的都不算
    Keyword arguments:
    无
    Return arguments:
    dict -- 前提id → [(模块文件名, 常量名, 函数名), ...]
    list -- 无法解析成前提id的装饰器参数
    """
    premise_constant = {name: value for name, value in vars(constant_promise.Premise).items() if not name.startswith("_") and isinstance(value, str)}
    decorated_dict = {}
    unresolved_list = []
    for path in sorted(glob.glob(os.path.join(ROOT, "Script", "Design", "handle_premise", "*.py"))):
        with open(path, encoding="utf-8") as source_file:
            tree = ast.parse(source_file.read(), filename=path)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not (isinstance(decorator, ast.Call) and getattr(decorator.func, "id", None) == "add_premise" and decorator.args):
                    continue
                argument = decorator.args[0]
                if isinstance(argument, ast.Attribute) and argument.attr in premise_constant:
                    constant_name, premise_id = argument.attr, premise_constant[argument.attr]
                elif isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    constant_name, premise_id = repr(argument.value), argument.value
                else:
                    unresolved_list.append(f"{os.path.basename(path)}:{node.lineno} {ast.dump(argument)[:60]}")
                    continue
                decorated_dict.setdefault(premise_id, []).append((os.path.basename(path), constant_name, node.name))
    return decorated_dict, unresolved_list


def is_single_argument_callable(func) -> bool:
    """
    判断处理函数能否按 handler(character_id) 调用：可调用、恰好一个必填位置参数、没有必填的仅关键字参数
    Keyword arguments:
    func -- 前提处理函数
    Return arguments:
    bool -- 调用形状正确时为 True
    """
    if not callable(func):
        return False
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return False
    positional_kind = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    required_positional = [param for param in signature.parameters.values() if param.kind in positional_kind and param.default is param.empty]
    required_keyword = [param for param in signature.parameters.values() if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default is param.empty]
    return len(required_positional) == 1 and not required_keyword


registry = constant.handle_premise_data
decorated_premise, unresolved_decorator = scan_decorated_premise()
registry_diff = sorted(set(registry) ^ set(decorated_premise))
check("注册表与前提包里生效的 @add_premise 装饰器一一对应（没有漏注册的，也没有包外塞进来的键）", len(registry) > 0 and not registry_diff and not unresolved_decorator, (registry_diff[:20], unresolved_decorator[:5]))
bad_shape = sorted(premise_id for premise_id, func in registry.items() if not is_single_argument_callable(func))
check("注册的处理函数都能按 handler(character_id) 调用（可调用、恰好一个必填位置参数）", not bad_shape, bad_shape[:20])
# 两个常量取了同一个id、或同一个id被装饰两次时，后导入的模块静默顶替先导入的，先注册的那个实现永远调不到
duplicate_premise = {premise_id: entry_list for premise_id, entry_list in decorated_premise.items() if len(entry_list) > 1}
duplicate_text = {premise_id: (entry_list, "生效：" + registry[premise_id].__name__) for premise_id, entry_list in duplicate_premise.items() if premise_id in registry}
new_duplicate_text = {premise_id: text for premise_id, text in duplicate_text.items() if premise_id not in KNOWN_DUPLICATE_PREMISE}
new_duplicate_premise = [premise_id for premise_id in duplicate_premise if premise_id not in KNOWN_DUPLICATE_PREMISE]
check("每个前提id只由一个处理函数注册（重复注册时后导入者静默顶替先导入者；已知的两个除外）", not new_duplicate_premise, new_duplicate_text)
known_duplicate_text = {premise_id: text for premise_id, text in duplicate_text.items() if premise_id in KNOWN_DUPLICATE_PREMISE}
known_issue("kiss_0 / t_kiss_0 各只由一个处理函数注册", not [premise_id for premise_id in duplicate_premise if premise_id in KNOWN_DUPLICATE_PREMISE],
            "KISS_0（自己无接吻经验，handle_premise_other）与 NO_FIRST_KISS（博士已没有初吻，handle_premise_first）同取 kiss_0，t_kiss_0 同理；"
            "后导入的 handle_premise_first 生效，含义与前者相反，口上 / 事件里共 223 处引用，待定以哪个含义为准并给另一个换id",
            known_duplicate_text)

# ==== 3. 三种世界状态 × 主体-对象组合：全部前提可求值且返回合法权重 ====
WORLD_LIST = [
    (
        "日常",
        build_world,
        [
            ("玩家（无交互对象）", 0, {0: 0}),
            ("NPC甲→玩家", NPC_A, {NPC_A: 0}),
            ("玩家→NPC甲", 0, {0: NPC_A}),
            ("NPC甲→NPC乙", NPC_A, {NPC_A: NPC_B}),
        ],
    ),
    (
        "H中",
        build_h_world,
        [
            ("玩家→H中的NPC甲", 0, {}),
            ("H中的NPC甲→玩家", NPC_A, {}),
            ("旁观的NPC乙→H中的NPC甲", NPC_B, {}),
        ],
    ),
    (
        "深夜睡眠猥亵",
        build_night_world,
        [
            ("玩家→熟睡的NPC甲", 0, {}),
            ("熟睡的NPC甲（对象为自己）", NPC_A, {}),
        ],
    ),
]
""" 世界状态列表：(名称, 构建函数, [(组合名, 主体id, 额外的交互对象设置), ...]) """
for world_name, world_builder, combo_list in WORLD_LIST:
    section(f"全部前提可求值：{world_name}")
    world_start = time.time()
    world_builder()
    for combo_name, subject_id, target_map in combo_list:
        set_targets(target_map)
        problem = split_known(sweep(subject_id), f"{world_name}·{combo_name}")
        check(f"全部前提可求值且返回合法权重：{world_name}·{combo_name}", not problem, format_problem(problem))
    print(f"  用时 {time.time() - world_start:.1f}s")

# ==== 4. 一周全时段：时段 / 星期类前提的各个分支 ====
section("全部前提可求值：一周全时段")
sweep_start = time.time()
build_world()
set_targets({0: NPC_A, NPC_A: 0})
week_problem = {}
monday_midnight = DEFAULT_TIME.replace(hour=0, minute=30)
for hour_offset in range(7 * 24):
    now_time = monday_midnight + datetime.timedelta(hours=hour_offset)
    set_time(now_time)
    for subject_id, subject_name in ((0, "玩家→NPC甲"), (NPC_A, "NPC甲→玩家")):
        where = f"{now_time:%a %H:%M}·{subject_name}"
        for premise_id, text in split_known(sweep(subject_id), where).items():
            week_problem.setdefault(premise_id, f"{text}（首见于 {where}）")
check("全部前提在一周 7×24 个整点半时刻都可求值且返回合法权重（玩家↔NPC甲 双向）", not week_problem, format_problem(week_problem))
print(f"  用时 {time.time() - sweep_start:.1f}s")

# ==== 5. 全部场景：地点类前提逐场景读场景数据 ====
section("全部前提可求值：全部场景")
sweep_start = time.time()
build_world()
set_targets({0: NPC_A, NPC_A: 0})
scene_problem = {}
scene_path_str_list = list(cache.scene_data.keys())
for scene_path_str in scene_path_str_list:
    scene_path = map_handle.get_map_system_path_for_str(scene_path_str)
    move_to(0, scene_path)
    move_to(NPC_A, scene_path)
    for subject_id, subject_name in ((0, "玩家→NPC甲"), (NPC_A, "NPC甲→玩家")):
        where = f"{scene_path_str}·{subject_name}"
        for premise_id, text in split_known(sweep(subject_id), where).items():
            scene_problem.setdefault(premise_id, f"{text}（首见于 {where}）")
check(f"全部前提在全部 {len(scene_path_str_list)} 个场景里都可求值且返回合法权重（玩家与NPC甲同场景、双向）", not scene_problem, format_problem(scene_problem))
print(f"  用时 {time.time() - sweep_start:.1f}s")

# ==== 6. 已确认的前提 BUG：每个一条专门断言，修好前一直失败 ====
# 三个前提都不被现有口上 / 事件 / AI目标 / 指令当作前提引用，所以眼下的游戏不会走到；
#    但它们都在编辑器前提表（tools/ArkEditor/csv/Premise.csv）里可选，写进任何一条口上或事件就会让游戏在判定时直接崩
section("已确认的前提 BUG")
for broken_premise_id, broken_reason in KNOWN_BROKEN_PREMISE.items():
    check(f"前提 {broken_premise_id} 在全部扫描状态下都可求值——{broken_reason}", broken_premise_id not in known_broken_problem, known_broken_problem.get(broken_premise_id, ""))

# ==== 7. 核心前提语义抽查（按口上 / AI目标 / 事件 / 指令里的引用量挑选） ====
section("核心前提语义抽查")


def fresh_world() -> game_type.Character:
    """
    重建日常世界并返回 NPC甲
    Keyword arguments:
    无
    Return arguments:
    game_type.Character -- NPC甲
    """
    build_world()
    return cache.character_data[NPC_A]


# 6.1 权重前提：口上 / 事件里引用最多的一组（high_1 两万多处），权重就是它们的返回值
fresh_world()
weight_got = {premise_id: (HP(premise_id, 0), HP(premise_id, NPC_A)) for premise_id in WEIGHT_PREMISE}
weight_expect = {premise_id: (weight, weight) for premise_id, weight in WEIGHT_PREMISE.items()}
check("权重前提 high_1/2/5/10/999 对任何主体都恒返回各自的权重值", weight_got == weight_expect, weight_got)

# 6.2 主体是否玩家：sys_0 是口上 / 事件里引用最多的条件前提之一
fresh_world()
player_got = {"玩家": (flag(HP(P.IS_PLAYER, 0)), flag(HP(P.NO_PLAYER, 0))), "NPC甲": (flag(HP(P.IS_PLAYER, NPC_A)), flag(HP(P.NO_PLAYER, NPC_A)))}
check("sys_0 / sys_1（主体是否玩家）随主体翻转", player_got == {"玩家": (1, 0), "NPC甲": (0, 1)}, player_got)

# 6.3 交互对象：sys_2 是指令前提里引用最多的一个，sys_4 是口上常用条件
npc_a_data = fresh_world()
target_got = []
for target_id in (NPC_A, 0, NPC_B):
    npc_a_data.target_character_id = target_id
    target_got.append((target_id, flag(HP(P.HAVE_TARGET, NPC_A)), flag(HP(P.TARGET_IS_PLAYER, NPC_A))))
check("sys_2 / sys_4（有交互对象 / 交互对象是玩家）随 target_character_id 翻转", target_got == [(NPC_A, 0, 0), (0, 1, 1), (NPC_B, 1, 0)], target_got)

# 6.4 同场景：place_0 在口上、AI目标、事件里都被大量引用
fresh_world()
scene_got = [("同在宿舍", flag(HP(P.IN_PLAYER_SCENE, NPC_A)), flag(HP(P.NOT_IN_PLAYER_SCENE, NPC_A)))]
move_to(NPC_A, OFFICE)
scene_got.append(("NPC甲去了办公室", flag(HP(P.IN_PLAYER_SCENE, NPC_A)), flag(HP(P.NOT_IN_PLAYER_SCENE, NPC_A))))
move_to(0, OFFICE)
scene_got.append(("玩家也到了办公室", flag(HP(P.IN_PLAYER_SCENE, NPC_A)), flag(HP(P.NOT_IN_PLAYER_SCENE, NPC_A))))
check("place_0 / 不在玩家场景 随 move_to 翻转", [row[1:] for row in scene_got] == [(1, 0), (0, 1), (1, 0)], scene_got)

# 6.5 在场有意识者：place_someone_not_in_hidden_and_conscious 是引用量第二大的前提（通用口上一万六千多处）
npc_a_data = fresh_world()
move_to(0, OFFICE)
someone_got = [("玩家独处办公室", flag(HP(P.SCENE_SOMEONE_NOT_IN_HIDDEN_AND_CONSCIOUS, 0)))]
move_to(NPC_A, OFFICE)
someone_got.append(("清醒的NPC甲进来", flag(HP(P.SCENE_SOMEONE_NOT_IN_HIDDEN_AND_CONSCIOUS, 0))))
npc_a_data.sp_flag.unconscious_h = 1
handle_premise.settle_chara_unnormal_flag(NPC_A, 5)
handle_premise.settle_chara_unnormal_flag(NPC_A, 6)
someone_got.append(("NPC甲进入睡眠无意识", flag(HP(P.SCENE_SOMEONE_NOT_IN_HIDDEN_AND_CONSCIOUS, 0))))
check("在场有意识者前提随有人进场、进场者失去意识翻转", [row[1] for row in someone_got] == [0, 1, 0], someone_got)

# 6.6 时段：time_morning（4~7点）/ time_night（18~5点）是口上里最常用的时段前提，读的是行为起始时间
fresh_world()
clock_got = {}
for hour, minute in ((3, 59), (4, 0), (5, 59), (6, 0), (7, 59), (8, 0), (17, 59), (18, 0)):
    set_time(datetime.datetime(2026, 9, 7, hour, minute))
    clock_got[f"{hour:02d}:{minute:02d}"] = (flag(HP(P.TIME_MORNING, 0)), flag(HP(P.TIME_NIGHT, 0)))
clock_expect = {"03:59": (0, 1), "04:00": (1, 1), "05:59": (1, 1), "06:00": (1, 0), "07:59": (1, 0), "08:00": (0, 0), "17:59": (0, 0), "18:00": (0, 1)}
check("time_morning / time_night 在边界时刻随 set_time 翻转", clock_got == clock_expect, clock_got)

# 6.7 好感阈值：好感等级3的门槛取配置表，看的是「指令双方中NPC方对玩家」的好感；两边都不是玩家时两条都不成立
npc_a_data = fresh_world()
favorability_threshold = game_config.config_favorability_level[3].Favorability_point
favorability_got = []
for favorability_value in (favorability_threshold - 1, favorability_threshold):
    npc_a_data.favorability[0] = favorability_value
    set_targets({0: NPC_A, NPC_A: 0})
    favorability_got.append((favorability_value, "玩家→NPC甲", flag(HP(P.FAVORABILITY_GE_3, 0)), flag(HP(P.FAVORABILITY_LE_2, 0))))
    favorability_got.append((favorability_value, "NPC甲→玩家", flag(HP(P.FAVORABILITY_GE_3, NPC_A)), flag(HP(P.FAVORABILITY_LE_2, NPC_A))))
    set_targets({NPC_A: NPC_B})
    favorability_got.append((favorability_value, "NPC甲→NPC乙", flag(HP(P.FAVORABILITY_GE_3, NPC_A)), flag(HP(P.FAVORABILITY_LE_2, NPC_A))))
favorability_expect = [(0, 1), (0, 1), (0, 0), (1, 0), (1, 0), (0, 0)]
check(f"favorability_ge_3 / favorability_le_2 在好感 {favorability_threshold} 处翻转（两个视角一致，NPC之间都不成立）", [row[2:] for row in favorability_got] == favorability_expect, favorability_got)

# 6.8 能力阈值：t_desire_ge_5（交互对象欲望≥5）是口上里引用最多的能力前提
npc_a_data = fresh_world()
set_targets({0: NPC_A})
desire_got = {}
for ability_level in (4, 5):
    npc_a_data.ability[33] = ability_level
    desire_got[ability_level] = flag(HP(P.TARGET_DESIRE_GE_5, 0))
check(f"t_desire_ge_5（交互对象{game_config.config_ability[33].name}≥5）在 4→5 时翻转", desire_got == {4: 0, 5: 1}, desire_got)

# 6.9 H 状态：not_h / t_is_h 各被近两百条指令当作前提，is_h / not_h 看的是玩家与玩家的交互对象（与主体无关）
npc_a_data = fresh_world()
set_targets({0: NPC_A, NPC_A: 0})
h_got = {"进入H前": (flag(HP(P.IS_H, 0)), flag(HP(P.NOT_H, 0)), flag(HP(P.TARGET_IS_H, 0)), flag(HP(P.IS_H, NPC_A)))}
npc_a_data.sp_flag.is_h = True
h_got["NPC甲进入H后"] = (flag(HP(P.IS_H, 0)), flag(HP(P.NOT_H, 0)), flag(HP(P.TARGET_IS_H, 0)), flag(HP(P.IS_H, NPC_A)))
check("is_h / not_h / t_is_h 随交互对象的 H 标记翻转", h_got == {"进入H前": (0, 1, 0, 0), "NPC甲进入H后": (1, 0, 1, 1)}, h_got)

# 6.10 指令门槛：hp_g_1 与 tired_le_84 各挡着一百多条指令，是玩家能否行动的总开关
fresh_world()
gate_got = {}
for hit_point in (2, 1):
    pl.hit_point = hit_point
    gate_got[f"体力{hit_point}"] = flag(HP(P.HP_G_1, 0))
for tired_point in (134, 135):
    pl.tired_point = tired_point
    gate_got[f"疲劳{tired_point}/160"] = flag(HP(P.TIRED_LE_84, 0))
check("hp_g_1（体力>1）/ tired_le_84（疲劳≤84%）在门槛处翻转", gate_got == {"体力2": 1, "体力1": 0, "疲劳134/160": 1, "疲劳135/160": 0}, gate_got)

finish()
