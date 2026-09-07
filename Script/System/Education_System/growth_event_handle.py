"""养成事件系统的入队、出队与结算（Plan 22 三期 §3.7）

养成事件与既有事件系统（`Script/Design/event.py`）**触发模型不同**：
既有事件是「做了某个行为时触发」，养成事件是「孩子的成长状态满足条件时，按日入队」。
所以这里复用它的数据形态（uid / premise / effect）与 CVP/CVE token，但另起一套触发逻辑。

流程：
    每日结算 → check_new_day_growth_event() 按前提筛选、加权随机入队（每日最多2条）
    → 玩家在博士办公室「处理公务」→ growth_event_panel 逐条弹出决断
    → settle_growth_event_option() 结算选项并写入该孩子的 event_history

⚠️ 两条不可省的护栏：
   1. **入队节流**：多孩时不节流，一次公务会涌出十几条，玩家会直接失去判断意愿（口径32）
   2. **一次性事件的幂等**：`once == 1` 的事件入队前查 `event_history`，出队结算时写入
"""
import random
from types import FunctionType
from typing import List, Optional

from Script.Core import cache_control, constant, game_type, get_text
from Script.Config import game_config
from Script.System.Education_System import growth_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

GROWTH_EVENT_DAILY_MAX = 2
""" 每日入队上限（口径32）。⚠️ 这是**全局**上限不是每孩上限：养三个孩子也只会每天多出两条待决断 """

GROWTH_EVENT_QUEUE_MAX = 12
""" 队列长度硬上限。玩家可以很久不处理公务，不封顶的话回来时会面对一长串陈年旧事；
    满了就不再入队（丢弃新事件而非挤掉旧事件，旧的至少还有上下文） """

STAGE_ANY = 0
""" 事件的 stage 列取0时表示适用于全部成长阶段（101婴儿~103萝莉），⚠️ 不含已成年的104 """

STAGE_ALL_CHILD = (101, 102, 103)
""" stage 为 0 的事件实际覆盖的阶段。成年（104）只接 stage 明确写 104 的事件（如毕业典礼） """


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
    取同为孩子的兄弟姐妹列表（方案 §3.25）

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
    取同班同学列表：个人课表上有重合节次的其他孩子（方案 §3.25）

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

    event_data = game_config.config_growth_event.get(uid)
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


def judge_premise_pass(premise_text: str, character_id: int, partner_id: int = 0) -> int:
    """
    判定一组前提对该孩子是否成立，返回总权重

    ⚠️ 判定期间临时把孩子的交互对象指向 partner_id：前提里的 A2 与 target_* 系列
       于是指向本次事件的互动对象（无互动对象时为博士），判完立刻还原，
       不能留着不还——孩子的交互对象是行为循环在用的实时字段
    Keyword arguments:
    premise_text -- & 连接的前提串
    character_id -- 孩子角色id
    partner_id -- 互动对象角色id，默认0为玩家
    Return arguments:
    int -- 总权重，0为不通过
    """
    from Script.Design import handle_premise

    premise_set = get_premise_set(premise_text)
    if not premise_set:
        return 1
    character_data: game_type.Character = cache.character_data[character_id]
    old_target_id = character_data.target_character_id
    character_data.target_character_id = partner_id
    try:
        now_weight, _unused = handle_premise.get_weight_from_premise_dict(
            premise_set, character_id, {}, unconscious_pass_flag=True)
    finally:
        character_data.target_character_id = old_target_id
    return now_weight


def judge_event_already_in_queue(uid: str, character_id: int) -> bool:
    """
    判定同一个孩子的同一条事件是否已在队列里等着
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    Return arguments:
    bool -- 是否已在队列中
    """
    for one in cache.rhodes_island.growth_event_queue:
        if one.get("uid") == uid and one.get("chara_id") == character_id:
            return True
    return False


