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



@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_N_EXPERIENCE)
def handle_target_add_1_n_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1N经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(0, 0)
    target_data.experience[0] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(0, 0)
    target_change.experience[0] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_B_EXPERIENCE)
def handle_target_add_1_b_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1B经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience[1] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(1, 0)
    target_change.experience[1] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_C_EXPERIENCE)
def handle_target_add_1_c_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1C经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(2, 0)
    target_data.experience[2] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(2, 0)
    target_change.experience[2] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_P_EXPERIENCE)
def handle_target_add_1_p_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1P经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(3, 0)
    target_data.experience[3] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(3, 0)
    target_change.experience[3] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_V_EXPERIENCE)
def handle_target_add_1_v_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1V经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(4, 0)
    target_data.experience[4] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(4, 0)
    target_change.experience[4] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_A_EXPERIENCE)
def handle_target_add_1_a_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1A经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(5, 0)
    target_data.experience[5] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(5, 0)
    target_change.experience[5] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_U_EXPERIENCE)
def handle_target_add_1_u_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1U经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(6, 0)
    target_data.experience[6] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(6, 0)
    target_change.experience[6] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_W_EXPERIENCE)
def handle_target_add_1_w_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1W经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(7, 0)
    target_data.experience[7] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(7, 0)
    target_change.experience[7] += 1

"""
    8-9留空
"""

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_NClimax_EXPERIENCE)
def handle_target_add_1_nclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1N绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(10, 0)
    target_data.experience[10] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(10, 0)
    target_change.experience[10] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_BClimax_EXPERIENCE)
def handle_target_add_1_bclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1B绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(11, 0)
    target_data.experience[11] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(11, 0)
    target_change.experience[11] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_CClimax_EXPERIENCE)
def handle_target_add_1_cclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1C绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(12, 0)
    target_data.experience[12] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(12, 0)
    target_change.experience[12] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

# @settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_PClimax_EXPERIENCE)
# def handle_target_add_1_pclimax_experience(
#     character_id: int,
#     add_time: int,
#     change_data: game_type.CharacterStatusChange,
#     now_time: datetime.datetime,
# ):
#     """
#     交互对象增加1P绝顶经验
#     Keyword arguments:
#     character_id -- 角色id
#     add_time -- 结算时间
#     change_data -- 状态变更信息记录对象
#     now_time -- 结算的时间
#     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     if target_data.dead:
#         return
#     target_data.experience.setdefault(13, 0)
#     target_data.experience[13] += 1
#     target_data.experience.setdefault(20, 0)
#     target_data.experience[20] += 1
#     change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
#     target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
#     target_change.experience.setdefault(13, 0)
#     target_change.experience[13] += 1
#     target_change.experience.setdefault(20, 0)
#     target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_VClimax_EXPERIENCE)
def handle_target_add_1_vclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1V绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(14, 0)
    target_data.experience[14] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(14, 0)
    target_change.experience[14] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_AClimax_EXPERIENCE)
def handle_target_add_1_aclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1A绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(15, 0)
    target_data.experience[15] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(15, 0)
    target_change.experience[15] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UClimax_EXPERIENCE)
def handle_target_add_1_uclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1U绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(16, 0)
    target_data.experience[16] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(16, 0)
    target_change.experience[16] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_WClimax_EXPERIENCE)
def handle_target_add_1_wclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1W绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(17, 0)
    target_data.experience[17] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(17, 0)
    target_change.experience[17] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

"""
    8-9留空
"""

