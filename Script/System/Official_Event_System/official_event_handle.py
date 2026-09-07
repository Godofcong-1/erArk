"""公务事件系统的入队、出队与结算（Plan 23 方案 §3.2）

公务事件 = 玩家在博士办公室「处理公务」时需要逐条决断的事。
养成事件（教育区）只是它的一个部门分类，生产、医疗、人事、后勤、外勤、装备等部门同样往这里挂事件。

流程：
    每日结算 → check_new_day_official_event() 各部门的提供者各自节流后给出今日候选 → 入队
    → 玩家在博士办公室「处理公务」→ official_event_panel 逐条弹出决断
    → settle_official_event_option() 结算选项并写入履历

三条不可省的护栏：
    1. **入队节流**：不节流的话多女儿或多部门时一次公务会涌出十几条，玩家会直接失去判断意愿
    2. **不重复触发**：同一个角色不再遇到同一条事件（别的角色仍可各自触发同一条），
       靠出队结算时写入的履历来保证
    3. **交互对象还原**：判前提与跑结算时会临时把主体的 `target_character_id` 指向互动对象，
       必须放在 `finally` 里还原——那是行为循环在实时读的字段

⚠️ 本模块**不 import 任何部门**：部门在自己的模块里用 `register_provider` 反向注册，
   注册表是唯一的耦合点。未注册提供者的部门走默认提供者，于是新增一个部门的事件只要写 CSV。
"""
import random
from types import FunctionType
from typing import Callable, Dict, List, Optional

from Script.Core import cache_control, constant, game_type, get_text
from Script.Config import game_config
from Script.System.Official_Event_System import ri_value

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

OFFICIAL_EVENT_DAILY_MAX = 8
""" 全局每日入队硬顶（养成 + 各部门合计）。⚠️ 这是安全阀不是常态：
    常态由各部门提供者自己的节流决定，撞到这个数说明部门开得太多了 """

DEPARTMENT_EVENT_DAILY_MAX = 2
""" 走默认提供者的部门事件每日入队上限（全部门合计） """

OFFICIAL_EVENT_QUEUE_MAX_BASE = 12
""" 队列长度硬上限的基数。玩家可以很久不处理公务，不封顶的话回来时会面对一长串陈年旧事；
    满了就不再入队（丢弃新事件而非挤掉旧事件，旧的至少还有上下文） """

OFFICIAL_EVENT_QUEUE_MAX_EXTRA = 6
""" 队列上限里留给部门事件的固定余量，各部门的额外容量在这之上累加 """

SUBJECT_NONE = 0
""" 事件主体：无主体，部门事务，结算只落在罗德岛全局数值上 """

SUBJECT_CHARACTER = 1
""" 事件主体：角色，A1指向该角色 """

SUB_KEY_ANY = 0
""" 分类内子桶键取0时表示「本分类的通用事件」，具体语义由该部门的提供者解释 """

EVENT_PROVIDER: Dict[int, Callable] = {}
""" 部门id -> 今日候选提供者。提供者自行节流，返回
    [{"uid": str, "chara_id": int, "partner_id": int}, ...]，本模块只负责汇总与封顶 """

EVENT_CAPACITY: Dict[int, Callable] = {}
""" 部门id -> 队列容量提供者，返回该部门需要的额外队列容量int。
    养成用它把上限随女儿数放宽——女儿多的时候队列本来就该更长 """

EVENT_TITLE: Dict[int, Callable] = {}
""" 部门id -> 事件抬头提供者，入参为队列元素dict，返回抬头str。未注册则画「公务事件·部门名」 """


def register_provider(department: int) -> Callable:
    """
    装饰器：把一个部门的今日候选提供者注册进来
    Keyword arguments:
    department -- 部门id（Facility.csv 中 type 为 -1 的区块cid）
    Return arguments:
    Callable -- 装饰器
    """

    def decorator(func: Callable) -> Callable:
        EVENT_PROVIDER[department] = func
        return func

    return decorator


def register_capacity(department: int) -> Callable:
    """
    装饰器：注册一个部门的队列容量提供者
    Keyword arguments:
    department -- 部门id
    Return arguments:
    Callable -- 装饰器
    """

    def decorator(func: Callable) -> Callable:
        EVENT_CAPACITY[department] = func
        return func

    return decorator


