import datetime
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
from Script.Design import map_handle, game_time, attr_calculation
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """


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


@add_premise(constant_promise.Premise.HP_G_1)
def handle_self_not_tired(character_id: int) -> int:
    """
    自身体力大于1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hit_point > 1


@add_premise(constant_promise.Premise.HP_LOW)
def handle_hp_low(character_id: int) -> int:
    """
    角色体力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.hit_point / character_data.hit_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HP_HIGH)
def handle_hp_high(character_id: int) -> int:
    """
    角色体力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.hit_point / character_data.hit_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HP_MAX)
def handle_hp_max(character_id: int) -> int:
    """
    角色自身体力等于100%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.hit_point / character_data.hit_point_max
    if value >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MP_0)
def handle_mp_0(character_id: int) -> int:
    """
    角色气力为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point
    if value == 0:
        return_value = max(1, character_data.hit_point_max - character_data.hit_point)
        return return_value
    else:
        return 0


@add_premise(constant_promise.Premise.MP_LOW)
def handle_mp_low(character_id: int) -> int:
    """
    角色气力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point / character_data.mana_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MP_HIGH)
def handle_mp_high(character_id: int) -> int:
    """
    角色气力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point / character_data.mana_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MP_MAX)
def handle_mp_max(character_id: int) -> int:
    """
    自身气力等于100%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    value = character_data.mana_point / character_data.mana_point_max
    if value >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HP_OR_MP_LOW)
def handle_hp_or_mp_low(character_id: int) -> int:
    """
    自身体力或气力有一项低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    hp_value = character_data.hit_point / character_data.hit_point_max
    mp_value = character_data.mana_point / character_data.mana_point_max
    if hp_value < 0.3:
        return 1
    elif mp_value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HP_OR_MP_GE_80)
def handle_hp_or_mp_ge_80(character_id: int) -> int:
    """
    自身体力或气力有一项低于80%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    hp_value = character_data.hit_point / character_data.hit_point_max
    mp_value = character_data.mana_point / character_data.mana_point_max
    if hp_value < 0.8:
        return 1
    elif mp_value < 0.8:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HP_LOW)
def handle_target_hp_low(character_id: int) -> int:
    """
    交互对象体力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.hit_point / target_data.hit_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HP_HIGH)
def handle_target_hp_high(character_id: int) -> int:
    """
    交互对象体力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.hit_point / target_data.hit_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HP_NE_1)
def handle_target_hp_ne_1(character_id: int) -> int:
    """
    交互对象体力不等于1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.hit_point > 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MP_0)
def handle_target_mp_0(character_id: int) -> int:
    """
    交互对象气力为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.mana_point
    if value == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MP_LOW)
def handle_target_mp_low(character_id: int) -> int:
    """
    交互对象气力低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.mana_point / target_data.mana_point_max
    if value < 0.3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MP_HIGH)
def handle_target_mp_high(character_id: int) -> int:
    """
    交互对象气力高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value = target_data.mana_point / target_data.mana_point_max
    if value > 0.7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SELF_AND_TARGET_HP_GE_70)
def handle_self_and_target_hp_ge_70(character_id: int) -> int:
    """
    自身和交互对象体力都高于70%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value1 = character_data.hit_point / character_data.hit_point_max
    value2 = target_data.hit_point / target_data.hit_point_max
    if value1 > 0.7 and value2 > 0.7:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HP_OR_MP_LOW)
def handle_t_hp_or_mp_low(character_id: int) -> int:
    """
    交互对象体力或气力有一项低于30%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    value1 = target_data.hit_point / target_data.hit_point_max
    value2 = target_data.mana_point / target_data.mana_point_max
    if value1 < 0.3:
        return 1
    elif value2 < 0.3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIRED_LE_0)
def handle_tired_le_0(character_id: int) -> int:
    """
    疲劳条≤0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value <= 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_10)
def handle_tired_ge_10(character_id: int) -> int:
    """
    疲劳条≥10%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value >= 0.1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_50)
def handle_tired_ge_50(character_id: int) -> int:
    """
    疲劳条≥50%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value >= 0.5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_LE_74)
def handle_tired_le_74(character_id: int) -> int:
    """
    疲劳条≤74%，全指令自由
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value <= 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_75)
def handle_tired_ge_75(character_id: int) -> int:
    """
    疲劳条≥75%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value > 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_LE_84)
