# -*- coding: UTF-8 -*-
"""
助理的早安榨精 / 晚安榨精：可选部位、执行时的可用判定与上交衣物的先后

早安服务（助理服务5）与晚安服务（助理服务6）的第4个选项。玩家开启该选项时从干员身上选一个身体部位或服装部位，
助理到点后用这个部位为玩家做一次部位交或服装交，并让玩家射在该部位上（结算见 Script/Settle/default.py 的 handle_salutation_4_add_adjust）。

部位用与 h_state.insert_position 相同的编码：身体部位为 BodyPart.csv 的 id，服装部位为 20 + ClothingType.csv 的 id，-1 为未选。
选定的部位存在助理自己的 work.assistant_milking_position（选项切到第4项时总会重新选部位）。

可选范围：
    身体部位：有对应 H 部位交指令的部位，且干员身上有（兽尾 / 兽角 / 兽耳看素质），并且不会夺走她还保有的处女（与自动挑选行为用同一个判定）
    服装部位：干员默认服装（角色模板里的服装，加上每名干员都会配的胸衣与内裤）里有的部位
执行时再判一次：身体部位同上，服装部位要求此刻身上还穿着，否则本次无法执行。
"""
from types import FunctionType
from typing import List, Set, Tuple

from Script.Config import game_config
from Script.Core import cache_control, constant, game_type, get_text
from Script.Design import handle_premise, virgin_break_gate

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """

MILKING_OPTION = 4
""" 早安服务与晚安服务里「榨精」选项的序号 """
MILKING_SERVICE_BEHAVIOR = {
    5: constant.Behavior.MORNING_SALUTATION_4,
    6: constant.Behavior.NIGHT_SALUTATION_4,
}
""" 助理服务id: 对应的榨精行为 """
CLOTH_POSITION_OFFSET = 20
""" 服装部位编码的偏移量，与 h_state.insert_position 一致 """

BODY_PART_JOB_BEHAVIOR = {
    0: "hairjob",
    1: "face_rub",
    2: "blowjob",
    3: "paizuri",
    4: "axillajob",
    5: "handjob",
    6: "riding_sex",
    7: "riding_womb_sex",
    8: "riding_anal_sex",
    9: "riding_urethral_sex",
    10: "legjob",
    11: "footjob",
    12: "tailjob",
    13: "horn_rub",
    14: "ears_rub",
}
""" 可选的身体部位id: 同部位的 H 部位交行为。
    行为的 tag 用来做破处判定，行为的经验结算用来决定榨精给双方的经验。
    插入类由干员主动，取骑乘位；胃部（深喉）并入口腔，胯部 / 腹部 / 背部没有部位交，都不在此列 """
BODY_PART_TALENT = {12: 113, 13: 112, 14: 111}
""" 只有部分干员才有的身体部位: 需要的素质id（兽尾 / 兽角 / 兽耳） """
CLOTH_TYPE_JOB_BEHAVIOR = {
    0: "hat_job",
    1: "glasses_job",
    2: "ear_ornament_job",
    3: "neck_ornament_job",
    4: "mouth_ornament_job",
    5: "top_job",
    6: "corset_job",
    7: "gloves_job",
    8: "skirt_job",
    9: "underwear_job",
    10: "socks_job",
    11: "shoes_job",
    12: "weapons_job",
}
""" 可选的服装类型id: 同部位的 H 服装交行为。下衣（8）穿着裤子时改用 trousers_job；附属物（13）没有服装交，不在此列 """
DEFAULT_UNDERWEAR_CLOTH_TYPE_SET = {6, 9}
""" 每名干员换衣时都会配上的胸衣与内裤（clothing.get_underwear），不在角色模板里也算默认服装 """


def get_position_name(position: int) -> str:
    """
    取部位的显示名
    Keyword arguments:
    position -- 部位编码
    Return arguments:
    str -- 身体部位名或服装部位名
    """
    if position >= CLOTH_POSITION_OFFSET:
        return game_config.config_clothing_type[position - CLOTH_POSITION_OFFSET].name
    return game_config.config_body_part[position].name


def get_body_part_unable_reason(character_id: int, body_part_id: int) -> str:
    """
    判断干员的某个身体部位能否用来榨精（选择与执行共用）
    Keyword arguments:
    character_id -- 干员id
    body_part_id -- 身体部位id
    Return arguments:
    str -- 不能用的原因，能用时为空字符串
    """
    character_data: game_type.Character = cache.character_data[character_id]
    part_name = game_config.config_body_part[body_part_id].name
    if body_part_id not in BODY_PART_JOB_BEHAVIOR:
        return _("{0}没有对应的部位交").format(part_name)
    # 兽尾、兽角、兽耳要有对应的素质
    if body_part_id in BODY_PART_TALENT and not character_data.talent.get(BODY_PART_TALENT[body_part_id], 0):
        return _("没有{0}").format(part_name)
    # 会夺走她还保有的处女时不可用，判定与 NPC 自动挑选行为相同（口交会夺走「无接吻经验」）
    tag_list = game_config.config_behavior[BODY_PART_JOB_BEHAVIOR[body_part_id]].tag.split("|")
    if virgin_break_gate.takes_kept_virginity(tag_list, character_data.talent):
        return _("{0}尚未破处").format(part_name)
    return ""


def get_default_cloth_type_set(character_id: int) -> Set[int]:
    """
    取干员默认服装里有的服装类型
    Keyword arguments:
    character_id -- 干员id
    Return arguments:
    Set[int] -- 服装类型id集合
    """
    character_data: game_type.Character = cache.character_data[character_id]
    cloth_type_set = set(DEFAULT_UNDERWEAR_CLOTH_TYPE_SET)
    for cloth_id in character_data.cloth.clothing_tem:
        if cloth_id in game_config.config_clothing_tem:
            cloth_type_set.add(game_config.config_clothing_tem[cloth_id].clothing_type)
    return cloth_type_set


def get_selectable_position_list(character_id: int) -> List[int]:
    """
    取干员身上可选为榨精部位的全部部位
    Keyword arguments:
    character_id -- 干员id
    Return arguments:
    List[int] -- 部位编码列表，身体部位在前、服装部位在后，各自按id升序
    """
    position_list = [body_part_id for body_part_id in sorted(BODY_PART_JOB_BEHAVIOR) if get_body_part_unable_reason(character_id, body_part_id) == ""]
    default_cloth_type_set = get_default_cloth_type_set(character_id)
    position_list += [CLOTH_POSITION_OFFSET + cloth_type for cloth_type in sorted(CLOTH_TYPE_JOB_BEHAVIOR) if cloth_type in default_cloth_type_set]
    return position_list


def get_milking_position(character_id: int, service_cid: int) -> int:
    """
    取干员某项服务选定的榨精部位
    Keyword arguments:
    character_id -- 干员id
    service_cid -- 助理服务id（5早安 / 6晚安）
    Return arguments:
    int -- 部位编码，未选为-1
    """
    return cache.character_data[character_id].work.assistant_milking_position.get(service_cid, -1)


def set_milking_position(character_id: int, service_cid: int, position: int):
    """
    设定干员某项服务的榨精部位
    Keyword arguments:
    character_id -- 干员id
    service_cid -- 助理服务id（5早安 / 6晚安）
    position -- 部位编码
    Return arguments:
    无
    """
    cache.character_data[character_id].work.assistant_milking_position[service_cid] = position


def get_service_cid_by_behavior(behavior_id: str) -> int:
    """
    由榨精行为反查助理服务id
    Keyword arguments:
    behavior_id -- 行为id
    Return arguments:
    int -- 助理服务id，不是榨精行为时为0
    """
    for service_cid, milking_behavior_id in MILKING_SERVICE_BEHAVIOR.items():
        if milking_behavior_id == behavior_id:
            return service_cid
    return 0


def judge_now_milking_position(character_id: int, position: int) -> bool:
    """
    判断干员此刻正在进行的早安榨精 / 晚安榨精用的是不是某个部位（综合数值前提「榨精部位」用）
    Keyword arguments:
    character_id -- 干员id
    position -- 部位编码
    Return arguments:
    bool -- 正在榨精且选定的正是该部位时为True
    """
    service_cid = get_service_cid_by_behavior(cache.character_data[character_id].behavior.behavior_id)
    return service_cid != 0 and get_milking_position(character_id, service_cid) == position


def get_job_behavior_and_unable_reason(character_id: int, service_cid: int) -> Tuple[str, str]:
    """
    执行榨精时判断选定的部位此刻能否使用，能用时给出该部位对应的 H 部位交 / 服装交行为
    Keyword arguments:
    character_id -- 干员id
    service_cid -- 助理服务id（5早安 / 6晚安）
    Return arguments:
    str -- 对应的 H 行为id，不能执行时为空字符串
    str -- 不能执行的原因，能执行时为空字符串
    """
    character_data: game_type.Character = cache.character_data[character_id]
    position = get_milking_position(character_id, service_cid)
    if position == -1:
        return "", _("还没有选定部位")
    # 身体部位
    if position < CLOTH_POSITION_OFFSET:
        body_unable_reason = get_body_part_unable_reason(character_id, position)
        if body_unable_reason:
            return "", body_unable_reason
        return BODY_PART_JOB_BEHAVIOR[position], ""
    # 服装部位：此刻身上要穿着
    cloth_type = position - CLOTH_POSITION_OFFSET
    if cloth_type not in CLOTH_TYPE_JOB_BEHAVIOR:
        return "", _("{0}没有对应的服装交").format(get_position_name(position))
    if not len(character_data.cloth.cloth_wear.get(cloth_type, [])):
        return "", _("身上没有穿着{0}").format(get_position_name(position))
    if cloth_type == 8 and not handle_premise.handle_wear_skirt(character_id):
        return "trousers_job", ""
    return CLOTH_TYPE_JOB_BEHAVIOR[cloth_type], ""


def judge_defer_day_first_meet(character_id: int) -> bool:
    """
    判断今天的每日招呼（含上交内裤与袜子）是否要推迟到早安榨精之后
    Keyword arguments:
    character_id -- 干员id
    Return arguments:
    bool -- 要推迟时为True
    功能: 早安榨精选了内裤或袜子、她被要求每天上交这件且此刻穿着、今天还没进行早安问候、本次能执行时推迟。
          早安问候的状态机先把早安问候置为已完成再结算，于是榨精行为结算末尾的二段结算里就会补上每日招呼与上交，
          上交的正是刚被射过的那一件。早安问候到中午作罢时同样置为已完成，届时照常上交。
          开着早安服务的助理本来就不做每日招呼，推迟只影响上交的时机
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if cache.character_data[0].assistant_character_id != character_id:
        return False
    if character_data.assistant_services.get(5, 0) != MILKING_OPTION:
        return False
    if character_data.sp_flag.morning_salutation == 2:
        return False
    # 选的是今天要上交的那件：条件与 second_behavior.judge_character_first_meet 里的上交条件一致
    cloth_type = get_milking_position(character_id, 5) - CLOTH_POSITION_OFFSET
    if cloth_type == 9:
        hand_in_flag = handle_premise.handle_wear_pan(character_id) and handle_premise.handle_ask_give_pan_everyday(character_id)
    elif cloth_type == 10:
        hand_in_flag = handle_premise.handle_wear_socks(character_id) and handle_premise.handle_ask_give_socks_everyday(character_id)
    else:
        hand_in_flag = False
    if not hand_in_flag:
        return False
    # 本次执行不了（部位）时不推迟，免得白白压到中午
    job_behavior_id, _unable_reason = get_job_behavior_and_unable_reason(character_id, 5)
    return job_behavior_id != ""