def register_title(department: int) -> Callable:
    """
    装饰器：注册一个部门的事件抬头提供者
    Keyword arguments:
    department -- 部门id
    Return arguments:
    Callable -- 装饰器
    """

    def decorator(func: Callable) -> Callable:
        EVENT_TITLE[department] = func
        return func

    return decorator


def init_provider():
    """
    载入各部门的候选提供者

    ⚠️ 在函数内 import：提供者住在 Script/System 的各部门包里，模块级 import 会绕出循环导入。
       这是本模块与各部门之间**唯一**的接触点，新增部门时在这里加一行即可（不加也能用默认提供者）。
    Keyword arguments:
    无
    Return arguments:
    无
    """
    from Script.System.Education_System import growth_event_handle  # noqa: F401  养成事件（教育区15）


def get_event_data(uid: str) -> Optional[dict]:
    """
    取一条公务事件的配置
    Keyword arguments:
    uid -- 事件uid
    Return arguments:
    Optional[dict] -- 事件原始dict，不存在则None
    """
    return game_config.config_official_event.get(uid)


def get_event_department(uid: str) -> int:
    """
    取一条公务事件所属的部门id
    Keyword arguments:
    uid -- 事件uid
    Return arguments:
    int -- 部门id，事件不存在则-1
    """
    event_data = get_event_data(uid)
    if event_data is None:
        return -1
    return int(event_data.get("department", 0))


def get_department_name(department: int) -> str:
    """
    取部门的中文名（直接查既有的设施配置，不另维护一套分类名）
    Keyword arguments:
    department -- 部门id
    Return arguments:
    str -- 部门名，查不到时为「公务」
    """
    if department in game_config.config_facility:
        return game_config.config_facility[department].name
    return _("公务")


def get_queue() -> list:
    """
    取待处理的公务事件队列
    Keyword arguments:
    无
    Return arguments:
    list -- 队列本体（可原地修改）
    """
    return cache.rhodes_island.official_event_queue


def get_queue_max() -> int:
    """
    取当前的队列长度硬上限

    ⚠️ 上限随各部门声明的容量放宽：养三个女儿的玩家本来就该有更长的待办清单，
       用一个固定的12会让后面的事件全被丢掉
    Keyword arguments:
    无
    Return arguments:
    int -- 队列长度上限
    """
    extra = 0
    for func in EVENT_CAPACITY.values():
        try:
            extra += int(func())
        except Exception:
            # 某个部门的容量算错不该拖垮整条入队链，退回基数即可
            continue
    return max(OFFICIAL_EVENT_QUEUE_MAX_BASE, OFFICIAL_EVENT_QUEUE_MAX_EXTRA + extra)


def get_premise_set(premise_text: str) -> set:
    """
    把CSV里 & 连接的前提串拆成集合
    Keyword arguments:
    premise_text -- 前提串
    Return arguments:
    set -- 前提id集合，空串返回空集合
    """
    if not premise_text:
        return set()
    return {one.strip() for one in premise_text.split("&") if one.strip()}


def judge_premise_pass(premise_text: str, character_id: int = 0, partner_id: int = 0) -> int:
    """
    判定一组前提是否成立，返回总权重

    ⚠️ 判定期间临时把主体的交互对象指向 partner_id：前提里的 A2 与 target_* 系列
       于是指向本次事件的互动对象（无互动对象时为博士），判完立刻还原，
       不能留着不还——交互对象是行为循环在用的实时字段
    Keyword arguments:
    premise_text -- & 连接的前提串
    character_id -- 主体角色id，无主体的部门事件传0（即以博士为判定主体）
    partner_id -- 互动对象角色id，默认0为玩家
    Return arguments:
    int -- 总权重，0为不通过
    """
    from Script.Design import handle_premise

    premise_set = get_premise_set(premise_text)
    if not premise_set:
        return 1
    if character_id not in cache.character_data:
        return 0
    character_data: game_type.Character = cache.character_data[character_id]
    old_target_id = character_data.target_character_id
    character_data.target_character_id = partner_id
    try:
        now_weight, _unused = handle_premise.get_weight_from_premise_dict(premise_set, character_id, {}, unconscious_pass_flag=True)
    finally:
        character_data.target_character_id = old_target_id
    return now_weight


def judge_event_already_in_queue(uid: str, character_id: int) -> bool:
    """
    判定同一个主体的同一条事件是否已在队列里等着
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id（无主体为0）
    Return arguments:
    bool -- 是否已在队列中
    """
    for one in get_queue():
        if one.get("uid") == uid and one.get("chara_id") == character_id:
            return True
    return False


