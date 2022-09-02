import datetime
from types import FunctionType
from Script.Design import (
    settle_behavior,
    character,
    character_handle,
    map_handle,
    attr_calculation,
    game_time,
    cooking,
    update,
    attr_text,
)
from Script.Core import cache_control, constant, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw


_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


# @settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.N_orgasm_small)
# def handle_n_orgasm_small(
#     character_id: int,
#     change_data: game_type.CharacterStatusChange,
# ):
#     """
#     结算N小绝顶
#     Keyword arguments:
#     character_id -- 角色id
#     change_data -- 状态变更信息记录对象
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.dead:
#         return
#     #仅在H模式下才计算高潮次数计数
#     if character_data.is_h == 1:
#         character_data.orgasm_count[0] += 1


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_NClimax_EXPERIENCE)
def handle_add_1_nclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1N绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(10, 0)
    character_data.experience[10] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(10, 0)
    change_data.experience[10] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[0] += 1


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_BClimax_EXPERIENCE)
def handle_add_1_bclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1B绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(11, 0)
    character_data.experience[11] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(11, 0)
    change_data.experience[11] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[1] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_CClimax_EXPERIENCE)
def handle_add_1_cclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1C绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(12, 0)
    character_data.experience[12] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(12, 0)
    change_data.experience[12] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[2] += 1

# @settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_PClimax_EXPERIENCE)
# def handle_add_1_pclimax_experience(
#     character_id: int,
# #     change_data: game_type.CharacterStatusChange,
# # ):
#     """
#     增加1P绝顶经验
#     Keyword arguments:
#     character_id -- 角色id
# #     change_data -- 状态变更信息记录对象
# #     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.dead:
#         return
#     character_data.experience.setdefault(13, 0)
#     character_data.experience[13] += 1
#     character_data.experience.setdefault(20, 0)
#     character_data.experience[20] += 1
#     change_data.experience.setdefault(13, 0)
#     change_data.experience[13] += 1
#     change_data.experience.setdefault(20, 0)
#     change_data.experience[20] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_VClimax_EXPERIENCE)
def handle_add_1_vclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1V绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(14, 0)
    character_data.experience[14] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(14, 0)
    change_data.experience[14] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[4] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_AClimax_EXPERIENCE)
def handle_add_1_aclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1A绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(15, 0)
    character_data.experience[15] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(15, 0)
    change_data.experience[15] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[5] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_UClimax_EXPERIENCE)
def handle_add_1_uclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1U绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(16, 0)
    character_data.experience[16] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(16, 0)
    change_data.experience[16] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[6] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_WClimax_EXPERIENCE)
def handle_add_1_wclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1W绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(17, 0)
    character_data.experience[17] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(17, 0)
    change_data.experience[17] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[7] += 1

"""
    8-9留空
"""

# @settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_Climax_EXPERIENCE)
# def handle_add_1_climax_experience(
#     character_id: int,
# #     change_data: game_type.CharacterStatusChange,
# # ):
#     """
#     增加1绝顶经验
#     Keyword arguments:
#     character_id -- 角色id
# #     change_data -- 状态变更信息记录对象
# #     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.dead:
#         return
#     character_data.experience.setdefault(20, 0)
#     character_data.experience[20] += 1
#     change_data.experience.setdefault(20, 0)
#     change_data.experience[20] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_Cumming_EXPERIENCE)
def handle_add_1_cumming_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1射精经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(21, 0)
    character_data.experience[21] += 1
    change_data.experience.setdefault(21, 0)
    change_data.experience[21] += 1
    if character_data.is_h == 1:
        character_data.orgasm_count[3] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_Milking_EXPERIENCE)
def handle_add_1_milking_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1喷乳经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(22, 0)
    character_data.experience[22] += 1
    change_data.experience.setdefault(22, 0)
    change_data.experience[22] += 1

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_1_Peeing_EXPERIENCE)
def handle_add_1_peeing_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1放尿经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(23, 0)
    character_data.experience[23] += 1
    change_data.experience.setdefault(23, 0)
    change_data.experience[23] += 1


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.TARGET_ADD_1_Cums_EXPERIENCE)
def handle_target_add_1_cums_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    交互对象增加1精液经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_data.experience.setdefault(24, 0)
    target_data.experience[24] += 1
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(24, 0)
    target_change.experience[24] += 1


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.TARGET_ADD_SMALL_LUBRICATION)
def handle_target_add_small_lubrication(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    交互对象增加少量润滑
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return

    now_add_lust = 500
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.TARGET_ADD_MIDDLE_LUBRICATION)
def handle_target_add_middle_lubrication(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    交互对象增加中量润滑
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return

    now_add_lust = 1500
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.TARGET_ADD_LARGE_LUBRICATION)
def handle_target_add_large_lubrication(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    交互对象增加大量润滑
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return

    now_add_lust = 5000
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_LUBRICATION)
def handle_add_small_lubrication(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量润滑
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    now_add_lust = 500
    character_data.status_data.setdefault(8, 0)
    character_data.status_data[8] += now_add_lust
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_MIDDLE_LUBRICATION)
def handle_add_middle_lubrication(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量润滑
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    now_add_lust = 1500
    character_data.status_data.setdefault(8, 0)
    character_data.status_data[8] += now_add_lust
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_LARGE_LUBRICATION)
def handle_add_large_lubrication(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量润滑
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    now_add_lust = 5000
    character_data.status_data.setdefault(8, 0)
    character_data.status_data[8] += now_add_lust
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.DOWN_SMALL_HIT_POINT)
def handle_down_small_hit_point(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少少量体力
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    sub_hit = 30
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    #气力为0时体力消耗3倍#
    if character_data.mana_point == 0:
        sub_hit *= 3
    #体力不足0时锁为1#
    if character_data.hit_point >= sub_hit:
        character_data.hit_point -= sub_hit
        change_data.hit_point -= sub_hit
    else:
        change_data.hit_point -= character_data.hit_point
        character_data.hit_point = 1
        if not character_data.tired:
            character_data.tired = 1
            now_draw = draw.NormalDraw()
            now_draw.width = window_width
            now_draw.text = "\n" + character_data.name + "太累了\n"
            now_draw.draw()


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.DOWN_SMALL_MANA_POINT)
def handle_down_small_mana_point(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少少量气力
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    sub_mana = 50
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    if character_data.mana_point >= sub_mana:
        character_data.mana_point -= sub_mana
        change_data.mana_point -= sub_mana
    else:
        change_data.mana_point -= character_data.mana_point
        sub_mana -= character_data.mana_point
        character_data.mana_point = 0
        character_data.hit_point -= sub_mana
        change_data.hit_point -= sub_mana
        if character_data.hit_point <= 0:
            character_data.hit_point = 1
            if not character_data.tired:
                character_data.tired = 1
                now_draw = draw.NormalDraw()
                now_draw.width = window_width
                now_draw.text = "\n" + character_data.name + "太累了\n"
                now_draw.draw()


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_N_FEEL)
def handle_add_small_n_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｎ快（N感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[0]
    now_add_lust = 100 + now_lust / 10
    adjust = attr_calculation.get_ability_adjust(character_data.ability[0])
    now_add_lust *= adjust

    character_data.status_data[0] += now_add_lust
    change_data.status_data.setdefault(0, 0)
    change_data.status_data[0] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_B_FEEL)
