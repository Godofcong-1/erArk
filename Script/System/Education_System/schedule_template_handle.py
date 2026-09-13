"""孩子日常日程的模板读写与每日改写（Plan 22 二期 §3.6）

日程与课表是**两层不同粒度**的东西，本模块只管前者：

    课表 —— 按 45 分钟的**节次**排（一期，见 schedule_handle），管的是"上什么课"
    日程 —— 按上午/下午/晚上三个**时段**排（本模块），管的是"没课的时候干什么"

所以日程的执行方式不是另造一条 AI 链，而是改写既有的 `entertainment.entertainment_type`
这三个槽位——既有的娱乐 AI 链会照着它去做事，一行新 AI 都不用写。

**改写必须发生在每日娱乐刷新之后**（`past_day_settle` 里 `get_chara_entertainment` 的下一行），
否则当天写进去的值立刻被随机值冲掉，症状是"日程时灵时不灵"，极难查。挂点照抄
`egg_handle.replace_entertainment_for_eggs`。

**优先级是节次级别的**（2026-09-10，二期方案 §9.2.9）：有课的节次由工作链里学生岗的上课目标行先接管
（target.csv 组 08，Plan 24 起；此前是 class_ai 的上课判定），没课的节次工作链没有行命中，才轮到槽位里的活动，
所以改写时不避让有课的时段。幼女在节次内没课、且该时段是「自由选择」时默认见学
（class_ai.judge_should_follow_mother），明确排了活动就去做活动；学生岗白天也算娱乐时间
（handle_premise_time._judge_free_daytime），否则周一~周六的白天根本走不到娱乐链。

数据分两层存（口径 4「操作量不随孩子数翻倍」的落点）：

    模板本体  Rhodes_Island.child_schedule_template   全局共享一份
    孩子身上  CHILD_GROWTH.schedule_template_id       只存模板编号
              CHILD_GROWTH.schedule_override          只存对模板的单项覆盖

给三个孩子都改成玩乐优先，是改一个模板而不是改三份日程。
"""
from types import FunctionType
from typing import List, Optional, Tuple
from Script.Core import cache_control, game_type, get_text
from Script.Config import game_config
from Script.System.Education_System import education_constant, growth_handle, schedule_handle

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

# 模板数据的两个键（TEMPLATE_KEY_NAME / TEMPLATE_KEY_SLOT）与 need 列的分隔符（TEMPLATE_NEED_*）集中在 education_constant（Plan 32 L28），
#    本模块与日程模板面板一律用常量，不写字面量


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
    for template_id, name in education_constant.PRESET_TEMPLATE_NAME.items():
        slot_data = {}
        for slot, entertainment_name in enumerate(education_constant.PRESET_TEMPLATE_SLOT_NAME[template_id]):
            slot_data[slot] = get_entertainment_cid_by_name(entertainment_name)
        cache.rhodes_island.child_schedule_template[template_id] = {education_constant.TEMPLATE_KEY_NAME: name, education_constant.TEMPLATE_KEY_SLOT: slot_data}