def get_history_key(uid: str, character_id: int) -> str:
    """
    取全局履历里的键：无主体事件用uid本身，有主体但没有养成数据的角色用 uid@角色id
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id
    Return arguments:
    str -- 履历键
    """
    if not character_id:
        return uid
    return f"{uid}@{character_id}"


def judge_event_done(uid: str, character_id: int) -> bool:
    """
    判定这个主体是否已经经历过这条事件

    ⚠️ **所有**事件都按角色去重（Plan 23 方案 §3.3），不再只查一次性事件：
       同一个孩子不会再遇到同一件事，但别的孩子仍可各自触发同一条
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id（无主体为0）
    Return arguments:
    bool -- 是否已触发过
    """
    if character_id and character_id in cache.character_data:
        growth_data = cache.character_data[character_id].child_growth
        if growth_data is not None:
            return uid in growth_data.event_history
    return get_history_key(uid, character_id) in cache.rhodes_island.official_event_history


def record_event_done(uid: str, character_id: int, option_index: int):
    """
    把这次决断写进履历（有养成数据的角色记在自己身上，其余记进罗德岛的全局履历）
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id（无主体为0）
    option_index -- 玩家选定的选项序号
    Return arguments:
    无
    """
    now_record = {"time": cache.game_time, "choice": option_index}
    if character_id and character_id in cache.character_data:
        growth_data = cache.character_data[character_id].child_growth
        if growth_data is not None:
            growth_data.event_history[uid] = now_record
            return
    cache.rhodes_island.official_event_history[get_history_key(uid, character_id)] = now_record


def judge_event_can_enqueue(uid: str, character_id: int = 0) -> bool:
    """
    判定一条事件当前能否派给这个主体（不含部门自己的桶筛选、权重与随机）
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id（无主体为0）
    Return arguments:
    bool -- 能否入队
    """
    if get_event_data(uid) is None:
        return False
    if judge_event_done(uid, character_id):
        return False
    if judge_event_already_in_queue(uid, character_id):
        return False
    return True


def get_event_weight(uid: str) -> int:
    """
    取一条事件的配置权重
    Keyword arguments:
    uid -- 事件uid
    Return arguments:
    int -- 权重，至少为1
    """
    event_data = get_event_data(uid)
    if event_data is None:
        return 1
    try:
        return max(1, int(event_data.get("weight", 1)))
    except (TypeError, ValueError):
        # 权重写成了非数字，退回1而不是崩在每日结算里
        return 1


def push_official_event(uid: str, character_id: int = 0, partner_id: int = 0, to_front: bool = False) -> bool:
    """
    把一条事件推进待处理队列
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id，无主体为0
    partner_id -- 互动对象角色id，默认0为玩家
    to_front -- 是否插到队首（一次性的叙事节点用，如毕业典礼）
    Return arguments:
    bool -- 是否成功入队
    """
    if get_event_data(uid) is None:
        return False
    queue = get_queue()
    if len(queue) >= get_queue_max():
        return False
    queue_data = {
        "uid": uid,
        "department": get_event_department(uid),
        "chara_id": character_id,
        "partner_id": partner_id,
        "add_time": cache.game_time,
    }
    if to_front:
        queue.insert(0, queue_data)
    else:
        queue.append(queue_data)
    return True


def get_default_department_pick_list() -> List[dict]:
    """
    默认提供者：给没有注册专属提供者的部门挑今日候选

    以博士（角色0）为判定主体，按前提筛选、按权重加权抽取，最多 DEPARTMENT_EVENT_DAILY_MAX 条。
    ⚠️ 这条路径是「新增一个部门只写CSV」的兑现处：不写任何代码也能让部门事件跑起来
    Keyword arguments:
    无
    Return arguments:
    List[dict] -- [{"uid": str, "chara_id": int, "partner_id": int}, ...]
    """
    candidate = []
    for department in game_config.config_official_event_by_department:
        if department in EVENT_PROVIDER:
            continue
        for uid in game_config.config_official_event_by_department[department]:
            if not judge_event_can_enqueue(uid, 0):
                continue
            event_data = game_config.config_official_event[uid]
            now_weight = judge_premise_pass(event_data.get("premise", ""), 0, 0)
            if not now_weight:
                continue
            candidate.append([uid, get_event_weight(uid) * now_weight])
    result = []
    for _index in range(DEPARTMENT_EVENT_DAILY_MAX):
        if not candidate:
            break
        weight_list = [one[1] for one in candidate]
        chosen = random.choices(candidate, weights=weight_list, k=1)[0]
        candidate.remove(chosen)
        result.append({"uid": chosen[0], "chara_id": 0, "partner_id": 0})
    return result