def judge_event_can_enqueue(uid: str, character_id: int) -> bool:
    """
    判定一条事件当前能否派给这个孩子（不含权重与随机）

    ⚠️ 幂等在这里：`once == 1` 的事件查过 `event_history` 就不再入队（方案 §7-2）
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    Return arguments:
    bool -- 能否入队
    """
    event_data = game_config.config_growth_event.get(uid)
    if event_data is None:
        return False
    # 阶段筛选：stage 为 0 时覆盖全部未成年阶段，写了具体阶段就只派给该阶段
    stage = event_data.get("stage", STAGE_ANY)
    now_stage = get_character_stage(character_id)
    if stage == STAGE_ANY:
        if now_stage not in STAGE_ALL_CHILD:
            return False
    elif stage != now_stage:
        return False
    # 一次性事件的幂等
    if event_data.get("once", 0):
        growth_data = cache.character_data[character_id].child_growth
        if growth_data is not None and uid in growth_data.event_history:
            return False
    # 同一条事件不重复排队
    if judge_event_already_in_queue(uid, character_id):
        return False
    return True


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
    for stage in (STAGE_ANY, now_stage):
        for uid in game_config.config_growth_event_by_stage.get(stage, ()):
            if not judge_event_can_enqueue(uid, character_id):
                continue
            event_data = game_config.config_growth_event[uid]
            partner_id = get_event_partner(uid, character_id)
            now_weight = judge_premise_pass(event_data.get("premise", ""), character_id, partner_id)
            if not now_weight:
                continue
            # 配置权重与前提权重相乘：前提里的 high_ 系列照样能拉高稀有事件的出场率
            result.append([uid, max(1, int(event_data.get("weight", 1))) * now_weight, partner_id])
    return result


def push_growth_event(uid: str, character_id: int, partner_id: int = 0, to_front: bool = False) -> bool:
    """
    把一条事件推进待处理队列
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    partner_id -- 互动对象角色id，默认0为玩家
    to_front -- 是否插到队首（阶段跃迁类事件用，如毕业典礼）
    Return arguments:
    bool -- 是否成功入队
    """
    if uid not in game_config.config_growth_event:
        return False
    queue = cache.rhodes_island.growth_event_queue
    if len(queue) >= GROWTH_EVENT_QUEUE_MAX:
        return False
    now_data = {
        "uid": uid,
        "chara_id": character_id,
        "partner_id": partner_id,
        "add_time": cache.game_time,
    }
    if to_front:
        queue.insert(0, now_data)
    else:
        queue.append(now_data)
    return True


GRADUATION_EVENT_UID = "通用1"
""" 毕业典礼的事件uid（方案 §3.26）。uid由「文件名+cid」拼成，对应 data/growth_event/通用.csv 的 cid=1 """

ADULT_MEMORIAL_EVENT_UID = "通用2"
""" 成年纪念的事件uid（方案 §3.26），紧跟在毕业典礼之后 """


def push_graduation_event(character_id: int):
    """
    成年结算时把毕业典礼与成年纪念插到队首（方案 §3.26）

    ⚠️ **不做成玩家指令**（口径44）：一辈子只触发一次的叙事节点，
       做成指令要配行为、时长、口上、前提一整套，事件系统的一次性叙事正是为此而生
    ⚠️ 插队首而不是追加：成年是叙事上的大节点，让它排在一堆日常事件后面会很怪
    ⚠️ 幂等由成年结算本身的守卫保证（素质 103→104，一个孩子只会经过一次），
       这里不再另查 event_history
    Keyword arguments:
    character_id -- 刚成年的孩子角色id
    Return arguments:
    无
    """
    # 倒序插入，使毕业典礼最终排在成年纪念之前
    push_growth_event(ADULT_MEMORIAL_EVENT_UID, character_id, to_front=True)
    push_growth_event(GRADUATION_EVENT_UID, character_id, to_front=True)


def check_new_day_growth_event():
    """
    每日结算时筛选并入队养成事件（方案 §3.7 的第1步）

    ⚠️ 先把所有孩子的候选汇成一个池子再抽，而不是每个孩子各抽一条：
       后者等于把上限变成「孩子数×1」，节流就没了
    Keyword arguments:
    无
    Return arguments:
    无
    """
    if not game_config.config_growth_event:
        return
    all_candidate = []
    for character_id in get_growth_event_character_list():
        for uid, weight, partner_id in get_candidate_event_list(character_id):
            all_candidate.append([uid, weight, character_id, partner_id])
    if not all_candidate:
        return
    for _index in range(GROWTH_EVENT_DAILY_MAX):
        if not all_candidate:
            break
        if len(cache.rhodes_island.growth_event_queue) >= GROWTH_EVENT_QUEUE_MAX:
            break
        weight_list = [one[1] for one in all_candidate]
        chosen = random.choices(all_candidate, weights=weight_list, k=1)[0]
        all_candidate.remove(chosen)
        push_growth_event(chosen[0], chosen[2], chosen[3])


def clean_growth_event_queue():
    """
    清掉队列里已经失效的项（方案 §7-4）

    失效的两种：孩子已不在角色表里（跨版本存档、周目切换），事件已从配置里删掉。
    ⚠️ 静默丢弃，不报错也不提示——玩家对一条自己从没见过的事件消失没有感知，
       但一个 KeyError 会直接打断公务流程
    Keyword arguments:
    无
    Return arguments:
    无
    """
    queue = cache.rhodes_island.growth_event_queue
    valid = []
    for one in queue:
        if not isinstance(one, dict):
            continue
        if one.get("chara_id") not in cache.character_data:
            continue
        if one.get("uid") not in game_config.config_growth_event:
            continue
        valid.append(one)
    if len(valid) != len(queue):
        cache.rhodes_island.growth_event_queue = valid


