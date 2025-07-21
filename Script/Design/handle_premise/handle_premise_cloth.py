from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type
from Script.Config import game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

def add_premise(premise: str) -> FunctionType:
    """
    添加前提
    Keyword arguments:
    premise -- 前提id
    Return arguments:
    FunctionType -- 前提处理函数对象
    """

    def decoraror(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.handle_premise_data[premise] = return_wrapper
        return return_wrapper

    return decoraror


@add_premise(constant_promise.Premise.TARGET_WEAR_HAT)
def handle_t_wear_hat(character_id: int) -> int:
    """
    交互对象穿着帽子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[0]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_HAT)
def handle_t_not_wear_hat(character_id: int) -> int:
    """
    交互对象没有穿着帽子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_not_wear_hat(character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_GLASS)
def handle_t_wear_glass(character_id: int) -> int:
    """
    交互对象戴着眼镜
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[1]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_GLASS)
def handle_t_not_wear_glass(character_id: int) -> int:
    """
    交互对象没有戴着眼镜
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_glass(character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_IN_EAR)
def handle_t_wear_in_ear(character_id: int) -> int:
    """
    交互对象戴耳饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[2]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_EAR)
def handle_t_not_wear_in_ear(character_id: int) -> int:
    """
    交互对象没有戴耳饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_ear(character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_IN_NECK)
def handle_t_wear_in_neck(character_id: int) -> int:
    """
    交互对象戴脖饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[3]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_NECK)
def handle_t_not_wear_in_neck(character_id: int) -> int:
    """
    交互对象没有戴脖饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_neck(character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_IN_MOUSE)
def handle_t_wear_in_mouse(character_id: int) -> int:
    """
    交互对象戴口饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[4]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_MOUSE)
def handle_t_not_wear_in_mouse(character_id: int) -> int:
    """
    交互对象没有戴口饰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_mouse(character_id)

@add_premise(constant_promise.Premise.WEAR_IN_UP)
def handle_wear_in_up(character_id: int) -> int:
    """
    穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[5]):
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_WEAR_IN_UP)
def handle_not_wear_in_up(character_id: int) -> int:
    """
    没有穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_wear_in_up(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.TARGET_WEAR_IN_UP)
def handle_t_wear_in_up(character_id: int) -> int:
    """
    交互对象穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_wear_in_up(character_data.target_character_id):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_UP)
def handle_t_not_wear_in_up(character_id: int) -> int:
    """
    交互对象没有穿着上衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_wear_in_up(character_data.target_character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.WEAR_BRA)
def handle_wear_bra(character_id: int) -> int:
    """
    穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[6]):
        return 1
    else:
        return 0

@add_premise(constant_promise.Premise.NOT_WEAR_BRA)
def handle_not_wear_bra(character_id: int) -> int:
    """
    没有穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_wear_bra(character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_BRA)
def handle_t_wear_bra(character_id: int) -> int:
    """
    交互对象穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_wear_bra(character_data.target_character_id)

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_BRA)
def handle_t_not_wear_bra(character_id: int) -> int:
    """
    交互对象没有穿着胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_wear_bra(character_data.target_character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_GLOVES)
def handle_t_wear_gloves(character_id: int) -> int:
    """
    交互对象戴着手套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[7]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_GLOVES)
def handle_t_not_wear_gloves(character_id: int) -> int:
    """
    交互对象没有戴着手套
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_gloves(character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_IN_DOWN)
def handle_t_wear_in_down(character_id: int) -> int:
    """
    交互对象穿着下衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[8]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_IN_DOWN)
def handle_t_not_wear_in_down(character_id: int) -> int:
    """
    交互对象没有穿着下衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_in_down(character_id)

@add_premise(constant_promise.Premise.WEAR_SKIRT)
def handle_wear_skirt(character_id: int) -> int:
    """
    穿着裙子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[8]):
        cloth_id = character_data.cloth.cloth_wear[8][0]
        if game_config.config_clothing_tem[cloth_id].tag == 5:
            return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_WEAR_SKIRT)
def handle_t_wear_skirt(character_id: int) -> int:
    """
    交互对象穿着裙子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[8]):
        cloth_id = target_data.cloth.cloth_wear[8][0]
        if game_config.config_clothing_tem[cloth_id].tag == 5:
            return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_WEAR_TROUSERS)
