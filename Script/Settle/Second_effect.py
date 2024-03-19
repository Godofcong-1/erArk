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
from Script.Core import cache_control, constant, constant_effect, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw


_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


# @settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.N_orgasm_small)
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


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_1_NClimax_EXPERIENCE)
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
    character_data.experience.setdefault(11, 0)
    character_data.experience[11] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(11, 0)
    change_data.experience[11] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
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
    character_data.experience.setdefault(12, 0)
    character_data.experience[12] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(12, 0)
    change_data.experience[12] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
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
    character_data.experience.setdefault(14, 0)
    character_data.experience[14] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(14, 0)
    change_data.experience[14] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
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
    character_data.experience.setdefault(15, 0)
    character_data.experience[15] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(15, 0)
    change_data.experience[15] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
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
    character_data.experience.setdefault(16, 0)
    character_data.experience[16] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(16, 0)
    change_data.experience[16] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
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
    character_data.experience.setdefault(17, 0)
    character_data.experience[17] += 1
    character_data.experience.setdefault(20, 0)
    character_data.experience[20] += 1
    change_data.experience.setdefault(17, 0)
    change_data.experience[17] += 1
    change_data.experience.setdefault(20, 0)
    change_data.experience[20] += 1
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
    character_data.experience.setdefault(21, 0)
    character_data.experience[21] += 1
    change_data.experience.setdefault(21, 0)
    change_data.experience[21] += 1
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
    character_data.experience.setdefault(22, 0)
    character_data.experience[22] += 1
    change_data.experience.setdefault(22, 0)
    change_data.experience[22] += 1

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
    character_data.experience.setdefault(23, 0)
    character_data.experience[23] += 1
    change_data.experience.setdefault(23, 0)
    change_data.experience[23] += 1


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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_data.experience.setdefault(24, 0)
    target_data.experience[24] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(24, 0)
    target_change.experience[24] += 1


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
    sub_hit = 20
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
        if not character_data.sp_flag.tired:
            character_data.sp_flag.tired = 1
            # 如果和玩家位于同一地点，则输出提示信息
            if character_data.position == cache.character_data[0].position:
                now_draw = draw.NormalDraw()
                now_draw.width = window_width
                now_draw.text = "\n" + character_data.name + "太累了\n"
                now_draw.draw()


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

    sub_mana = 40
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
            if not character_data.sp_flag.tired:
                character_data.sp_flag.tired = 1
                # 如果和玩家位于同一地点，则输出提示信息
                if character_data.position == cache.character_data[0].position:
                    now_draw = draw.NormalDraw()
                    now_draw.width = window_width
                    now_draw.text = "\n" + character_data.name + "太累了\n"
                    now_draw.draw()


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_N_FEEL)
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
    now_add_lust = 20
    adjust = attr_calculation.get_ability_adjust(character_data.ability[0])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20

    character_data.status_data[0] += now_add_lust
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

    character_data.status_data[1] += now_add_lust
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

    character_data.status_data[2] += now_add_lust
    change_data.status_data.setdefault(2, 0)
    change_data.status_data[2] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_SMALL_P_FEEL)
def handle_add_small_p_feel(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加少量射精值（P感补正）
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

    character_data.status_data[4] += now_add_lust
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

    character_data.status_data[5] += now_add_lust
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

    character_data.status_data[6] += now_add_lust
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

    character_data.status_data[7] += now_add_lust
    change_data.status_data.setdefault(7, 0)
    change_data.status_data[7] += now_add_lust


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

    character_data.status_data[8] += now_add_lust
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

    character_data.status_data[9] += now_add_lust
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

    character_data.status_data[10] += now_add_lust
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

    character_data.status_data[11] += now_add_lust
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

    character_data.status_data[12] += now_add_lust
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

    character_data.status_data[13] += now_add_lust
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

    character_data.status_data[14] += now_add_lust
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
    now_add_lust = 20
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[14])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20

    character_data.status_data[15] += now_add_lust
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

    character_data.status_data[16] += now_add_lust
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

    character_data.status_data[17] += now_add_lust
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

    character_data.status_data[18] += now_add_lust
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

    character_data.status_data[19] += now_add_lust
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

    now_lust = character_data.status_data[20]
    now_add_lust = 20
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[18])
    now_add_lust *= adjust
    now_add_lust += now_lust / 20

    character_data.status_data[20] += now_add_lust
    change_data.status_data.setdefault(20, 0)
    change_data.status_data[20] += now_add_lust


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

    character_data.status_data[0] += now_add_lust
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

    character_data.status_data[1] += now_add_lust
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

    character_data.status_data[2] += now_add_lust
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

    character_data.status_data[3] += now_add_lust
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

    character_data.status_data[4] += now_add_lust
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

    character_data.status_data[5] += now_add_lust
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

    character_data.status_data[6] += now_add_lust
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

    character_data.status_data[7] += now_add_lust
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

    character_data.status_data[8] += now_add_lust
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

    character_data.status_data[9] += now_add_lust
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

    character_data.status_data[10] += now_add_lust
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

    character_data.status_data[11] += now_add_lust
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

    character_data.status_data[12] += now_add_lust
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

    character_data.status_data[13] += now_add_lust
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

    character_data.status_data[14] += now_add_lust
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
    now_add_lust = 100
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[14])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10

    character_data.status_data[15] += now_add_lust
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

    character_data.status_data[16] += now_add_lust
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

    character_data.status_data[17] += now_add_lust
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

    character_data.status_data[18] += now_add_lust
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

    now_lust = character_data.status_data[20]
    now_add_lust = 100
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[18])
    now_add_lust *= adjust
    now_add_lust += now_lust / 10

    character_data.status_data[20] += now_add_lust
    change_data.status_data.setdefault(20, 0)
    change_data.status_data[20] += now_add_lust


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

    character_data.status_data[0] += now_add_lust
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

    character_data.status_data[1] += now_add_lust
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

    character_data.status_data[2] += now_add_lust
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

    character_data.status_data[3] += now_add_lust
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

    character_data.status_data[4] += now_add_lust
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

    character_data.status_data[5] += now_add_lust
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

    character_data.status_data[6] += now_add_lust
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

    character_data.status_data[7] += now_add_lust
    change_data.status_data.setdefault(7, 0)
    change_data.status_data[7] += now_add_lust


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
    change_data.status_data.setdefault(8, 0)
    change_data.status_data[8] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_LEARN)