# @settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Climax_EXPERIENCE)
# def handle_target_add_1_climax_experience(
#     character_id: int,
#     add_time: int,
#     change_data: game_type.CharacterStatusChange,
#     now_time: datetime.datetime,
# ):
#     """
#     交互对象增加1绝顶经验
#     Keyword arguments:
#     character_id -- 角色id
#     add_time -- 结算时间
#     change_data -- 状态变更信息记录对象
#     now_time -- 结算的时间
#     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#     if target_data.dead:
#         return
#     target_data.experience.setdefault(20, 0)
#     target_data.experience[20] += 1
#     change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
#     target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
#     target_change.experience.setdefault(20, 0)
#     target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Cumming_EXPERIENCE)
def handle_target_add_1_cumming_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1射精经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(21, 0)
    target_data.experience[21] += 1
    target_data.experience.setdefault(20, 0)
    target_data.experience[20] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(21, 0)
    target_change.experience[21] += 1
    target_change.experience.setdefault(20, 0)
    target_change.experience[20] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Milking_EXPERIENCE)
def handle_target_add_1_milking_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1喷乳经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(22, 0)
    target_data.experience[22] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(22, 0)
    target_change.experience[22] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Peeing_EXPERIENCE)
def handle_target_add_1_peeing_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1放尿经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(23, 0)
    target_data.experience[23] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(23, 0)
    target_change.experience[23] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Cums_EXPERIENCE)
def handle_target_add_1_cums_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1精液经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(24, 0)
    target_data.experience[24] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(24, 0)
    target_change.experience[24] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_CumsDrink_EXPERIENCE)
def handle_target_add_1_cumsdrink_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1饮精经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(25, 0)
    target_data.experience[25] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(25, 0)
    target_change.experience[25] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Creampie_EXPERIENCE)
def handle_target_add_1_creampie_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1膣射经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(26, 0)
    target_data.experience[26] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(26, 0)
    target_change.experience[26] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_AnalCums_EXPERIENCE)
def handle_target_add_1_analcums_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1肛射经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(27, 0)
    target_data.experience[27] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(27, 0)
    target_change.experience[27] += 1

"""
    28-29留空
"""

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_plServe_EXPERIENCE)
def handle_target_add_1_plserve_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1奉仕快乐经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(30, 0)
    target_data.experience[30] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(30, 0)
    target_change.experience[30] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Love_EXPERIENCE)
def handle_target_add_1_love_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1爱情经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(31, 0)
    target_data.experience[31] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(31, 0)
    target_change.experience[31] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_plPain_EXPERIENCE)
def handle_target_add_1_plpain_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1苦痛快乐经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(32, 0)
    target_data.experience[32] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(32, 0)
    target_change.experience[32] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_plSadism_EXPERIENCE)
def handle_target_add_1_plsadism_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1嗜虐快乐经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(33, 0)
    target_data.experience[33] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(33, 0)
    target_change.experience[33] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_plExhibit_EXPERIENCE)
def handle_target_add_1_plexhibit_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1露出快乐经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(34, 0)
    target_data.experience[34] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(34, 0)
    target_change.experience[34] += 1

"""
    35-39留空
"""

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Kiss_EXPERIENCE)
def handle_target_add_1_kiss_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1接吻经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience[40] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(40, 0)
    target_change.experience[40] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Handjob_EXPERIENCE)
def handle_target_add_1_handjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1手淫经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience[41] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(41, 0)
    target_change.experience[41] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Blowjob_EXPERIENCE)
def handle_target_add_1_blowjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1口淫经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience[42] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(42, 0)
    target_change.experience[42] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Paizuri_EXPERIENCE)
def handle_target_add_1_paizuri_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1乳交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience[43] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(43, 0)
    target_change.experience[43] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Footjob_EXPERIENCE)
def handle_target_add_1_footjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1足交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience[44] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(44, 0)
    target_change.experience[44] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Hairjob_EXPERIENCE)
def handle_target_add_1_blowjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1发交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience[45] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(45, 0)
    target_change.experience[45] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Masterbate_EXPERIENCE)
def handle_target_add_1_masterbate_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1自慰经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(46, 0)
    target_data.experience[46] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(46, 0)
    target_change.experience[46] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_bdsmMasterbate_EXPERIENCE)
def handle_target_add_1_bdsmmasterbate_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1调教自慰经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(47, 0)
    target_data.experience[47] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(47, 0)
    target_change.experience[47] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Toys_EXPERIENCE)
