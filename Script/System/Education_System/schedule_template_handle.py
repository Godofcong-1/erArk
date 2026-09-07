"""孩子日常日程的模板读写与每日改写（Plan 22 二期 §3.6）

日程与课表是**两层不同粒度**的东西，本模块只管前者：

    课表 —— 按 45 分钟的**节次**排（一期，见 schedule_handle），管的是"上什么课"
    日程 —— 按上午/下午/晚上三个**时段**排（本模块），管的是"没课的时候干什么"

所以日程的执行方式不是另造一条 AI 链，而是改写既有的 `entertainment.entertainment_type`
这三个槽位——既有的娱乐 AI 链会照着它去做事，一行新 AI 都不用写。

⚠️ **改写必须发生在每日娱乐刷新之后**（`past_day_settle` 里 `get_chara_entertainment` 的下一行），
否则当天写进去的值立刻被随机值冲掉，症状是"日程时灵时不灵"，极难查。挂点照抄
`egg_handle.replace_entertainment_for_eggs`。

数据分两层存（口径 4「操作量不随孩子数翻倍」的落点）：

    模板本体  Rhodes_Island.child_schedule_template   全局共享一份
    孩子身上  CHILD_GROWTH.schedule_template_id       只存模板编号
              CHILD_GROWTH.schedule_override          只存对模板的单项覆盖

给三个孩子都改成玩乐优先，是改一个模板而不是改三份日程。
"""
from types import FunctionType
from typing import Dict, List, Optional
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.System.Education_System import growth_handle, schedule_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

SLOT_COUNT = 3
""" 日程时段数：0上午 / 1下午 / 2晚上，与 entertainment.entertainment_type 的三个槽位一一对应 """

SLOT_NAME = {0: "上午", 1: "下午", 2: "晚上"}
""" 时段编号到中文名 """

SLOT_PERIOD_RANGE = {
    0: (0, 4),
    1: (4, 9),
    2: (9, 9),
}
""" 每个时段覆盖的课表节次区间 [起, 止)（`game_time.CLASS_PERIOD_START`：上午4节 + 下午5节）。
    晚上是空区间——19~22 点本就不排课，所以晚上的日程永远生效 """

ENTERTAINMENT_FOLLOW_MOTHER = 176
""" 娱乐配置「跟随母亲」的cid（Entertainment.csv）。它没有固定地点，执行走 class_ai 的见学分支 """

ENTERTAINMENT_FREE_PLAY = 177
""" 娱乐配置「自由玩耍」的cid，地点为育儿室，也是见学的回落目标 """

ENTERTAINMENT_SELF_STUDY = 154
""" 娱乐配置「自习」的cid，实施时按名字反查，此处只作为查不到时的兜底 """

TEMPLATE_ACADEMIC = 1
""" 预设模板：学业优先 """
TEMPLATE_BALANCED = 2
""" 预设模板：均衡（默认推荐） """
TEMPLATE_PLAYFUL = 3
""" 预设模板：玩乐优先 """
TEMPLATE_CUSTOM = 4
""" 预设模板：自定义（初始三个时段全空，由玩家逐时段指定） """

PRESET_TEMPLATE_NAME = {
    TEMPLATE_ACADEMIC: "学业优先",
    TEMPLATE_BALANCED: "均衡",
    TEMPLATE_PLAYFUL: "玩乐优先",
    TEMPLATE_CUSTOM: "自定义",
}
""" 四套预设模板的名字（方案 §3.6 的表） """

PRESET_TEMPLATE_SLOT_NAME = {
    TEMPLATE_ACADEMIC: ("自习", "自习", "读书"),
    TEMPLATE_BALANCED: ("自习", "下棋", "自由玩耍"),
    TEMPLATE_PLAYFUL: ("过家家", "下棋", "自由玩耍"),
    TEMPLATE_CUSTOM: ("", "", ""),
}
""" 预设模板各时段的娱乐**名字**（不是cid）。
    ⚠️ 写名字而不是写cid，是因为 Entertainment.csv 的编号会随内容增删漂移，
    按名字反查一次比在代码里钉死一串数字安全。查不到的名字落为0（该时段不改写）。
    方案 §3.6 的"兴趣活动"在配置里没有同名项，取「下棋」作为代表性的兴趣类娱乐 """


