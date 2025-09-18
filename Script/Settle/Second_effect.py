from types import FunctionType
from Script.Design import (
    settle_behavior,
    attr_calculation,
    handle_premise,
)
from Script.Core import cache_control, constant_effect, game_type, get_text
from Script.Config import normal_config
from Script.UI.Moudle import draw
from Script.Settle.common_default import base_chara_experience_common_settle, base_chara_hp_mp_common_settle, base_chara_state_common_settle


_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


# @settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.S_orgasm_small)
# def handle_s_orgasm_small(
#     character_id: int,
#     change_data: game_type.CharacterStatusChange,
# ):
#     """
#     结算S小绝顶
#     Keyword arguments:
#     character_id -- 角色id
#     change_data -- 状态变更信息记录对象
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.dead:
#         return
#     #仅在H模式下才计算高潮次数计数
#     if character_data.sp_flag.is_h == 1:
#         character_data.h_state.orgasm_count[0] += 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.Nothing)
def handle_nothing(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    空白结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    _ = 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.Must_Show)
def handle_must_show(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    必须显示的空白结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    _ = 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.Must_Settle)
def handle_must_settle(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    必须计算但不必须显示的空白结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    _ = 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_NClimax_EXPERIENCE)
def handle_add_1_nclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1S绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    base_chara_experience_common_settle(character_id, 10, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[0][0] += 1
        character_data.h_state.orgasm_count[0][1] += 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_BClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 11, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[1][0] += 1
        character_data.h_state.orgasm_count[1][1] += 1

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_CClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 12, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[2][0] += 1
        character_data.h_state.orgasm_count[2][1] += 1

# @settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_PClimax_EXPERIENCE)
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

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_VClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 14, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[4][0] += 1
        character_data.h_state.orgasm_count[4][1] += 1

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_AClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 15, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[5][0] += 1
        character_data.h_state.orgasm_count[5][1] += 1

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_UClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 16, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[6][0] += 1
        character_data.h_state.orgasm_count[6][1] += 1

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_WClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 17, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[7][0] += 1
        character_data.h_state.orgasm_count[7][1] += 1

"""
    8-9留空
"""

# @settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_Climax_EXPERIENCE)
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

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_Cumming_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 21, 1, change_data=change_data)
    character_data.h_state.orgasm_count[3][0] += 1
    character_data.h_state.orgasm_count[3][1] += 1

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_Milking_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 22, 1, change_data=change_data)

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_Peeing_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 23, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.TARGET_ADD_1_Cums_EXPERIENCE)
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
    if character_data.dead:
        return
    base_chara_experience_common_settle(character_data.target_character_id, 24, 1, target_flag=False, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.TARGET_ADD_SMALL_LUBRICATION)
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

    now_add_lust = 300
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.TARGET_ADD_MIDDLE_LUBRICATION)
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

    now_add_lust = 900
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.TARGET_ADD_LARGE_LUBRICATION)
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

    now_add_lust = 3000
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_LUBRICATION)
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

    now_add_lust = 300
    character_data.status_data.setdefault(8, 0)
    character_data.status_data[8] += now_add_lust
    character_data.status_data[8] = min(99999, character_data.status_data[8])
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_LUBRICATION)
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

    now_add_lust = 900
    character_data.status_data.setdefault(8, 0)
    character_data.status_data[8] += now_add_lust
    character_data.status_data[8] = min(99999, character_data.status_data[8])
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_LUBRICATION)
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

    now_add_lust = 3000
    character_data.status_data.setdefault(8, 0)
    character_data.status_data[8] += now_add_lust
    character_data.status_data[8] = min(99999, character_data.status_data[8])
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_SMALL_HIT_POINT)
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

    base_chara_hp_mp_common_settle(character_id, 10, -1, degree=0, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_SMALL_MANA_POINT)
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

    base_chara_hp_mp_common_settle(character_id, 20, mp_value=-1, degree=0, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_MIDDLE_HIT_POINT)
def handle_down_middle_hit_point(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少中量体力
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    base_chara_hp_mp_common_settle(character_id, 20, -1, degree=1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_MIDDLE_MANA_POINT)
def handle_down_middle_mana_point(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少中量气力
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    base_chara_hp_mp_common_settle(character_id, 25, mp_value=-1, degree=1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_LARGE_HIT_POINT)
def handle_down_large_hit_point(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少大量体力
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    base_chara_hp_mp_common_settle(character_id, 30, -1, degree=2, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_LARGE_MANA_POINT)
def handle_down_large_mana_point(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少大量气力
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    base_chara_hp_mp_common_settle(character_id, 30, mp_value=-1, degree=2, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_S_FEEL)
def handle_add_small_s_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｎ快（S感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[0]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[0])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[0] += now_add_lust
    character_data.status_data[0] = min(99999, character_data.status_data[0])
    change_data.status_data.setdefault(0, 0)
    change_data.status_data[0] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_B_FEEL)
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
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[1])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[1] += now_add_lust
    character_data.status_data[1] = min(99999, character_data.status_data[1])
    change_data.status_data.setdefault(1, 0)
    change_data.status_data[1] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_C_FEEL)
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
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[2])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[2] += now_add_lust
    character_data.status_data[2] = min(99999, character_data.status_data[2])
    change_data.status_data.setdefault(2, 0)
    change_data.status_data[2] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_P_FEEL)