def get_template_data(template_id: int) -> Optional[dict]:
    """
    取一套模板的数据
    Keyword arguments:
    template_id -- 模板编号
    Return arguments:
    Optional[dict] -- {TEMPLATE_KEY_NAME: 模板名str, TEMPLATE_KEY_SLOT: {时段int: 娱乐cid int}}（键见 education_constant），不存在则为None
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
    template_data.setdefault(education_constant.TEMPLATE_KEY_SLOT, {})[slot] = entertainment_id


def judge_template_is_preset(template_id: int) -> bool:
    """
    校验一套模板是不是四套预设之一（Plan 22 二期第一轮追加）
    Keyword arguments:
    template_id -- 模板编号
    Return arguments:
    bool -- 是否为预设
    """
    return template_id in education_constant.PRESET_TEMPLATE_NAME


def create_template(name: str) -> int:
    """
    新建一套空模板（Plan 22 二期第一轮追加）

    方案 §1 要的是「可定义**若干套**日常日程模板」，四套预设只是起点。
    编号取「现存最大编号 + 1」，不补中间的空缺号；但被删的**最大**编号会被下一套新模板复用
       （收尾轮测试发现，与原注释「删过的编号不复用」不符）。这不会串日程：delete_template 删之前
       已把引用它的孩子解开（schedule_template_id 归 0、覆盖清空；Plan 32 起连不在岛上的人一起解开），
       不存在"孩子还指着旧编号"的情形。
    Keyword arguments:
    name -- 模板名，留空则自动命名
    Return arguments:
    int -- 新模板的编号，建失败为0
    """
    init_default_template()
    template_dict = cache.rhodes_island.child_schedule_template
    new_id = (max(template_dict.keys()) if template_dict else 0) + 1
    name = name.strip() if name else ""
    if not name:
        name = _("模板{0}").format(new_id)
    template_dict[new_id] = {education_constant.TEMPLATE_KEY_NAME: name, education_constant.TEMPLATE_KEY_SLOT: {}}
    return new_id


def rename_template(template_id: int, name: str) -> bool:
    """
    给一套模板改名（Plan 22 二期第一轮追加）。预设也可改名，改的只是显示用的名字
    Keyword arguments:
    template_id -- 模板编号
    name -- 新名字，留空则不改
    Return arguments:
    bool -- 是否改成功
    """
    template_data = get_template_data(template_id)
    if template_data is None:
        return False
    name = name.strip() if name else ""
    if not name:
        return False
    template_data[education_constant.TEMPLATE_KEY_NAME] = name
    return True


def delete_template(template_id: int) -> bool:
    """
    删掉一套自建模板（Plan 22 二期第一轮追加）

    四套预设不可删：init_default_template 只在整张表为空时才补，
       删掉一套预设不会被补回来，而 PRESET_TEMPLATE_NAME 的编号在代码里被引用着。
    删之前必须把引用它的孩子解开，否则那些孩子的 schedule_template_id
       指向一个不存在的编号，get_child_slot_activity 每天都拿到 None。
       解开的范围是全部角色，含外勤 / 外交等不在岛上的人（Plan 32 §3.12 L17）：被删的最大编号会被下一套新模板复用
    Keyword arguments:
    template_id -- 模板编号
    Return arguments:
    bool -- 是否删成功
    """
    init_default_template()
    if judge_template_is_preset(template_id):
        return False
    if template_id not in cache.rhodes_island.child_schedule_template:
        return False
    # 遍历全部角色，不只是在岛的人（Plan 32 §3.12 L17）：外勤 / 外交 / 离线中的女儿不在 npc_id_got，
    #    此前她仍指着被删的编号，新模板复用这个编号时，她回岛后静默套上新模板
    for character_data in cache.character_data.values():
        growth_data = character_data.child_growth
        if growth_data is None or growth_data.schedule_template_id != template_id:
            continue
        growth_data.schedule_template_id = 0
        growth_data.schedule_override = {}
    del cache.rhodes_island.child_schedule_template[template_id]
    return True


def apply_template(character_id: int, template_id: int) -> None:
    """
    给一个孩子套用模板。换模板时一并清空该孩子的单项覆盖——
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
    return template_data.get(education_constant.TEMPLATE_KEY_SLOT, {}).get(slot, 0)


def judge_activity_need_pass(character_id: int, entertainment_id: int) -> bool:
    """
    校验一个孩子是否满足某项娱乐的 need 条件（Plan 22 二期第一轮追加）

    这道校验非做不可：模板是**全局共享**的，而 need 是**逐人**的。
       过家家 / 跟随母亲 / 自由玩耍配的 need 是 T102|1/T103|1（限幼女或萝莉），
       上课（无课时自习）配的是 W152|1（限学生岗）；同一套模板套到少女或非学生岗的干员身上时，
       不校验就会把活动照写进她的 entertainment_type，那一格既做不了该活动也不会随机娱乐，白白空转一个时段。
       不满足的时段就跳过不改写、保留当天的随机娱乐——这就是面板上说的「退回到自由选择娱乐活动」。
    引擎只在**随机抽娱乐**时校验过 need（handle_npc_ai.get_chara_entertainment），
       日程改写是另一条写入路径，必须自己校验。
    Keyword arguments:
    character_id -- 角色id
    entertainment_id -- 娱乐配置cid
    Return arguments:
    bool -- 是否满足；无 need 条件的一律为True
    """
    from Script.Design import attr_calculation

    if entertainment_id not in game_config.config_entertainment:
        return False
    need_text = game_config.config_entertainment[entertainment_id].need
    if not need_text or need_text == education_constant.TEMPLATE_NEED_NONE:
        return True
    need_list = need_text.split(education_constant.TEMPLATE_NEED_SPLIT) if education_constant.TEMPLATE_NEED_SPLIT in need_text else [need_text]
    judge, _reason = attr_calculation.judge_require(need_list, character_id)
    return bool(judge)


