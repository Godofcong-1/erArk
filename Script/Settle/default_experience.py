import datetime
from types import FunctionType
from Script.Design import (
    settle_behavior,
    map_handle,
    handle_premise
)
from Script.Core import cache_control, constant, constant_effect, game_type, get_text
from Script.Config import game_config, normal_config

_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

def base_chara_experience_common_settle(
        character_id: int,
        experience_id: int,
        base_value: int = 1,
        target_flag: bool = False,
        change_data: game_type.CharacterStatusChange = None,
        change_data_to_target_change: game_type.CharacterStatusChange = None,
        ):
    """
    基础角色经验通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    experience_id -- 经验id\n
    base_value -- 基础固定值\n
    target_flag -- 是否加到交互对象身上\n
    change_data -- 状态变更信息记录对象\n
    change_data_to_target_change -- 交互对象结算信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    final_character_id = character_id
    if character_data.dead:
        return
    # 改为加到交互对象身上
    if target_flag:
        final_character_id = character_data.target_character_id
        character_data = cache.character_data[final_character_id]

    # 深度无意识下部分经验不结算
    conscious_experience_set = {30, 31, 32, 33, 34}
    if experience_id in conscious_experience_set and not handle_premise.handle_normal_6(final_character_id):
        return

    # 结算最终值
    character_data.experience.setdefault(experience_id, 0)
    character_data.experience[experience_id] += base_value
    character_data.experience[experience_id] = max(0, character_data.experience[experience_id])

    # 确认结算信息记录对象
    final_change_data = change_data
    if change_data != None and target_flag:
        change_data.target_change.setdefault(final_character_id, game_type.TargetChange())
        final_change_data: game_type.TargetChange = change_data.target_change[final_character_id]
    elif change_data_to_target_change != None:
        change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
        final_change_data: game_type.TargetChange = change_data_to_target_change.target_change[character_id]

    # 结算信息记录对象增加经验
    final_change_data.experience.setdefault(experience_id, 0)
    final_change_data.experience[experience_id] += base_value


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_N_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 0, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_B_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 1, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_C_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 2, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_P_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 3, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_V_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 4, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_A_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 5, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_U_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 6, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_W_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 7, target_flag = True, change_data = change_data)


"""
    8-9留空
"""


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_NClimax_EXPERIENCE)
def handle_target_add_1_nclimax_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1N绝顶经验+1绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 10, target_flag = True, change_data = change_data)
    base_chara_experience_common_settle(character_id, 20, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_BClimax_EXPERIENCE)
def handle_target_add_1_bclimax_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1B绝顶经验+1绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 11, target_flag = True, change_data = change_data)
    base_chara_experience_common_settle(character_id, 20, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_CClimax_EXPERIENCE)
def handle_target_add_1_cclimax_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1C绝顶经验+1绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 12, target_flag = True, change_data = change_data)
    base_chara_experience_common_settle(character_id, 20, target_flag = True, change_data = change_data)


# @settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_PClimax_EXPERIENCE)
# def handle_target_add_1_pclimax_experience(
#     character_id: int,
#     add_time: int,
#     change_data: game_type.CharacterStatusChange,
#     now_time: datetime.datetime,
# ):
#     """
#     交互对象增加1P绝顶经验+1绝顶经验
#     Keyword arguments:
#     character_id -- 角色id
#     add_time -- 结算时间
#     change_data -- 状态变更信息记录对象
#     now_time -- 结算的时间
#     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
    # base_chara_experience_common_settle(character_data.target_character_id, 13, target_flag = True, change_data = change_data)
    # base_chara_experience_common_settle(character_data.target_character_id, 20, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_VClimax_EXPERIENCE)
def handle_target_add_1_vclimax_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1V绝顶经验+1绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 14, target_flag = True, change_data = change_data)
    base_chara_experience_common_settle(character_id, 20, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_AClimax_EXPERIENCE)
def handle_target_add_1_aclimax_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1A绝顶经验+1绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 15, target_flag = True, change_data = change_data)
    base_chara_experience_common_settle(character_id, 20, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UClimax_EXPERIENCE)
def handle_target_add_1_uclimax_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1U绝顶经验+1绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 16, target_flag = True, change_data = change_data)
    base_chara_experience_common_settle(character_id, 20, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_WClimax_EXPERIENCE)
def handle_target_add_1_wclimax_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1W绝顶经验+1绝顶经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 17, target_flag = True, change_data = change_data)
    base_chara_experience_common_settle(character_id, 20, target_flag = True, change_data = change_data)


"""
    8-9留空
"""


# @settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Climax_EXPERIENCE)
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

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Cumming_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 21, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Milking_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 22, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Peeing_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 23, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Cums_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 24, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_CumsDrink_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 25, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Creampie_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 26, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_AnalCums_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 27, target_flag = True, change_data = change_data)


"""
    28-29留空
"""


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_plServe_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 30, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Love_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 31, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_plPain_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 32, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_plSadism_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 33, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_plExhibit_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 34, target_flag = True, change_data = change_data)


"""
    35-39留空
"""


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Kiss_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 40, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Handjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 41, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Blowjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 42, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Paizuri_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 43, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Footjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 44, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Hairjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 45, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Masterbate_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 54, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_bdsmMasterbate_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 55, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Toys_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 51, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Tiedup_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 52, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Insert_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 60, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_sexV_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 61, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_sexA_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 62, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_sexU_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 63, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_sexW_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 64, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_expandV_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 65, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_expandA_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 66, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_expandU_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 67, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_expandW_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 68, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_TWRape_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 124, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_SlumberRape_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 120, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Abnormal_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 50, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Axillajob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 46, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Enema_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 53, target_flag = True, change_data = change_data)


