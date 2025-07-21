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


@add_premise(constant_promise.Premise.T_NFEEL_GE_1)
def handle_t_nfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_GE_3)
def handle_t_nfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_GE_5)
def handle_t_nfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_GE_7)
def handle_t_nfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_L_1)
def handle_t_nfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_L_3)
def handle_t_nfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NFEEL_L_5)
def handle_t_nfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｎ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[0] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_1)
def handle_t_bfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_3)
def handle_t_bfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_5)
def handle_t_bfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_GE_7)
def handle_t_bfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_L_1)
def handle_t_bfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_L_3)
def handle_t_bfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BFEEL_L_5)
def handle_t_bfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｂ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[1] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_1)
def handle_t_cfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_3)
def handle_t_cfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_5)
def handle_t_cfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_GE_7)
def handle_t_cfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_L_1)
def handle_t_cfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_L_3)
def handle_t_cfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_CFEEL_L_5)
def handle_t_cfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｃ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[2] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_1)
def handle_pfeel_ge_1(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_3)
def handle_pfeel_ge_3(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_5)
def handle_pfeel_ge_5(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_GE_7)
def handle_pfeel_ge_7(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_L_1)
def handle_pfeel_l_1(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_L_3)
def handle_pfeel_l_3(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.PFEEL_L_5)
def handle_pfeel_l_5(character_id: int) -> int:
    """
    校验角色是否Ｐ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[3] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_1)
def handle_t_vfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_3)
def handle_t_vfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_5)
def handle_t_vfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_GE_7)
def handle_t_vfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_L_1)
def handle_t_vfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_L_3)
def handle_t_vfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VFEEL_L_5)
def handle_t_vfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｖ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[4] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_1)
def handle_t_afeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_3)
def handle_t_afeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_5)
def handle_t_afeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_GE_7)
def handle_t_afeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_L_1)
def handle_t_afeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_L_3)
def handle_t_afeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_AFEEL_L_5)
def handle_t_afeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ａ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[5] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_1)
def handle_t_ufeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_3)
def handle_t_ufeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_5)
def handle_t_ufeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_GE_7)
def handle_t_ufeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_L_1)
def handle_t_ufeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_L_3)
def handle_t_ufeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UFEEL_L_5)
def handle_t_ufeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｕ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[6] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_1)
def handle_t_wfeel_ge_1(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_3)
def handle_t_wfeel_ge_3(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_5)
def handle_t_wfeel_ge_5(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_GE_7)
def handle_t_wfeel_ge_7(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_L_1)
def handle_t_wfeel_l_1(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_L_3)
def handle_t_wfeel_l_3(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WFEEL_L_5)
def handle_t_wfeel_l_5(character_id: int) -> int:
    """
    校验交互对象是否Ｗ感觉<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[7] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_1)
def handle_t_u_dilate_ge_1(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_2)
def handle_t_u_dilate_ge_2(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_3)
def handle_t_u_dilate_ge_3(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_U_DILATE_GE_5)
def handle_t_u_dilate_ge_5(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｕ扩张>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[11] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_W_DILATE_GE_3)
def handle_t_w_dilate_ge_3(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｗ扩张>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[12] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_W_DILATE_GE_5)
def handle_t_w_dilate_ge_5(character_id: int) -> int:
    """
    校验交互对象是否交互对象Ｗ扩张>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[12] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TECHNIQUE_GE_3)
def handle_technique_ge_3(character_id: int) -> int:
    """
    校验角色是否技巧技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[30] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TECHNIQUE_GE_5)
def handle_technique_ge_3(character_id: int) -> int:
    """
    校验角色是否技巧技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[30] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_TECHNIQUE_GE_3)
def handle_t_technique_ge_3(character_id: int) -> int:
    """
    校验交互对象是否技巧技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[30] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_TECHNIQUE_GE_5)