def judge_activity_place_open(entertainment_id: int) -> bool:
    """
    校验一项娱乐的地点此刻是否已开放（Plan 27 §3.1）
    Keyword arguments:
    entertainment_id -- 娱乐配置cid
    Return arguments:
    bool -- 是否已开放；地点为「无」或不在 Facility_open 表里的恒为True，配置里没有的娱乐为False
    功能: 与寻路的 wait_open、成年干员随机娱乐的场所判定同口径（schedule_handle.judge_scene_open）。
          幼女的默认娱乐池与日程改写都是把活动直接写进 entertainment_type 的路径，不查这一道就会把孩子派到还没解锁的场所
             （如教育区 2 级才开的黄澄澄游戏室）：寻路在门口返回 wait_open、移动时长为 0，通用移动模块退成等待 1 分钟，
             下一次决策又派同一个移动，整个时段在门口一分钟一分钟地空转
    """
    if entertainment_id not in game_config.config_entertainment:
        return False
    return schedule_handle.judge_scene_open(game_config.config_entertainment[entertainment_id].place)


def judge_activity_schedulable(entertainment_id: int) -> bool:
    """
    校验一项娱乐能不能排进孩子的日程（Plan 28 §3.3）
    Keyword arguments:
    entertainment_id -- 娱乐配置cid
    Return arguments:
    bool -- 能排为True；照料卵（pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID）为False
    功能: 照料卵是妊娠系统给持卵者的专用娱乐：随机池专门排除它，只由每日的持卵钩子（egg_handle.replace_entertainment_for_eggs）换上；
          它的 need 列却是「无」，不在这里挡的话「选择活动」里就有它。排给孩子后她每晚去育儿室，
          状态机 427 找不到可鉴定的卵就「孵化卵」一小时，还拿医疗经验。
          候选表、每日改写、日程行三处共用本函数
    """
    from Script.System.Pregnancy_System import pregnancy_constant

    return entertainment_id != pregnancy_constant.TEND_EGGS_ENTERTAINMENT_ID


