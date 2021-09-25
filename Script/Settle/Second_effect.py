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