def handle_t_technique_ge_3(character_id: int) -> int:
    """
    校验交互对象是否技巧技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[30] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_TECHNIQUE_GE_5_OR_IS_UNCONSCIOUS_H)
def handle_t_technique_ge_5_or_is_unconscious_h(character_id: int) -> int:
    """
    校验交互对象是否技巧技能>=5或处于无意识状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    from Script.Design.handle_premise import (
        handle_is_unconscious_h,
    )
    if handle_t_technique_ge_3(character_id) or handle_is_unconscious_h(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_1)
def handle_t_submit_ge_1(character_id: int) -> int:
    """
    校验交互对象是否顺从>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_3)
def handle_t_submit_ge_3(character_id: int) -> int:
    """
    校验交互对象是否顺从>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_5)
def handle_t_submit_ge_5(character_id: int) -> int:
    """
    校验交互对象是否顺从>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_GE_7)
def handle_t_submit_ge_7(character_id: int) -> int:
    """
    校验交互对象是否顺从>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_L_1)
def handle_t_submit_l_1(character_id: int) -> int:
    """
    校验交互对象是否顺从<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_L_3)
def handle_t_submit_l_3(character_id: int) -> int:
    """
    校验交互对象是否顺从<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SUBMIT_L_5)
def handle_t_submit_l_5(character_id: int) -> int:
    """
    校验交互对象是否顺从<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[31] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_8)
def handle_target_intimacy_8(character_id: int) -> int:
    """
    校验交互对象是否亲密==8
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[32] == 8:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_LE_1)
def handle_target_intimacy_le_1(character_id: int) -> int:
    """
    校验交互对象是否亲密<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[32] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_GE_3)
def handle_target_intimacy_ge_3(character_id: int) -> int:
    """
    校验交互对象是否亲密>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[32] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_INTIMACY_GE_5)
def handle_target_intimacy_ge_3(character_id: int) -> int:
    """
    校验交互对象是否亲密>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[32] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_DESIRE_GE_5)
def handle_target_desire_ge_5(character_id: int) -> int:
    """
    校验交互对象是否欲望技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[33] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_DESIRE_GE_7)
def handle_target_desire_ge_7(character_id: int) -> int:
    """
    校验交互对象是否欲望技能>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[33] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_1)
def handle_t_exhibit_ge_1(character_id: int) -> int:
    """
    校验交互对象是否露出>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_3)
def handle_t_exhibit_ge_3(character_id: int) -> int:
    """
    校验交互对象是否露出>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_5)
def handle_t_exhibit_ge_5(character_id: int) -> int:
    """
    校验交互对象是否露出>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_GE_7)
def handle_t_exhibit_ge_7(character_id: int) -> int:
    """
    校验交互对象是否露出>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_L_1)
def handle_t_exhibit_l_1(character_id: int) -> int:
    """
    校验交互对象是否露出<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_L_3)
def handle_t_exhibit_l_3(character_id: int) -> int:
    """
    校验交互对象是否露出<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXHIBIT_L_5)
def handle_t_exhibit_l_5(character_id: int) -> int:
    """
    校验交互对象是否露出<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[34] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_1)
def handle_s_ge_1(character_id: int) -> int:
    """
    校验角色是否施虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_3)
def handle_s_ge_3(character_id: int) -> int:
    """
    校验角色是否施虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_5)
def handle_s_ge_5(character_id: int) -> int:
    """
    校验角色是否施虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_GE_7)
def handle_s_ge_7(character_id: int) -> int:
    """
    校验角色是否施虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_L_1)
def handle_s_l_1(character_id: int) -> int:
    """
    校验角色是否施虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_L_3)
def handle_s_l_3(character_id: int) -> int:
    """
    校验角色是否施虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.S_L_5)
def handle_s_l_5(character_id: int) -> int:
    """
    校验角色是否施虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[35] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_1)
def handle_t_s_ge_1(character_id: int) -> int:
    """
    校验交互对象是否施虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_3)
def handle_t_s_ge_3(character_id: int) -> int:
    """
    校验交互对象是否施虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_5)
def handle_t_s_ge_5(character_id: int) -> int:
    """
    校验交互对象是否施虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_GE_7)
