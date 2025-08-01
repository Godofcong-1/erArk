from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
from Script.Config import game_config

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


@add_premise(constant_promise.Premise.AT_LEAST_ONE_ARTS_ON)
def handle_at_least_one_arts_on(character_id: int) -> int:
    """
    至少有一种源石技艺开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    # 催眠
    if handle_target_in_hypnosis(character_id):
        return 1
    # 透视
    if handle_penetrating_vision_on(character_id):
        return 1
    # 时停
    if handle_time_stop_on(character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.PRIMARY_HYPNOSIS)
def handle_primary_hypnosis(character_id: int) -> int:
    """
    自己拥有初级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[331]


@add_premise(constant_promise.Premise.INTERMEDIATE_HYPNOSIS)
def handle_intermediate_hypnosis(character_id: int) -> int:
    """
    自己拥有中级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[332]


@add_premise(constant_promise.Premise.ADVANCED_HYPNOSIS)
def handle_advanced_hypnosis(character_id: int) -> int:
    """
    自己拥有高级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[333]


@add_premise(constant_promise.Premise.SPECIAL_HYPNOSIS)
def handle_special_hypnosis(character_id: int) -> int:
    """
    自己拥有特级催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[334]


@add_premise(constant_promise.Premise.SELF_HYPNOSIS_0)
def handle_self_hypnosis_0(character_id: int) -> int:
    """
    自己的被催眠程度为0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.hypnosis.hypnosis_degree == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_HYPNOSIS_NE_0)
def handle_self_hypnosis_ne_0(character_id: int) -> int:
    """
    自己的被催眠程度不是0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_hypnosis_0(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_0)
def handle_target_hypnosis_0(character_id: int) -> int:
    """
    交互对象的被催眠程度为0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_self_hypnosis_0(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_NE_0)
def handle_target_hypnosis_ne_0(character_id: int) -> int:
    """
    交互对象的被催眠程度不是0%
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_self_hypnosis_0(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_HAS_BEEN_HYPNOSIS)
def handle_self_has_been_hypnosis(character_id: int) -> int:
    """
    自己有至少一种被催眠素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for cid in {71,72,73}:
        if character_data.talent[cid]:
            return 1
    return 0


@add_premise(constant_promise.Premise.SELF_HAS_NOT_BEEN_HYPNOSIS)
def handle_self_has_not_been_hypnosis(character_id: int) -> int:
    """
    自己没有任何被催眠素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_self_has_been_hypnosis(character_id)


@add_premise(constant_promise.Premise.SELF_HAS_BEEN_PRIMARY_HYPNOSIS)
def handle_self_has_been_primary_hypnosis(character_id: int) -> int:
    """
    自己拥有被浅层催眠素质(50%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[71]


@add_premise(constant_promise.Premise.SELF_HAS_BEEN_DEEP_HYPNOSIS)
def handle_self_has_been_deep_hypnosis(character_id: int) -> int:
    """
    自己拥有被深层催眠素质(100%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[72]


@add_premise(constant_promise.Premise.SELF_HAS_BEEN_COMPLETE_HYPNOSIS)
def handle_self_has_been_complete_hypnosis(character_id: int) -> int:
    """
    自己拥有被完全催眠素质(200%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[73]


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_HYPNOSIS)
def handle_target_has_been_hypnosis(character_id: int) -> int:
    """
    交互对象有至少一种被催眠素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_self_has_been_hypnosis(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_HAS_NOT_BEEN_HYPNOSIS)
def handle_target_has_not_been_hypnosis(character_id: int) -> int:
    """
    交互对象没有任何被催眠素质
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_self_has_been_hypnosis(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_PRIMARY_HYPNOSIS)
def handle_target_has_been_primary_hypnosis(character_id: int) -> int:
    """
    交互对象拥有被浅层催眠素质(50%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_self_has_been_primary_hypnosis(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_DEEP_HYPNOSIS)
def handle_target_has_been_deep_hypnosis(character_id: int) -> int:
    """
    交互对象拥有被深层催眠素质(100%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_self_has_been_deep_hypnosis(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_HAS_BEEN_COMPLETE_HYPNOSIS)
def handle_target_has_been_complete_hypnosis(character_id: int) -> int:
    """
    交互对象拥有被完全催眠素质(200%)
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_self_has_been_complete_hypnosis(character_data.target_character_id)


@add_premise(constant_promise.Premise.IN_HYPNOSIS)
def handle_in_hypnosis(character_id: int) -> int:
    """
    自己正在被催眠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_IN_HYPNOSIS)
def handle_not_in_hypnosis(character_id: int) -> int:
    """
    自己没有正在被催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_IN_HYPNOSIS)
def handle_target_in_hypnosis(character_id: int) -> int:
    """
    交互对象正在被催眠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_IN_HYPNOSIS)
