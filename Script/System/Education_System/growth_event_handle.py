"""养成事件：公务事件系统里「教育区」这个部门的候选提供者（Plan 23 方案 §3.2）

通用的入队/出队/结算/履历都在 `Script/System/Official_Event_System/official_event_handle.py`，
这里只留养成专属的三件事：

    1. 候选从**玩家的女儿**里找，按成长阶段分桶（本阶段桶 + 跨阶段的通用桶）
    2. 互动对象从兄弟姐妹或同班同学里挑（事件里的 A2 于是指向本次事件的对手）
    3. 事件抬头写成「薇薇安 · 萝莉期第 38 天」

触发频率（方案 §3.4）：**按女儿逐个判定**，每个女儿每天最多 1 条、有 70% 的概率派到，
于是单个女儿约一两天一条，女儿越多每天的事件越多，但总量仍受公务事件系统的全局硬顶约束。
"""
import random
from types import FunctionType
from typing import List

from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.System.Education_System import growth_handle
from Script.System.Official_Event_System import official_event_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

GROWTH_EVENT_DEPARTMENT = 15
""" 养成事件所属的部门id：教育区（Facility.csv 中 type 为 -1 的区块cid） """

GROWTH_EVENT_DAILY_CHANCE = 70
""" 每个女儿每天入队一条养成事件的概率（百分比）。约1.4天一条，
    ⚠️ 不设成100：天天都有事要定夺会让养成变成日常打卡，留出空白日子反而更像在过日子 """

GROWTH_EVENT_DAILY_MAX_PER_CHILD = 1
""" 每个女儿每天最多入队的条数。⚠️ 这是**每孩**上限，全局上限在公务事件系统那边 """

GROWTH_EVENT_QUEUE_PER_CHILD = 4
""" 每个女儿为队列贡献的容量。女儿多的时候待办清单本来就该更长，否则后面的事件会被直接丢掉 """

STAGE_ANY = official_event_handle.SUB_KEY_ANY
""" 事件的 sub_key 取0时表示适用于全部成长阶段（101婴儿~103萝莉），⚠️ 不含已成年的104 """

STAGE_ALL_CHILD = (101, 102, 103)
""" sub_key 为 0 的事件实际覆盖的阶段。成年（104）只接 sub_key 明确写 104 的事件（如毕业典礼） """

GRADUATION_EVENT_UID = "通用1"
""" 毕业典礼的事件uid。uid由「文件名+cid」拼成，对应 data/official_event/通用.csv 的 cid=1 """

ADULT_MEMORIAL_EVENT_UID = "通用2"
""" 成年纪念的事件uid，紧跟在毕业典礼之后 """

SEMESTER_EVENT_SUB_KEY = 200
""" 期末事件的**保留**子桶键（对应 data/official_event/期末.csv 的 sub_key 列）。

    ⚠️ 绝不能用 0 或 101~104：get_candidate_event_list() 每天翻的正是
       (15, 0) 与 (15, 当前阶段) 这两个桶，期末事件写进去会天天被抽到。
       用一个日常池永远不会翻的键，期末事件就只能由学期结算显式推入。
    ⚠️ 于是期末事件的**阶段区分只能写进 premise**（CVP_A1_T|102_E_1 等），
       不能像日常养成事件那样靠 sub_key 分桶 """