def handle_add_small_p_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加玩家少量射精值（P感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[0]

    now_add_lust = 100 + character_data.eja_point*0.4
    # adjust = attr_calculation.get_ability_adjust(character_data.ability[3])
    # now_add_lust *= adjust
    now_add_lust = int(now_add_lust)
    character_data.eja_point += now_add_lust
    change_data.eja_point += now_add_lust
    character_data.action_info.last_eaj_add_time = cache.game_time


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_V_FEEL)
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
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[4])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[4] += now_add_lust
    character_data.status_data[4] = min(99999, character_data.status_data[4])
    change_data.status_data.setdefault(4, 0)
    change_data.status_data[4] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_A_FEEL)
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
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[5])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[5] += now_add_lust
    character_data.status_data[5] = min(99999, character_data.status_data[5])
    change_data.status_data.setdefault(5, 0)
    change_data.status_data[5] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_U_FEEL)
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
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[6])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[6] += now_add_lust
    character_data.status_data[6] = min(99999, character_data.status_data[6])
    change_data.status_data.setdefault(6, 0)
    change_data.status_data[6] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_W_FEEL)
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
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[7])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[7] += now_add_lust
    character_data.status_data[7] = min(99999, character_data.status_data[7])
    change_data.status_data.setdefault(7, 0)
    change_data.status_data[7] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_M_FEEL)
