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


@add_premise(constant_promise.Premise.T_LOVE_SENSE_TASTE_0)
def handle_t_love_sense_taste_0(character_id: int) -> int:
    """
    校验交互对象是否精爱味觉==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[31] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_SEXUAL_IGNORANCE_0)
def handle_self_sexual_ignorance_0(character_id: int) -> int:
    """
    校验自己没有性无知
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[222] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_SEXUAL_IGNORANCE_1)
def handle_self_sexual_ignorance_1(character_id: int) -> int:
    """
    校验自己有性无知
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[222] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_LOVE_SENSE_TASTE_1)
def handle_t_love_sense_taste_1(character_id: int) -> int:
    """
    校验交互对象是否精爱味觉==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[31] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SADISM_0)
def handle_t_sadism_0(character_id: int) -> int:
    """
    校验交互对象是否施虐狂==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[229] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SADISM_1)
def handle_t_sadism_1(character_id: int) -> int:
    """
    校验交互对象是否施虐狂==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[229] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_MASOCHISM_0)
def handle_t_masochism_0(character_id: int) -> int:
    """
    校验交互对象是否受虐狂==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[230] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_MASOCHISM_1)
def handle_t_masochism_1(character_id: int) -> int:
    """
    校验交互对象是否受虐狂==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[230] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_OESTRUS_0)
def handle_t_oestrus_0(character_id: int) -> int:
    """
    校验交互对象是否发情期==0
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[62] == 0:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_OESTRUS_1)
def handle_t_oestrus_1(character_id: int) -> int:
    """
    校验交互对象是否发情期==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data = cache.character_data[character_data.target_character_id]
    if target_data.talent[62] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_IS_CHILD)
def handle_self_is_child(character_id: int) -> int:
    """
    校验自己是幼女
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[102] == 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHILD_OR_LOLI_1)
def handle_self_child_or_loli_1(character_id: int) -> int:
    """
    校验交互对象是否幼女或萝莉==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.talent[102] == 1 or character_data.talent[103] == 1:
        return 1
    return 0

@add_premise(constant_promise.Premise.T_CHILD_OR_LOLI_1)
def handle_t_child_or_loli_1(character_id: int) -> int:
    """
    校验交互对象是否幼女或萝莉==1
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_self_child_or_loli_1(character_data.target_character_id)


@add_premise(constant_promise.Premise.SELF_CHEST_IS_CLIFF)
def handle_self_chest_is_cliff(character_id: int) -> int:
    """
    自己胸部大小是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[121]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_CLIFF)
def handle_target_chest_is_cliff(character_id: int) -> int:
    """
    交互对象胸部大小是绝壁
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_cliff(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_SMALL)
def handle_self_chest_is_small(character_id: int) -> int:
    """
    自己胸部大小是贫乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[122]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_SMALL)
def handle_target_chest_is_small(character_id: int) -> int:
    """
    交互对象胸部大小是贫乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_small(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_NORMAL)
def handle_self_chest_is_normal(character_id: int) -> int:
    """
    自己胸部大小是普乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[123]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_NORMAL)
def handle_target_chest_is_normal(character_id: int) -> int:
    """
    交互对象胸部大小是普乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_normal(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_BIG)
def handle_self_chest_is_big(character_id: int) -> int:
    """
    自己胸部大小是巨乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[124]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_BIG)
def handle_target_chest_is_big(character_id: int) -> int:
    """
    交互对象胸部大小是巨乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_big(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.SELF_CHEST_IS_SUPER)
def handle_self_chest_is_super(character_id: int) -> int:
    """
    自己胸部大小是爆乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    return character_data.talent[125]


@add_premise(constant_promise.Premise.TARGET_CHEST_IS_SUPER)
def handle_target_chest_is_super(character_id: int) -> int:
    """
    交互对象胸部大小是爆乳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_self_chest_is_super(character_data.target_character_id):
        return 1
    return 0


@add_premise(constant_promise.Premise.TARGET_BUTTOCKS_IS_SMALL)
def handle_target_buttock_is_small(character_id: int) -> int:
    """
    交互对象屁股大小是小臀
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[126]


@add_premise(constant_promise.Premise.TARGET_BUTTOCKS_IS_NORMAL)
def handle_target_buttock_is_normal(character_id: int) -> int:
    """
    交互对象胸部大小是普臀
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[127]


@add_premise(constant_promise.Premise.TARGET_BUTTOCKS_IS_BIG)
def handle_target_buttock_is_big(character_id: int) -> int:
    """
    交互对象胸部大小是巨臀
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[128]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_EARS)
def handle_target_have_no_eras(character_id: int) -> int:
    """
    交互对象没有兽耳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[111]


@add_premise(constant_promise.Premise.TARGET_HAVE_EARS)
def handle_target_have_eras(character_id: int) -> int:
    """
    交互对象有兽耳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[111]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_HORN)