def get_character_stage(character_id: int) -> int:
    """
    取角色当前的成长阶段素质id
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 101婴儿/102幼女/103萝莉/104少女，都不是则0
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for talent_id in growth_handle.CHILD_TALENT_SET:
        if character_data.talent.get(talent_id, 0):
            return talent_id
    return 0


def get_growth_event_character_list() -> List[int]:
    """
    取本次入队要遍历的角色列表

    ⚠️ 只看玩家的女儿：普通干员也可能因为选课被建出 child_growth（口径24），
       但养成事件是给孩子的，给成年干员派「第一次上课」只会显得莫名其妙
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 角色id列表
    """
    from Script.Design import handle_premise

    result = []
    for character_id in cache.npc_id_got:
        if not get_character_stage(character_id):
            continue
        if not handle_premise.handle_self_is_player_daughter(character_id):
            continue
        result.append(character_id)
    return result


def get_sibling_child_list(character_id: int) -> List[int]:
    """
    取同为孩子的兄弟姐妹列表

    ⚠️ 直接读既有的 relationship，不新建亲缘结构：同父同母、同父异母都算兄弟姐妹，
       判据是「父亲相同或母亲相同」
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    List[int] -- 兄弟姐妹的角色id列表
    """
    character_data: game_type.Character = cache.character_data[character_id]
    father_id = character_data.relationship.father_id
    mother_id = character_data.relationship.mother_id
    # ⚠️ 双亲未登记时是 -1，两个都没登记的角色会互相认成兄弟姐妹（世界设定的萝莉化会给一大批
    #    干员挂上萝莉素质，正好撞进这个洞），所以只认有效的双亲id
    result = []
    for other_id in cache.npc_id_got:
        if other_id == character_id:
            continue
        if not get_character_stage(other_id):
            continue
        other_data: game_type.Character = cache.character_data[other_id]
        if father_id >= 0 and other_data.relationship.father_id == father_id:
            result.append(other_id)
        elif mother_id >= 0 and other_data.relationship.mother_id == mother_id:
            result.append(other_id)
    return result


def get_classmate_list(character_id: int) -> List[int]:
    """
    取同班同学列表：个人课表上有重合节次的其他孩子

    ⚠️ 同学关系由课表反查，不落成字段——课表一改，同学关系就跟着变，
       存成字段反而要多一处同步点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    List[int] -- 同学的角色id列表
    """
    growth_data = cache.character_data[character_id].child_growth
    if growth_data is None or not growth_data.selected_course:
        return []
    # 把自己的课表压成 (星期, 节次, 课型, 目标) 的集合，再看别人有没有踩在同一个格子上
    self_slot = set()
    for week_day, day_data in growth_data.selected_course.items():
        for period, course in day_data.items():
            self_slot.add((week_day, period, course[0], str(course[1])))
    result = []
    for other_id in cache.npc_id_got:
        if other_id == character_id:
            continue
        if not get_character_stage(other_id):
            continue
        other_growth = cache.character_data[other_id].child_growth
        if other_growth is None or not other_growth.selected_course:
            continue
        for week_day, day_data in other_growth.selected_course.items():
            hit = False
            for period, course in day_data.items():
                if (week_day, period, course[0], str(course[1])) in self_slot:
                    result.append(other_id)
                    hit = True
                    break
            if hit:
                break
    return result


def get_event_partner(uid: str, character_id: int) -> int:
    """
    按事件前提挑一个互动对象

    没有互动对象需求时返回0（玩家）——事件里的 A2 于是指向博士，这是绝大多数事件的情形。
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    Return arguments:
    int -- 互动对象角色id，无则0
    """
    from Script.Core import constant_promise

    event_data = official_event_handle.get_event_data(uid)
    if event_data is None:
        return 0
    premise_text = event_data.get("premise", "")
    candidate = []
    if constant_promise.Premise.SELF_HAVE_SIBLING_CHILD in premise_text:
        candidate = get_sibling_child_list(character_id)
    elif constant_promise.Premise.SELF_HAVE_CLASSMATE in premise_text:
        candidate = get_classmate_list(character_id)
    if not candidate:
        return 0
    return random.choice(candidate)


def judge_stage_pass(uid: str, character_id: int) -> bool:
    """
    判定一条养成事件的适用阶段与孩子当前的成长阶段是否对得上
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    Return arguments:
    bool -- 阶段是否匹配
    """
    event_data = official_event_handle.get_event_data(uid)
    if event_data is None:
        return False
    sub_key = event_data.get("sub_key", STAGE_ANY)
    now_stage = get_character_stage(character_id)
    # sub_key 为 0 时覆盖全部未成年阶段，写了具体阶段就只派给该阶段
    if sub_key == STAGE_ANY:
        return now_stage in STAGE_ALL_CHILD
    return sub_key == now_stage


def get_candidate_event_list(character_id: int) -> List[list]:
    """
    列出这个孩子当前可触发的全部事件
    Keyword arguments:
    character_id -- 孩子角色id
    Return arguments:
    List[list] -- [事件uid str, 权重 int, 互动对象id int] 的列表
    """
    result = []
    now_stage = get_character_stage(character_id)
    # 只翻本阶段桶与通用桶，不遍历全表
    for sub_key in (STAGE_ANY, now_stage):
        for uid in game_config.config_official_event_by_sub_key.get((GROWTH_EVENT_DEPARTMENT, sub_key), ()):
            if not official_event_handle.judge_event_can_enqueue(uid, character_id):
                continue
            if not judge_stage_pass(uid, character_id):
                continue
            event_data = game_config.config_official_event[uid]
            partner_id = get_event_partner(uid, character_id)
            now_weight = official_event_handle.judge_premise_pass(event_data.get("premise", ""), character_id, partner_id)
            if not now_weight:
                continue
            # 配置权重与前提权重相乘：前提里的 high_ 系列照样能拉高稀有事件的出场率
            result.append([uid, official_event_handle.get_event_weight(uid) * now_weight, partner_id])
    return result


@official_event_handle.register_provider(GROWTH_EVENT_DEPARTMENT)
def get_today_growth_event_pick_list() -> List[dict]:
    """
    每日结算时给出今日的养成事件候选（已按女儿逐个节流）

    ⚠️ 遍历前先 shuffle：撞上公务事件系统的全局硬顶时，不打散的话永远是 id 小的那几个女儿吃满名额
    Keyword arguments:
    无
    Return arguments:
    List[dict] -- [{"uid": str, "chara_id": int, "partner_id": int}, ...]
    """
    character_list = get_growth_event_character_list()
    random.shuffle(character_list)
    result = []
    for character_id in character_list:
        # 每个女儿每天只有一定概率派到事件，于是单个女儿约一两天一条
        if random.randint(1, 100) > GROWTH_EVENT_DAILY_CHANCE:
            continue
        candidate = get_candidate_event_list(character_id)
        if not candidate:
            continue
        for _index in range(GROWTH_EVENT_DAILY_MAX_PER_CHILD):
            if not candidate:
                break
            weight_list = [one[1] for one in candidate]
            chosen = random.choices(candidate, weights=weight_list, k=1)[0]
            candidate.remove(chosen)
            result.append({"uid": chosen[0], "chara_id": character_id, "partner_id": chosen[2]})
    return result


@official_event_handle.register_capacity(GROWTH_EVENT_DEPARTMENT)
def get_growth_event_queue_capacity() -> int:
    """
    养成事件为公务队列贡献的容量：每个女儿 4 条
    Keyword arguments:
    无
    Return arguments:
    int -- 容量
    """
    return GROWTH_EVENT_QUEUE_PER_CHILD * len(get_growth_event_character_list())


@official_event_handle.register_title(GROWTH_EVENT_DEPARTMENT)
def get_growth_event_title(queue_data: dict) -> str:
    """
    取养成事件的抬头："薇薇安 · 萝莉期第 38 天"
    Keyword arguments:
    queue_data -- 队列元素dict
    Return arguments:
    str -- 抬头文本
    """
    from Script.System.Education_System import growth_panel
    from Script.System.Pregnancy_System import pregnancy_handle

    character_id = queue_data.get("chara_id", 0)
    if character_id not in cache.character_data:
        return official_event_handle.get_department_name(GROWTH_EVENT_DEPARTMENT)
    character_data: game_type.Character = cache.character_data[character_id]
    stage = get_character_stage(character_id)
    stage_name = _(growth_panel.STAGE_TALENT_NAME.get(stage, "少女"))
    # 成长天数由妊娠系统统一计算（含成长加速药），这里只取用不重算
    grow_day = pregnancy_handle.get_child_grow_day(character_id)
    return _("{0} · {1}期第 {2} 天").format(character_data.name, stage_name, grow_day)


def push_graduation_event(character_id: int):
    """
    成年结算时把毕业典礼与成年纪念插到队首

    ⚠️ **不做成玩家指令**（口径44）：一辈子只触发一次的叙事节点，
       做成指令要配行为、时长、口上、前提一整套，事件系统的一次性叙事正是为此而生
    ⚠️ 插队首而不是追加：成年是叙事上的大节点，让它排在一堆日常事件后面会很怪
    ⚠️ 幂等由成年结算本身的守卫保证（素质 103→104，一个孩子只会经过一次）
    Keyword arguments:
    character_id -- 刚成年的孩子角色id
    Return arguments:
    无
    """
    # 倒序插入，使毕业典礼最终排在成年纪念之前
    official_event_handle.push_official_event(ADULT_MEMORIAL_EVENT_UID, character_id, to_front=True)
    official_event_handle.push_official_event(GRADUATION_EVENT_UID, character_id, to_front=True)


def push_semester_event(character_id: int) -> bool:
    """
    学期结算时给某个孩子推一条期末事件（Plan 22 一期 §3.13 第2条）

    ⚠️ 事件是**按角色去重**的（official_event_handle.judge_event_done），
       同一个孩子不会重复遇到同一条期末事件。幼女到少女约十几个学期，
       所以池子迟早会被抽干——抽干时本函数只是返回 False，不报错也不重复派发
    Keyword arguments:
    character_id -- 孩子的角色id
    Return arguments:
    bool -- 是否成功入队
    """
    candidate = []
    for uid in game_config.config_official_event_by_sub_key.get(
            (GROWTH_EVENT_DEPARTMENT, SEMESTER_EVENT_SUB_KEY), ()):
        if not official_event_handle.judge_event_can_enqueue(uid, character_id):
            continue
        partner_id = get_event_partner(uid, character_id)
        now_weight = official_event_handle.judge_premise_pass(
            game_config.config_official_event[uid].get("premise", ""), character_id, partner_id)
        if not now_weight:
            continue
        candidate.append([uid, official_event_handle.get_event_weight(uid) * now_weight, partner_id])
    if not candidate:
        return False
    chosen = random.choices(candidate, weights=[one[1] for one in candidate], k=1)[0]
    return official_event_handle.push_official_event(chosen[0], character_id, chosen[2])


def push_semester_event_for_list(character_list: List[int]) -> int:
    """
    给一批刚出了成绩单的孩子各推一条期末事件
    Keyword arguments:
    character_list -- 孩子角色id列表
    Return arguments:
    int -- 实际入队的条数
    """
    push_count = 0
    for character_id in character_list:
        if push_semester_event(character_id):
            push_count += 1
    return push_count


def get_growth_event_queue_count(character_id: int) -> int:
    """
    取某个孩子待处理的养成事件条数（养成总览的「待处理」栏用）
    Keyword arguments:
    character_id -- 孩子角色id
    Return arguments:
    int -- 待处理条数
    """
    return official_event_handle.get_official_event_queue_count(character_id)
