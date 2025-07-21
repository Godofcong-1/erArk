from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, constant_promise, game_type, get_text
from Script.UI.Panel import dirty_panel


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

@add_premise(constant_promise.Premise.A_SHIT)
def handle_a_shit(character_id: int) -> int:
    """
    自身肠内脏污
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_A_SHIT)
def handle_t_a_shit(character_id: int) -> int:
    """
    交互对象肠内脏污
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ENEMA)
def handle_enema(character_id: int) -> int:
    """
    自身正在灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_ENEMA)
def handle_t_enema(character_id: int) -> int:
    """
    交互对象正在灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NOT_ENEMA)
def handle_not_enema(character_id: int) -> int:
    """
    自身非灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean not in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NOT_ENEMA)
def handle_t_not_enema(character_id: int) -> int:
    """
    交互对象非灌肠中（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean not in [1, 3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ENEMA_END)
def handle_enema_end(character_id: int) -> int:
    """
    自身已灌肠（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [2, 4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_ENEMA_END)
def handle_t_enema_end(character_id: int) -> int:
    """
    交互对象已灌肠（含全种类灌肠）
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [2, 4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NORMAL_ENEMA)
def handle_normal_enema(character_id: int) -> int:
    """
    自身普通灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NORMAL_ENEMA)
def handle_t_normal_enema(character_id: int) -> int:
    """
    交互对象普通灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SEMEN_ENEMA)
def handle_semen_enema(character_id: int) -> int:
    """
    自身精液灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SEMEN_ENEMA)
def handle_t_semen_enema(character_id: int) -> int:
    """
    交互对象精液灌肠中
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [3]:
        return 1
    return 0


@add_premise(constant_promise.Premise.NORMAL_ENEMA_END)
def handle_normal_enema_end(character_id: int) -> int:
    """
    自身已普通灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [2]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_NORMAL_ENEMA_END)
def handle_t_normal_enema_end(character_id: int) -> int:
    """
    交互对象已普通灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [2]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SEMEN_ENEMA_END)
def handle_semen_enema_end(character_id: int) -> int:
    """
    自身已精液灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.a_clean in [4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SEMEN_ENEMA_END)
def handle_t_semen_enema_end(character_id: int) -> int:
    """
    交互对象已精液灌肠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.a_clean in [4]:
        return 1
    return 0


@add_premise(constant_promise.Premise.ENEMA_CAPACITY_0)
def handle_enama_capacity_0(character_id: int) -> int:
    """
    自己灌肠液量为无
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.dirty.enema_capacity == 0


@add_premise(constant_promise.Premise.T_ENEMA_CAPACITY_0)
def handle_t_enama_capacity_0(character_id: int) -> int:
    """
    交互对象灌肠液量为无
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_enama_capacity_0(character_data.target_character_id)


@add_premise(constant_promise.Premise.ENEMA_CAPACITY_GE_1)
def handle_enama_capacity_ge_1(character_id: int) -> int:
    """
    自己灌肠液量为大于等于少量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.dirty.enema_capacity >= 1


@add_premise(constant_promise.Premise.T_ENEMA_CAPACITY_GE_1)
def handle_t_enama_capacity_ge_1(character_id: int) -> int:
    """
    交互对象灌肠液量为大于等于少量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_enama_capacity_ge_1(character_data.target_character_id)


@add_premise(constant_promise.Premise.ENEMA_CAPACITY_5)
def handle_enama_capacity_5(character_id: int) -> int:
    """
    自己灌肠液量为极量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.dirty.enema_capacity == 5


@add_premise(constant_promise.Premise.T_ENEMA_CAPACITY_5)
def handle_t_enama_capacity_5(character_id: int) -> int:
    """
    交互对象灌肠液量为极量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_enama_capacity_5(character_data.target_character_id)


@add_premise(constant_promise.Premise.ENEMA_CAPACITY_L_5)
def handle_enama_capacity_l_5(character_id: int) -> int:
    """
    自己灌肠液量为少于极量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return character_data.dirty.enema_capacity < 5


@add_premise(constant_promise.Premise.T_ENEMA_CAPACITY_L_5)
def handle_t_enama_capacity_l_5(character_id: int) -> int:
    """
    交互对象灌肠液量为少于极量
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    return handle_enama_capacity_l_5(character_data.target_character_id)


@add_premise(constant_promise.Premise.T_HAIR_SEMEN)
def handle_t_hair_semen(character_id: int) -> int:
    """
    交互对象当前头发有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.body_semen[0][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WOMB_SEMEN)
def handle_t_womb_semen(character_id: int) -> int:
    """
    交互对象当前子宫有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.body_semen[7][1]:
        return 1
    return 0