def handle_tired_le_84(character_id: int) -> int:
    """
    疲劳条≤84%，自由活动的极限
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value <= 0.84:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_GE_85)
def handle_tired_ge_85(character_id: int) -> int:
    """
    疲劳条≥85%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value > 0.84:
        return character_data.tired_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_L_100)
def handle_tired_l_100(character_id: int) -> int:
    """
    疲劳条<100%，还不至于当场爆睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value < 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TIRED_100)
def handle_tired_100(character_id: int) -> int:
    """
    疲劳条100%，当场爆睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.tired_point / 160
    if value >= 1:
        return character_data.tired_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_GE_50)
def handle_t_tired_ge_50(character_id: int) -> int:
    """
    交互对象疲劳条≥50%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value >= 0.5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_LE_74)
def handle_t_tired_le_74(character_id: int) -> int:
    """
    交互对象疲劳条≤74%，全指令自由
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value <= 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_GE_75)
def handle_t_tired_ge_75(character_id: int) -> int:
    """
    交互对象疲劳条≥75%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value > 0.74:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_LE_84)
def handle_t_tired_le_84(character_id: int) -> int:
    """
    交互对象疲劳条≤84%，自由活动的极限
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value <= 0.84:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_GE_85)
def handle_t_tired_ge_85(character_id: int) -> int:
    """
    交互对象疲劳条≥85%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value > 0.84:
        return target_data.tired_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_TIRED_100)
def handle_t_tired_100(character_id: int) -> int:
    """
    交互对象疲劳条100%，当场爆睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]

    value = target_data.tired_point / 160
    if value >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_LE_12)
def handle_urinate_le_12(character_id: int) -> int:
    """
    尿意条≤12.5%，刚排空过
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value <= 0.125:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_LE_49)
def handle_urinate_le_49(character_id: int) -> int:
    """
    尿意条≤49%，可以继续喝咖啡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value <= 0.49:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_LE_79)
def handle_urinate_le_79(character_id: int) -> int:
    """
    尿意条≤79%，不需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_GE_80)
def handle_urinate_ge_80(character_id: int) -> int:
    """
    尿意条≥80%，需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value > 0.79:
        extra_value = int(character_data.urinate_point -  240 * 0.8)
        return extra_value * 5
    else:
        return 0


@add_premise(constant_promise.Premise.URINATE_GE_125)
def handle_urinate_ge_125(character_id: int) -> int:
    """
    尿意条≥150%，需要当场排尿
    之前设为125%，但出现失禁的频率过高，所以改为150%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.urinate_point / 240
    if value >= 1.5:
        return character_data.urinate_point * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_URINATE_LE_49)
def handle_target_urinate_le_49(character_id: int) -> int:
    """
    交互对象尿意条≤49%，可以继续喝咖啡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.urinate_point / 240
    if value <= 0.49:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_URINATE_LE_79)
def handle_target_urinate_le_79(character_id: int) -> int:
    """
    交互对象尿意条≤79%，不需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.urinate_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_URINATE_GE_80)
def handle_target_urinate_ge_80(character_id: int) -> int:
    """
    交互对象尿意条≥80%，需要排尿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.urinate_point / 240
    if value > 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HUNGER_LE_79)
def handle_hunger_le_79(character_id: int) -> int:
    """
    饥饿值≤79%，不需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.hunger_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.HUNGER_GE_80)
def handle_hunger_ge_80(character_id: int) -> int:
    """
    饥饿值≥80%，需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.hunger_point / 240
    if value > 0.79:
        # print(f"debug {character_id}角色饿了")
        extra_value = character_data.hunger_point -  240 * 0.8
        return extra_value * 5
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HUNGER_LE_79)
def handle_target_hunger_le_79(character_id: int) -> int:
    """
    交互对象饥饿值≤79%，不需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.hunger_point / 240
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_HUNGER_GE_80)
def handle_target_hunger_ge_80(character_id: int) -> int:
    """
    交互对象饥饿值≥80%，需要吃饭
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_data.hunger_point / 240
    if value > 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_LE_29)
def handle_milk_le_29(character_id: int) -> int:
    """
    奶量≤29%，无法挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max
    if value <= 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_GE_30)
def handle_milk_ge_30(character_id: int) -> int:
    """
    奶量≥30%，可以挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max
    if value > 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_LE_79)