def handle_target_not_in_hypnosis(character_id: int) -> int:
    """
    交互对象没有正在被催眠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.sp_flag.unconscious_h in [4,5,6,7]:
        return 0
    return 1


@add_premise(constant_promise.Premise.PRIMARY_PENETRATING_VISION)
def handle_primary_penetrating_vision(character_id: int) -> int:
    """
    拥有初级透视
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[307]


@add_premise(constant_promise.Premise.INTERMEDIATE_PENETRATING_VISION)
def handle_intermediate_penetrating_vision(character_id: int) -> int:
    """
    拥有中级透视
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[308]


@add_premise(constant_promise.Premise.ADVANCED_PENETRATING_VISION)
def handle_advanced_penetrating_vision(character_id: int) -> int:
    """
    拥有高级透视
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[309]


@add_premise(constant_promise.Premise.PENETRATING_VISION_ON)
def handle_penetrating_vision_on(character_id: int) -> int:
    """
    透视开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.pl_ability.visual


@add_premise(constant_promise.Premise.PENETRATING_VISION_OFF)
def handle_penetrating_vision_off(character_id: int) -> int:
    """
    透视关闭中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not character_data.pl_ability.visual


@add_premise(constant_promise.Premise.PRIMARY_HORMONE)
def handle_primary_hormone(character_id: int) -> int:
    """
    拥有初级信息素
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[304]


@add_premise(constant_promise.Premise.INTERMEDIATE_HORMONE)
def handle_intermediate_hormone(character_id: int) -> int:
    """
    拥有中级信息素
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[305]


@add_premise(constant_promise.Premise.ADVANCED_HORMONE)
def handle_advanced_hormone(character_id: int) -> int:
    """
    拥有高级信息素
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[306]


@add_premise(constant_promise.Premise.HORMONE_ON)
def handle_hormone_on(character_id: int) -> int:
    """
    信息素开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.pl_ability.hormone


@add_premise(constant_promise.Premise.HORMONE_OFF)
def handle_hormone_off(character_id: int) -> int:
    """
    信息素关闭中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not character_data.pl_ability.hormone


@add_premise(constant_promise.Premise.PRIMARY_TELEKINESIS)
def handle_primary_telekinesis(character_id: int) -> int:
    """
    拥有初级隔空肢体
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[310]


@add_premise(constant_promise.Premise.INTERMEDIATE_TELEKINESIS)
def handle_intermediate_telekinesis(character_id: int) -> int:
    """
    拥有中级隔空肢体
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[311]


@add_premise(constant_promise.Premise.ADVANCED_TELEKINESIS)
def handle_advanced_telekinesis(character_id: int) -> int:
    """
    拥有高级隔空肢体
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[312]


@add_premise(constant_promise.Premise.HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    自己被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.increase_body_sensitivity


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_not_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    自己未被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_increase_body_sensitivity(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_target_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    交互对象被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_increase_body_sensitivity(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_INCREASE_BODY_SENSITIVITY)
def handle_target_not_hypnosis_increase_body_sensitivity(character_id: int) -> int:
    """
    交互对象未被体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_increase_body_sensitivity(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_FORCE_OVULATION)
def handle_hypnosis_force_ovulation(character_id: int) -> int:
    """
    自己被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.force_ovulation


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_FORCE_OVULATION)
def handle_not_hypnosis_force_ovulation(character_id: int) -> int:
    """
    自己未被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_force_ovulation(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_FORCE_OVULATION)
def handle_target_hypnosis_force_ovulation(character_id: int) -> int:
    """
    交互对象被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_force_ovulation(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_FORCE_OVULATION)
def handle_target_not_hypnosis_force_ovulation(character_id: int) -> int:
    """
    交互对象未被体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_force_ovulation(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_BLOCKHEAD)
def handle_hypnosis_blockhead(character_id: int) -> int:
    """
    自己被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.blockhead


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_BLOCKHEAD)
def handle_not_hypnosis_blockhead(character_id: int) -> int:
    """
    自己未被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_blockhead(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_BLOCKHEAD)
def handle_target_hypnosis_blockhead(character_id: int) -> int:
    """
    交互对象被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_blockhead(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_BLOCKHEAD)