@add_premise(constant_promise.Premise.VW_SEMEN_G_1)
def handle_vw_semen_g_1(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量大于1ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count > 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_G_1)
def handle_t_vw_semen_g_1(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量大于1ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count > 1:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_LE_200)
def handle_vw_semen_le_200(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量小于等于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count <= 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_LE_200)
def handle_t_vw_semen_le_200(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量小于等于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count <= 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_G_200)
def handle_vw_semen_g_200(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量大于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count > 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_G_200)
def handle_t_vw_semen_g_200(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量大于200ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count > 200:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_LE_1000)
def handle_vw_semen_le_1000(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量小于等于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count <= 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_LE_1000)
def handle_t_vw_semen_le_1000(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量小于等于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count <= 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.VW_SEMEN_G_1000)
def handle_vw_semen_g_1000(character_id: int) -> int:
    """
    自身当前小穴和子宫总精液量大于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_id)
    if all_semen_count > 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_VW_SEMEN_G_1000)
def handle_t_vw_semen_g_1000(character_id: int) -> int:
    """
    交互对象当前小穴和子宫总精液量大于1000ml
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    all_semen_count = dirty_panel.get_v_and_w_semen_count(character_data.target_character_id)
    if all_semen_count > 1000:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_PENIS_SEMEN_DIRTY)
def handle_pl_penis_semen_dirty(character_id: int) -> int:
    """
    玩家阴茎上精液污浊
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    pl_character_data = cache.character_data[0]
    penis_dirty = pl_character_data.dirty.penis_dirty_dict.get("semen", False)
    if penis_dirty:
        return 1
    return 0


@add_premise(constant_promise.Premise.PL_PENIS_NOT_SEMEN_DIRTY)
def handle_pl_penis_not_semen_dirty(character_id: int) -> int:
    """
    玩家阴茎上没有精液污浊
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    if handle_pl_penis_semen_dirty(0):
        return 0
    return 1


@add_premise(constant_promise.Premise.HAT_SEMEN)
def handle_hat_semen(character_id: int) -> int:
    """
    自身当前帽子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[0][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_HAT_SEMEN)
def handle_t_hat_semen(character_id: int) -> int:
    """
    交互对象当前帽子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[0][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.GLASS_SEMEN)
def handle_glass_semen(character_id: int) -> int:
    """
    自身当前眼镜有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[1][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_GLASS_SEMEN)
def handle_t_glass_semen(character_id: int) -> int:
    """
    交互对象当前眼镜有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[1][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_EAR_SEMEN)
def handle_in_ear_semen(character_id: int) -> int:
    """
    自身当前耳饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[2][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_IN_EAR_SEMEN)
def handle_t_in_ear_semen(character_id: int) -> int:
    """
    交互对象当前耳饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[2][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_NECK_SEMEN)
def handle_in_neck_semen(character_id: int) -> int:
    """
    自身当前脖饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[3][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_IN_NECK_SEMEN)
def handle_t_in_neck_semen(character_id: int) -> int:
    """
    交互对象当前脖饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[3][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.IN_MOUSE_SEMEN)
def handle_in_mouse_semen(character_id: int) -> int:
    """
    自身当前口饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[4][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_IN_MOUSE_SEMEN)
def handle_t_in_mouse_semen(character_id: int) -> int:
    """
    交互对象当前口饰有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[4][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.UP_CLOTH_SEMEN)
def handle_up_cloth_semen(character_id: int) -> int:
    """
    自身当前上衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[5][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_UP_CLOTH_SEMEN)
def handle_t_up_cloth_semen(character_id: int) -> int:
    """
    交互对象当前上衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[5][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.BRA_SEMEN)
def handle_bra_semen(character_id: int) -> int:
    """
    自身当前胸衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[6][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BRA_SEMEN)
def handle_t_bra_semen(character_id: int) -> int:
    """
    交互对象当前胸衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[6][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.GLOVE_SEMEN)
def handle_glove_semen(character_id: int) -> int:
    """
    自身当前手套有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[7][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_GLOVE_SEMEN)
def handle_t_glove_semen(character_id: int) -> int:
    """
    交互对象当前手套有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[7][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.DOWN_CLOTH_SEMEN)
def handle_down_cloth_semen(character_id: int) -> int:
    """
    自身当前下衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[8][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_BOTTOM_CLOTH_SEMEN)
def handle_t_botton_cloth_semen(character_id: int) -> int:
    """
    交互对象当前下衣有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[8][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.PAN_SEMEN)
def handle_pan_semen(character_id: int) -> int:
    """
    自身当前内裤有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[9][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_PAN_SEMEN)
def handle_t_pan_semen(character_id: int) -> int:
    """
    交互对象当前内裤有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[9][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SOCKS_SEMEN)
def handle_socks_semen(character_id: int) -> int:
    """
    自身当前袜子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[10][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SOCKS_SEMEN)
def handle_t_socks_semen(character_id: int) -> int:
    """
    交互对象当前袜子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[10][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.SHOES_SEMEN)
def handle_shoes_semen(character_id: int) -> int:
    """
    自身当前鞋子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[11][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_SHOES_SEMEN)
def handle_t_shoes_semen(character_id: int) -> int:
    """
    交互对象当前鞋子有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[11][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.WEAPON_SEMEN)
def handle_weapon_semen(character_id: int) -> int:
    """
    自身当前武器有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[12][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_WEAPON_SEMEN)
def handle_t_weapon_semen(character_id: int) -> int:
    """
    交互对象当前武器有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[12][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.EXTRAS_SEMEN)
def handle_extras_semen(character_id: int) -> int:
    """
    自身当前附属物有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    if character_data.dirty.cloth_semen[13][1]:
        return 1
    return 0


@add_premise(constant_promise.Premise.T_EXTRAS_SEMEN)
def handle_t_extras_semen(character_id: int) -> int:
    """
    交互对象当前附属物有精液
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dirty.cloth_semen[13][1]:
        return 1
    return 0
