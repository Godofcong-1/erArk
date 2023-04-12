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
    character_data.cloth.cloth_wear[6] = []
    character_data.cloth.cloth_wear[9] = []
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
    character_data.cloth.cloth_see[6] = True


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
    target_data.cloth.cloth_see[6] = True


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
    character_data.cloth.cloth_see[9] = True


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
    target_data.cloth.cloth_see[9] = True


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
    character_data.cloth.cloth_see = {6:False,9:False}


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
        character_data.cloth.cloth_wear = attr_calculation.get_cloth_wear_zero()
        character_tem = cache.npc_tem_data[character_id-1]
        for cloth_id in character_tem.Cloth:
            type = game_config.config_clothing_tem[cloth_id].clothing_type
            # print(f"debug cloth_id = {cloth_id},name = {game_config.config_clothing_tem[cloth_id].name},type = {type}")
            if type in {6,9}:
                continue
            if cloth_id not in character_data.cloth.cloth_wear[type]:
                character_data.cloth.cloth_wear[type].append(cloth_id)


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
    character_data.pl_collection.npc_panties_tem[character_data.target_character_id].append(target_data.cloth.cloth_wear[9][0])
    TagetPanId = target_data.cloth.cloth_wear[9][0]
    TPanName = game_config.config_clothing_tem[TagetPanId].name
    character_data.behavior.pan_name = TPanName
    target_data.cloth.cloth_wear[9] = []
    target_data.cloth.cloth_see[9] = True

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
    character_data.pl_collection.npc_socks_tem[character_data.target_character_id].append(target_data.cloth.cloth_wear[10][0])
    TagetSocId = target_data.cloth.cloth_wear[10][0]
    TSocName = game_config.config_clothing_tem[TagetSocId].name
    character_data.behavior.socks_name = TSocName
    target_data.cloth.cloth_wear[10] = []


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
        if len(target_data.cloth.cloth_off[i]):
            target_data.cloth.cloth_wear[i],target_data.cloth.cloth_off[i] = target_data.cloth.cloth_off[i],[]
            wear_flag = True
    if wear_flag:
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = _(f"\n{target_data.name}穿回了脱下的衣服")
        now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WEAR_CLOTH_OFF)
def handle_wear_cloth_off(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    脱掉全部衣服
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    clothing.get_cloth_off(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WEAR_CLOTH_OFF_MOST)
def handle_wear_cloth_off_most(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    脱掉大部分衣服（保留首饰等）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    clothing.get_cloth_wear_zero_except_need(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_SHOWER_CLOTH)
def handle_get_shower_cloth(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    换上浴帽和浴巾
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    clothing.get_shower_cloth(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_SWIM_CLOTH)
def handle_get_swim_cloth(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    清零其他衣服并换上泳衣
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    clothing.get_swim_cloth(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.LOCKER_CLOTH_RESET)
def handle_locker_cloth_reset(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    衣柜里的衣服清零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data = cache.character_data[character_id]
    character_data.cloth.cloth_locker = attr_calculation.get_cloth_locker_zero()
    # print(f"debug {character_data.name} cloth_locker = {character_data.cloth.cloth_locker}")
    character_data.dirty.cloth_locker_semen = []


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WEAR_TO_LOCKER)
def handle_wear_to_locker(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    身上首饰以外的衣服转移到柜子里
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data = cache.character_data[character_id]

    for clothing_type in game_config.config_clothing_type:
        if len(character_data.cloth.cloth_wear[clothing_type]):
            tem_list = character_data.cloth.cloth_wear[clothing_type].copy()
            for cloth_id in tem_list:
                # print(f"debug cloth_id = {cloth_id}")
                # 不转移首饰和必须穿着的衣服
                if (
                    game_config.config_clothing_tem[cloth_id].tag != 6 
                    and cloth_id not in clothing.chara_special_wear_cloth(character_id)
                ):
                    # print(f"debug move_cloth_id = {cloth_id}")
                    character_data.cloth.cloth_wear[clothing_type].remove(cloth_id)
                    character_data.cloth.cloth_locker[clothing_type].append(cloth_id)
    character_data.dirty.cloth_locker_semen = character_data.dirty.cloth_semen


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.LOCKER_TO_WEAR)
def handle_locker_to_wear(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    衣柜里的衣服转移到身上
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 从缓存中获取角色数据
    character_data = cache.character_data[character_id]

    # 遍历游戏配置中的所有服装类型
    for clothing_type in game_config.config_clothing_type:
        # 如果某个服装类型的衣柜不为空
        if len(character_data.cloth.cloth_locker[clothing_type]):
            # 复制该服装类型的衣柜列表
            tem_list = character_data.cloth.cloth_locker[clothing_type].copy()
            # 遍历该服装类型的衣柜列表
            for cloth_id in tem_list:
                # 将服装添加到穿着列表中
                character_data.cloth.cloth_wear[clothing_type].append(cloth_id)
                # 将服装从衣柜列表中移除
                character_data.cloth.cloth_locker[clothing_type].remove(cloth_id)

    # 将衣服脏污设置为衣柜脏污中的内容
    character_data.dirty.cloth_semen = character_data.dirty.cloth_locker_semen
    # 穿特殊服装
    clothing.chara_special_wear_cloth(character_id)