def handle_target_have_no_horn(character_id: int) -> int:
    """
    交互对象没有兽角
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[112]


@add_premise(constant_promise.Premise.TARGET_HAVE_HORN)
def handle_target_have_horn(character_id: int) -> int:
    """
    交互对象有兽角
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[112]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_TAIL)
def handle_target_have_no_tail(character_id: int) -> int:
    """
    交互对象没有兽尾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[113]


@add_premise(constant_promise.Premise.TARGET_HAVE_TAIL)
def handle_target_have_tail(character_id: int) -> int:
    """
    交互对象有兽尾
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[113]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_RING)
def handle_target_have_no_ring(character_id: int) -> int:
    """
    交互对象没有光环
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[114]


@add_premise(constant_promise.Premise.TARGET_HAVE_RING)
def handle_target_have_ring(character_id: int) -> int:
    """
    交互对象有光环
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[114]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_WING)
def handle_target_have_no_wing(character_id: int) -> int:
    """
    交互对象没有光翼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[115]


@add_premise(constant_promise.Premise.TARGET_HAVE_WING)
def handle_target_have_wing(character_id: int) -> int:
    """
    交互对象有光翼
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[115]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_TENTACLE)
def handle_target_have_no_tentacle(character_id: int) -> int:
    """
    交互对象没有触手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[116]


@add_premise(constant_promise.Premise.TARGET_HAVE_TENTACLE)
def handle_target_have_tentacle(character_id: int) -> int:
    """
    交互对象有触手
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[116]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_CAR)
def handle_target_have_no_car(character_id: int) -> int:
    """
    交互对象没有小车
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[117]


@add_premise(constant_promise.Premise.TARGET_HAVE_CAR)
def handle_target_have_car(character_id: int) -> int:
    """
    交互对象有小车
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[117]


@add_premise(constant_promise.Premise.TARGET_NOT_PATIENT)
def handle_target_not_patient(character_id: int) -> int:
    """
    交互对象不是源石病感染者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[150]


@add_premise(constant_promise.Premise.TARGET_IS_PATIENT)
def handle_target_is_patient(character_id: int) -> int:
    """
    交互对象是源石病感染者
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[150]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_CRYSTAL)
def handle_target_have_no_crystal(character_id: int) -> int:
    """
    交互对象没有体表源石结晶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[162]


@add_premise(constant_promise.Premise.TARGET_HAVE_CRYSTAL)
def handle_target_have_crystal(character_id: int) -> int:
    """
    交互对象有体表源石结晶
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[162]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_DILIGENT)
def handle_target_have_no_diligent(character_id: int) -> int:
    """
    交互对象非勤劳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[271]


@add_premise(constant_promise.Premise.TARGET_HAVE_DILIGENT)
def handle_target_have_diligent(character_id: int) -> int:
    """
    交互对象勤劳
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[271]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_LAZY)
def handle_target_have_no_lazy(character_id: int) -> int:
    """
    交互对象非懒散
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[272]


@add_premise(constant_promise.Premise.TARGET_HAVE_LAZY)
def handle_target_have_lazy(character_id: int) -> int:
    """
    交互对象懒散
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[272]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_FRAGILE)
def handle_target_have_no_fragile(character_id: int) -> int:
    """
    交互对象非脆弱
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[273]


@add_premise(constant_promise.Premise.TARGET_HAVE_FRAGILE)
def handle_target_have_fragile(character_id: int) -> int:
    """
    交互对象脆弱
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[273]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_FORCEFUL)
def handle_target_have_no_forceful(character_id: int) -> int:
    """
    交互对象非坚强
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[274]


@add_premise(constant_promise.Premise.TARGET_HAVE_FORCEFUL)
def handle_target_have_forceful(character_id: int) -> int:
    """
    交互对象坚强
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[274]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_ENTHUSIACTIC)
def handle_target_have_no_enthusiactic(character_id: int) -> int:
    """
    交互对象非热情
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[275]


@add_premise(constant_promise.Premise.TARGET_HAVE_ENTHUSIACTIC)
def handle_target_have_enthusiactic(character_id: int) -> int:
    """
    交互对象热情
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[275]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_ALONE)
def handle_target_have_no_alone(character_id: int) -> int:
    """
    交互对象非孤僻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[276]


@add_premise(constant_promise.Premise.TARGET_HAVE_ALONE)
def handle_target_have_alone(character_id: int) -> int:
    """
    交互对象孤僻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[276]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_SHAME)
def handle_target_have_no_shame(character_id: int) -> int:
    """
    交互对象非羞耻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[277]


@add_premise(constant_promise.Premise.TARGET_HAVE_SHAME)
def handle_target_have_shame(character_id: int) -> int:
    """
    交互对象羞耻
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[277]


@add_premise(constant_promise.Premise.TARGET_HAVE_NO_OPEN)
def handle_target_have_no_open(character_id: int) -> int:
    """
    交互对象非开放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return not target_data.talent[278]


@add_premise(constant_promise.Premise.TARGET_HAVE_OPEN)
def handle_target_have_open(character_id: int) -> int:
    """
    交互对象开放
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    return target_data.talent[278]