def handle_milk_le_79(character_id: int) -> int:
    """
    奶量≤79%，未涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.MILK_GE_80)
def handle_milk_ge_80(character_id: int) -> int:
    """
    奶量≥80%，涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.pregnancy.milk == 0:
        return 0

    value = character_data.pregnancy.milk / character_data.pregnancy.milk_max

    if value > 0.80:
        return character_data.pregnancy.milk
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_LE_29)
def handle_target_milk_le_29(character_id: int) -> int:
    """
    交互对象奶量≤29%，无法挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value <= 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_GE_30)
def handle_target_milk_ge_30(character_id: int) -> int:
    """
    交互对象奶量≥30%，可以挤奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value > 0.29:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_LE_79)
def handle_target_milk_le_79(character_id: int) -> int:
    """
    交互对象奶量≤79%，未涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value <= 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_MILK_GE_80)
def handle_target_milk_ge_80(character_id: int) -> int:
    """
    交互对象奶量≥80%，涨奶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]

    value = target_character_data.pregnancy.milk / target_character_data.pregnancy.milk_max
    if value > 0.79:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_0)
def handle_sleep_level_0(character_id: int) -> int:
    """
    睡眠等级：半梦半醒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_1)
def handle_sleep_level_1(character_id: int) -> int:
    """
    睡眠等级：浅睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_2)
def handle_sleep_level_2(character_id: int) -> int:
    """
    睡眠等级：熟睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 2:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_3)
def handle_sleep_level_3(character_id: int) -> int:
    """
    睡眠等级：完全深眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level == 3:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SLEEP_LEVEL_GE_1)
def handle_sleep_level_ge_1(character_id: int) -> int:
    """
    睡眠等级≥1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    level,tem = attr_calculation.get_sleep_level(character_data.sleep_point)
    if level >= 1:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_0)
def handle_sanity_point_0(character_id: int) -> int:
    """
    理智值为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point == 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_G_0)
def handle_sanity_point_g_0(character_id: int) -> int:
    """
    理智值不为0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point > 0:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_L_5)
def handle_sanity_point_l_5(character_id: int) -> int:
    """
    理智值<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point < 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_5)
def handle_sanity_point_ge_5(character_id: int) -> int:
    """
    理智值≥5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 5:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_L_10)
def handle_sanity_point_l_10(character_id: int) -> int:
    """
    理智值<10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point < 10:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_10)
def handle_sanity_point_ge_10(character_id: int) -> int:
    """
    理智值≥10
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 10:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_20)
def handle_sanity_point_ge_20(character_id: int) -> int:
    """
    理智值≥20
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 20:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_40)
def handle_sanity_point_ge_40(character_id: int) -> int:
    """
    理智值≥40
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 40:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.SANITY_POINT_GE_50)
def handle_sanity_point_ge_50(character_id: int) -> int:
    """
    理智值≥50
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.sanity_point >= 50:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.DESIRE_POINT_GE_80)
def handle_desire_point_ge_80(character_id: int) -> int:
    """
    欲望值≥80
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.desire_point >= 80:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.DESIRE_POINT_L_80)
def handle_desire_point_l_80(character_id: int) -> int:
    """
    欲望值<80
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.desire_point < 80:
        return 1
    else:
        return 0


@add_premise(constant_promise.Premise.DESIRE_POINT_GE_100)
def handle_desire_point_ge_100(character_id: int) -> int:
    """
    欲望值≥100
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]

    if character_data.desire_point >= 100:
        return character_data.desire_point * 2
    else:
        return 0


@add_premise(constant_promise.Premise.TARGET_DESIRE_POINT_GE_80)
def handle_t_desire_point_ge_80(character_id: int) -> int:
    """
    交互对象欲望值≥80
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_desire_point_ge_80(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_DESIRE_POINT_L_80)
def handle_t_desire_point_l_80(character_id: int) -> int:
    """
    交互对象欲望值<80
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_desire_point_l_80(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_DESIRE_POINT_GE_100)
def handle_t_desire_point_ge_100(character_id: int) -> int:
    """
    交互对象欲望值≥100
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_desire_point_ge_100(character_data.target_character_id)