def handle_add_small_b_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｂ快（B感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[1]
    now_add_lust = 100 + now_lust / 10
    adjust = attr_calculation.get_ability_adjust(character_data.ability[1])
    now_add_lust *= adjust

    character_data.status_data[1] += now_add_lust
    change_data.status_data.setdefault(1, 0)
    change_data.status_data[1] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_C_FEEL)
def handle_add_small_c_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｃ快（C感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[2]
    now_add_lust = 100 + now_lust / 10
    adjust = attr_calculation.get_ability_adjust(character_data.ability[2])
    now_add_lust *= adjust

    character_data.status_data[2] += now_add_lust
    change_data.status_data.setdefault(2, 0)
    change_data.status_data[2] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_V_FEEL)
def handle_add_small_v_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｖ快（V感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[4]
    now_add_lust = 100 + now_lust / 10
    adjust = attr_calculation.get_ability_adjust(character_data.ability[4])
    now_add_lust *= adjust

    character_data.status_data[4] += now_add_lust
    change_data.status_data.setdefault(4, 0)
    change_data.status_data[4] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_A_FEEL)
def handle_add_small_a_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ａ快（A感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[5]
    now_add_lust = 100 + now_lust / 10
    adjust = attr_calculation.get_ability_adjust(character_data.ability[5])
    now_add_lust *= adjust

    character_data.status_data[5] += now_add_lust
    change_data.status_data.setdefault(5, 0)
    change_data.status_data[5] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_U_FEEL)
def handle_add_small_u_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｕ快（U感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[6]
    now_add_lust = 100 + now_lust / 10
    adjust = attr_calculation.get_ability_adjust(character_data.ability[6])
    now_add_lust *= adjust

    character_data.status_data[6] += now_add_lust
    change_data.status_data.setdefault(6, 0)
    change_data.status_data[6] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_W_FEEL)
def handle_add_small_w_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｗ快（W感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[7]
    now_add_lust = 100 + now_lust / 10
    adjust = attr_calculation.get_ability_adjust(character_data.ability[7])
    now_add_lust *= adjust

    character_data.status_data[7] += now_add_lust
    change_data.status_data.setdefault(7, 0)
    change_data.status_data[7] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_LUBRICATION)
def handle_add_small_lubrication(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量润滑（欲望补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[8])
    now_add_lust *= adjust

    character_data.status_data[8] += now_add_lust
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_DESIRE)
def handle_add_small_desire(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量欲情（欲望补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[22])
    now_add_lust *= adjust

    character_data.status_data[12] += now_add_lust
    change_data.status_data.setdefault(12, 0)
    change_data.status_data[12] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_HAPPY)
def handle_add_small_happy(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量快乐（快乐刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[13])
    now_add_lust *= adjust

    character_data.status_data[13] += now_add_lust
    change_data.status_data.setdefault(13, 0)
    change_data.status_data[13] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_SUBMIT)
def handle_add_small_submit(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量屈服（屈服刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[14])
    now_add_lust *= adjust

    character_data.status_data[15] += now_add_lust
    change_data.status_data.setdefault(15, 0)
    change_data.status_data[15] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_PAIN)
def handle_add_small_pain(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量苦痛（苦痛刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[15])
    now_add_lust *= adjust

    character_data.status_data[17] += now_add_lust
    change_data.status_data.setdefault(17, 0)
    change_data.status_data[17] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_TERROR)
def handle_add_small_terror(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量恐怖（恐怖刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[17])
    now_add_lust *= adjust

    character_data.status_data[18] += now_add_lust
    change_data.status_data.setdefault(18, 0)
    change_data.status_data[18] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant.SecondEffect.ADD_SMALL_DISGUST)
def handle_add_small_disgust(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量反感（反发刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[18])
    now_add_lust *= adjust

    character_data.status_data[20] += now_add_lust
    change_data.status_data.setdefault(20, 0)
    change_data.status_data[20] += now_add_lust