def handle_add_small_m_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｍ快（M感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加少量口喉快感。
    """
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[character_id]
    # 读取当前口喉快感值
    now_lust = character_data.status_data[21]
    # 设定基础增加量
    now_add_lust = 20
    # 计算能力修正
    adjust = attr_calculation.get_ability_adjust(character_data.ability[100])
    now_add_lust *= adjust
    # 按当前快感值微调
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)
    # 增加快感并限制最大值
    character_data.status_data[21] += now_add_lust
    character_data.status_data[21] = min(99999, character_data.status_data[21])
    # 记录变更
    change_data.status_data.setdefault(21, 0)
    change_data.status_data[21] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_M_FEEL)
def handle_add_middle_m_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｍ快（M感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加中量口喉快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[21]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[100])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)
    character_data.status_data[21] += now_add_lust
    character_data.status_data[21] = min(99999, character_data.status_data[21])
    change_data.status_data.setdefault(21, 0)
    change_data.status_data[21] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_F_FEEL)
def handle_add_small_f_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｆ快（F感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加少量兽部快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[22]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[101])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)
    character_data.status_data[22] += now_add_lust
    character_data.status_data[22] = min(99999, character_data.status_data[22])
    change_data.status_data.setdefault(22, 0)
    change_data.status_data[22] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_F_FEEL)
def handle_add_middle_f_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｆ快（F感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加中量兽部快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[22]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[101])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)
    character_data.status_data[22] += now_add_lust
    character_data.status_data[22] = min(99999, character_data.status_data[22])
    change_data.status_data.setdefault(22, 0)
    change_data.status_data[22] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_H_FEEL)
def handle_add_small_h_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量Ｈ快（H感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加少量心理快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[23]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[102])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)
    character_data.status_data[23] += now_add_lust
    character_data.status_data[23] = min(99999, character_data.status_data[23])
    change_data.status_data.setdefault(23, 0)
    change_data.status_data[23] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_H_FEEL)
def handle_add_middle_h_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｈ快（H感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加中量心理快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[23]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[102])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)
    character_data.status_data[23] += now_add_lust
    character_data.status_data[23] = min(99999, character_data.status_data[23])
    change_data.status_data.setdefault(23, 0)
    change_data.status_data[23] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_LUBRICATION_PLUS)
def handle_add_small_lubrication_plus(
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

    now_lust = character_data.status_data[8]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[33])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[8] += now_add_lust
    character_data.status_data[8] = min(99999, character_data.status_data[8])
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_LEARN)
def handle_add_small_learn_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量习得（技巧补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[9]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[30])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[9] += now_add_lust
    character_data.status_data[9] = min(99999, character_data.status_data[9])
    change_data.status_data.setdefault(9, 0)
    change_data.status_data[9] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_RESPECT)
def handle_add_small_respect_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量恭顺（顺从补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[10]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[31])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[10] += now_add_lust
    character_data.status_data[10] = min(99999, character_data.status_data[10])
    change_data.status_data.setdefault(10, 0)
    change_data.status_data[10] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_FRIENDLY)
def handle_add_small_friendly(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量好意（亲密补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[11]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[32])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[11] += now_add_lust
    character_data.status_data[11] = min(99999, character_data.status_data[11])
    change_data.status_data.setdefault(11, 0)
    change_data.status_data[11] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_DESIRE)
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

    now_lust = character_data.status_data[12]
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[33])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[12] += now_add_lust
    character_data.status_data[12] = min(99999, character_data.status_data[12])
    change_data.status_data.setdefault(12, 0)
    change_data.status_data[12] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_HAPPY)
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

    now_lust = character_data.status_data[13]
    now_add_lust = 20
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[13])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[13] += now_add_lust
    character_data.status_data[13] = min(99999, character_data.status_data[13])
    change_data.status_data.setdefault(13, 0)
    change_data.status_data[13] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_LEAD)
def handle_add_small_lead(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量先导（施虐补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[14]
    now_add_lust = 20
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[35])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[14] += now_add_lust
    character_data.status_data[14] = min(99999, character_data.status_data[14])
    change_data.status_data.setdefault(14, 0)
    change_data.status_data[14] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_SUBMIT)
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

    now_lust = character_data.status_data[15]
    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[14])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[15] += now_add_lust
    character_data.status_data[15] = min(99999, character_data.status_data[15])
    change_data.status_data.setdefault(15, 0)
    change_data.status_data[15] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_SHY)
def handle_add_small_shy(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量羞耻（露出补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[16]
    now_add_lust = 20
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[34])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[16] += now_add_lust
    character_data.status_data[16] = min(99999, character_data.status_data[16])
    change_data.status_data.setdefault(16, 0)
    change_data.status_data[16] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_PAIN)
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

    now_lust = character_data.status_data[17]
    now_add_lust = 20
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[17] += now_add_lust
    character_data.status_data[17] = min(99999, character_data.status_data[17])
    change_data.status_data.setdefault(17, 0)
    change_data.status_data[17] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_TERROR)
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

    now_lust = character_data.status_data[18]
    now_add_lust = 20
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[17])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[18] += now_add_lust
    character_data.status_data[18] = min(99999, character_data.status_data[18])
    change_data.status_data.setdefault(18, 0)
    change_data.status_data[18] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_DEPRESSION)
def handle_add_small_depression(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量抑郁
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[19]
    now_add_lust = 20
    now_add_lust = int(now_add_lust)

    character_data.status_data[19] += now_add_lust
    character_data.status_data[19] = min(99999, character_data.status_data[19])
    change_data.status_data.setdefault(19, 0)
    change_data.status_data[19] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_DISGUST)
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

    base_chara_state_common_settle(character_id, 0, 20, 20, ability_level = character_data.ability[18], change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_N_FEEL)
def handle_add_middle_n_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｎ快（N感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[0]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[0])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[0] += now_add_lust
    character_data.status_data[0] = min(99999, character_data.status_data[0])
    change_data.status_data.setdefault(0, 0)
    change_data.status_data[0] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_B_FEEL)
def handle_add_middle_b_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｂ快（B感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[1]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[1])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[1] += now_add_lust
    character_data.status_data[1] = min(99999, character_data.status_data[1])
    change_data.status_data.setdefault(1, 0)
    change_data.status_data[1] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_C_FEEL)
def handle_add_middle_c_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｃ快（C感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[2]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[2])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[2] += now_add_lust
    character_data.status_data[2] = min(99999, character_data.status_data[2])
    change_data.status_data.setdefault(2, 0)
    change_data.status_data[2] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_P_FEEL)
def handle_add_middle_p_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量P快（P感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[3]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[3])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[3] += now_add_lust
    character_data.status_data[3] = min(99999, character_data.status_data[3])
    change_data.status_data.setdefault(3, 0)
    change_data.status_data[3] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_V_FEEL)
def handle_add_middle_v_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｖ快（V感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[4]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[4])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[4] += now_add_lust
    character_data.status_data[4] = min(99999, character_data.status_data[4])
    change_data.status_data.setdefault(4, 0)
    change_data.status_data[4] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_A_FEEL)
def handle_add_middle_a_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ａ快（A感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[5]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[5])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[5] += now_add_lust
    character_data.status_data[5] = min(99999, character_data.status_data[5])
    change_data.status_data.setdefault(5, 0)
    change_data.status_data[5] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_U_FEEL)
def handle_add_middle_u_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｕ快（U感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[6]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[6])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[6] += now_add_lust
    character_data.status_data[6] = min(99999, character_data.status_data[6])
    change_data.status_data.setdefault(6, 0)
    change_data.status_data[6] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_W_FEEL)
def handle_add_middle_w_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量Ｗ快（W感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[7]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[7])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[7] += now_add_lust
    character_data.status_data[7] = min(99999, character_data.status_data[7])
    change_data.status_data.setdefault(7, 0)
    change_data.status_data[7] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_LUBRICATION_PLUS)
def handle_add_middle_lubrication_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量润滑（欲望补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[8]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[33])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[8] += now_add_lust
    character_data.status_data[8] = min(99999, character_data.status_data[8])
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_LEARN)
def handle_add_middle_learn_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量习得（技巧补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[9]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[30])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[9] += now_add_lust
    character_data.status_data[9] = min(99999, character_data.status_data[9])
    change_data.status_data.setdefault(9, 0)
    change_data.status_data[9] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_RESPECT)
def handle_add_middle_respect_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量恭顺（顺从补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[10]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[31])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[10] += now_add_lust
    character_data.status_data[10] = min(99999, character_data.status_data[10])
    change_data.status_data.setdefault(10, 0)
    change_data.status_data[10] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_FRIENDLY)
def handle_add_middle_friendly(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量好意（亲密补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[11]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[32])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[11] += now_add_lust
    character_data.status_data[11] = min(99999, character_data.status_data[11])
    change_data.status_data.setdefault(11, 0)
    change_data.status_data[11] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_DESIRE)
def handle_add_middle_desire(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量欲情（欲望补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[12]
    now_add_lust = 100
    adjust = attr_calculation.get_ability_adjust(character_data.ability[33])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[12] += now_add_lust
    character_data.status_data[12] = min(99999, character_data.status_data[12])
    change_data.status_data.setdefault(12, 0)
    change_data.status_data[12] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_HAPPY)
def handle_add_middle_happy(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量快乐（快乐刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[13]
    now_add_lust = 100
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[13])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[13] += now_add_lust
    character_data.status_data[13] = min(99999, character_data.status_data[13])
    change_data.status_data.setdefault(13, 0)
    change_data.status_data[13] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_LEAD)
def handle_add_middle_lead(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量先导（施虐补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[14]
    now_add_lust = 100
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[35])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[14] += now_add_lust
    character_data.status_data[14] = min(99999, character_data.status_data[14])
    change_data.status_data.setdefault(14, 0)
    change_data.status_data[14] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_SUBMIT)
def handle_add_middle_submit(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量屈服（屈服刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[15]
    now_add_lust = 5000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[14])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[15] += now_add_lust
    character_data.status_data[15] = min(99999, character_data.status_data[15])
    change_data.status_data.setdefault(15, 0)
    change_data.status_data[15] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_SHY)
def handle_add_middle_shy(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量羞耻（露出补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[16]
    now_add_lust = 100
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[34])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[16] += now_add_lust
    character_data.status_data[16] = min(99999, character_data.status_data[16])
    change_data.status_data.setdefault(16, 0)
    change_data.status_data[16] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_PAIN)
def handle_add_middle_pain(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量苦痛（苦痛刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[17]
    now_add_lust = 100
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[17] += now_add_lust
    character_data.status_data[17] = min(99999, character_data.status_data[17])
    change_data.status_data.setdefault(17, 0)
    change_data.status_data[17] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_TERROR)
def handle_add_middle_terror(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量恐怖（恐怖刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[18]
    now_add_lust = 100
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[17])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[18] += now_add_lust
    character_data.status_data[18] = min(99999, character_data.status_data[18])
    change_data.status_data.setdefault(18, 0)
    change_data.status_data[18] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_DEPRESSION)
def handle_add_middle_depression(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量抑郁
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[19]
    now_add_lust = 100

    character_data.status_data[19] += now_add_lust
    character_data.status_data[19] = min(99999, character_data.status_data[19])
    change_data.status_data.setdefault(19, 0)
    change_data.status_data[19] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MIDDLE_DISGUST)
def handle_add_middle_disgust(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加中量反感（反发刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    base_chara_state_common_settle(character_id, 0, 20, 100, ability_level = character_data.ability[18], change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_N_FEEL)
def handle_add_large_n_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｎ快（N感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[0]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[0])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[0] += now_add_lust
    character_data.status_data[0] = min(99999, character_data.status_data[0])
    change_data.status_data.setdefault(0, 0)
    change_data.status_data[0] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_B_FEEL)
def handle_add_large_b_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｂ快（B感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[1]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[1])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[1] += now_add_lust
    character_data.status_data[1] = min(99999, character_data.status_data[1])
    change_data.status_data.setdefault(1, 0)
    change_data.status_data[1] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_C_FEEL)
def handle_add_large_c_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｃ快（C感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[2]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[2])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[2] += now_add_lust
    character_data.status_data[2] = min(99999, character_data.status_data[2])
    change_data.status_data.setdefault(2, 0)
    change_data.status_data[2] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_P_FEEL)
def handle_add_large_p_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量P快（P感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[3]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[3])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[3] += now_add_lust
    character_data.status_data[3] = min(99999, character_data.status_data[3])
    change_data.status_data.setdefault(3, 0)
    change_data.status_data[3] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_V_FEEL)
def handle_add_large_v_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｖ快（V感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[4]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[4])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[4] += now_add_lust
    character_data.status_data[4] = min(99999, character_data.status_data[4])
    change_data.status_data.setdefault(4, 0)
    change_data.status_data[4] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_A_FEEL)
def handle_add_large_a_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ａ快（A感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[5]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[5])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[5] += now_add_lust
    character_data.status_data[5] = min(99999, character_data.status_data[5])
    change_data.status_data.setdefault(5, 0)
    change_data.status_data[5] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_U_FEEL)
def handle_add_large_u_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｕ快（U感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[6]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[6])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[6] += now_add_lust
    character_data.status_data[6] = min(99999, character_data.status_data[6])
    change_data.status_data.setdefault(6, 0)
    change_data.status_data[6] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_W_FEEL)
def handle_add_large_w_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｗ快（W感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_lust = character_data.status_data[7]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[7])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)

    character_data.status_data[7] += now_add_lust
    character_data.status_data[7] = min(99999, character_data.status_data[7])
    change_data.status_data.setdefault(7, 0)
    change_data.status_data[7] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_M_FEEL)
def handle_add_large_m_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｍ快（M感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加大量口喉快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[21]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[100])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)
    character_data.status_data[21] += now_add_lust
    character_data.status_data[21] = min(99999, character_data.status_data[21])
    change_data.status_data.setdefault(21, 0)
    change_data.status_data[21] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_F_FEEL)
def handle_add_large_f_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｆ快（F感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加大量兽部快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[22]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[101])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)
    character_data.status_data[22] += now_add_lust
    character_data.status_data[22] = min(99999, character_data.status_data[22])
    change_data.status_data.setdefault(22, 0)
    change_data.status_data[22] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_H_FEEL)
def handle_add_large_h_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量Ｈ快（H感补正）
    参数：
        character_id (int): 角色id
        change_data (game_type.CharacterStatusChange): 状态变更信息记录对象
    返回值：
        None
    功能描述：为角色增加大量心理快感。
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_lust = character_data.status_data[23]
    now_add_lust = 200
    adjust = attr_calculation.get_ability_adjust(character_data.ability[102])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10
    now_add_lust = int(now_add_lust)
    character_data.status_data[23] += now_add_lust
    character_data.status_data[23] = min(99999, character_data.status_data[23])
    change_data.status_data.setdefault(23, 0)
    change_data.status_data[23] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_LUBRICATION_PLUS)
def handle_add_large_lubrication_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量润滑（欲望补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_ability_adjust(character_data.ability[33])
    now_add_lust *= adjust

    character_data.status_data[8] += now_add_lust
    character_data.status_data[8] = min(99999, character_data.status_data[8])
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_LEARN)
def handle_add_large_learn_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量习得（技巧补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_ability_adjust(character_data.ability[30])
    now_add_lust *= adjust

    character_data.status_data[9] += now_add_lust
    character_data.status_data[9] = min(99999, character_data.status_data[9])
    change_data.status_data.setdefault(9, 0)
    change_data.status_data[9] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_RESPECT)
def handle_add_large_respect_plus(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量恭顺（顺从补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_ability_adjust(character_data.ability[31])
    now_add_lust *= adjust

    character_data.status_data[10] += now_add_lust
    character_data.status_data[10] = min(99999, character_data.status_data[10])
    change_data.status_data.setdefault(10, 0)
    change_data.status_data[10] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_FRIENDLY)
def handle_add_large_friendly(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量好意（亲密补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_ability_adjust(character_data.ability[32])
    now_add_lust *= adjust

    character_data.status_data[11] += now_add_lust
    character_data.status_data[11] = min(99999, character_data.status_data[11])
    change_data.status_data.setdefault(11, 0)
    change_data.status_data[11] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_DESIRE)
def handle_add_large_desire(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量欲情（欲望补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_ability_adjust(character_data.ability[33])
    now_add_lust *= adjust

    character_data.status_data[12] += now_add_lust
    character_data.status_data[12] = min(99999, character_data.status_data[12])
    change_data.status_data.setdefault(12, 0)
    change_data.status_data[12] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_HAPPY)
def handle_add_large_happy(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量快乐（快乐刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[13])
    now_add_lust *= adjust

    character_data.status_data[13] += now_add_lust
    character_data.status_data[13] = min(99999, character_data.status_data[13])
    change_data.status_data.setdefault(13, 0)
    change_data.status_data[13] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_LEAD)
def handle_add_large_lead(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量先导（受虐补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[25])
    now_add_lust *= adjust

    character_data.status_data[14] += now_add_lust
    character_data.status_data[14] = min(99999, character_data.status_data[14])
    change_data.status_data.setdefault(14, 0)
    change_data.status_data[14] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_SUBMIT)
def handle_add_large_submit(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量屈服（屈服刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 10000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[14])
    now_add_lust *= adjust

    character_data.status_data[15] += now_add_lust
    character_data.status_data[15] = min(99999, character_data.status_data[15])
    change_data.status_data.setdefault(15, 0)
    change_data.status_data[15] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_SHY)
def handle_add_large_shy(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量羞耻（露出补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[34])
    now_add_lust *= adjust

    character_data.status_data[16] += now_add_lust
    character_data.status_data[16] = min(99999, character_data.status_data[16])
    change_data.status_data.setdefault(16, 0)
    change_data.status_data[16] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_PAIN)
def handle_add_large_pain(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量苦痛（苦痛刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
    now_add_lust *= adjust

    character_data.status_data[17] += now_add_lust
    character_data.status_data[17] = min(99999, character_data.status_data[17])
    change_data.status_data.setdefault(17, 0)
    change_data.status_data[17] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_TERROR)
def handle_add_large_terror(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量恐怖（恐怖刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[17])
    now_add_lust *= adjust

    character_data.status_data[18] += now_add_lust
    character_data.status_data[18] = min(99999, character_data.status_data[18])
    change_data.status_data.setdefault(18, 0)
    change_data.status_data[18] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_DEPRESSION)
def handle_add_large_depression(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量抑郁
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000

    character_data.status_data[19] += now_add_lust
    character_data.status_data[19] = min(99999, character_data.status_data[19])
    change_data.status_data.setdefault(19, 0)
    change_data.status_data[19] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_DISGUST)
def handle_add_large_disgust(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加大量反感（反发刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[18])
    now_add_lust *= adjust

    character_data.status_data[20] += now_add_lust
    character_data.status_data[20] = min(99999, character_data.status_data[20])
    change_data.status_data.setdefault(20, 0)
    change_data.status_data[20] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_SMALL_PAIN)
def handle_down_small_pain(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少少量苦痛（苦痛刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]
    now_add_lust = -50 - character_data.status_data[17] / 10
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 17, base_value = 0, ability_level = character_data.ability[15], tenths_add = False, change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_SMALL_DISGUST)
def handle_down_small_disgust(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少少量反感（反发刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]
    now_add_lust = -50 - character_data.status_data[20] / 10
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 20, base_value = 0, ability_level = character_data.ability[18], tenths_add = False, change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_MIDDLE_PAIN)
def handle_down_middle_pain(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少中量苦痛（苦痛刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_add_lust = -500 - character_data.status_data[17] / 5
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 17, base_value = 0, ability_level = character_data.ability[15], tenths_add = False, change_data = change_data)



@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_MIDDLE_DISGUST)
def handle_down_middle_disgust(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少中量反感（反发刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_add_lust = -500 - character_data.status_data[20] / 5
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 20, base_value = 0, ability_level = character_data.ability[18], tenths_add = False, change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_LARGE_PAIN)
def handle_down_large_pain(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少大量苦痛（苦痛刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_add_lust = -2000 - character_data.status_data[17] / 3
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 17, base_value = 0, ability_level = character_data.ability[15], tenths_add = False, change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.DOWN_LARGE_DISGUST)
def handle_down_large_disgust(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    减少大量反感（反发刻印补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_add_lust = -2000 - character_data.status_data[20] / 3
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 20, base_value = 0, ability_level = character_data.ability[18], tenths_add = False, change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_PAIN_FIRST_SEX)
def handle_add_large_pain_first_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加巨量苦痛（破处修正）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 4000
    # 润滑修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[8])
    now_add_lust *= adjust
    # print("润滑修正", now_add_lust)
    # 欲情修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[12])
    adjust = adjust/3 if adjust >=2 else adjust/2
    now_add_lust *= adjust
    # print("欲情修正", now_add_lust)
    # V扩张修正
    adjust = attr_calculation.get_ability_adjust(character_data.ability[9])
    now_add_lust /= adjust * adjust
    # print("V扩张修正", now_add_lust)
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 17, base_value = 0, ability_level = character_data.ability[15], tenths_add = False, change_data = change_data)
    # print("破处修正", now_add_lust)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_PAIN_FIRST_A_SEX)
def handle_add_large_pain_first_a_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加巨量苦痛（A破处修正）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 2000
    # 润滑修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[8])
    now_add_lust *= adjust
    # 欲情修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[12])
    adjust = adjust/3 if adjust >=2 else adjust/2
    now_add_lust *= adjust
    # A扩张修正
    adjust = attr_calculation.get_ability_adjust(character_data.ability[10])
    now_add_lust /= adjust * adjust
    now_add_lust = int(now_add_lust)

    base_chara_state_common_settle(character_id, now_add_lust, 17, base_value = 0, ability_level = character_data.ability[15], tenths_add = False, change_data = change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_URINATE)
def handle_add_urinate(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加尿意（持续性利尿剂）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    if character_data.h_state.body_item[8][1]:
        if character_data.urinate_point >= 30:
            character_data.urinate_point = 240


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SLEEP_POINT)
def handle_add_sleep_point(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    维持熟睡值（安眠药）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    if handle_premise.handle_self_sleep_pills(character_id):
        character_data.sleep_point = 100
        character_data.tired_point = max(10, character_data.tired_point)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.MILKING_MACHINE)
def handle_milking_machine(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    角色的奶量转化为乳汁（搾乳机）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    if character_data.dead:
        return

    if character_data.h_state.body_item[4][1]:

        now_milk = 5 * character_data.behavior.duration
        now_milk = min(character_data.pregnancy.milk, now_milk)
        cache.rhodes_island.milk_in_fridge.setdefault(character_id, 0)
        cache.rhodes_island.milk_in_fridge[character_id] += now_milk
        pl_character_data.pl_collection.milk_total.setdefault(character_id, 0)
        pl_character_data.pl_collection.milk_total[character_id] += now_milk
        character_data.pregnancy.milk -= now_milk
        character_data.behavior.milk_ml += now_milk

        # 绘制信息
        if now_milk:
            now_draw = draw.NormalDraw()
            now_text = _("\n{0}被搾乳机榨出了{1}ml的乳汁\n").format(character_data.name, now_milk)
            now_draw.text = now_text
            now_draw.width = window_width
            now_draw.draw()

    """
    # 没有乳汁时停止榨乳
    # 去掉了该功能，在H结束前会一直榨乳
    if character_data.pregnancy.milk <= 0:
        character_data.pregnancy.milk = 0
        character_data.h_state.body_item[4][1] = 0
        character_data.second_behavior[1104] = 0
        # 绘制信息
        now_draw = draw.NormalDraw()
        now_text = f"{character_data.name}已经没有乳汁了，所以取下了搾乳机。\n"
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()
    """


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.URINE_COLLECTOR)
def handle_urine_collector(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    角色的尿液转化为圣水（采尿器）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    if character_data.dead:
        return

    if character_data.h_state.body_item[5][1]:

        now_urine = 5 * character_data.behavior.duration
        now_urine = min(character_data.urinate_point, now_urine)
        cache.rhodes_island.urine_in_fridge.setdefault(character_id, 0)
        cache.rhodes_island.urine_in_fridge[character_id] += now_urine
        pl_character_data.pl_collection.urine_total.setdefault(character_id, 0)
        pl_character_data.pl_collection.urine_total[character_id] += now_urine
        character_data.urinate_point -= now_urine
        character_data.behavior.urine_ml += now_urine

        # 绘制信息
        if now_urine:
            now_draw = draw.NormalDraw()
            now_text = _("\n{0}被采尿器吸出了{1}ml的圣水\n").format(character_data.name, now_urine)
            now_draw.text = now_text
            now_draw.width = window_width
            now_draw.draw()


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.B_ORGASM_TO_MILK)
def handle_b_orgasm_to_milk(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因B绝顶而被迫喷乳
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    if character_data.dead:
        return

    # 额外增加乳汁
    add_milk = int(character_data.pregnancy.milk_max * 0.2)
    character_data.pregnancy.milk += add_milk
    # 喷乳至回到最大值的40%，其余的喷出
    eject_milk = int(character_data.pregnancy.milk - character_data.pregnancy.milk_max * 0.4)
    if eject_milk > 0:
        character_data.pregnancy.milk = int(character_data.pregnancy.milk_max * 0.4)
        character_data.behavior.milk_ml += eject_milk

        # 如果已经装上搾乳机了，则收集至搾乳机中
        if character_data.h_state.body_item[4][1]:
            cache.rhodes_island.milk_in_fridge.setdefault(character_id, 0)
            cache.rhodes_island.milk_in_fridge[character_id] += eject_milk
            pl_character_data.pl_collection.milk_total.setdefault(character_id, 0)
            pl_character_data.pl_collection.milk_total[character_id] += eject_milk
            now_text = _("\n{0}在绝顶的同时喷出了{1}ml的乳汁，喷出的乳汁被收集到搾乳机中\n").format(character_data.name, eject_milk)
        # 否则普通的喷出
        else:
            now_text = _("\n{0}在绝顶的同时喷出了{1}ml的乳汁，喷出的乳汁散落的到处都是\n").format(character_data.name, eject_milk)

        # 绘制信息
        now_draw = draw.NormalDraw()
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.U_ORGASM_TO_PEE)
def handle_u_orgasm_to_pee(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因U绝顶而被迫漏尿
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    if character_data.dead:
        return

    # 额外增加尿意
    add_urine = int(240 * 0.2)
    character_data.urinate_point += add_urine
    # 喷至回到最大值的40%，其余的喷出
    eject_urine = int(character_data.urinate_point - 240 * 0.4)
    if eject_urine > 0:
        character_data.urinate_point = int(240 * 0.4)

        # 如果已经装上采尿器了，则收集至采尿器中
        if character_data.h_state.body_item[5][1]:
            cache.rhodes_island.urine_in_fridge.setdefault(character_id, 0)
            cache.rhodes_island.urine_in_fridge[character_id] += eject_urine
            pl_character_data.pl_collection.urine_total.setdefault(character_id, 0)
            pl_character_data.pl_collection.urine_total[character_id] += eject_urine
            now_text = _("\n{0}在绝顶的同时漏出了{1}ml的尿液，漏出的尿液被收集到采尿器中\n").format(character_data.name, eject_urine)
        # 否则普通的喷出
        else:
            now_text = _("\n{0}在绝顶的同时漏出了{1}ml的尿液，漏出的尿液在地上汇成一滩\n").format(character_data.name, eject_urine)

        # 绘制信息
        now_draw = draw.NormalDraw()
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.EXTRA_ORGASM)
def handle_extra_orgasm(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算额外绝顶(痛苦+恐怖)
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    # 额外高潮次数
    all_extra_count = character_data.h_state.extra_orgasm_count
    # 如果有额外高潮次数，则进行苦痛和恐怖结算
    if all_extra_count > 0:
        # 额外高潮次数的苦痛和恐怖
        extra_pain = 100 * (1.2 ** all_extra_count)
        extra_terror = 100 * (1.2 ** all_extra_count)
        # 痛苦刻印修正
        adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
        extra_pain *= adjust
        extra_pain = int(extra_pain)
        # 恐怖刻印修正
        adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[17])
        extra_terror *= adjust
        extra_terror = int(extra_terror)
        # 结算苦痛和恐怖
        character_data.status_data[17] += extra_pain
        character_data.status_data[17] = min(99999, character_data.status_data[17])
        change_data.status_data.setdefault(17, 0)
        change_data.status_data[17] += extra_pain
        character_data.status_data[18] += extra_terror
        character_data.status_data[18] = min(99999, character_data.status_data[18])
        change_data.status_data.setdefault(18, 0)
        change_data.status_data[18] += extra_terror
        # 绘制信息
        now_draw = draw.NormalDraw()
        now_text = _("\n{0}因为第{1}次的连续额外绝顶而被迫感受到了更多的苦痛和恐怖\n").format(character_data.name, all_extra_count)
        now_draw.text = now_text
        now_draw.width = window_width
        now_draw.draw()
        # 额外高潮次数清零
        character_data.h_state.extra_orgasm_count = 0


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.PLURAL_ORGASM)
def handle_plural_orgasm(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算多重绝顶(快乐+屈服)
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    from Script.Settle.default import base_chara_state_common_settle
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    # 多重高潮次数
    plural_orgasm_count = len(character_data.h_state.plural_orgasm_set) - 1
    # 如果有多重高潮次数，则进行结算
    if plural_orgasm_count > 0:
        base_value = 1000 * plural_orgasm_count
        extral_adjust = 1.4 ** plural_orgasm_count
        base_chara_state_common_settle(character_id, 0, 13, base_value = base_value, extra_adjust = extral_adjust, change_data = change_data)
        base_chara_state_common_settle(character_id, 0, 15, base_value = base_value, extra_adjust = extral_adjust, change_data = change_data)

        # 多重绝顶数据清零
        character_data.h_state.plural_orgasm_set = set()


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.BONDAGE_EFFECT)
def handle_bondage_effect(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算绳子捆绑效果(已弃用)
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    # 需要在捆绑中
    if handle_premise.handle_self_not_bondage(character_id):
        return

    # 因为character_data.behavior.duration的数值为0，所以改为在Script\Design\character_behavior.py的character_aotu_change_value中进行结算
    # bondage_id = character_data.h_state.bondage
    # bondage_data = game_config.config_bondage[bondage_id]
    # # 根据程度计算系数
    # bondage_adjust = bondage_data.level * 0.5
    # # 欲情
    # base_chara_state_common_settle(character_id, add_time=character_data.behavior.duration, state_id=12, base_value=0, ability_level=character_data.ability[33], extra_adjust=bondage_adjust, tenths_add=False)
    # # 苦痛
    # base_chara_state_common_settle(character_id, add_time=character_data.behavior.duration, state_id=17, base_value=0, ability_level=character_data.ability[15], extra_adjust=bondage_adjust, tenths_add=False)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.EXPOSED_ORGASM_SMALL_IN_HIDDEN_SEX)
def handle_exposed_orgasm_small_in_hidden_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因隐奸中的小绝顶而导致的暴露
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在隐奸中则返回
    if handle_premise.handle_hidden_sex_mode_0(character_id):
        return
    from Script.UI.Panel import hidden_sex_panel
    hidden_sex_panel.handle_hidden_sex_flow(character_id = 0, add_flag = True, now_duration = 5, now_intensity = 2)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.EXPOSED_ORGASM_NORMAL_IN_HIDDEN_SEX)
def handle_exposed_orgasm_normal_in_hidden_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因隐奸中的普绝顶而导致的暴露
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在隐奸中则返回
    if handle_premise.handle_hidden_sex_mode_0(character_id):
        return
    from Script.UI.Panel import hidden_sex_panel
    hidden_sex_panel.handle_hidden_sex_flow(character_id = 0, add_flag = True, now_duration = 6, now_intensity = 3)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.EXPOSED_ORGASM_STRONG_IN_HIDDEN_SEX)
def handle_exposed_orgasm_strong_in_hidden_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因隐奸中的强绝顶而导致的暴露
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在隐奸中则返回
    if handle_premise.handle_hidden_sex_mode_0(character_id):
        return
    from Script.UI.Panel import hidden_sex_panel
    hidden_sex_panel.handle_hidden_sex_flow(character_id = 0, add_flag = True, now_duration = 7, now_intensity = 4)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.EXPOSED_ORGASM_SUPER_IN_HIDDEN_SEX)
def handle_exposed_orgasm_super_in_hidden_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因隐奸中的超强绝顶而导致的暴露
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在隐奸中则返回
    if handle_premise.handle_hidden_sex_mode_0(character_id):
        return
    from Script.UI.Panel import hidden_sex_panel
    hidden_sex_panel.handle_hidden_sex_flow(character_id = 0, add_flag = True, now_duration = 10, now_intensity = 5)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.STORE_SMALL_ORGASM_CHARGE)
def handle_store_small_orgasm_charge(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因小绝顶而获得的电量
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在人力发电室中则返回
    if handle_premise.handle_not_in_human_power_room(character_id):
        return
    from Script.UI.Panel.manage_power_system_panel import store_power_by_human_power
    draw_flag = False
    # 如果和玩家在同一位置，则进行显示
    if handle_premise.handle_in_player_scene(character_id):
        draw_flag = True
    store_power_by_human_power(1, character_id, draw_flag)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.STORE_NORMAL_ORGASM_CHARGE)
def handle_store_normal_orgasm_charge(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因普绝顶而获得的电量
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在人力发电室中则返回
    if handle_premise.handle_not_in_human_power_room(character_id):
        return
    from Script.UI.Panel.manage_power_system_panel import store_power_by_human_power
    draw_flag = False
    # 如果和玩家在同一位置，则进行显示
    if handle_premise.handle_in_player_scene(character_id):
        draw_flag = True
    store_power_by_human_power(2, character_id, draw_flag)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.STORE_STRONG_ORGASM_CHARGE)
def handle_store_strong_orgasm_charge(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因强绝顶而获得的电量
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在人力发电室中则返回
    if handle_premise.handle_not_in_human_power_room(character_id):
        return
    from Script.UI.Panel.manage_power_system_panel import store_power_by_human_power
    draw_flag = False
    # 如果和玩家在同一位置，则进行显示
    if handle_premise.handle_in_player_scene(character_id):
        draw_flag = True
    store_power_by_human_power(3, character_id, draw_flag)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.STORE_SUPER_ORGASM_CHARGE)
def handle_store_super_orgasm_charge(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    结算因超强绝顶而获得的电量
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 不在人力发电室中则返回
    if handle_premise.handle_not_in_human_power_room(character_id):
        return
    from Script.UI.Panel.manage_power_system_panel import store_power_by_human_power
    draw_flag = False
    # 如果和玩家在同一位置，则进行显示
    if handle_premise.handle_in_player_scene(character_id):
        draw_flag = True
    store_power_by_human_power(4, character_id, draw_flag)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.PENIS_IN_T_RESET)
def handle_penis_in_t_reset(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    当前阴茎位置为交互对象_双方归零
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.h_state.insert_position = -1
    character_data.h_state.insert_position = -1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.GIVE_PAN_IN_DAY_FIRST_MEET)
def handle_give_pan_in_day_first_meet(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    在每日招呼时上交今天的内裤
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    from Script.Design import clothing
    # 转移到玩家的临时收藏
    clothing.pl_get_chara_pan(character_id)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.GIVE_SOCKS_IN_DAY_FIRST_MEET)
def handle_give_socks_in_day_first_meet(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    在每日招呼时上交今天的袜子
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    from Script.Design import clothing
    # 转移到玩家的临时收藏
    clothing.pl_get_chara_socks(character_id)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_SEX_V_EXPERIENCE)
def handle_add_1_sex_v_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1V性交经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 61, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_SEX_A_EXPERIENCE)
def handle_add_1_sex_a_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1A性交经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 62, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_SEX_U_EXPERIENCE)
def handle_add_1_sex_u_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1U性交经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 63, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_SEX_W_EXPERIENCE)
def handle_add_1_sex_w_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1W性交经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 64, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_EXPAND_V_EXPERIENCE)
def handle_add_1_expand_v_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1V扩张经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 65, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_EXPAND_A_EXPERIENCE)
def handle_add_1_expand_a_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1A扩张经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 66, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_EXPAND_U_EXPERIENCE)
def handle_add_1_expand_u_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1U扩张经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 67, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_EXPAND_W_EXPERIENCE)
def handle_add_1_expand_w_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1W扩张经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 68, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_N_EXPERIENCE)
def handle_add_1_n_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1N经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 0, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_B_EXPERIENCE)
def handle_add_1_b_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1B经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 1, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_C_EXPERIENCE)
def handle_add_1_c_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1C经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 2, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_P_EXPERIENCE)
def handle_add_1_p_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1P经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 3, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_V_EXPERIENCE)
def handle_add_1_v_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1V经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 4, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_A_EXPERIENCE)
def handle_add_1_a_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1A经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 5, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_U_EXPERIENCE)
def handle_add_1_u_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1U经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 6, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_W_EXPERIENCE)
def handle_add_1_w_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1W经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 7, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_MClimax_EXPERIENCE)
def handle_add_1_mclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1M绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    base_chara_experience_common_settle(character_id, 156, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[21][0] += 1
        character_data.h_state.orgasm_count[21][1] += 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_FClimax_EXPERIENCE)
def handle_add_1_fclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1F绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    base_chara_experience_common_settle(character_id, 157, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[22][0] += 1
        character_data.h_state.orgasm_count[22][1] += 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_HClimax_EXPERIENCE)
def handle_add_1_hclimax_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加1H绝顶经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    base_chara_experience_common_settle(character_id, 158, 1, change_data=change_data)
    base_chara_experience_common_settle(character_id, 20, 1, change_data=change_data)
    if character_data.sp_flag.is_h == 1:
        character_data.h_state.orgasm_count[23][0] += 1
        character_data.h_state.orgasm_count[23][1] += 1


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_M_EXPERIENCE)
def handle_add_1_m_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1M经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 153, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_F_EXPERIENCE)
def handle_add_1_f_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1F经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 154, 1, change_data=change_data)


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_H_EXPERIENCE)
def handle_add_1_h_experience(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    自己增加1H经验
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    base_chara_experience_common_settle(character_id, 155, 1, change_data=change_data)