def handle_target_add_1_toys_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1道具使用经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(48, 0)
    target_data.experience[48] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(48, 0)
    target_change.experience[48] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Tiedup_EXPERIENCE)
def handle_target_add_1_tiedup_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1紧缚经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(49, 0)
    target_data.experience[49] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(49, 0)
    target_change.experience[49] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Insert_EXPERIENCE)
def handle_target_add_1_insert_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1插入经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(50, 0)
    target_data.experience[50] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(50, 0)
    target_change.experience[50] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_sexV_EXPERIENCE)
def handle_target_add_1_sexv_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1V性交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(51, 0)
    target_data.experience[51] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(51, 0)
    target_change.experience[51] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_sexA_EXPERIENCE)
def handle_target_add_1_sexa_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1A性交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(52, 0)
    target_data.experience[52] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(52, 0)
    target_change.experience[52] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_sexU_EXPERIENCE)
def handle_target_add_1_sexu_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1U性交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(53, 0)
    target_data.experience[53] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(53, 0)
    target_change.experience[53] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_sexW_EXPERIENCE)
def handle_target_add_1_sexw_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1W性交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(54, 0)
    target_data.experience[54] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(54, 0)
    target_change.experience[54] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_expandV_EXPERIENCE)
def handle_target_add_1_expandv_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1V扩张经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(55, 0)
    target_data.experience[55] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(55, 0)
    target_change.experience[55] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_expandA_EXPERIENCE)
def handle_target_add_1_expanda_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1A扩张经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(56, 0)
    target_data.experience[56] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(56, 0)
    target_change.experience[56] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_expandU_EXPERIENCE)
def handle_target_add_1_expandu_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1U扩张经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(57, 0)
    target_data.experience[57] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(57, 0)
    target_change.experience[57] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_expandW_EXPERIENCE)
def handle_target_add_1_expandw_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1W扩张经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(58, 0)
    target_data.experience[58] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(58, 0)
    target_change.experience[58] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_TWRape_EXPERIENCE)
def handle_target_add_1_twrape_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1时奸经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(59, 0)
    target_data.experience[59] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(59, 0)
    target_change.experience[59] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_SlumberRape_EXPERIENCE)
def handle_target_add_1_slumberrape_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1睡奸经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(60, 0)
    target_data.experience[60] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(60, 0)
    target_change.experience[60] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Abnormal_EXPERIENCE)
def handle_target_add_1_abnormal_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1异常经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(61, 0)
    target_data.experience[61] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(61, 0)
    target_change.experience[61] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Axillajob_EXPERIENCE)
def handle_target_add_1_axillajob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1腋交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(62, 0)
    target_data.experience[62] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(62, 0)
    target_change.experience[62] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Enema_EXPERIENCE)
def handle_target_add_1_enema_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1灌肠经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(63, 0)
    target_data.experience[63] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(63, 0)
    target_change.experience[63] += 1


"""
    64-69留空
"""

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyN_EXPERIENCE)
def handle_target_add_1_unconsciouslyn_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识N经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(70, 0)
    target_data.experience[70] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(70, 0)
    target_change.experience[70] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyB_EXPERIENCE)
def handle_target_add_1_unconsciouslyb_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识B经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(71, 0)
    target_data.experience[71] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(71, 0)
    target_change.experience[71] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyC_EXPERIENCE)
def handle_target_add_1_unconsciouslyc_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识C经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(72, 0)
    target_data.experience[72] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(72, 0)
    target_change.experience[72] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyP_EXPERIENCE)
def handle_target_add_1_unconsciouslyp_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识P经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(73, 0)
    target_data.experience[73] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(73, 0)
    target_change.experience[73] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyV_EXPERIENCE)
def handle_target_add_1_unconsciouslyv_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识V经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(74, 0)
    target_data.experience[74] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(74, 0)
    target_change.experience[74] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyA_EXPERIENCE)