def handle_add_middle_learn_plus(
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
    change_data.status_data.setdefault(14, 0)
    change_data.status_data[14] += now_add_lust


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_SUBMIT)
def handle_add_middle_submit(
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

    now_add_lust = 1000
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[14])
    now_add_lust *= adjust

    character_data.status_data[15] += now_add_lust
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
    change_data.status_data.setdefault(20, 0)
    change_data.status_data[20] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_PAIN_FIRST_SEX)
def handle_add_large_pain_first_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加巨量苦痛（破处修正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    # 润滑修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[8])
    now_add_lust *= adjust
    # 欲情修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[12])
    adjust = adjust/3 if adjust >=2 else adjust/1.5
    now_add_lust *= adjust
    # 痛苦刻印修正
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
    now_add_lust *= adjust
    # V扩张修正
    adjust = attr_calculation.get_ability_adjust(character_data.ability[9]) * 6
    now_add_lust /= adjust

    character_data.status_data[17] += now_add_lust
    change_data.status_data.setdefault(17, 0)
    change_data.status_data[17] += now_add_lust

@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_LARGE_PAIN_FIRST_A_SEX)
def handle_add_large_pain_first_a_sex(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加巨量苦痛（A破处修正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """

    character_data: game_type.Character = cache.character_data[character_id]

    now_add_lust = 100
    # 润滑修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[8])
    now_add_lust *= adjust
    # 欲情修正
    adjust = attr_calculation.get_pain_adjust(character_data.status_data[12])
    adjust = adjust/3 if adjust >=2 else adjust/1.5
    now_add_lust *= adjust
    # 痛苦刻印修正
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
    now_add_lust *= adjust
    # A扩张修正
    adjust = attr_calculation.get_ability_adjust(character_data.ability[10]) * 6
    now_add_lust /= adjust

    character_data.status_data[17] += now_add_lust
    change_data.status_data.setdefault(17, 0)
    change_data.status_data[17] += now_add_lust


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


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_TIRED)
def handle_add_tired(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    维持疲劳和熟睡值（安眠药）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    if character_data.h_state.body_item[9][1]:
        character_data.tired_point = 160
        character_data.sleep_point = 100


@settle_behavior.add_settle_second_behavior_effect(constant_effect.SecondEffect.ADD_MILK)
def handle_add_milk(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
):
    """
    增加乳汁（挤奶）
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    if character_data.h_state.body_item[4][1]:

        now_milk = 5 * character_data.behavior.duration
        now_milk = min(character_data.pregnancy.milk, now_milk)
        cache.rhodes_island.milk_in_fridge.setdefault(character_id, 0)
        cache.rhodes_island.milk_in_fridge[character_id] += now_milk
        character_data.pregnancy.milk -= now_milk
        character_data.behavior.milk_ml += now_milk

        # 绘制信息
        if now_milk:
            now_draw = draw.NormalDraw()
            now_text = f"\n{character_data.name}榨出了{now_milk}ml的乳汁。\n"
            now_draw.text = now_text
            now_draw.width = window_width
            now_draw.draw()

    # 没有乳汁时停止榨乳
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

