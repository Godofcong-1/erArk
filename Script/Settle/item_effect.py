import datetime
import random
from types import FunctionType

from Script.Design import (
    settle_behavior,
    map_handle,
    attr_calculation,
    cooking,
    handle_premise,
    second_behavior,
)
from Script.Core import cache_control, constant_effect, game_type, get_text
from Script.Config import normal_config
from Script.UI.Moudle import draw

_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ITEM_OFF)
def handle_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    去掉身上所有的道具（含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    for i in range(len(character_data.h_state.body_item)):
        character_data.h_state.body_item[i][1] = False
        character_data.h_state.body_item[i][2] = None


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ITEM_OFF)
def handle_target_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉身上所有的道具（含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_item_off(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ITEM_OFF_EXCEPT_PILL)
def handle_item_off_except_pill(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    去掉身上所有的H道具（不含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    for i in range(len(character_data.h_state.body_item)):
        if i in {8,9,10,11,12}:
            continue
        character_data.h_state.body_item[i][1] = False
        character_data.h_state.body_item[i][2] = None


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ITEM_OFF_EXCEPT_PILL)
def handle_target_item_off_except_pill(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉身上所有的道具（不含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_item_off_except_pill(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_B_ITEM_OFF)
def handle_target_b_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉B部位的道具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    for i in [0, 4]:
        target_data.h_state.body_item[i][1] = False
        target_data.h_state.body_item[i][2] = None


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_A_ITEM_OFF)
def handle_target_a_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉A部位的道具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    for i in [3, 7]:
        target_data.h_state.body_item[i][1] = False
        target_data.h_state.body_item[i][2] = None