def handle_t_s_ge_7(character_id: int) -> int:
    """
    校验交互对象是否施虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_L_1)
def handle_t_s_l_1(character_id: int) -> int:
    """
    校验交互对象是否施虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_L_3)
def handle_t_s_l_3(character_id: int) -> int:
    """
    校验交互对象是否施虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_S_L_5)
def handle_t_s_l_5(character_id: int) -> int:
    """
    校验交互对象是否施虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[35] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_1)
def handle_m_ge_1(character_id: int) -> int:
    """
    校验角色是否受虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_3)
def handle_m_ge_3(character_id: int) -> int:
    """
    校验角色是否受虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_5)
def handle_m_ge_5(character_id: int) -> int:
    """
    校验角色是否受虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_GE_7)
def handle_m_ge_7(character_id: int) -> int:
    """
    校验角色是否受虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_L_1)
def handle_m_l_1(character_id: int) -> int:
    """
    校验角色是否受虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_L_3)
def handle_m_l_3(character_id: int) -> int:
    """
    校验角色是否受虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.M_L_5)
def handle_m_l_5(character_id: int) -> int:
    """
    校验角色是否受虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[36] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_1)
def handle_t_m_ge_1(character_id: int) -> int:
    """
    校验交互对象是否受虐>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_3)
def handle_t_m_ge_3(character_id: int) -> int:
    """
    校验交互对象是否受虐>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_5)
def handle_t_m_ge_5(character_id: int) -> int:
    """
    校验交互对象是否受虐>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_GE_7)
def handle_t_m_ge_7(character_id: int) -> int:
    """
    校验交互对象是否受虐>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_L_1)
def handle_t_m_l_1(character_id: int) -> int:
    """
    校验交互对象是否受虐<1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] < 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_L_3)
def handle_t_m_l_3(character_id: int) -> int:
    """
    校验交互对象是否受虐<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_M_L_5)
def handle_t_m_l_5(character_id: int) -> int:
    """
    校验交互对象是否受虐<5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[36] < 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_1)
def handle_t_happy_mark_1(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_2)
def handle_t_happy_mark_2(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_3)
def handle_t_happy_mark_3(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_GE_1)
def handle_t_happy_mark_ge_1(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAPPY_MARK_LE_2)
def handle_t_happy_mark_le_2(character_id: int) -> int:
    """
    校验交互对象是否快乐刻印<=2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[13] <= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_1)
def handle_t_yield_mark_1(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_2)
def handle_t_yield_mark_2(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_3)
def handle_t_yield_mark_3(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_GE_1)
def handle_t_yield_mark_ge_1(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_YIELD_MARK_LE_2)
def handle_t_yield_mark_le_2(character_id: int) -> int:
    """
    校验交互对象是否屈服刻印<=2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[14] <= 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.TALK_LE_1)
def handle_talk_le_1(character_id: int) -> int:
    """
    校验角色是否话术技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[40] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TALK_GE_3)
def handle_talk_ge_3(character_id: int) -> int:
    """
    校验角色是否话术技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[40] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TALK_GE_5)
def handle_talk_ge_5(character_id: int) -> int:
    """
    校验角色是否话术技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[40] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TALK_LE_1)
def handle_t_talk_le_1(character_id: int) -> int:
    """
    校验交互对象是否话术技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[40] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TALK_GE_3)
def handle_t_talk_ge_3(character_id: int) -> int:
    """
    校验交互对象是否话术技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[40] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_TALK_GE_5)
def handle_t_talk_ge_5(character_id: int) -> int:
    """
    校验交互对象是否话术技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[40] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_1)
def handle_cook_1(character_id: int) -> int:
    """
    校验角色是否料理技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_2)
def handle_cook_2(character_id: int) -> int:
    """
    校验角色是否料理技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_3)
def handle_cook_3(character_id: int) -> int:
    """
    校验角色是否料理技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_4)
def handle_cook_4(character_id: int) -> int:
    """
    校验角色是否料理技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_LE_1)