def check_new_day_official_event():
    """
    每日结算时筛选并入队今日的公务事件

    各部门的提供者**自行节流**后给出今日候选，这里只负责汇总、打散与封顶：
    ⚠️ 打散是必要的——不打散的话撞上全局硬顶时，永远是注册得早的那个部门吃满名额
    Keyword arguments:
    无
    Return arguments:
    无
    """
    if not game_config.config_official_event:
        return
    init_provider()
    pick_list = []
    for department in EVENT_PROVIDER:
        try:
            now_pick = EVENT_PROVIDER[department]()
        except Exception as now_error:
            print(f"\ndebug 公务事件的部门{department}候选提供者报错：{now_error}\n")
            continue
        if now_pick:
            pick_list.extend(now_pick)
    pick_list.extend(get_default_department_pick_list())
    if not pick_list:
        return
    random.shuffle(pick_list)
    for one in pick_list[:OFFICIAL_EVENT_DAILY_MAX]:
        push_official_event(one["uid"], one.get("chara_id", 0), one.get("partner_id", 0))


def clean_official_event_queue():
    """
    清掉队列里已经失效的项

    失效的三种：主体角色已不在角色表里（跨版本存档、周目切换）、事件已从配置里删掉、
    互动对象已不存在（后者不丢事件，退回博士即可，否则口上转换与结算会 KeyError 打断公务流程）。
    ⚠️ 静默处理，不报错也不提示——玩家对一条自己从没见过的事件消失没有感知，
       但一个 KeyError 会直接打断公务流程
    Keyword arguments:
    无
    Return arguments:
    无
    """
    queue = get_queue()
    valid = []
    changed = False
    for one in queue:
        if not isinstance(one, dict):
            changed = True
            continue
        if one.get("chara_id", 0) not in cache.character_data:
            changed = True
            continue
        if one.get("uid") not in game_config.config_official_event:
            changed = True
            continue
        if one.get("partner_id", 0) not in cache.character_data:
            one["partner_id"] = 0
            changed = True
        if "department" not in one:
            one["department"] = get_event_department(one["uid"])
            changed = True
        valid.append(one)
    if changed:
        cache.rhodes_island.official_event_queue = valid


def get_official_event_queue_count(character_id: int = -1) -> int:
    """
    取当前待处理的公务事件条数（清理失效项后）
    Keyword arguments:
    character_id -- 只数这个主体的条数，-1为全部
    Return arguments:
    int -- 待处理条数
    """
    clean_official_event_queue()
    if character_id < 0:
        return len(get_queue())
    return len([one for one in get_queue() if one.get("chara_id") == character_id])


def pop_official_event() -> Optional[dict]:
    """
    取出队首的一条待处理事件
    Keyword arguments:
    无
    Return arguments:
    Optional[dict] -- 队列元素，队列为空则None
    """
    clean_official_event_queue()
    queue = get_queue()
    if not queue:
        return None
    return queue.pop(0)


def get_option_list(uid: str, character_id: int = 0, partner_id: int = 0) -> List[dict]:
    """
    取一条事件的选项列表，并判定各选项的前提

    ⚠️ 不满足前提的选项**置灰保留**而不是隐藏：让玩家看见「这里本来有更好的选择，
       但我没养到」，隐藏了就等于这条线从没存在过
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id
    partner_id -- 互动对象角色id
    Return arguments:
    List[dict] -- [{"index": 选项序号1~4, "text": 选项文本, "tip": 后果提示,
                    "can_use": 是否可选, "reason": 不可选的原因, "effect": 结算串}]
    """
    event_data = get_event_data(uid)
    if event_data is None:
        return []
    result = []
    for index in range(1, 5):
        option_text = event_data.get(f"option_{index}", "")
        # 空着的选项列在构建时已被删掉，取不到就是这条事件没有这个选项
        if not option_text:
            continue
        can_use = bool(judge_premise_pass(event_data.get(f"option_{index}_premise", ""), character_id, partner_id))
        result.append(
            {
                "index": index,
                "text": option_text,
                "tip": event_data.get(f"option_{index}_tip", ""),
                "can_use": can_use,
                "reason": event_data.get(f"option_{index}_reason", ""),
                "effect": event_data.get(f"option_{index}_effect", ""),
            }
        )
    return result