def get_entertainment_cid_by_name(name: str) -> int:
    """
    按娱乐名反查 Entertainment.csv 的cid
    Keyword arguments:
    name -- 娱乐名
    Return arguments:
    int -- 娱乐cid，查不到则为0
    """
    if not name:
        return 0
    for cid, data in game_config.config_entertainment.items():
        if data.name == name:
            return cid
    return 0


def init_default_template() -> None:
    """
    把四套预设模板写进全局模板表（只在表为空时写一次，玩家改过之后不再覆盖）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    if not hasattr(cache.rhodes_island, "child_schedule_template"):
        cache.rhodes_island.child_schedule_template = {}
    if cache.rhodes_island.child_schedule_template:
        return
    for template_id, name in PRESET_TEMPLATE_NAME.items():
        slot_data = {}
        for slot, entertainment_name in enumerate(PRESET_TEMPLATE_SLOT_NAME[template_id]):
            slot_data[slot] = get_entertainment_cid_by_name(entertainment_name)
        cache.rhodes_island.child_schedule_template[template_id] = {"name": name, "slot": slot_data}


def get_template_data(template_id: int) -> Optional[dict]:
    """
    取一套模板的数据
    Keyword arguments:
    template_id -- 模板编号
    Return arguments:
    Optional[dict] -- {"name": 模板名str, "slot": {时段int: 娱乐cid int}}，不存在则为None
    """
    init_default_template()
    return cache.rhodes_island.child_schedule_template.get(template_id, None)


def get_all_template_id() -> List[int]:
    """
    取全部模板编号，按编号升序
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 模板编号列表
    """
    init_default_template()
    return sorted(cache.rhodes_island.child_schedule_template.keys())


def set_template_slot(template_id: int, slot: int, entertainment_id: int) -> None:
    """
    改一套模板某个时段的活动
    Keyword arguments:
    template_id -- 模板编号
    slot -- 时段0~2
    entertainment_id -- 娱乐cid，0表示该时段不改写（保持随机）
    Return arguments:
    无
    """
    template_data = get_template_data(template_id)
    if template_data is None:
        return
    template_data.setdefault("slot", {})[slot] = entertainment_id


def apply_template(character_id: int, template_id: int) -> None:
    """
    给一个孩子套用模板。⚠️ 换模板时一并清空该孩子的单项覆盖——
    覆盖是"针对某套模板的微调"，留着它跨模板生效只会让玩家看不懂自己的日程
    Keyword arguments:
    character_id -- 角色id
    template_id -- 模板编号，0表示取消套用
    Return arguments:
    无
    """
    growth_data = growth_handle.get_child_growth(character_id)
    if growth_data.schedule_template_id != template_id:
        growth_data.schedule_override = {}
    growth_data.schedule_template_id = template_id


def batch_apply_template(character_id_list: List[int], template_id: int) -> int:
    """
    把同一套模板批量套用到多个孩子（口径 4 的核心操作）
    Keyword arguments:
    character_id_list -- 角色id列表
    template_id -- 模板编号
    Return arguments:
    int -- 实际套用成功的人数
    """
    count = 0
    for character_id in character_id_list:
        if character_id not in cache.character_data:
            continue
        apply_template(character_id, template_id)
        count += 1
    return count


def set_child_override(character_id: int, slot: int, entertainment_id: int) -> None:
    """
    给一个孩子单独覆盖某个时段的活动，不影响模板本体与其他孩子
    Keyword arguments:
    character_id -- 角色id
    slot -- 时段0~2
    entertainment_id -- 娱乐cid，0表示取消覆盖（回到模板值）
    Return arguments:
    无
    """
    growth_data = growth_handle.get_child_growth(character_id)
    if entertainment_id:
        growth_data.schedule_override[slot] = entertainment_id
    else:
        growth_data.schedule_override.pop(slot, None)


def get_child_slot_activity(character_id: int, slot: int) -> int:
    """
    取一个孩子某时段最终生效的日程活动（覆盖优先于模板）
    Keyword arguments:
    character_id -- 角色id
    slot -- 时段0~2
    Return arguments:
    int -- 娱乐cid，0表示该时段没有固定日程（保持每日随机）
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None:
        return 0
    # 单孩覆盖优先
    if slot in growth_data.schedule_override:
        return growth_data.schedule_override[slot]
    template_data = get_template_data(growth_data.schedule_template_id)
    if template_data is None:
        return 0
    return template_data.get("slot", {}).get(slot, 0)