def handle_t_wear_trousers(character_id: int) -> int:
    """
    交互对象穿着裤子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[8]):
        cloth_id = target_data.cloth.cloth_wear[8][0]
        if game_config.config_clothing_tem[cloth_id].tag == 4:
            return 1
    return 0

@add_premise(constant_promise.Premise.WEAR_PAN)
def handle_wear_pan(character_id: int) -> int:
    """
    穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[9]):
        return 1
    else:
        return 0

@add_premise(constant_promise.Premise.NOT_WEAR_PAN)
def handle_not_wear_pan(character_id: int) -> int:
    """
    没有穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_wear_pan(character_id)

@add_premise(constant_promise.Premise.TARGET_WEAR_PAN)
def handle_t_wear_pan(character_id: int) -> int:
    """
    交互对象穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[9]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_PAN)
def handle_t_not_wear_pan(character_id: int) -> int:
    """
    交互对象没有穿着内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_pan(character_id)

@add_premise(constant_promise.Premise.NOW_WEAR_BRA_OR_PAN)
def handle_not_wear_bra_or_pan(character_id: int) -> int:
    """
    自己没有穿着胸衣或内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_not_wear_bra(character_id) or handle_not_wear_pan(character_id):
        return 1
    return 0

@add_premise(constant_promise.Premise.WEAR_SOCKS)
def handle_wear_socks(character_id: int) -> int:
    """
    穿着袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[10]):
        return 1
    else:
        return 0

@add_premise(constant_promise.Premise.TARGET_WEAR_SOCKS)
def handle_t_wear_socks(character_id: int) -> int:
    """
    交互对象穿着袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_wear_socks(character_data.target_character_id)

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_SOCKS)
def handle_t_not_wear_socks(character_id: int) -> int:
    """
    交互对象没有穿着袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_wear_socks(character_data.target_character_id)

@add_premise(constant_promise.Premise.NOT_WEAR_SHOES)
def handle_not_wear_shoes(character_id: int) -> int:
    """
    没有穿着鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if len(character_data.cloth.cloth_wear[11]):
        return 0
    else:
        return 1

@add_premise(constant_promise.Premise.TARGET_WEAR_SHOES)
def handle_t_wear_shoes(character_id: int) -> int:
    """
    交互对象穿着鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[11]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_WEAR_SHOES)
def handle_t_not_wear_shoes(character_id: int) -> int:
    """
    交互对象没有穿着鞋子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_wear_shoes(character_id)

@add_premise(constant_promise.Premise.TARGET_TAKE_WEAPON)
def handle_t_take_weapon(character_id: int) -> int:
    """
    交互对象拿着武器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[12]):
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_NOT_TAKE_WEAPON)
def handle_t_not_take_weapon(character_id: int) -> int:
    """
    交互对象没有拿着武器
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_t_take_weapon(character_id)

@add_premise(constant_promise.Premise.TARGET_NOT_TAKE_EXTRAS)
def handle_t_not_take_extras(character_id: int) -> int:
    """
    交互对象没有拿着附属物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if len(target_data.cloth.cloth_wear[13]):
        return 0
    return 1

@add_premise(constant_promise.Premise.CLOTH_OFF)
def handle_cloth_off(character_id: int) -> int:
    """
    当前全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for clothing_type in game_config.config_clothing_type:
        if len(character_data.cloth.cloth_wear[clothing_type]):
            # 如果是3脖饰的话，则只有项圈的情况下依然算全裸
            if clothing_type == 3:
                if len(character_data.cloth.cloth_wear[clothing_type]) == 1 and character_data.cloth.cloth_wear[clothing_type][0] == 352:
                    continue
            # 如果是7手套的话，则只有戒指的情况下依然算全裸
            elif clothing_type == 7:
                if len(character_data.cloth.cloth_wear[clothing_type]) == 1 and character_data.cloth.cloth_wear[clothing_type][0] == 751:
                    continue
            return 0
    return 1

