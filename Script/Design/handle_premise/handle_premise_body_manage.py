from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text

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


@add_premise(constant_promise.Premise.ASK_GIVE_PAN_EVERYDAY)
def handle_ask_give_pan_everyday(character_id: int) -> int:
    """
    自己被要求每天上交内裤
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[1]


@add_premise(constant_promise.Premise.ASK_GIVE_SOCKS_EVERYDAY)
def handle_ask_give_socks_everyday(character_id: int) -> int:
    """
    自己被要求每天上交袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[2]


@add_premise(constant_promise.Premise.ASK_NOT_WEAR_CORSET)
def handle_ask_not_wear_corset(character_id: int) -> int:
    """
    自己被要求以后不再穿胸衣
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[3]


@add_premise(constant_promise.Premise.ASK_NOT_WEAR_CLOTH_IN_SLEEP)
def handle_ask_not_wear_cloth_in_sleep(character_id: int) -> int:
    """
    自己被要求以后睡觉时不穿衣服裸睡
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[4]


@add_premise(constant_promise.Premise.ASK_WEAR_DIFFERENT_SOCKS_EVERYDAY)
def handle_ask_wear_different_socks_everyday(character_id: int) -> int:
    """
    自己被要求每天穿不同的袜子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[5]


@add_premise(constant_promise.Premise.ASK_EQUP_NIPPLE_CLAMP_IN_DAY)
def handle_ask_equp_nipple_clamp_in_day(character_id: int) -> int:
    """
    自己被要求白天时戴着乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[11]


@add_premise(constant_promise.Premise.ASK_EQUP_CLIT_CLAMP_IN_DAY)
def handle_ask_equp_clit_clamp_in_day(character_id: int) -> int:
    """
    自己被要求白天时戴着阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[12]


@add_premise(constant_promise.Premise.ASK_EQUP_V_VIBRATOR_IN_DAY)
def handle_ask_equp_v_bibrator_in_day(character_id: int) -> int:
    """
    自己被要求白天时V里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[13]


@add_premise(constant_promise.Premise.ASK_EQUP_A_VIBRATOR_IN_DAY)
def handle_ask_equp_a_bibrator_in_day(character_id: int) -> int:
    """
    自己被要求白天时A里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[14]


@add_premise(constant_promise.Premise.ASK_EQUP_NIPPLE_CLAMP_IN_SLEEP)
def handle_ask_equp_nipple_clamp_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时戴着乳头夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[15]


@add_premise(constant_promise.Premise.ASK_EQUP_CLIT_CLAMP_IN_SLEEP)
def handle_ask_equp_clit_clamp_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时戴着阴蒂夹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[16]


@add_premise(constant_promise.Premise.ASK_EQUP_V_VIBRATOR_IN_SLEEP)
def handle_ask_equp_v_bibrator_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时V里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[17]


@add_premise(constant_promise.Premise.ASK_EQUP_A_VIBRATOR_IN_SLEEP)
def handle_ask_equp_a_bibrator_in_sleep(character_id: int) -> int:
    """
    自己被要求睡觉时A里插着振动棒
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[18]


@add_premise(constant_promise.Premise.ASK_NOT_WASH_SEMEN)
def handle_ask_not_wash_semen(character_id: int) -> int:
    """
    自己被要求洗澡时不再清洗阴道内的精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[21]


@add_premise(constant_promise.Premise.ASK_MASTURBATION_BEFORE_SLEEP)
def handle_ask_masturbation_before_sleep(character_id: int) -> int:
    """
    自己被要求每天晚上睡前都要自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[22]


@add_premise(constant_promise.Premise.ASK_NOT_MASTURBATION)
def handle_ask_not_masturbation(character_id: int) -> int:
    """
    自己被要求禁止自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[23]


@add_premise(constant_promise.Premise.NOT_ASK_NOT_MASTURBATION)
def handle_not_ask_not_masturbation(character_id: int) -> int:
    """
    自己没有被要求禁止自慰
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_ask_not_masturbation(character_id)


@add_premise(constant_promise.Premise.ASK_NOT_LOCK_DOOR_BEFORE_SLEEPING)
def handle_ask_not_lock_door_bedore_sleeping(character_id: int) -> int:
    """
    自己被要求晚上睡觉不锁门
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[24]


@add_premise(constant_promise.Premise.ASK_NONE_EXERCISES)
def handle_ask_none_exercises(character_id: int) -> int:
    """
    自己没有被要求进行任何练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_ask_one_exercises(character_id)


@add_premise(constant_promise.Premise.ASK_ONE_EXERCISES)
def handle_ask_one_exercises(character_id: int) -> int:
    """
    自己被要求进行了至少一项练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for i in range(30,40):
        if i in character_data.body_manage and character_data.body_manage[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.ASK_GE_3_EXERCISES)
def handle_ask_ge_3_exercises(character_id: int) -> int:
    """
    自己被要求进行了至少3项练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    count = 0
    for i in range(30,40):
        if i in character_data.body_manage and character_data.body_manage[i]:
            count += 1
    if count >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.ASK_SUCKING_AND_SWALLOWING_EXERCISES)
def handle_ask_sucking_and_swallowing_exercises(character_id: int) -> int:
    """
    自己被要求进行吮吸与吞咽力练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[31]


@add_premise(constant_promise.Premise.ASK_ARMPIT_CLAMPING_EXERCISES)
def handle_ask_armpit_clamping_exercises(character_id: int) -> int:
    """
    自己被要求进行腋下夹持力练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[32]


@add_premise(constant_promise.Premise.ASK_BREAST_CLAMPING_EXERCISES)
def handle_ask_breast_clamping_exercise(character_id: int) -> int:
    """
    自己被要求进行胸部夹持力练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[33]


@add_premise(constant_promise.Premise.ASK_HANDS_FLEXIBILITY_EXERCISES)
def handle_ask_hands_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行手部灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[34]


@add_premise(constant_promise.Premise.ASK_FOOTS_FLEXIBILITY_EXERCISES)
def handle_ask_foots_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行足部灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[35]


@add_premise(constant_promise.Premise.ASK_VAGINA_FIRMNESS_EXERCISES)
def handle_ask_vagina_firmness_exercises(character_id: int) -> int:
    """
    自己被要求进行阴道紧致度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[36]


@add_premise(constant_promise.Premise.ASK_INTESTINE_FIRMNESS_EXERCISES)
def handle_ask_intestine_firmness_exercises(character_id: int) -> int:
    """
    自己被要求进行肠道紧致度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[37]


@add_premise(constant_promise.Premise.ASK_TAIL_FLEXIBILITY_EXERCISES)
def handle_ask_tail_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行尾巴灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[38]


@add_premise(constant_promise.Premise.ASK_TENTACLE_FLEXIBILITY_EXERCISES)
def handle_ask_tentacle_flexibility_exercises(character_id: int) -> int:
    """
    自己被要求进行触手灵活度练习
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.body_manage[39]