@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_VIBRATOR_ON)
def handle_target_vibrator_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象插入V震动棒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[2][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_VIBRATOR_OFF)
def handle_target_vibrator_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象拔出V震动棒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[2][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_VIBRATOR_ON)
def handle_target_anal_vibrator_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象插入A震动棒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[3][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_VIBRATOR_OFF)
def handle_target_anal_vibrator_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象拔出A震动棒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[3][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NIPPLE_CLAMP_ON)
def handle_target_nipple_clamp_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上乳头夹
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[0][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NIPPLE_CLAMP_OFF)
def handle_target_nipple_clamp_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下乳头夹
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[0][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_CLIT_CLAMP_ON)
def handle_target_clit_clamp_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[1][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_CLIT_CLAMP_OFF)
def handle_target_clit_clamp_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[1][1] = False

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_BEADS_ON)
def handle_target_anal_beads_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象塞入肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[7][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_BEADS_OFF)
def handle_target_anal_beads_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象拔出肛门拉珠
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[7][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MILKING_MACHINE_ON)
def handle_target_milking_machine_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上搾乳机
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[4][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MILKING_MACHINE_OFF)
def handle_target_milking_machine_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下搾乳机
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[4][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_URINE_COLLECTOR_ON)
def handle_target_urine_collector_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上采尿器
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[5][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_URINE_COLLECTOR_OFF)
def handle_target_urine_collector_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下采尿器
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[5][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_PATCH_ON)
def handle_target_patch_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上眼罩
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[6][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_PATCH_OFF)
def handle_target_patch_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下眼罩
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[6][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_GAG_ON)
def handle_target_gag_on(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象戴上口球
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[14][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_GAG_OFF)
def handle_target_gag_off(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象取下口球
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[14][1] = False



@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADJUST_BODY_MANAGE_DAY_ITEM)
def handle_adjust_body_manage_day_item(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    调整自己的身体管理_白天道具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id == 0:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 这里把交互对象设为自己是因为下面的装备/取下道具函数都是让交互对象结算的
    character_data.target_character_id = character_id
    # 身体管理_乳头夹
    if handle_premise.handle_ask_equp_nipple_clamp_in_day(character_id) and not handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_nipple_clamp_in_day(character_id) and handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_阴蒂夹
    if handle_premise.handle_ask_equp_clit_clamp_in_day(character_id) and not handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_clit_clamp_in_day(character_id) and handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_V振动棒
    if handle_premise.handle_ask_equp_v_bibrator_in_day(character_id) and not handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_v_bibrator_in_day(character_id) and handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_off(character_id, add_time, change_data, now_time)
    # 身体管理_A振动棒
    if handle_premise.handle_ask_equp_a_bibrator_in_day(character_id) and not handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_a_bibrator_in_day(character_id) and handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_off(character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADJUST_BODY_MANAGE_SLEEP_ITEM)
def handle_adjust_body_manage_sleep_item(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    调整自己的身体管理_睡觉道具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id == 0:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 这里把交互对象设为自己是因为下面的装备/取下道具函数都是让交互对象结算的
    character_data.target_character_id = character_id
    # 身体管理_乳头夹
    if handle_premise.handle_ask_equp_nipple_clamp_in_sleep(character_id) and not handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_nipple_clamp_in_sleep(character_id) and handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_阴蒂夹
    if handle_premise.handle_ask_equp_clit_clamp_in_sleep(character_id) and not handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_clit_clamp_in_sleep(character_id) and handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_V振动棒
    if handle_premise.handle_ask_equp_v_bibrator_in_sleep(character_id) and not handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_v_bibrator_in_sleep(character_id) and handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_off(character_id, add_time, change_data, now_time)
    # 身体管理_A振动棒
    if handle_premise.handle_ask_equp_a_bibrator_in_sleep(character_id) and not handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_a_bibrator_in_sleep(character_id) and handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_off(character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_BODY_LUBRICANT)
def handle_use_body_lubricant(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个润滑液
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[100] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_PHILTER)
def handle_use_philter(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个媚药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[103] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_ENEMAS)
def handle_use_enemas(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个灌肠液
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[104] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_DIURETICS_ONCE)
def handle_use_diuretics_once(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个一次性利尿剂
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[105] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_DIURETICS_PERSISTENT)
def handle_use_diuretics_persistent(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个持续性利尿剂
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[106] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_SLEEPING_PILLS)
def handle_use_sleeping_pills(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个安眠药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[107] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_OVULATION_PROMOTING_DRUGS)
def handle_use_ovulation_promoting_drugs(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个排卵促进药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[108] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_CONTRACEPTIVE_BEFORE)
def handle_use_contraceptive_before(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个事前避孕药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[101] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_CONTRACEPTIVE_AFTER)
def handle_use_contraceptive_after(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个事后避孕药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[102] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_RING)
def handle_use_ring(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个戒指
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[201] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_COLLAR)
def handle_use_collar(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个项圈
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[202] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_BAG)
def handle_use_bag(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个干员携袋
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[151] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_CONDOM)
def handle_use_condom(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个避孕套
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[120] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_URETHRAL_SWAB)
def handle_use_urethral_swab(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个尿道棉棒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[139] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_SAFE_CANDLES)
def handle_use_safe_candles(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个低温蜡烛
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[136] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DELETE_FOOD)
def handle_delete_food(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    删除当前行动中的对象食物
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    if character_data.behavior.target_food is not None:
        food: game_type.Food = character_data.behavior.target_food
        if food.uid in character_data.food_bag:
            del character_data.food_bag[food.uid]


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MAKE_FOOD)
def handle_make_food(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    结算因为制作食物而加好感
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    from Script.Settle.common_default import base_chara_favorability_and_trust_common_settle

    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    if character_data.behavior.target_food is not None:
        food: game_type.Food = character_data.behavior.target_food
        food_name = ""
        make_food_time = 0
        food_name = cache.recipe_data[food.recipe].name
        make_food_time = cache.recipe_data[food.recipe].time
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, 0, change_data)



@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NPC_MAKE_FOOD_TO_SHOP)
def handle_npc_make_food_to_shop(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    NPC随机制作一个食物，并补充到当前所在食物商店中
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 随机选择一个食谱，根据食谱难度，高难度的有高出现权重
    cookable_recipes_list = cooking.get_character_cookable_recipes(character_id, weight_flag=True)
    recipes_id = random.choice(cookable_recipes_list)
    # 获取角色数据与食谱数据
    character_data: game_type.Character = cache.character_data[character_id]
    cook_ability_lv = character_data.ability[43]
    food_recipe: game_type.Recipes = cache.recipe_data[recipes_id]
    # 制作食物
    food_list = {}
    # 每级料理技能等级增加一次制作次数
    for i in range(cook_ability_lv + 1):
        new_food = cooking.cook(food_list, recipes_id, cook_ability_lv, character_data.name)
        # 将食物添加到当前所在食物商店中
        cache.rhodes_island.dining_hall_data.setdefault(str(recipes_id), {})
        cache.rhodes_island.dining_hall_data[str(recipes_id)][new_food.uid] = new_food
    # 将食物名记录到角色数据中
    character_data.behavior.food_name = food_recipe.name


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NPC_MAKE_FOOD_TO_BAG)
def handle_npc_make_food_to_bag(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    NPC随机制作一个食物，并补充到自己背包中
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[character_id]
    # 随机选择一个食谱，根据食谱难度，高难度的有高出现权重
    cookable_recipes_list = cooking.get_character_cookable_recipes(character_id, weight_flag=True)
    recipes_id = random.choice(cookable_recipes_list)
    food_recipe: game_type.Recipes = cache.recipe_data[recipes_id]
    food_list = {}
    new_food = cooking.cook(food_list, recipes_id, character_data.ability[43], character_data.name)
    character_data.food_bag[new_food.uid] = new_food
    character_data.behavior.food_name = food_recipe.name


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DELETE_ALL_FOOD)
def handle_delete_all_food(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    删除背包内所有食物
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    for food_id in character_data.food_bag.copy():
        food: game_type.Food = character_data.food_bag[food_id]
        del character_data.food_bag[food.uid]



@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_HUGE_LUBRICATION)
def handle_target_add_huge_lubrication(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加大量润滑（润滑液）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(8, 0)
    now_lust = target_data.status_data[8]
    now_lust_multiple = 10000 - int(now_lust *0.1)
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    target_data.status_data[8] = min(99999, target_data.status_data[8])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_HUGE_DESIRE_AND_SUBMIT)
def handle_target_add_huge_desire_and_submit(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加大量欲情和屈服和欲望值（媚药）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return

    # 欲情
    target_data.status_data.setdefault(12, 0)
    now_lust = target_data.status_data[12]
    now_lust_multiple = 10000 - int(now_lust *0.016) 
    now_add_lust = now_lust_multiple
    target_data.status_data[12] += now_add_lust
    target_data.status_data[12] = min(99999, target_data.status_data[12])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(12, 0)
    target_change.status_data[12] += now_add_lust

    # 屈服
    target_data.status_data.setdefault(15, 0)
    now_lust = target_data.status_data[15]
    now_lust_multiple = 10000 - int(now_lust *0.016) 
    now_add_lust = now_lust_multiple
    target_data.status_data[15] += now_add_lust
    target_data.status_data[15] = min(99999, target_data.status_data[15])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(15, 0)
    target_change.status_data[15] += now_add_lust

    # 欲望值
    target_data.desire_point = 100

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ENEMA)
def handle_target_enema(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象A灌肠并增加中量润滑
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    from Script.Settle.common_default import base_chara_state_common_settle
    from Script.Design import handle_ability

    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return

    # 增加润滑
    target_data.status_data.setdefault(8, 0)
    now_lust = target_data.status_data[8]
    now_lust_multiple = 2500 - int(now_lust *0.04) 
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    target_data.status_data[8] = min(99999, target_data.status_data[8])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

    # 根据A扩张和当前灌肠液量来判定苦痛程度
    ability_lv = target_data.ability[10]
    ability_adjust = handle_ability.get_ability_adjust(ability_lv)
    enema_capacity = target_data.dirty.enema_capacity
    enema_capacity_adjust = 2 ** (enema_capacity + 1)
    extra_adjust = enema_capacity_adjust / ability_adjust
    base_chara_state_common_settle(character_data.target_character_id, add_time, 17, base_value = 1000, ability_level = target_data.ability[15], extra_adjust = extra_adjust, change_data_to_target_change = change_data)

    # A灌肠
    target_data.dirty.a_clean = 1
    target_data.dirty.enema_capacity += 1
    target_data.dirty.enema_capacity = min(6, target_data.dirty.enema_capacity)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ENEMA_END)
def handle_target_enema_end(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象结束A灌肠并增加中量润滑
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return

    # 增加润滑
    target_data.status_data.setdefault(8, 0)
    now_lust = target_data.status_data[8]
    now_lust_multiple = 2500 - int(now_lust *0.04) 
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    target_data.status_data[8] = min(99999, target_data.status_data[8])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

    # A灌肠结束
    if target_data.dirty.a_clean == 1:
        target_data.dirty.a_clean = 2
    elif target_data.dirty.a_clean == 3:
        target_data.dirty.a_clean = 4
        # 清空肠内精液量的90%
        now_semen_data = character_data.dirty.body_semen[8]
        semen_num = now_semen_data[1] * 0.9
        if semen_num > 1:
            now_semen_data[1] -= semen_num
            now_semen_data[2] = attr_calculation.get_semen_now_level(now_semen_data[1], 8, 0)
            # 绘制提示信息
            info_text  = _("{0}的后穴喷出了{1}ml的精液\n").format(target_data.name, int(semen_num))
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = width
            info_draw.draw()
    # 清空灌肠液量
    target_data.dirty.enema_capacity = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_URINATE)
def handle_target_add_urinate(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象尿意值全满
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.urinate_point = 240


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_DIURETICS_ON)
def handle_target_diuretics_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象获得利尿剂状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    end_time = now_time + datetime.timedelta(hours=4)
    target_data.h_state.body_item[8][1] = True
    target_data.h_state.body_item[8][2] = end_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_TIRED_TO_SLEEP)
def handle_target_add_tired_tosleep(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象疲劳值全满，进入8h的睡眠
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.tired_point = 160
    target_data.sleep_point = 100
    target_data.h_state.body_item[9][1] = True
    target_data.h_state.body_item[9][2] = now_time + datetime.timedelta(hours=8)
    handle_premise.settle_chara_unnormal_flag(character_data.target_character_id, 6)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_PREGNANCY_CHANCE)
def handle_target_add_pregnancy_chance(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    道具_使用效果 交互对象获得排卵促进药状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[10][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NO_PREGNANCY_NEXT_DAY)
def handle_target_no_pregnancy_next_day(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象获得事前避孕药状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[11][1] = True
    target_data.h_state.body_item[11][2] = now_time + datetime.timedelta(days=30)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NO_PREGNANCY_FROM_LAST_H)
def handle_target_no_pregnancy_from_last_h(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象获得事后避孕药状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.body_item[12][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WEAR_CONDOM)
def handle_wear_condom(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己获得戴上避孕套状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.h_state.body_item[13][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TAKE_CONDOM_OFF)
def handle_take_condom_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己去掉戴上避孕套状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.h_state.body_item[13][1] = False

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_REMOTE_TOY_OFF)
def handle_self_remote_toy_off(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    关闭自己身上的情趣玩具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.sex_toy_level = 0

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_REMOTE_TOY_SET_WEAK)
def handle_self_remote_toy_set_weak(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将自己身上的情趣玩具调到弱档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.sex_toy_level = 1

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_REMOTE_TOY_SET_MEDIUM)
def handle_self_remote_toy_set_medium(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将自己身上的情趣玩具调到中档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.sex_toy_level = 2

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_REMOTE_TOY_SET_STRONG)
def handle_self_remote_toy_set_strong(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将自己身上的情趣玩具调到强档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.sex_toy_level = 3

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_REMOTE_TOY_OFF)
def handle_target_remote_toy_off(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    关闭交互对象身上的情趣玩具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_self_remote_toy_off(character_data.target_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_REMOTE_TOY_SET_WEAK)
def handle_target_remote_toy_set_weak(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将交互对象身上的情趣玩具调到弱档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 如果对方没有情趣玩具则跳过
    if handle_premise.handle_self_no_sex_toy(character_data.target_character_id):
        return
    handle_self_remote_toy_set_weak(character_data.target_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_REMOTE_TOY_SET_MEDIUM)
def handle_target_remote_toy_set_medium(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将交互对象身上的情趣玩具调到中档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 如果对方没有情趣玩具则跳过
    if handle_premise.handle_self_no_sex_toy(character_data.target_character_id):
        return
    handle_self_remote_toy_set_medium(character_data.target_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_REMOTE_TOY_SET_STRONG)
def handle_target_remote_toy_set_strong(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将交互对象身上的情趣玩具调到强档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 如果对方没有情趣玩具则跳过
    if handle_premise.handle_self_no_sex_toy(character_data.target_character_id):
        return
    handle_self_remote_toy_set_strong(character_data.target_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ALL_REMOTE_TOY_OFF)
def handle_all_remote_toy_off(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    关闭在场所有人身上的情趣玩具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    for now_character_id in character_list:
        # 跳过玩家
        if now_character_id == 0:
            continue
        # 跳过没有情趣玩具的人
        if handle_premise.handle_self_no_sex_toy(now_character_id):
            continue
        handle_self_remote_toy_off(now_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ALL_REMOTE_TOY_SET_WEAK)
def handle_all_remote_toy_set_weak(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将在场所有人身上的情趣玩具调到弱档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    for now_character_id in character_list:
        if now_character_id == 0:
            continue
        if handle_premise.handle_self_no_sex_toy(now_character_id):
            continue
        handle_self_remote_toy_set_weak(now_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ALL_REMOTE_TOY_SET_MEDIUM)
def handle_all_remote_toy_set_medium(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将在场所有人身上的情趣玩具调到中档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    for now_character_id in character_list:
        if now_character_id == 0:
            continue
        if handle_premise.handle_self_no_sex_toy(now_character_id):
            continue
        handle_self_remote_toy_set_medium(now_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ALL_REMOTE_TOY_SET_STRONG)
def handle_all_remote_toy_set_strong(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    将在场所有人身上的情趣玩具调到强档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_list = map_handle.get_chara_now_scene_all_chara_id_list(character_id)
    for now_character_id in character_list:
        if now_character_id == 0:
            continue
        if handle_premise.handle_self_no_sex_toy(now_character_id):
            continue
        handle_self_remote_toy_set_strong(now_character_id, add_time, change_data, now_time)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_REMOTE_TOY_USE_OR_SET_WEAK)
def handle_target_remote_toy_use_or_set_weak(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    如果交互对象已有强度设定则继续使用，否则开启到弱档
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 如果对方没有情趣玩具则跳过
    if handle_premise.handle_self_no_sex_toy(character_data.target_character_id):
        return
    # 交互对象已有强度设定则继续使用
    if handle_premise.handle_self_now_sex_toy_on(character_data.target_character_id):
        return
    # 否则开启到弱档
    handle_self_remote_toy_set_weak(character_data.target_character_id, add_time, change_data, now_time)