def handle_target_not_hypnosis_blockhead(character_id: int) -> int:
    """
    交互对象未被体控-木头人
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_blockhead(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_ACTIVE_H)
def handle_hypnosis_active_h(character_id: int) -> int:
    """
    自己被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.active_h


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_ACTIVE_H)
def handle_not_hypnosis_active_h(character_id: int) -> int:
    """
    自己未被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_active_h(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ACTIVE_H)
def handle_target_hypnosis_active_h(character_id: int) -> int:
    """
    交互对象被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_active_h(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_ACTIVE_H)
def handle_target_not_hypnosis_active_h(character_id: int) -> int:
    """
    交互对象未被体控-逆推
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_active_h(character_data.target_character_id)


@add_premise(constant_promise.Premise.HYPNOSIS_ROLEPLAY)
def handle_hypnosis_roleplay(character_id: int) -> int:
    """
    自己被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return len(character_data.hypnosis.roleplay)


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_ROLEPLAY)
def handle_not_hypnosis_roleplay(character_id: int) -> int:
    """
    自己未被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_roleplay(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY)
def handle_target_hypnosis_roleplay(character_id: int) -> int:
    """
    交互对象被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_roleplay(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_ROLEPLAY)
def handle_target_not_hypnosis_roleplay(character_id: int) -> int:
    """
    交互对象未被心控-角色扮演
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_roleplay(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_1)
def handle_target_hypnosis_roleplay_1(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-妻子
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for cid in game_config.config_roleplay:
        roleplay_data = game_config.config_roleplay[cid]
        if roleplay_data.name == _("妻子") and cid in target_data.hypnosis.roleplay:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_2)
def handle_target_hypnosis_roleplay_2(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-妹妹
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for cid in game_config.config_roleplay:
        roleplay_data = game_config.config_roleplay[cid]
        if roleplay_data.name == _("妹妹") and cid in target_data.hypnosis.roleplay:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_3)
def handle_target_hypnosis_roleplay_3(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-女儿
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for cid in game_config.config_roleplay:
        roleplay_data = game_config.config_roleplay[cid]
        if roleplay_data.name == _("女儿") and cid in target_data.hypnosis.roleplay:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_4)
def handle_target_hypnosis_roleplay_4(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-女仆
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for cid in game_config.config_roleplay:
        roleplay_data = game_config.config_roleplay[cid]
        if roleplay_data.name == _("女仆") and cid in target_data.hypnosis.roleplay:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_5)
def handle_target_hypnosis_roleplay_5(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-宠物猫
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for cid in game_config.config_roleplay:
        roleplay_data = game_config.config_roleplay[cid]
        if roleplay_data.name == _("宠物猫") and cid in target_data.hypnosis.roleplay:
            return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_ROLEPLAY_6)
def handle_target_hypnosis_roleplay_6(character_id: int) -> int:
    """
    交互对象被心控-角色扮演-宠物狗
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    for cid in game_config.config_roleplay:
        roleplay_data = game_config.config_roleplay[cid]
        if roleplay_data.name == _("宠物狗") and cid in target_data.hypnosis.roleplay:
            return 1
    return 0


@add_premise(constant_promise.Premise.HYPNOSIS_PAIN_AS_PLEASURE)
def handle_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    自己被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.hypnosis.pain_as_pleasure


@add_premise(constant_promise.Premise.NOT_HYPNOSIS_PAIN_AS_PLEASURE)
def handle_not_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    自己未被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_hypnosis_pain_as_pleasure(character_id)


@add_premise(constant_promise.Premise.TARGET_HYPNOSIS_PAIN_AS_PLEASURE)
def handle_t_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    交互对象被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return handle_hypnosis_pain_as_pleasure(character_data.target_character_id)