def handle_target_add_1_unconsciouslya_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识A经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(75, 0)
    target_data.experience[75] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(75, 0)
    target_change.experience[75] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyU_EXPERIENCE)
def handle_target_add_1_unconsciouslyu_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识U经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(76, 0)
    target_data.experience[76] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(76, 0)
    target_change.experience[76] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyW_EXPERIENCE)
def handle_target_add_1_unconsciouslyw_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识W经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(77, 0)
    target_data.experience[77] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(77, 0)
    target_change.experience[77] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_UnconsciouslyClimax_EXPERIENCE)
def handle_target_add_1_unconsciouslyclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1无意识绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(78, 0)
    target_data.experience[78] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(78, 0)
    target_change.experience[78] += 1

"""
79留空
"""

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Chat_EXPERIENCE)
def handle_target_add_1_chat_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1对话经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(80, 0)
    target_data.experience[80] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(80, 0)
    target_change.experience[80] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Combat_EXPERIENCE)
def handle_target_add_1_combat_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1战斗经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(81, 0)
    target_data.experience[81] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(81, 0)
    target_change.experience[81] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Learn_EXPERIENCE)
def handle_target_add_1_learn_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1学习经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(82, 0)
    target_data.experience[82] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(82, 0)
    target_change.experience[82] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Cooking_EXPERIENCE)
def handle_target_add_1_cooking_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1料理经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(83, 0)
    target_data.experience[83] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(83, 0)
    target_change.experience[83] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Date_EXPERIENCE)
def handle_target_add_1_Date_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1约会经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(84, 0)
    target_data.experience[84] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(84, 0)
    target_change.experience[84] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Music_EXPERIENCE)
def handle_target_add_1_music_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1音乐经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(85, 0)
    target_data.experience[85] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(85, 0)
    target_change.experience[85] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_GiveBirth_EXPERIENCE)
def handle_target_add_1_givebirth_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1出产经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(86, 0)
    target_data.experience[86] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(86, 0)
    target_change.experience[86] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Command_EXPERIENCE)
def handle_target_add_1_command_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1指挥经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(87, 0)
    target_data.experience[87] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(87, 0)
    target_change.experience[87] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_Cure_EXPERIENCE)
def handle_target_add_1_cure_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1医疗经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(88, 0)
    target_data.experience[88] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(88, 0)
    target_change.experience[88] += 1

"""
    89-99留空
"""

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_ForwardClimax_EXPERIENCE)
def handle_target_add_1_forwardclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1正面位绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(100, 0)
    target_data.experience[100] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(100, 0)
    target_change.experience[100] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_BackClimax_EXPERIENCE)
def handle_target_add_1_backclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1后入位绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(101, 0)
    target_data.experience[101] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(101, 0)
    target_change.experience[101] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_RideClimax_EXPERIENCE)
def handle_target_add_1_rideclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1骑乘位绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(102, 0)
    target_data.experience[102] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(102, 0)
    target_change.experience[102] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_FSeatClimax_EXPERIENCE)
def handle_target_add_1_fseatclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1对面座位绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(103, 0)
    target_data.experience[103] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(103, 0)
    target_change.experience[103] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_BSeatClimax_EXPERIENCE)
def handle_target_add_1_bseatclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1背面座位绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(104, 0)
    target_data.experience[104] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(104, 0)
    target_change.experience[104] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_FStandClimax_EXPERIENCE)
def handle_target_add_1_fstandclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1对面立位绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(105, 0)
    target_data.experience[105] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(105, 0)
    target_change.experience[105] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_1_BStandClimax_EXPERIENCE)
def handle_target_add_1_bstandclimax_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加1背面立位绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id == character_data.target_character_id:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.experience.setdefault(106, 0)
    target_data.experience[106] += 1
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.experience.setdefault(106, 0)
    target_change.experience[106] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Kiss_EXPERIENCE)
