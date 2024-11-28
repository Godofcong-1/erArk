import datetime
from types import FunctionType
from Script.Design import (
    settle_behavior,
    attr_calculation,
    clothing,
    map_handle,
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
    handle_bra_see(character_data.target_character_id, add_time, change_data, now_time)


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
    handle_pan_see(character_data.target_character_id, add_time, change_data, now_time)


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
        clothing.get_npc_cloth(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_BRA_PAN_SEE)
def handle_scene_all_characters_bra_pan_see(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    场景内所有角色胸罩、内裤可视
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        if chara_id == 0:
            continue
        handle_bra_see(chara_id, add_time, change_data, now_time)
        handle_pan_see(chara_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_T_PAN)
def handle_get_t_pan(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    获得交互对象的内裤
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    clothing.pl_get_chara_pan(character_data.target_character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_T_SOCKS)
def handle_get_t_sock(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    获得交互对象的袜子
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    clothing.pl_get_chara_socks(character_data.target_character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_SCENE_T_PAN)
def handle_get_scene_t_pan(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    获得场景内所有其他角色的内裤
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 遍历当前角色列表
    for chara_id in scene_data.character_list:
        # 遍历非玩家的角色
        if chara_id > 0:
            clothing.pl_get_chara_pan(chara_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_SCENE_T_SOCKS)
def handle_get_scene_t_socks(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    获得场景内所有其他角色的袜子
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 遍历当前角色列表
    for chara_id in scene_data.character_list:
        # 遍历非玩家的角色
        if chara_id > 0:
            clothing.pl_get_chara_socks(chara_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_CLOTH_BACK)
def handle_self_cloth_back(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    自己穿回H时脱掉的衣服
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]

    # 穿回脱下的衣服
    wear_flag = False
    for i in game_config.config_clothing_type:
        if len(character_data.cloth.cloth_off[i]):
            character_data.cloth.cloth_wear[i],character_data.cloth.cloth_off[i] = character_data.cloth.cloth_off[i],[]
            wear_flag = True
    if wear_flag:
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        if character_data.sp_flag.unconscious_h:
            now_draw.text = _("\n给{0}穿上了脱下的衣服，并尽量整理成H前的样子\n").format(character_data.name)
        else:
            now_draw.text = _("\n{0}穿回了脱下的衣服\n").format(character_data.name)
        now_draw.draw()


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
    handle_self_cloth_back(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_CLOTH_BACK)
def handle_scene_all_characters_cloth_back(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    场景内所有角色穿回H时脱掉的衣服
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 遍历当前角色列表
    for chara_id in scene_data.character_list:
        if chara_id == 0:
            continue
        handle_self_cloth_back(chara_id, add_time, change_data, now_time)


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
    clothing.get_all_cloth_off(character_id)


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
    清零其他衣服并换上浴帽和浴巾
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    clothing.get_shower_cloth(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_SLEEP_CLOTH)
def handle_get_sleep_cloth(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    清零其他衣服并换上睡衣（管理中则全裸）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    from Script.Design import handle_premise
    if handle_premise.handle_ask_not_wear_cloth_in_sleep(character_id):
        clothing.get_all_cloth_off(character_id)
    else:
        clothing.get_sleep_cloth(character_id)


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


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.LOCKER_CLOTH_IN_SHOWER_RESET)
def handle_locker_cloth_in_shower_reset(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    大浴场衣柜里的衣服清零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data = cache.character_data[character_id]
    character_data.cloth.cloth_locker_in_shower = attr_calculation.get_shower_cloth_locker_zero()
    # print(f"debug {character_data.name} cloth_locker = {character_data.cloth.cloth_locker}")
    clothing.clean_locker_semen(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WEAR_TO_SHOWER_LOCKER)
def handle_wear_to_shower_locker(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    身上首饰以外的衣服转移到大浴场柜子里
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
                    character_data.cloth.cloth_locker_in_shower[clothing_type].append(cloth_id)
    character_data.dirty.cloth_locker_semen, character_data.dirty.cloth_semen = character_data.dirty.cloth_semen, character_data.dirty.cloth_locker_semen


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SHOWER_LOCKER_TO_WEAR)
def handle_shower_locker_to_wear(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    大浴场衣柜里的衣服转移到身上
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
        if len(character_data.cloth.cloth_locker_in_shower[clothing_type]):
            # 复制该服装类型的衣柜列表
            tem_list = character_data.cloth.cloth_locker_in_shower[clothing_type].copy()
            # 遍历该服装类型的衣柜列表
            for cloth_id in tem_list:
                # 将服装添加到穿着列表中
                character_data.cloth.cloth_wear[clothing_type].append(cloth_id)
                # 将服装从衣柜列表中移除
                character_data.cloth.cloth_locker_in_shower[clothing_type].remove(cloth_id)

    # 将衣柜里的衣服精液转移到穿着的衣服上
    clothing.locker_cloth_semen_to_wear_cloth_semen(character_id)
    # 穿特殊服装
    clothing.chara_special_wear_cloth(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FOOT_CLOTH_TO_SHOWER_LOCKER)
def handle_foot_cloth_to_shower_locker(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    袜子和鞋子转移到大浴场衣柜里
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data = cache.character_data[character_id]

    for clothing_type in {10,11}:
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
                    character_data.cloth.cloth_locker_in_shower[clothing_type].append(cloth_id)
        character_data.dirty.cloth_locker_semen[clothing_type] = character_data.dirty.cloth_semen[clothing_type]


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SHOWER_LOCKER_TO_DORMITORY_LOCKER)
def handle_shower_locker_to_dormitory_locker(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    大浴场衣柜里的衣服转移到宿舍衣柜
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

    character_data.cloth.cloth_locker_in_dormitory = character_data.cloth.cloth_locker_in_shower.copy()
    character_data.cloth.cloth_locker_in_shower = attr_calculation.get_shower_cloth_locker_zero()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CLEAN_LOCKER_CLOTH_SEMEN)
def handle_clean_locker_cloth_semen(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    清理衣柜里的衣服精液
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    clothing.clean_locker_semen(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GET_CLOTH_FROM_DORMITORY_LOCKER)
def handle_get_cloth_from_dormitory_locker(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    清空身上的旧衣服，从宿舍的衣柜里穿上衣服、内衣内裤，并转移衣柜中的精液数据到穿着的衣服上
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    clothing.get_cloth_from_dormitory_locker(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UP_AND_BRA_TO_TEM)
def handle_up_and_bra_to_tem(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    自己的上衣和胸罩转移到临时脱下
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]

    for i in [5,6]:
        if len(character_data.cloth.cloth_wear[i]):
            character_data.cloth.cloth_off[i], character_data.cloth.cloth_wear[i] = character_data.cloth.cloth_wear[i], []


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_AND_PAN_TO_TEM)
def handle_down_and_pan_to_tem(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    自己的下衣和内裤转移到临时脱下
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]

    for i in [8,9]:
        if len(character_data.cloth.cloth_wear[i]):
            character_data.cloth.cloth_off[i], character_data.cloth.cloth_wear[i] = character_data.cloth.cloth_wear[i], []


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_UP_AND_BRA_TO_TEM)
def handle_target_up_and_bra_to_tem(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象的上衣和胸罩转移到临时脱下
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

    for i in [5,6]:
        if len(target_data.cloth.cloth_wear[i]):
            target_data.cloth.cloth_off[i], target_data.cloth.cloth_wear[i] = target_data.cloth.cloth_wear[i], []


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_DOWN_AND_PAN_TO_TEM)
def handle_target_down_and_pan_to_tem(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象的下衣和内裤转移到临时脱下
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

    for i in [8,9]:
        if len(target_data.cloth.cloth_wear[i]):
            target_data.cloth.cloth_off[i], target_data.cloth.cloth_wear[i] = target_data.cloth.cloth_wear[i], []
