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


@add_premise(constant_promise.Premise.SELF_FALL)
def handle_self_fall(character_id: int) -> int:
    """
    自己有陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {201, 202, 203, 204, 211, 212, 213, 214}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_FALL)
def handle_self_not_fall(character_id: int) -> int:
    """
    自己无陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_self_fall(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_FALL_1)
def handle_self_fall_1(character_id: int) -> int:
    """
    自己有1级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {201, 211}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_2)
def handle_self_fall_2(character_id: int) -> int:
    """
    自己有2级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {202, 212}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_3)
def handle_self_fall_3(character_id: int) -> int:
    """
    自己有3级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {203, 213}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_4)
def handle_self_fall_4(character_id: int) -> int:
    """
    自己有4级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {204, 214}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_FALL_3_or_4)
def handle_self_fall_3_or_4(character_id: int) -> int:
    """
    自己有3级或4级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return handle_self_fall_3(character_id) or handle_self_fall_4(character_id)


@add_premise(constant_promise.Premise.TARGET_FALL_3_or_4)
def handle_target_fall_3_or_4(character_id: int) -> int:
    """
    交互对象有3级或4级陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_fall_3(character_data.target_character_id) or handle_self_fall_4(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_FALL_LOVE)
def handle_self_fall_love(character_id: int) -> int:
    """
    自己有爱情系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {201, 202, 203, 204}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_FALL_LOVE)
def handle_self_not_fall_love(character_id: int) -> int:
    """
    自己没有爱情系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_fall_love(character_id)


@add_premise(constant_promise.Premise.SELF_FALL_OBEY)
def handle_self_fall_obey(character_id: int) -> int:
    """
    自己有隶属系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    for i in {211, 212, 213, 214}:
        if character_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_FALL_OBEY)
def handle_self_not_fall_obey(character_id: int) -> int:
    """
    自己没有隶属系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_fall_obey(character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_FALL)
def handle_target_not_fall(character_id: int) -> int:
    """
    交互对象无陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_fall(character_data.target_character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_FALL)
def handle_target_fall(character_id: int) -> int:
    """
    交互对象有陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_fall(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_FALL_LOVE)
def handle_target_not_fall_love(character_id: int) -> int:
    """
    交互对象没有爱情系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_fall_love(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_FALL_OBEY)
def handle_target_not_fall_obey(character_id: int) -> int:
    """
    交互对象没有隶属系陷落素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return not handle_self_fall_obey(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_LOVE_1)
def handle_target_love_1(character_id: int) -> int:
    """
    校验交互对象是否是思慕,爱情系第一阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[201]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_2)
def handle_target_love_2(character_id: int) -> int:
    """
    校验交互对象是否是恋慕,爱情系第二阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[202]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_3)
def handle_target_love_3(character_id: int) -> int:
    """
    校验交互对象是否是恋人,爱情系第三阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[203]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_LOVE_4)
def handle_self_love_4(character_id: int) -> int:
    """
    校验自己是否是爱侣,爱情系第四阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.talent[204]


@add_premise(constant_promise.Premise.TARGET_LOVE_4)
def handle_target_love_4(character_id: int) -> int:
    """
    校验交互对象是否是爱侣,爱情系第四阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_love_4(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_LOVE_GE_1)
def handle_target_love_ge_1(character_id: int) -> int:
    """
    交互对象爱情系>=思慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {201, 202, 203, 204}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_GE_2)
def handle_target_love_ge_2(character_id: int) -> int:
    """
    交互对象爱情系>=恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {202, 203, 204}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_GE_3)
def handle_target_love_ge_3(character_id: int) -> int:
    """
    交互对象爱情系>=恋人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {203, 204}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_LE_2)
def handle_target_love_le_2(character_id: int) -> int:
    """
    交互对象爱情系<=恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {201, 202}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_0_OR_LE_1)
def handle_target_love_0_or_le_1(character_id: int) -> int:
    """
    交互对象无陷落或爱情系<=思慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_love_1(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_LOVE_0_OR_LE_2)
def handle_target_love_0_or_le_2(character_id: int) -> int:
    """
    交互对象无陷落或爱情系<=恋慕
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_love_le_2(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_1)
def handle_target_obey_1(character_id: int) -> int:
    """
    校验交互对象是否是屈从,隶属系第一阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[211]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_2)
def handle_target_obey_2(character_id: int) -> int:
    """
    校验交互对象是否是驯服,隶属系第二阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[212]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_3)
def handle_target_obey_3(character_id: int) -> int:
    """
    校验交互对象是否是宠物,隶属系第三阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[213]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_OBEY_4)