def handle_add_1_kiss_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1接吻经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(40, 0)
    character_data.experience[40] += 1
    change_data.experience.setdefault(40, 0)
    change_data.experience[40] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Handjob_EXPERIENCE)
def handle_add_1_handjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1手淫经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(41, 0)
    character_data.experience[41] += 1
    change_data.experience.setdefault(41, 0)
    change_data.experience[41] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Blowjob_EXPERIENCE)
def handle_add_1_blowjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1口淫经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(42, 0)
    character_data.experience[42] += 1
    change_data.experience.setdefault(42, 0)
    change_data.experience[42] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Paizuri_EXPERIENCE)
def handle_add_1_paizuri_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1乳交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(43, 0)
    character_data.experience[43] += 1
    change_data.experience.setdefault(43, 0)
    change_data.experience[43] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Footjob_EXPERIENCE)
def handle_add_1_footjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1足交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(44, 0)
    character_data.experience[44] += 1
    change_data.experience.setdefault(44, 0)
    change_data.experience[44] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Hairjob_EXPERIENCE)
def handle_add_1_blowjob_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1发交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(45, 0)
    character_data.experience[45] += 1
    change_data.experience.setdefault(45, 0)
    change_data.experience[45] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Chat_EXPERIENCE)
def handle_add_1_chat_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1对话经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(80, 0)
    character_data.experience[80] += 1
    change_data.experience.setdefault(80, 0)
    change_data.experience[80] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Combat_EXPERIENCE)
def handle_add_1_combat_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1战斗经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(81, 0)
    character_data.experience[81] += 1
    change_data.experience.setdefault(81, 0)
    change_data.experience[81] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Learn_EXPERIENCE)
def handle_add_1_learn_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1学习经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(82, 0)
    character_data.experience[82] += 1
    change_data.experience.setdefault(82, 0)
    change_data.experience[82] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Cooking_EXPERIENCE)
def handle_add_1_cooking_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1料理经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(83, 0)
    character_data.experience[83] += 1
    change_data.experience.setdefault(83, 0)
    change_data.experience[83] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Date_EXPERIENCE)
def handle_add_1_date_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1约会经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(84, 0)
    character_data.experience[84] += 1
    change_data.experience.setdefault(84, 0)
    change_data.experience[84] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Music_EXPERIENCE)
def handle_add_1_music_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1音乐经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(85, 0)
    character_data.experience[85] += 1
    change_data.experience.setdefault(85, 0)
    change_data.experience[85] += 1

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_GiveBirth_EXPERIENCE)
def handle_add_1_giveBirth_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1妊娠经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(86, 0)
    character_data.experience[86] += 1
    change_data.experience.setdefault(86, 0)
    change_data.experience[86] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Insert_EXPERIENCE)
def handle_add_1_insert_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1插入经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(50, 0)
    character_data.experience[50] += 1
    change_data.experience.setdefault(50, 0)
    change_data.experience[50] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Command_EXPERIENCE)
def handle_add_1_command_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1指挥经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(87, 0)
    character_data.experience[87] += 1
    change_data.experience.setdefault(87, 0)
    change_data.experience[87] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_1_Cure_EXPERIENCE)
def handle_add_1_cure_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    增加1医疗经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    character_data.experience.setdefault(88, 0)
    character_data.experience[88] += 1
    change_data.experience.setdefault(88, 0)
    change_data.experience[88] += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.Both_ADD_1_Learn_EXPERIENCE)
def handle_both_add_1_learn_experience(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    自己（和对方一起）增加1学识经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return

    # 自己增加1学识经验
    character_data.experience.setdefault(82, 0)
    character_data.experience[82] += 1
    change_data.experience.setdefault(82, 0)
    change_data.experience[82] += 1

    # 如果有交互对象的话，对方增加1学识经验
    if character_data.target_character_id != 0:
        target_data.experience.setdefault(82, 0)
        target_data.experience[82] += 1
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.experience.setdefault(82, 0)
        target_change.experience[82] += 1