def apply_schedule_for_child(character_id: int) -> None:
    """
    按日程把一个孩子今天的 entertainment_type 三个槽位改写掉（每日一次）

    本函数必须在 `handle_npc_ai.get_chara_entertainment` **之后**调用，见模块头注释。
    时段里有课的节次不用避让：上课（工作链里学生岗的目标行，Plan 24）在**节次**级别排在娱乐链之前，
       有课的节次照常上课，同一时段里没课的节次才按这里写进去的活动走（2026-09-10 二期方案 §9.2.9；
       此前要求整段没课才改写，结果上午只要有一节课，整个上午的日程都不生效）。
    不满足 need 的、地点还没开放的（Plan 27 §3.1）、不可排进日程的（旧档里排上的照料卵，Plan 28 §3.3）时段都跳过不改写，
       保留当天的随机娱乐，即退回自由选择。
    当天已被持卵钩子换成照料卵的时段也不覆盖（Plan 28 §3.3）：跨天结算里钩子先于本函数（past_day_settle），
       改回模板的活动的话，持卵者那个时段就不去照料卵了。
    不是女儿、又不在学生岗的整个跳过（Plan 32 §3.12 L18）：成年干员当学生时套的模板，改岗后不再改写她的娱乐
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
    # 不是女儿、又不在学生岗的不改写（Plan 32 §3.12 L18）：成年干员离开学生岗后，她既不在个人课表名单、也不在批量套用名单，
    #    此前当学生时套的模板每天照写、面板上又解除不了，只能先改回学生岗。模板与覆盖都留着，改回学生岗照旧生效。
    #    女儿不看岗位：改了岗的萝莉晚上照旧按日程走，工作时间里的「跟随母亲」由见学判定另外让路（Plan 32 §3.6）
    if character_data.relationship.father_id != 0 and character_data.work.work_type != education_constant.STUDENT_WORK_TYPE:
        return
    for slot in range(education_constant.SLOT_COUNT):
        entertainment_id = get_child_slot_activity(character_id, slot)
        if not entertainment_id:
            continue
        if entertainment_id not in game_config.config_entertainment:
            continue
        # 持卵钩子今天换上的照料卵不覆盖：照料卵只有钩子会写（随机池与日程候选都排除它），槽位里是它就是今天换上的
        if not judge_activity_schedulable(character_data.entertainment.entertainment_type[slot]):
            continue
        # 不可排进日程的（旧档里已排上的照料卵）跳过，退回自由选择
        if not judge_activity_schedulable(entertainment_id):
            continue
        # 不满足该娱乐 need 条件的孩子跳过这一格，留着当天的随机娱乐比空转强
        if not judge_activity_need_pass(character_id, entertainment_id):
            continue
        # 地点还没开放的同样跳过（Plan 27 §3.1）：写进去孩子会走到门口，一分钟一分钟地空转一整个时段
        if not judge_activity_place_open(entertainment_id):
            continue
        character_data.entertainment.entertainment_type[slot] = entertainment_id


def get_child_schedule_text(character_id: int) -> str:
    """
    取一个孩子当前日程的一行摘要，供个人课表面板显示
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    str -- 形如「均衡（上课（无课时自习） / 下棋 / 自由玩耍）」，未套用模板则为「未设置」；
           时段值为 0 显示「自由选择娱乐活动」，这个孩子不满足条件的活动带「（条件不符→自由选择）」标注，
           地点还没开放的带「（未开放→自由选择）」（Plan 27）
    """
    character_data: game_type.Character = cache.character_data[character_id]
    growth_data = character_data.child_growth
    if growth_data is None or (not growth_data.schedule_template_id and not growth_data.schedule_override):
        return _("未设置")
    template_data = get_template_data(growth_data.schedule_template_id)
    template_name = template_data[education_constant.TEMPLATE_KEY_NAME] if template_data is not None else _("自定义")
    slot_text_list = [get_child_slot_activity_text(character_id, slot) for slot in range(education_constant.SLOT_COUNT)]
    return "{0}（{1}）".format(template_name, " / ".join(slot_text_list))


def get_template_use_count(template_id: int) -> int:
    """
    统计有多少个孩子正在套用某套模板，供模板面板的「套用中」列显示
    Keyword arguments:
    template_id -- 模板编号
    Return arguments:
    int -- 人数
    功能: 遍历全部角色（Plan 32 §3.12 L17）：外勤 / 外交 / 离线中的女儿不在 npc_id_got，回岛后照样套着这套模板，
          此前漏数；与 delete_template 解开引用的范围一致
    """
    count = 0
    for character_data in cache.character_data.values():
        if character_data.child_growth is None:
            continue
        if character_data.child_growth.schedule_template_id == template_id:
            count += 1
    return count


def get_schedule_activity_candidate() -> List[int]:
    """
    取可排进日程的娱乐候选表：全部娱乐（含教育区 15x 段的日程专用活动），去掉0号模板行与不可排的照料卵（Plan 28 §3.3）
    Keyword arguments:
    无
    Return arguments:
    List[int] -- 娱乐cid列表，按cid升序
    """
    return sorted(cid for cid in game_config.config_entertainment if cid and judge_activity_schedulable(cid))


def get_activity_name(entertainment_id: int) -> str:
    """
    取一项日程活动的显示名
    Keyword arguments:
    entertainment_id -- 娱乐cid，0 表示「自由选择娱乐活动」
    Return arguments:
    str -- 0 为「自由选择娱乐活动」；配置里有的取娱乐名；配置里没有的（如被删掉的旧编号）为「--」
    """
    if entertainment_id == education_constant.SCHEDULE_FREE_CHOICE:
        return education_constant.SCHEDULE_FREE_CHOICE_NAME
    if entertainment_id in game_config.config_entertainment:
        return game_config.config_entertainment[entertainment_id].name
    return "--"


def get_activity_age_limit_talent_list(entertainment_id: int) -> List[int]:
    """
    从一项娱乐的 need 列里解出它要求的成长阶段素质（年龄限制）
    Keyword arguments:
    entertainment_id -- 娱乐cid
    Return arguments:
    List[int] -- 要求持有的阶段素质id列表（101~104 之一或多个），没有年龄限制则为空表
    功能: need 先按 & 拆成「且」项，再按 / 拆成「或」项，只认 T<阶段素质id>|1 这种写法。
          不写死「过家家 / 跟随母亲 / 自由玩耍」三项：年龄限制是配置，往后再加一项带年龄需求的活动，
             面板的第二行与「限幼女/萝莉」标注会自动跟上
    """
    if entertainment_id not in game_config.config_entertainment:
        return []
    need_text = game_config.config_entertainment[entertainment_id].need
    if not need_text or need_text == education_constant.TEMPLATE_NEED_NONE:
        return []
    result = []
    for and_text in need_text.split(education_constant.TEMPLATE_NEED_SPLIT):
        for one_text in and_text.split(education_constant.TEMPLATE_NEED_OR_SPLIT):
            one_text = one_text.strip()
            if not one_text.startswith("T") or "|" not in one_text:
                continue
            talent_part, value_part = one_text[1:].split("|", 1)
            if not talent_part.isdigit() or value_part.strip() != "1":
                continue
            talent_id = int(talent_part)
            if talent_id in education_constant.STAGE_TALENT_NAME and talent_id not in result:
                result.append(talent_id)
    return result


def get_activity_age_limit_text(entertainment_id: int) -> str:
    """
    取一项娱乐的年龄限制标注文本，供「选择活动」面板显示
    Keyword arguments:
    entertainment_id -- 娱乐cid
    Return arguments:
    str -- 形如「限幼女/萝莉」，没有年龄限制则为空串
    """
    talent_list = get_activity_age_limit_talent_list(entertainment_id)
    if not talent_list:
        return ""
    return _("限{0}").format("/".join(education_constant.STAGE_TALENT_NAME[talent_id] for talent_id in talent_list))


def get_schedule_activity_rows() -> Tuple[List[int], List[int], List[int]]:
    """
    把可排进日程的活动分成「选择活动」面板的三组
    Keyword arguments:
    无
    Return arguments:
    Tuple[List[int], List[int], List[int]] -- (第一行, 第二行, 其余)：
        第一行固定是 上课（无课时自习）与 自由选择娱乐活动（0）；
        第二行是有年龄需求的活动（过家家 / 跟随母亲 / 自由玩耍，从 need 列现算）；
        其余娱乐按 cid 升序
    """
    candidate_list = get_schedule_activity_candidate()
    first_row = [cid for cid in education_constant.CHILD_SCHEDULE_FIRST_ROW if cid == education_constant.SCHEDULE_FREE_CHOICE or cid in candidate_list]
    age_row = [cid for cid in candidate_list if cid not in first_row and get_activity_age_limit_talent_list(cid)]
    other_list = [cid for cid in candidate_list if cid not in first_row and cid not in age_row]
    return first_row, age_row, other_list


def get_child_slot_activity_text(character_id: int, slot: int) -> str:
    """
    取一个孩子某时段日程活动的显示文本，条件不符时标注会退回自由选择
    Keyword arguments:
    character_id -- 角色id
    slot -- 时段0~2
    Return arguments:
    str -- 活动名；0 为「自由选择娱乐活动」；活动存在但这个孩子不满足其 need 条件、或是不可排进日程的照料卵（Plan 28 §3.3）时为
           「X（条件不符→自由选择）」，满足条件但地点还没开放时为「X（未开放→自由选择）」（Plan 27 §3.1）
    功能: 供个人课表的日程行与日程微调页共用。
          只做显示：真正的「退回」发生在 apply_schedule_for_child 的可排、need 与地点校验里，这里只是把它说给玩家听
    """
    entertainment_id = get_child_slot_activity(character_id, slot)
    name = get_activity_name(entertainment_id)
    if entertainment_id and entertainment_id in game_config.config_entertainment:
        # 旧档里已排上的照料卵：改写时直接跳过，排在 need 判定之前
        if not judge_activity_schedulable(entertainment_id) or not judge_activity_need_pass(character_id, entertainment_id):
            return _("{0}（条件不符→自由选择）").format(name)
        if not judge_activity_place_open(entertainment_id):
            return _("{0}（未开放→自由选择）").format(name)
    return name