"""
    64-69留空
"""


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyN_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 70, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyB_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 71, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyC_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 72, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyP_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 73, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyV_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 74, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyA_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 75, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyU_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 76, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyW_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 77, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslyClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 78, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_UnconsciouslySex_EXPERIENCE)
def handle_target_add_1_unconsciouslysex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1无意识性交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 79, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Chat_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 80, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Combat_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 81, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Learn_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 82, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Cooking_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 83, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Date_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 84, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Music_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 85, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_GiveBirth_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 86, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Command_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 87, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_Cure_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 88, target_flag = True, change_data = change_data)


"""
    89-99留空
"""


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_ForwardClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 100, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_BackClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 101, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_RideClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 102, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_FSeatClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 103, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_BSeatClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 104, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_FStandClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 105, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_BStandClimax_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 106, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Kiss_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 40, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Handjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 41, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Blowjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 42, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Paizuri_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 43, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Footjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 44, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Hairjob_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 45, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Chat_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 80, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Combat_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 81, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Learn_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 82, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Cooking_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 83, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Date_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 84, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Music_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 85, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_GiveBirth_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 86, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Insert_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 60, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Command_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 87, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Cure_EXPERIENCE)
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
    base_chara_experience_common_settle(character_id, 88, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Cumming_EXPERIENCE)
def handle_add_1_cumming_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1射精经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 21, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Milking_EXPERIENCE)
def handle_add_1_milking_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1喷乳经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 22, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Peeing_EXPERIENCE)
def handle_add_1_peeing_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1放尿经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 23, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Cums_EXPERIENCE)
def handle_add_1_cums_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1精液经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 24, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_CumsDrink_EXPERIENCE)
def handle_add_1_cumsdrink_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1饮精经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 25, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Creampie_EXPERIENCE)
def handle_add_1_creampie_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1膣射经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 26, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_AnalCums_EXPERIENCE)
def handle_add_1_analcums_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1肛射经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 27, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Hypnosis_EXPERIENCE)
def handle_add_1_hypnosis_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1催眠经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 122, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_BEEN_Hypnosis_EXPERIENCE)
def handle_target_add_1_been_hypnosis_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1被催眠经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 123, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PLACE_ALL_CHARA_ADD_1_BEEN_Hypnosis_EXPERIENCE)
def handle_place_all_chara_add_1_been_hypnosis_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有其他角色均增加1被催眠经验
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
    # 获取当前场景的全角色名单
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    scene_character_list = scene_data.character_list.copy()
    # 去掉里的自己
    if character_id in scene_character_list:
        scene_character_list.remove(character_id)
    for target_id in scene_character_list:
        base_chara_experience_common_settle(target_id, 123, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Agriculture_EXPERIENCE)
def handle_add_1_agriculture_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1农业经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 89, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Create_EXPERIENCE)
def handle_add_1_create_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1制造经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 90, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Paint_EXPERIENCE)
def handle_add_1_paint_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1制造经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 91, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Read_EXPERIENCE)
def handle_add_1_read_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1阅读经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 92, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Read_H_EXPERIENCE)
def handle_add_1_read_h_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1阅读经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 93, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.Both_ADD_1_Learn_EXPERIENCE)
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
    if character_data.dead:
        return

    # 自己增加1学识经验
    base_chara_experience_common_settle(character_id, 82, change_data = change_data)

    # 如果有交互对象的话，对方增加1学识经验
    if character_data.target_character_id != character_id:
        base_chara_experience_common_settle(character_id, 82, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Masterbate_EXPERIENCE)
def handle_add_1_masterbate_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1自慰经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 54, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Sleep_Sex_EXPERIENCE)
def handle_add_1_sleep_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1睡姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 120, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_be_Sleep_Sex_EXPERIENCE)
def handle_add_1_be_sleep_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1被睡姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 121, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Time_Stop_Sex_EXPERIENCE)
def handle_add_1_time_stop_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1时姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 124, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_be_Time_Stop_Sex_EXPERIENCE)
def handle_add_1_be_time_stop_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1被时姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 125, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_be_Sleep_Sex_EXPERIENCE)
def handle_target_add_1_be_sleep_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1被睡姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 121, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_be_Time_Stop_Sex_EXPERIENCE)
def handle_target_add_1_be_time_stop_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1被时姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 125, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_Hypnosis_Sex_EXPERIENCE)
def handle_add_1_hypnosis_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1催眠姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 126, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_be_Hypnosis_Sex_EXPERIENCE)
def handle_add_1_be_hypnosis_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1被催眠姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 127, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_be_Hypnosis_Sex_EXPERIENCE)
def handle_target_add_1_be_hypnosis_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1被催眠姦经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 127, target_flag = True, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_1_CLOTH_JOB_EXPERIENCE)
def handle_target_add_1_cloth_job_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加1服装交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 47, target_flag = True, change_data = change_data)

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_1_GROUP_SEX_EXPERIENCE)
def handle_add_1_group_sex_experience(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加1群交经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_experience_common_settle(character_id, 56, change_data = change_data)

