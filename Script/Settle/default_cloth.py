import datetime
from types import FunctionType
from Script.Design import (
    settle_behavior,
    character,
    character_handle,
    map_handle,
    attr_calculation,
    game_time,
    clothing,
)
from Script.Core import cache_control, constant, constant_effect, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw


_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """



@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CHANGE_UNDERWERA)
def handle_change_underware(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    换新的内衣（胸部+内裤）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.cloth[6] = []
    character_data.cloth[9] = []
    if character_id:
        clothing.get_underwear(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BRA_SEE)
def handle_bra_see(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    胸罩可视
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.cloth_see[6] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_BRA_SEE)
def handle_target_bra_see(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象胸罩可视
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
    target_data.cloth_see[6] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PAN_SEE)
def handle_pan_see(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    内裤可视
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.cloth_see[9] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_PAN_SEE)
def handle_target_pan_see(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象内裤可视
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
    target_data.cloth_see[9] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CLOTH_SEE_ZERO)
def handle_cloth_see_zero(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    内衣可视清零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.cloth_see = {6:False,9:False}


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.RESTE_CLOTH)
def handle_reset_cloth(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    衣服重置为初始状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id:
        character_data: game_type.Character = cache.character_data[character_id]
        character_tem = cache.npc_tem_data[character_id-1]
        for cloth_id in character_tem.Cloth:
            type = game_config.config_clothing_tem[cloth_id].clothing_type
            # print(f"debug cloth_id = {cloth_id},name = {game_config.config_clothing_tem[cloth_id].name},type = {type}")
            if type in {6,9}:
                continue
            if cloth_id not in character_data.cloth[type]:
                character_data.cloth[type].append(cloth_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ASK_FOR_PAN)
def handle_ask_for_pan(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    索要内裤
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
    character_data.pl_collection.npc_panties_tem[character_data.target_character_id] = []
    character_data.pl_collection.npc_panties_tem[character_data.target_character_id].append(target_data.cloth[9][0])
    TagetPanId = target_data.cloth[9][0]
    TPanName = game_config.config_clothing_tem[TagetPanId].name
    character_data.behavior.pan_name = TPanName
    target_data.cloth[9] = []
    target_data.cloth_see[9] = True

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ASK_FOR_SOCKS)
def handle_ask_for_sock(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    索要袜子
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
    character_data.pl_collection.npc_socks_tem[character_data.target_character_id] = []
    character_data.pl_collection.npc_socks_tem[character_data.target_character_id].append(target_data.cloth[10][0])
    TagetSocId = target_data.cloth[10][0]
    TSocName = game_config.config_clothing_tem[TagetSocId].name
    character_data.behavior.socks_name = TSocName
    target_data.cloth[10] = []


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.T_CLOTH_BACK)
def handle_t_cloth_back(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象穿回H时脱掉的衣服
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

    # 穿回脱下的衣服
    wear_flag = False
    for i in game_config.config_clothing_type:
        if len(target_data.cloth_off[i]):
            target_data.cloth[i],target_data.cloth_off[i] = target_data.cloth_off[i],[]
            wear_flag = True
    if wear_flag:
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n{target_data.name}穿回了脱下的衣服")
        now_draw.draw()