def handle_cook_le_1(character_id: int) -> int:
    """
    校验角色是否料理技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_LE_3)
def handle_cook_le_3(character_id: int) -> int:
    """
    校验角色是否料理技能<=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] <= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_GE_3)
def handle_cook_ge_3(character_id: int) -> int:
    """
    校验角色是否料理技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.COOK_GE_5)
def handle_cook_ge_3(character_id: int) -> int:
    """
    校验角色是否料理技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[43] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_1)
def handle_target_cook_1(character_id: int) -> int:
    """
    校验交互对象是否料理技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_2)
def handle_target_cook_2(character_id: int) -> int:
    """
    校验交互对象是否料理技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_3)
def handle_target_cook_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_4)
def handle_target_cook_4(character_id: int) -> int:
    """
    校验交互对象是否料理技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_LE_1)
def handle_target_cook_le_1(character_id: int) -> int:
    """
    校验交互对象是否料理技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_LE_3)
def handle_target_cook_le_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能<=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] <= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_GE_3)
def handle_target_cook_ge_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_G_3)
def handle_target_cook_g_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能>3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] > 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_COOK_GE_5)
def handle_target_cook_ge_3(character_id: int) -> int:
    """
    校验交互对象是否料理技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[43] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_1)
def handle_music_1(character_id: int) -> int:
    """
    校验角色是否音乐技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_2)
def handle_music_2(character_id: int) -> int:
    """
    校验角色是否音乐技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_3)
def handle_music_3(character_id: int) -> int:
    """
    校验角色是否音乐技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_4)
def handle_music_4(character_id: int) -> int:
    """
    校验角色是否音乐技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_LE_1)
def handle_music_le_1(character_id: int) -> int:
    """
    校验角色是否音乐技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_GE_3)
def handle_music_ge_3(character_id: int) -> int:
    """
    校验角色是否音乐技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_GE_5)
def handle_music_ge_3(character_id: int) -> int:
    """
    校验角色是否音乐技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.ability[44] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.MUSIC_GE_2_LE_4)
def handle_music_ge_2_le_4(character_id: int) -> int:
    """
    校验自身音乐技能>=2,<=4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if 2 <= character_data.ability[44] <= 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_1)
def handle_target_music_1(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[44] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_2)
def handle_target_music_2(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==2
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[44] == 2:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_3)
def handle_target_music_3(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[44] == 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_4)
def handle_target_music_4(character_id: int) -> int:
    """
    校验交互对象是否音乐技能==4
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[44] == 4:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_LE_1)
def handle_target_music_le_1(character_id: int) -> int:
    """
    校验交互对象是否音乐技能<=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[44] <= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_GE_3)
def handle_target_music_ge_3(character_id: int) -> int:
    """
    校验交互对象是否音乐技能>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[44] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_MUSIC_GE_5)
def handle_target_music_ge_3(character_id: int) -> int:
    """
    校验交互对象是否音乐技能>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[44] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_1)
def handle_t_finger_tec_ge_1(character_id: int) -> int:
    """
    校验交互对象是否指技>=1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_3)
def handle_t_finger_tec_ge_3(character_id: int) -> int:
    """
    校验交互对象是否指技>=3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_5)
def handle_t_finger_tec_ge_5(character_id: int) -> int:
    """
    校验交互对象是否指技>=5
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 5:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_GE_7)
def handle_t_finger_tec_ge_7(character_id: int) -> int:
    """
    校验交互对象是否指技>=7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] >= 7:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_0)
def handle_t_finger_tec_0(character_id: int) -> int:
    """
    校验交互对象是否指技==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_L_3)
def handle_t_finger_tec_l_3(character_id: int) -> int:
    """
    校验交互对象是否指技<3
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] < 3:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_FINGER_TEC_L_7)
def handle_t_finger_tec_l_7(character_id: int) -> int:
    """
    校验交互对象是否指技<7
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.ability[70] < 7:
        return 1
    return 0