@add_premise(constant_promise.Premise.TARGET_NOT_HYPNOSIS_PAIN_AS_PLEASURE)
def handle_t_not_hypnosis_pain_as_pleasure(character_id: int) -> int:
    """
    交互对象未被心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return not handle_hypnosis_pain_as_pleasure(character_data.target_character_id)


@add_premise(constant_promise.Premise.PRIMARY_TIME_STOP)
def handle_primary_time_stop(character_id: int) -> int:
    """
    自己拥有初级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.talent[316]:
        return 1
    return 0


@add_premise(constant_promise.Premise.INTERMEDIATE_TIME_STOP)
def handle_intermediate_time_stop(character_id: int) -> int:
    """
    自己拥有中级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.talent[317]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ADVANCED_TIME_STOP)
def handle_advanced_time_stop(character_id: int) -> int:
    """
    自己拥有高级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.talent[318]:
        return 1
    return 0


@add_premise(constant_promise.Premise.TIME_STOP_ON)
def handle_time_stop_on(character_id: int) -> int:
    """
    时停开启中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return cache.time_stop_mode


@add_premise(constant_promise.Premise.TIME_STOP_OFF)
def handle_time_stop_off(character_id: int) -> int:
    """
    时停关闭中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_time_stop_on(character_id)


@add_premise(constant_promise.Premise.TIME_STOP_JUDGE_FOR_MOVE)
def handle_time_stop_judge_for_move(character_id: int) -> int:
    """
    (移动用)未开启时停，或时停开启且有中级时停
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_time_stop_off(character_id):
        return 1
    else:
        if handle_intermediate_time_stop(character_id):
            return 1
    return 0


@add_premise(constant_promise.Premise.NOBODY_FREE_IN_TIME_STOP)
def handle_nobody_free_in_time_stop(character_id: int) -> int:
    """
    没有指定可以在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.pl_ability.free_in_time_stop_chara_id > 0:
        return 0
    return 1


@add_premise(constant_promise.Premise.NOT_CARRY_ANYBODY_IN_TIME_STOP)
def handle_not_carry_anybody_in_time_stop(character_id: int) -> int:
    """
    没有在时停中搬运干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.pl_ability.carry_chara_id_in_time_stop > 0:
        return 0
    return 1


@add_premise(constant_promise.Premise.CARRY_SOMEBODY_IN_TIME_STOP)
def handle_carry_somebody_in_time_stop(character_id: int) -> int:
    """
    正在时停中搬运干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    return not handle_not_carry_anybody_in_time_stop(character_id)


@add_premise(constant_promise.Premise.TARGET_IS_CARRIED_IN_TIME_STOP)
def handle_target_is_carried_in_time_stop(character_id: int) -> int:
    """
    交互对象是自己正在时停中搬运的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if pl_character_data.pl_ability.carry_chara_id_in_time_stop > 0:
        if pl_character_data.target_character_id == pl_character_data.pl_ability.carry_chara_id_in_time_stop:
            return 1
    return 0


@add_premise(constant_promise.Premise.SOMEBODY_FREE_IN_TIME_STOP)
def handle_somebody_free_in_time_stop(character_id: int) -> int:
    """
    玩家已指定可以在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_nobody_free_in_time_stop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.SELF_FREE_IN_TIME_STOP)
def handle_self_free_in_time_stop(character_id: int) -> int:
    """
    自己是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    if character_id > 0 and character_id == pl_character_data.pl_ability.free_in_time_stop_chara_id:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_NOT_FREE_IN_TIME_STOP)
def handle_self_not_free_in_time_stop(character_id: int) -> int:
    """
    自己不是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_self_free_in_time_stop(character_id):
        return 0
    return 1


@add_premise(constant_promise.Premise.TARGET_FREE_IN_TIME_STOP)
def handle_target_free_in_time_stop(character_id: int) -> int:
    """
    交互对象是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_free_in_time_stop(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_NOT_FREE_IN_TIME_STOP)
def handle_target_not_free_in_time_stop(character_id: int) -> int:
    """
    交互对象不是在时停中自由活动的干员
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_free_in_time_stop(character_data.target_character_id):
        return 0
    return 1