def judge_slot_free_of_class(character_id: int, slot: int, week_day: int) -> bool:
    """
    判断某孩子某时段是否**完全没有课**（方案 §3.6：有课的节次由课表优先，日程不生效）
    Keyword arguments:
    character_id -- 角色id
    slot -- 时段0~2
    week_day -- 星期，0周一~6周日
    Return arguments:
    bool -- 该时段的每一节次都没排课则为True
    """
    start, end = SLOT_PERIOD_RANGE.get(slot, (0, 0))
    for period in range(start, end):
        if schedule_handle.get_selected_course(character_id, week_day, period) is not None:
            return False
    return True


def apply_schedule_for_child(character_id: int) -> None:
    """
    按日程把一个孩子今天的 entertainment_type 三个槽位改写掉（每日一次）

    ⚠️ 本函数必须在 `handle_npc_ai.get_chara_entertainment` **之后**调用，见模块头注释。
    ⚠️ 只改"该时段完全没有课"的槽位；有课的时段留着随机值也无所谓——
       那个时段的 AI 根本走不到娱乐链，会被上课分支先接管。
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    无
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    # 没有养成数据、或没套用任何模板且没有任何覆盖的，不改写
    if growth_data is None:
        return
    if not growth_data.schedule_template_id and not growth_data.schedule_override:
        return
    week_day = cache.game_time.weekday()
    for slot in range(SLOT_COUNT):
        entertainment_id = get_child_slot_activity(character_id, slot)
        if not entertainment_id:
            continue
        if entertainment_id not in game_config.config_entertainment:
            continue
        if not judge_slot_free_of_class(character_id, slot, week_day):
            continue
        character_data.entertainment.entertainment_type[slot] = entertainment_id


def get_child_schedule_text(character_id: int) -> str:
    """
    取一个孩子当前日程的一行摘要，供个人课表面板显示
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 形如「均衡（自习 / 下棋 / 自由玩耍）」，未套用模板则为「未设置」
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None or (not growth_data.schedule_template_id and not growth_data.schedule_override):
        return _("未设置")
    template_data = get_template_data(growth_data.schedule_template_id)
    template_name = template_data["name"] if template_data is not None else _("自定义")
    slot_text_list = []
    for slot in range(SLOT_COUNT):
        entertainment_id = get_child_slot_activity(character_id, slot)
        if entertainment_id and entertainment_id in game_config.config_entertainment:
            slot_text_list.append(game_config.config_entertainment[entertainment_id].name)
        else:
            slot_text_list.append("--")
    return "{0}（{1}）".format(template_name, " / ".join(slot_text_list))


def get_template_use_count(template_id: int) -> int:
    """
    统计有多少个孩子正在套用某套模板，供模板面板的「套用中」列显示
    Keyword arguments:
    template_id -- 模板编号
    Return arguments:
    int -- 人数
    """
    count = 0
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        if character_data.child_growth is None:
            continue
        if character_data.child_growth.schedule_template_id == template_id:
            count += 1
    return count


def get_child_candidate_list() -> List[int]:
    """
    取可安排日程的孩子列表：处于成长链四个年龄阶段之一的角色
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 角色id列表，按id升序
    """
    child_list = []
    for character_id in cache.npc_id_got:
        if growth_handle.judge_is_child(character_id):
            child_list.append(character_id)
    return sorted(child_list)


def get_schedule_activity_candidate() -> List[int]:
    """
    取可排进日程的娱乐候选表：全部娱乐，加上本期新增的两项，去掉0号模板行
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 娱乐cid列表，按cid升序
    """
    return sorted(cid for cid in game_config.config_entertainment if cid)