@add_premise(constant_promise.Premise.NOT_CLOTH_OFF)
def handle_not_cloth_off(character_id: int) -> int:
    """
    当前不是全裸
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_cloth_off(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.CLOTH_MOST_OFF)
def handle_cloth_most_off(character_id: int) -> int:
    """
    当前大致全裸（没穿上下外衣内衣）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for clothing_type in [5, 6, 8, 9]:
        if len(character_data.cloth.cloth_wear[clothing_type]):
            return 0
    return 1

@add_premise(constant_promise.Premise.NOT_CLOTH_MOST_OFF)
def handle_not_cloth_most_off(character_id: int) -> int:
    """
    当前不是大致全裸（没穿上下外衣内衣）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_cloth_most_off(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.SHOWER_CLOTH)
def handle_shower_cloth(character_id: int) -> int:
    """
    围着浴巾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 551 in character_data.cloth.cloth_wear[5] and 851 in character_data.cloth.cloth_wear[8]:
        return 1
    return 0

@add_premise(constant_promise.Premise.NOT_SHOWER_CLOTH)
def handle_not_shower_cloth(character_id: int) -> int:
    """
    没有围着浴巾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_shower_cloth(character_id):
        return 0
    return 1

@add_premise(constant_promise.Premise.SLEEP_CLOTH)
def handle_sleep_cloth(character_id: int) -> int:
    """
    穿着睡衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 552 in character_data.cloth.cloth_wear[5] and 852 in character_data.cloth.cloth_wear[8]:
        return 1
    elif 553 in character_data.cloth.cloth_wear[5] and 853 in character_data.cloth.cloth_wear[8]:
        return 1
    return 0

@add_premise(constant_promise.Premise.SLEEP_CLOTH_OR_NOT_NORMAL_4)
def handle_sleep_cloth_or_not_normal_4(character_id: int) -> int:
    """
    穿着睡衣或服装异常
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import handle_normal_4
    if handle_sleep_cloth(character_id):
        return 1
    elif not handle_normal_4(character_id):
        return 1
    return 0

@add_premise(constant_promise.Premise.SELF_EQUIPMENT_DAMAGED_GE_2)
def handle_self_equipment_damaged_ge_2(character_id: int) -> int:
    """
    自身装备损坏程度大于等于中度损坏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.cloth.equipment_condition < -1:
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_EQUIPMENT_DAMAGED_GE_2)
def handle_t_equipment_damaged_ge_2(character_id: int) -> int:
    """
    交互对象装备损坏程度大于等于中度损坏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_equipment_damaged_ge_2(character_data.target_character_id)

@add_premise(constant_promise.Premise.SELF_EQUIPMENT_DAMAGED_GE_3)
def handle_self_equipment_damaged_ge_3(character_id: int) -> int:
    """
    自身装备损坏程度大于等于严重损坏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.cloth.equipment_condition < -2:
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_EQUIPMENT_DAMAGED_GE_3)
def handle_t_equipment_damaged_ge_3(character_id: int) -> int:
    """
    交互对象装备损坏程度大于等于严重损坏
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_equipment_damaged_ge_3(character_data.target_character_id)

@add_premise(constant_promise.Premise.SELF_EQUIPMENT_MAINTANCE_GE_2)
def handle_self_equipment_maintenance_ge_2(character_id: int) -> int:
    """
    自身装备保养程度大于等于完美保养
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.cloth.equipment_condition >= 2:
        return 1
    return 0

@add_premise(constant_promise.Premise.TARGET_EQUIPMENT_MAINTANCE_GE_2)
def handle_t_equipment_maintenance_ge_2(character_id: int) -> int:
    """
    交互对象装备保养程度大于等于完美保养
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_equipment_maintenance_ge_2(character_data.target_character_id)