def get_growth_event_queue_count() -> int:
    """
    取当前待处理的养成事件条数（清理失效项后）
    Keyword arguments:
    无
    Return arguments:
    int -- 待处理条数
    """
    clean_growth_event_queue()
    return len(cache.rhodes_island.growth_event_queue)


def pop_growth_event() -> Optional[dict]:
    """
    取出队首的一条待处理事件
    Keyword arguments:
    无
    Return arguments:
    Optional[dict] -- 队列元素，队列为空则None
    """
    clean_growth_event_queue()
    queue = cache.rhodes_island.growth_event_queue
    if not queue:
        return None
    return queue.pop(0)


def get_option_list(uid: str, character_id: int, partner_id: int = 0) -> List[dict]:
    """
    取一条事件的选项列表，并判定各选项的前提（口径34）

    ⚠️ 不满足前提的选项**置灰保留**而不是隐藏：让玩家看见「这里本来有更好的选择，
       但我没养到」，隐藏了就等于这条养成线从没存在过
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    partner_id -- 互动对象角色id
    Return arguments:
    List[dict] -- [{"index": 选项序号1~4, "text": 选项文本, "tip": 后果提示,
                    "can_use": 是否可选, "reason": 不可选的原因, "effect": 结算串}]
    """
    event_data = game_config.config_growth_event.get(uid)
    if event_data is None:
        return []
    result = []
    for index in range(1, 5):
        option_text = event_data.get(f"option_{index}", "")
        # 空着的选项列在构建时已被整列删掉，取不到就是这条事件没有这个选项
        if not option_text:
            continue
        can_use = bool(judge_premise_pass(event_data.get(f"option_{index}_premise", ""), character_id, partner_id))
        result.append({
            "index": index,
            "text": option_text,
            "tip": event_data.get(f"option_{index}_tip", ""),
            "can_use": can_use,
            "reason": event_data.get(f"option_{index}_reason", ""),
            "effect": event_data.get(f"option_{index}_effect", ""),
        })
    return result


def handle_effect_text(effect_text: str, character_id: int, partner_id: int = 0):
    """
    执行一串 & 连接的结算

    支持两类写法，与既有事件的 effect 一致（`settle_behavior.handle_event_data`）：
        CVE_...  综合数值结算（含本期新增的 CVE_A1_Growth|N_G_值 养成数值）
        纯数字   Behavior_Effect 表里的结算函数id
    ⚠️ 结算全程把孩子的交互对象指向 partner_id，使 A2 指向本次事件的互动对象；
       结算完立刻还原
    ⚠️ 结算用的 change_data 是一次性的、不往界面上抛数字（方案 §5.1）：
       养成事件写方向不写数值，抛出「好感+8」会把养成变成算数题
    Keyword arguments:
    effect_text -- & 连接的结算串
    character_id -- 孩子角色id
    partner_id -- 互动对象角色id
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
                settle_behavior.handle_comprehensive_value_effect(
                    character_id, effect.split("_")[1:], change_data)
            elif effect.isdigit():
                handler = constant.settle_behavior_effect_data.get(int(effect))
                if handler is not None:
                    handler(character_id, 1, change_data, cache.game_time)
                else:
                    print(f"\ndebug 养成事件的结算{effect}不存在，请检查结算是否正确\n")
            else:
                print(f"\ndebug 养成事件的结算{effect}格式不正确，请检查结算是否正确\n")
    finally:
        character_data.target_character_id = old_target_id


def settle_growth_event_option(uid: str, character_id: int, partner_id: int, option_index: int):
    """
    结算玩家选定的选项，并把这次选择写进该孩子的养成事件履历

    ⚠️ 无论事件是不是一次性都写 `event_history`：一次性事件靠它防重复触发，
       非一次性事件靠它给养成总览的履历栏提供内容（方案 §5.2）
    Keyword arguments:
    uid -- 事件uid
    character_id -- 孩子角色id
    partner_id -- 互动对象角色id
    option_index -- 玩家选定的选项序号（1~4）
    """
    for option in get_option_list(uid, character_id, partner_id):
        if option["index"] != option_index:
            continue
        handle_effect_text(option["effect"], character_id, partner_id)
        break
    growth_data = growth_handle.get_child_growth(character_id)
    growth_data.event_history[uid] = {"time": cache.game_time, "choice": option_index}