def handle_self_obey_4(character_id: int) -> int:
    """
    校验自己是否是奴隶,隶属系第四阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.talent[214]


@add_premise(constant_promise.Premise.TARGET_OBEY_4)
def handle_target_obey_4(character_id: int) -> int:
    """
    校验交互对象是否是奴隶,隶属系第四阶段
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_obey_4(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_OBEY_GE_1)
def handle_target_obey_ge_1(character_id: int) -> int:
    """
    交互对象隶属系>=屈从
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {211, 212, 213, 214}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_GE_2)
def handle_target_obey_ge_2(character_id: int) -> int:
    """
    交互对象隶属系>=驯服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {212, 213, 214}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_GE_3)
def handle_target_obey_ge_3(character_id: int) -> int:
    """
    交互对象隶属系>=宠物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {213, 214}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_LE_2)
def handle_target_obey_le_2(character_id: int) -> int:
    """
    交互对象隶属系<=驯服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for i in {211, 212}:
        if target_data.talent[i]:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_0_OR_LE_1)
def handle_target_obey_0_or_le_1(character_id: int) -> int:
    """
    交互对象无陷落或隶属系==屈从
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_obey_1(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_OBEY_0_OR_LE_2)
def handle_target_obey_0_or_le_2(character_id: int) -> int:
    """
    交互对象无陷落或隶属系<=驯服
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if handle_self_not_fall(character_data.target_character_id):
        return 1
    if handle_target_obey_le_2(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.PLAYER_HAVE_OTHER_LOVER)
def handle_player_have_other_lover(character_id: int) -> int:
    """
    玩家有除了自己之外的恋人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    for chara_id in cache.npc_id_got:
        if chara_id == 0:
            continue
        if chara_id == character_id:
            continue
        if handle_self_fall_love(chara_id) and (handle_self_fall_3(chara_id) or handle_self_fall_4(chara_id)):
            return 1
    return 0


@add_premise(constant_promise.Premise.PLAYER_NO_OTHER_LOVER)
def handle_player_no_other_lover(character_id: int) -> int:
    """
    玩家没有除了自己之外的恋人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_player_have_other_lover(character_id)


@add_premise(constant_promise.Premise.PLAYER_HAVE_OTHER_LOVER_EXCEPT_TARGET)
def handle_player_have_other_lover_except_target(character_id: int) -> int:
    """
    玩家有除了玩家交互对象之外的恋人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    for chara_id in cache.npc_id_got:
        if chara_id == 0:
            continue
        if chara_id == pl_character_data.target_character_id:
            continue
        if handle_self_fall_love(chara_id) and (handle_self_fall_3(chara_id) or handle_self_fall_4(chara_id)):
            return 1
    return 0


@add_premise(constant_promise.Premise.PLAYER_NO_OTHER_LOVER_EXCEPT_TARGET)
def handle_player_no_other_lover_except_target(character_id: int) -> int:
    """
    玩家没有除了玩家交互对象之外的恋人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_player_have_other_lover_except_target(character_id)


@add_premise(constant_promise.Premise.PLAYER_HAVE_OTHER_PET)
def handle_player_have_other_pet(character_id: int) -> int:
    """
    玩家有除了自己之外的宠物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    for chara_id in cache.npc_id_got:
        if chara_id == 0:
            continue
        if chara_id == character_id:
            continue
        if handle_self_fall_obey(chara_id) and (handle_self_fall_3(chara_id) or handle_self_fall_4(chara_id)):
            return 1
    return 0


@add_premise(constant_promise.Premise.PLAYER_NO_OTHER_PET)
def handle_player_no_other_pet(character_id: int) -> int:
    """
    玩家没有除了自己之外的宠物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_player_have_other_pet(character_id)


@add_premise(constant_promise.Premise.PLAYER_HAVE_OTHER_PET_EXCEPT_TARGET)
def handle_player_have_other_pet_except_target(character_id: int) -> int:
    """
    玩家有除了玩家交互对象之外的宠物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    for chara_id in cache.npc_id_got:
        if chara_id == 0:
            continue
        if chara_id == pl_character_data.target_character_id:
            continue
        if handle_self_fall_obey(chara_id) and (handle_self_fall_3(chara_id) or handle_self_fall_4(chara_id)):
            return 1
    return 0


@add_premise(constant_promise.Premise.PLAYER_NO_OTHER_PET_EXCEPT_TARGET)
def handle_player_no_other_pet_except_target(character_id: int) -> int:
    """
    玩家没有除了玩家交互对象之外的宠物
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_player_have_other_pet_except_target(character_id)