def handle_ri_effect(effect_list: List[str]):
    """
    执行一条罗德岛全局数值的结算（CVE_RI_<类型>_<G/L/E>_<值>）

    ⚠️ 不去扩 settle_behavior 的主体判别：那里的属性映射是 getattr(character_data, ...)
       硬绑角色对象的，加一个全局主体要同时改主体判别、change_data 记录与Web数值收集三处。
       公务事件的结算串本来就由本模块逐项分发，在这里认前缀成本最低（方案 §3.6）
    Keyword arguments:
    effect_list -- token 去掉 CVE_ 前缀后的分段，形如 ["RI", "R|13", "L", "100"]
    Return arguments:
    无
    """
    if len(effect_list) < 4:
        print(f"\ndebug 公务事件的全局结算{effect_list}段数不足，请检查结算是否正确\n")
        return
    type_text = effect_list[1]
    operator_text = effect_list[2]
    try:
        value = float(effect_list[3])
    except (TypeError, ValueError):
        print(f"\ndebug 公务事件的全局结算{effect_list}的数值不是数字\n")
        return
    if operator_text == "G":
        ri_value.change_ri_value(type_text, value)
    elif operator_text == "L":
        ri_value.change_ri_value(type_text, -value)
    elif operator_text == "E":
        ri_value.set_ri_value(type_text, value)
    else:
        print(f"\ndebug 公务事件的全局结算{effect_list}的运算符{operator_text}不支持\n")


def handle_effect_text(effect_text: str, character_id: int = 0, partner_id: int = 0):
    """
    执行一串 & 连接的结算

    支持三类写法：
        CVE_A1/A2/A3...  角色数值结算（含养成数值 CVE_A1_Growth|N_G_值），走既有的综合结算
        CVE_RI_...       罗德岛全局数值结算（本系统新增，方案 §3.6）
        纯数字            Behavior_Effect 表里的结算函数id，复杂效果走这条
    ⚠️ 结算全程把主体的交互对象指向 partner_id，使 A2 指向本次事件的互动对象；结算完立刻还原
    ⚠️ 结算用的 change_data 是一次性的、不往界面上抛数字：
       事件的后果提示写方向不写数值，抛出「好感+8」会把决断变成算数题
    Keyword arguments:
    effect_text -- & 连接的结算串
    character_id -- 主体角色id，无主体为0
    partner_id -- 互动对象角色id
    Return arguments:
    无
    """
    from Script.Design import settle_behavior

    if not effect_text:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    old_target_id = character_data.target_character_id
    character_data.target_character_id = partner_id
    change_data = game_type.CharacterStatusChange()
    try:
        for effect in effect_text.split("&"):
            effect = effect.strip()
            if not effect:
                continue
            if effect.startswith("CVE"):
                effect_list = effect.split("_")[1:]
                # 全局数值的主体是 RI，必须先认出来，否则会被当成角色主体去查 character_data
                if effect_list and effect_list[0] == "RI":
                    handle_ri_effect(effect_list)
                else:
                    settle_behavior.handle_comprehensive_value_effect(character_id, effect_list, change_data)
            elif effect.isdigit():
                handler = constant.settle_behavior_effect_data.get(int(effect))
                if handler is not None:
                    handler(character_id, 1, change_data, cache.game_time)
                else:
                    print(f"\ndebug 公务事件的结算{effect}不存在，请检查结算是否正确\n")
            else:
                print(f"\ndebug 公务事件的结算{effect}格式不正确，请检查结算是否正确\n")
    finally:
        character_data.target_character_id = old_target_id


def settle_official_event_option(uid: str, character_id: int, partner_id: int, option_index: int):
    """
    结算玩家选定的选项，并把这次决断写进履历

    ⚠️ 无论事件标没标里程碑都写履历：它既是「同一个角色不重复触发」的依据，
       也是养成总览里履历栏的内容来源
    Keyword arguments:
    uid -- 事件uid
    character_id -- 主体角色id
    partner_id -- 互动对象角色id
    option_index -- 玩家选定的选项序号（1~4）
    Return arguments:
    无
    """
    for option in get_option_list(uid, character_id, partner_id):
        if option["index"] != option_index:
            continue
        handle_effect_text(option["effect"], character_id, partner_id)
        break
    record_event_done(uid, character_id, option_index)
