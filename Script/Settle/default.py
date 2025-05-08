import datetime
import random, math
from types import FunctionType
from Script.Design import (
    settle_behavior,
    instuct_judege,
    map_handle,
    attr_calculation,
    game_time,
    cooking,
    handle_instruct,
    character_behavior,
    handle_npc_ai_in_h,
    handle_premise,
    clothing,
)
from Script.Core import cache_control, constant, constant_effect, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw
from Script.UI.Panel import dirty_panel, event_option_panel, originium_arts, ejaculation_panel

from Script.Settle.common_default import (
    base_chara_hp_mp_common_settle,
    base_chara_state_common_settle,
    base_chara_favorability_and_trust_common_settle,
    base_chara_climix_common_settle,
    base_chara_experience_common_settle,
)

_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NOTHING)
def handle_nothing(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    空结算
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    pass


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_HIT_POINT)
def handle_add_small_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加少量体力
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
    add_hit_point = add_time * (10 + character_data.hit_point_max * 0.005)
    now_add_hit_point = add_hit_point
    # 如果气力=0则恢复减半
    if character_data.mana_point == 0:
        now_add_hit_point /= 2
    character_data.hit_point += now_add_hit_point
    change_data.hit_point += now_add_hit_point
    # 如果超过最大值则=最大值
    if character_data.hit_point >= character_data.hit_point_max:
        character_data.hit_point = character_data.hit_point_max


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_MANA_POINT)
def handle_add_small_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加少量气力
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
    add_mana_point = add_time * (20 + character_data.hit_point_max * 0.01)
    character_data.mana_point += add_mana_point
    change_data.mana_point += add_mana_point
    if character_data.mana_point > character_data.mana_point_max:
        character_data.mana_point = character_data.mana_point_max


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_INTERACTION_FAVORABILITY)
def handle_add_interaction_favoravility(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加基础互动好感
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, 0, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_INTERACTION_FAVORABILITY)
def handle_down_interaction_favoravility(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    降低基础互动好感
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, -1, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_TRUST)
def handle_add_small_trust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加基础互动信赖
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, 0, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_SMALL_TRUST)
def handle_down_small_trust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    降低基础互动信赖
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, -1, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_BOTH_SMALL_HIT_POINT)
def handle_sub_both_small_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方减少少量体力（若没有交互对象则仅减少自己）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, hp_value=-1, target_flag=True, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_BOTH_SMALL_MANA_POINT)
def handle_sub_both_small_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方减少少量气力（若没有交互对象则仅减少自己）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, mp_value=-1, target_flag=True, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_BOTH_MEDIUM_HIT_POINT)
def handle_sub_both_medium_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方减少中量体力（若没有交互对象则仅减少自己）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, hp_value=-1, dregree=1, target_flag=True, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_BOTH_MEDIUM_MANA_POINT)
def handle_sub_both_medium_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方减少中量气力（若没有交互对象则仅减少自己）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, mp_value=-1, dregree=1, target_flag=True, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_BOTH_LARGE_HIT_POINT)
def handle_sub_both_large_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方减少大量体力（若没有交互对象则仅减少自己）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, hp_value=-1, dregree=2, target_flag=True, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_BOTH_LARGE_MANA_POINT)
def handle_sub_both_large_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方减少大量气力（若没有交互对象则仅减少自己）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, mp_value=-1, dregree=2, target_flag=True, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_SELF_SMALL_HIT_POINT)
def handle_sub_self_small_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少自己少量体力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, hp_value=-1, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_SELF_SMALL_MANA_POINT)
def handle_sub_self_small_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少自己少量气力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, mp_value=-1, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_SELF_MEDIUM_HIT_POINT)
def handle_sub_self_medium_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少自己中量体力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, hp_value=-1, dregree=1, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_SELF_MEDIUM_MANA_POINT)
def handle_sub_self_medium_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少自己中量气力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, mp_value=-1, dregree=1, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_SELF_LARGE_HIT_POINT)
def handle_sub_self_large_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少自己大量体力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, hp_value=-1, dregree=2, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_SELF_LARGE_MANA_POINT)
def handle_sub_self_large_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少自己大量气力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    base_chara_hp_mp_common_settle(character_id, add_time, mp_value=-1, dregree=2, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_TARGET_MEDIUM_HIT_POINT)
def handle_sub_target_medium_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少交互对象中量体力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data = cache.character_data[character_id]
    base_chara_hp_mp_common_settle(character_data.target_character_id, add_time, hp_value=-1, dregree=1, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_TARGET_MEDIUM_MANA_POINT)
def handle_sub_target_medium_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少交互对象中量气力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data = cache.character_data[character_id]
    base_chara_hp_mp_common_settle(character_data.target_character_id, add_time, mp_value=-1, dregree=1, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_TARGET_LARGE_HIT_POINT)
def handle_sub_target_large_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少交互对象大量体力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data = cache.character_data[character_id]
    base_chara_hp_mp_common_settle(character_data.target_character_id, add_time, hp_value=-1, dregree=2, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOWN_TARGET_LARGE_MANA_POINT)
def handle_sub_target_large_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    减少交互对象大量气力
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data = cache.character_data[character_id]
    base_chara_hp_mp_common_settle(character_data.target_character_id, add_time, mp_value=-1, dregree=2, change_data=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MOOD_TO_GOOD)
def handle_mood_to_good(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己心情变为好
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.angry_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MOOD_TO_NORMAL)
def handle_mood_to_normal(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己心情变为普通
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.angry_point = 20


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MOOD_TO_BAD)
def handle_mood_to_bad(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己心情变为不好
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.angry_point = 40


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MOOD_TO_ANGRY)
def handle_mood_to_angry(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己心情变为愤怒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.angry_point = 75


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MOOD_TO_GOOD)
def handle_target_mood_to_good(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象心情变为好
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    handle_mood_to_good(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MOOD_TO_NORMAL)
def handle_target_mood_to_normal(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象心情变为普通
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    handle_mood_to_normal(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MOOD_TO_BAD)
def handle_target_mood_to_bad(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象心情变为不好
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    handle_mood_to_bad(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MOOD_TO_ANGRY)
def handle_target_mood_to_angry(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象心情变为愤怒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    handle_mood_to_angry(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_DESIRE_POINT_ZERO)
def handle_scene_all_characters_desire_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有角色欲望值归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        if chara_id == 0:
            continue
        character_data.desire_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_BOTH_SMALL_HIT_POINT)
def handle_add_both_small_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加双方少量体力
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
    add_hit_point = add_time * (10 + character_data.hit_point_max * 0.005)
    now_add_hit_point = add_hit_point
    # 如果气力=0则恢复减半
    if character_data.mana_point == 0:
        now_add_hit_point /= 2
    character_data.hit_point += now_add_hit_point
    change_data.hit_point += now_add_hit_point
    # 如果超过最大值则=最大值
    if character_data.hit_point >= character_data.hit_point_max:
        character_data.hit_point = character_data.hit_point_max
    # 交互对象也同样#
    if character_data.target_character_id != character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        add_hit_point = add_time * (10 + target_data.hit_point_max * 0.005)
        now_add_hit_point = add_hit_point
        # 如果气力=0则恢复减半
        if target_data.mana_point == 0:
            now_add_hit_point /= 2
        target_data.hit_point += now_add_hit_point
        target_change.hit_point += now_add_hit_point
        # 如果超过最大值则=最大值
        if target_data.hit_point >= target_data.hit_point_max:
            target_data.hit_point = target_data.hit_point_max


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_BOTH_SMALL_MANA_POINT)
def handle_add_both_small_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加双方少量气力
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
    add_mana_point = add_time * (20 + character_data.hit_point_max * 0.01)
    character_data.mana_point += add_mana_point
    change_data.mana_point += add_mana_point
    if character_data.mana_point > character_data.mana_point_max:
        character_data.mana_point = character_data.mana_point_max
    # 交互对象也同样#
    if character_data.target_character_id != character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        add_mana_point = add_time * (20 + target_data.hit_point_max * 0.01)
        target_data.mana_point += add_mana_point
        target_change.mana_point += add_mana_point
        # 如果超过最大值则=最大值
        if target_data.mana_point >= target_data.mana_point_max:
            target_data.mana_point = target_data.mana_point_max


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MOVE_TO_TARGET_SCENE)
def handle_move_to_target_scene(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    移动至目标场景
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
    if len(character_data.behavior.move_target):
        # 如果未开始屏蔽，且和玩家位于同一地点，则输出提示信息
        if cache.all_system_setting.draw_setting[8] == 1 and character_id > 0 and character_data.position == cache.character_data[0].position:
            target_position_name = character_data.behavior.move_target[-1]
            if target_position_name == "0":
                target_position_name = _("入口")
            draw_text = _("{0}向{1}移动了\n").format(character_data.name, target_position_name)
            now_draw = draw.NormalDraw()
            now_draw.text = draw_text
            now_draw.width = width
            now_draw.draw()
        map_handle.character_move_scene(
            character_data.position, character_data.behavior.move_target, character_id
        )


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DELETE_FOOD)
def handle_delete_food(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    删除当前行动中的对象食物
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
    if character_data.behavior.target_food is not None:
        food: game_type.Food = character_data.behavior.target_food
        if food.uid in character_data.food_bag:
            del character_data.food_bag[food.uid]


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MAKE_FOOD)
def handle_make_food(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    结算因为制作食物而加好感
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
    if character_data.behavior.target_food is not None:
        food: game_type.Food = character_data.behavior.target_food
        food_name = ""
        make_food_time = 0
        food_name = cache.recipe_data[food.recipe].name
        make_food_time = cache.recipe_data[food.recipe].time
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, 0, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NPC_MAKE_FOOD_TO_SHOP)
def handle_npc_make_food_to_shop(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    NPC随机制作一个食物，并补充到当前所在食物商店中
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 随机选择一个食谱，根据食谱难度，高难度的有高出现权重
    cookable_recipes_list = cooking.get_character_cookable_recipes(character_id, weight_flag=True)
    recipes_id = random.choice(cookable_recipes_list)
    # 获取角色数据与食谱数据
    character_data: game_type.Character = cache.character_data[character_id]
    cook_ability_lv = character_data.ability[43]
    food_recipe: game_type.Recipes = cache.recipe_data[recipes_id]
    # 制作食物
    food_list = {}
    # 每级料理技能等级增加一次制作次数
    for i in range(cook_ability_lv + 1):
        new_food = cooking.cook(food_list, recipes_id, cook_ability_lv, character_data.name)
        # 将食物添加到当前所在食物商店中
        cache.rhodes_island.dining_hall_data.setdefault(str(recipes_id), {})
        cache.rhodes_island.dining_hall_data[str(recipes_id)][new_food.uid] = new_food
    # 将食物名记录到角色数据中
    character_data.behavior.food_name = food_recipe.name


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NPC_MAKE_FOOD_TO_BAG)
def handle_npc_make_food_to_bag(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    NPC随机制作一个食物，并补充到自己背包中
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[character_id]
    # 随机选择一个食谱，根据食谱难度，高难度的有高出现权重
    cookable_recipes_list = cooking.get_character_cookable_recipes(character_id, weight_flag=True)
    recipes_id = random.choice(cookable_recipes_list)
    food_recipe: game_type.Recipes = cache.recipe_data[recipes_id]
    food_list = {}
    new_food = cooking.cook(food_list, recipes_id, character_data.ability[43], character_data.name)
    character_data.food_bag[new_food.uid] = new_food
    character_data.behavior.food_name = food_recipe.name


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DELETE_ALL_FOOD)
def handle_delete_all_food(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    删除背包内所有食物
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
    for food_id in character_data.food_bag.copy():
        food: game_type.Food = character_data.food_bag[food_id]
        del character_data.food_bag[food.uid]


# @settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SOCIAL_FAVORABILITY)
# def handle_add_social_favorability(
#     character_id: int,
#     add_time: int,
#     change_data: game_type.CharacterStatusChange,
#     now_time: datetime.datetime,
# ):
#     """
#     增加社交关系好感
#     Keyword arguments:
#     character_id -- 角色id
#     add_time -- 结算时间
#     change_data -- 状态变更信息记录对象
#     now_time -- 结算的时间
#     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):
#         target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#         if target_data.dead:
#             return
#         if (
#             character_id in target_data.social_contact_data
#             and target_data.social_contact_data[character_id]
#         ):
#             change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
#             target_change = change_data.target_change[target_data.cid]
#             add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
#             add_favorability *= target_data.social_contact_data[character_id]
#             if add_favorability:
#                 character_handle.add_favorability(
#                     character_id, target_data.cid, add_favorability, change_data, target_change, now_time
#                 )


# @settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_INTIMACY_FAVORABILITY)
# def handle_add_intimacy_favorability(
#     character_id: int,
#     add_time: int,
#     change_data: game_type.CharacterStatusChange,
#     now_time: datetime.datetime,
# ):
#     """
#     增加亲密行为好感
#     Keyword arguments:
#     character_id -- 角色id
#     add_time -- 结算时间
#     change_data -- 状态变更信息记录对象
#     now_time -- 结算的时间
#     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):
#         target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#         if target_data.dead:
#             return
#         add_favorability = character.calculation_favorability(
#             character_id, character_data.target_character_id, add_time * 1.5
#         )
#         add_favorability_coefficient = add_favorability / (add_time * 1.5)
#         social = 0
#         if character_id in target_data.social_contact_data:
#             social = target_data.social_contact_data[character_id]
#         change_data.target_change.setdefault(character_data.target_character_id, game_type.TargetChange())
#         target_change = change_data.target_change[target_data.cid]
#         if social >= 2:
#             add_favorability += add_favorability_coefficient * social
#             character_handle.add_favorability(
#                 character_id, target_data.cid, add_favorability, change_data, target_change, now_time
#             )
#         else:
#             add_favorability -= add_favorability_coefficient * social
#             cal_social = social
#             if not cal_social:
#                 cal_social = 1
#             add_disgust = (500 - add_favorability) / cal_social
#             target_data.status.setdefault(12, 0)
#             target_data.status[12] += add_disgust
#             target_change.status.setdefault(12, 0)
#             target_change.status[12] += add_disgust
#             character_handle.add_favorability(
#                 character_id, target_data.cid, add_favorability, change_data, target_change, now_time
#             )


# @settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_INTIMATE_FAVORABILITY)
# def handle_add_intimate_favorability(
#     character_id: int,
#     add_time: int,
#     change_data: game_type.CharacterStatusChange,
#     now_time: datetime.datetime,
# ):
#     """
#     增加私密行为好感
#     Keyword arguments:
#     character_id -- 角色id
#     add_time -- 结算时间
#     change_data -- 状态变更信息记录对象
#     now_time -- 结算的时间
#     """
#     if not add_time:
#         return
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):
#         target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#         if target_data.dead:
#             return
#         add_favorability = character.calculation_favorability(
#             character_id, character_data.target_character_id, add_time * 2
#         )
#         add_favorability_coefficient = add_favorability / (add_time * 2)
#         social = 0
#         if character_id in target_data.social_contact_data:
#             social = target_data.social_contact_data[character_id]
#         change_data.target_change.setdefault(character_data.target_character_id, game_type.TargetChange())
#         target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
#         target_data: game_type.Character = cache.character_data[character_data.target_character_id]
#         if social >= 3:
#             add_favorability += add_favorability_coefficient * social
#             character_handle.add_favorability(
#                 character_id, target_data.cid, add_favorability, change_data, target_change, now_time
#             )
#         else:
#             add_favorability -= add_favorability_coefficient * social
#             cal_social = social
#             if not cal_social:
#                 cal_social = 1
#             add_disgust = (1000 - add_favorability) / cal_social
#             target_data.status.setdefault(12, 0)
#             target_data.status[12] += add_disgust
#             target_change.status.setdefault(12, 0)
#             target_change.status[12] += add_disgust
#             character_handle.add_favorability(
#                 character_id, target_data.cid, add_favorability, change_data, target_change, now_time
#             )


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FIRST_KISS)
def handle_first_kiss(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    记录初吻
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
    # target_data.social_contact_data.setdefault(character_id, 0)

    if character_data.talent[4] == 1:
        character_data.talent[4] = 0
        character_data.first_record.first_kiss_id = target_data.cid
        character_data.first_record.first_kiss_time = cache.game_time
        character_data.first_record.first_kiss_place = character_data.position
        # if (not character_id) or (not target_data.cid):
        # now_draw = draw.NormalDraw()
        # now_draw.text = _("{character_name}博士于{kiss_time}在{kiss_palce}失去了初吻\n").format(
        #     character_name=character_data.name,
        #     kiss_time = str(character_data.first_record.first_kiss_time.month) + "月" + str (character_data.first_record.first_kiss_time.day) + "日",
        #     kiss_palce = attr_text.get_scene_path_text(character_data.first_record.first_kiss_place),
        # )
        # now_draw.width = window_width
        # now_draw.draw()
    if target_data.talent[4] == 1:
        target_data.talent[4] = 0
        target_data.first_record.first_kiss_id = character_id
        target_data.first_record.first_kiss_time = cache.game_time
        target_data.first_record.first_kiss_place = target_data.position
        if (not character_id) or (not target_data.cid):
            # now_draw = draw.NormalDraw()
            # now_draw.text = _("{character_name}于{kiss_time}在{kiss_palce}失去了初吻\n").format(
            #     character_name=target_data.name,
            #     kiss_time = str(target_data.first_record.first_kiss_time.month) + "月" + str (target_data.first_record.first_kiss_time.day) + "日",
            #     kiss_palce = attr_text.get_scene_path_text(target_data.first_record.first_kiss_place),
            # )
            # now_draw.width = window_width
            # now_draw.draw()
            # 初吻的二段结算
            target_data.second_behavior[1050] = 1


# @settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FIRST_HAND_IN_HAND)
# def handle_first_hand_in_hand(
#         character_id: int,
#         add_time: int,
#         change_data: game_type.CharacterStatusChange,
#         now_time: datetime.datetime,
# ):
#     """
#     记录初次牵手
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
#     target_data.social_contact_data.setdefault(character_id, 0)
#     social = 0
#     if character_id in target_data.social_contact_data:
#         social = target_data.social_contact_data[character_id]
#     if social >= 2:
#         if character_data.first_hand_in_hand == -1:
#             character_data.first_kiss = target_data.cid
#         if target_data.first_hand_in_hand == -1:
#             target_data.first_kiss = character_id


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FIRST_SEX)
def handle_first_sex(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    记录处女
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

    item_flag = False

    # 获取玩家最后一个指令的中文名
    behavior_id = cache.pl_pre_behavior_instruce[-1]
    behavior_data = game_config.config_behavior[behavior_id]
    instruct_name = behavior_data.name

    if character_data.talent[5] == 1 and (not item_flag):
        character_data.talent[5] = 0
        character_data.first_record.first_sex_id = target_data.cid
        character_data.first_record.first_sex_time = cache.game_time
        character_data.first_record.first_sex_place = character_data.position
        character_data.first_record.first_sex_posture = instruct_name
        # if (not character_id) or (not target_data.cid):
        # now_draw = draw.NormalDraw()
        # now_draw.text = _("{character_name}博士于{sex_time}在{sex_palce}失去了童贞\n").format(
        #     character_name=character_data.name,
        #     sex_time = str(character_data.first_record.first_sex_time.month) + "月" + str (character_data.first_record.first_sex_time.day) + "日",
        #     sex_palce = attr_text.get_scene_path_text(character_data.first_record.first_sex_place),
        # )
        # now_draw.width = window_width
        # now_draw.draw()
    if target_data.talent[0] == 1:
        target_data.talent[0] = 0
        target_data.first_record.first_sex_id = character_id
        target_data.first_record.first_sex_time = cache.game_time
        target_data.first_record.first_sex_place = target_data.position
        target_data.first_record.first_sex_posture = instruct_name
        target_data.second_behavior[1051] = 1
        # 失去性无知
        if target_data.talent[222] == 1:
            target_data.talent[222] = 0
            now_draw = draw.NormalDraw()
            now_draw.text = _("\n{0}失去了【性无知】\n\n").format(target_data.name)
            now_draw.draw()

        # 处子血胖次
        no_pan_flag = False
        now_draw = draw.NormalDraw()
        if len(target_data.cloth.cloth_wear[9]):
            pan_id = target_data.cloth.cloth_wear[9][-1]
        elif len(target_data.cloth.cloth_off[9]):
            pan_id = target_data.cloth.cloth_off[9][-1]
        # BUG 这一块疑似有BUG，但是未能确定来源，所以先多加个限制条件
        elif character_data.pl_collection.npc_panties_tem.get(character_data.target_character_id):
            pan_id = character_data.pl_collection.npc_panties_tem[character_data.target_character_id][-1]
        else:
            no_pan_flag = True
        if not no_pan_flag:
            pan_name = game_config.config_clothing_tem[pan_id].name
            target_data.cloth.cloth_wear[9] = []
            now_draw.text = _("\n获得了{0}穿着的{1}(沾有处子血)，已自动存入收藏品列表，可在藏物馆查看\n\n").format(target_data.name, pan_name)
            now_draw.draw()
            character_data.pl_collection.first_panties[character_data.target_character_id] = _("{0}(沾有处子血)").format(pan_name)
        else:
            now_draw.text = _("\n{0}的处子血滴了下去，被你谨慎地用试管接了一滴，已自动存入收藏品列表，可在藏物馆查看\n\n").format(target_data.name)
            character_data.pl_collection.first_panties[
                character_data.target_character_id] = _("一滴{0}的处子血").format(target_data.name)
            now_draw.draw()

        # 道具破处
        if item_flag:
            target_data.first_record.first_sex_item = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FIRST_A_SEX)
def handle_first_a_sex(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    记录A处女
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

    # 判定是否为道具性交
    item_flag = False
    if cache.input_cache[len(cache.input_cache) - 1] == str(constant.Instruct.VIBRATOR_INSERTION_ANAL):
        item_flag = True

    # 获取玩家最后一个指令的中文名
    behavior_id = cache.pl_pre_behavior_instruce[-1]
    behavior_data = game_config.config_behavior[behavior_id]
    instruct_name = behavior_data.name

    if character_data.talent[5] == 1 and (not item_flag):
        character_data.talent[5] = 0
        character_data.first_record.first_sex_id = target_data.cid
        character_data.first_record.first_sex_time = cache.game_time
        character_data.first_record.first_sex_place = character_data.position
        character_data.first_record.first_sex_posture = instruct_name
        # if (not character_id) or (not target_data.cid):
        # now_draw = draw.NormalDraw()
        # now_draw.text = _("{character_name}博士于{sex_time}在{sex_palce}失去了童贞\n").format(
        #     character_name=character_data.name,
        #     sex_time = str(character_data.first_record.first_sex_time.month) + "月" + str (character_data.first_record.first_sex_time.day) + "日",
        #     sex_palce = attr_text.get_scene_path_text(character_data.first_record.first_sex_place),
        # )
        # now_draw.width = window_width
        # now_draw.draw()
    if target_data.talent[1] == 1:
        target_data.talent[1] = 0
        target_data.first_record.first_a_sex_id = character_id
        target_data.first_record.first_a_sex_time = cache.game_time
        target_data.first_record.first_a_sex_place = target_data.position
        target_data.first_record.first_a_sex_posture = instruct_name
        if item_flag:
            target_data.first_record.first_a_sex_item = 1
        if (not character_id) or (not target_data.cid):
            # now_draw = draw.NormalDraw()
            # now_draw.text = _("{character_name}于{a_sex_time}在{a_sex_palce}失去了A处女\n").format(
            #     character_name=target_data.name,
            #     a_sex_time = str(target_data.first_record.first_a_sex_time.month) + "月" + str (target_data.first_record.first_a_sex_time.day) + "日",
            #     a_sex_palce = attr_text.get_scene_path_text(target_data.first_record.first_a_sex_place),
            # )
            # now_draw.width = window_width
            # now_draw.draw()
            # 处女的二段结算
            target_data.second_behavior[1052] = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DAY_FIRST_MEET_0)
def handle_day_first_meet_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己变为今天已见过面
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
    character_data.first_record.day_first_meet = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DAY_FIRST_MEET_1)
def handle_day_first_meet_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己变为今天未见过面
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
    character_data.first_record.day_first_meet = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FIRST_KISS_TO_PENIS)
def handle_first_kiss_to_penis(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    记录阴茎初吻
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
    # target_data.social_contact_data.setdefault(character_id, 0)
    if character_data.target_character_id == character_id:
        return

    if target_data.talent[4] == 1:
        target_data.talent[4] = 0
        target_data.first_record.first_kiss_id = character_id
        target_data.first_record.first_kiss_time = cache.game_time
        target_data.first_record.first_kiss_place = target_data.position
        target_data.first_record.first_kiss_body_part = 1
        if (not character_id) or (not target_data.cid):
            # 初吻的二段结算
            target_data.second_behavior[1050] = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENETRATING_VISION_ON)
def handle_penetrating_vision_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    开启透视（含理智消耗）
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
    character_data.pl_ability.visual = True
    character_data.sanity_point = max(character_data.sanity_point - 1, 0)
    change_data.sanity_point -= 1
    character_data.pl_ability.today_sanity_point_cost += 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENETRATING_VISION_OFF)
def handle_penetrating_vision_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    关闭透视
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
    character_data.pl_ability.visual = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HORMONE_ON)
def handle_hormone_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    开启信息素
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
    character_data.pl_ability.hormone = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HORMONE_OFF)
def handle_hormone_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    关闭信息素
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
    character_data.pl_ability.hormone = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HYPNOSIS_ONE)
def handle_hypnosis_one(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    单人催眠（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
     """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    change_data.target_change.setdefault(target_character_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_character_data.cid]
    if character_data.dead:
        return
    # 结算理智消耗
    santi_down = originium_arts.calculate_hypnosis_sanity_cost(character_data.target_character_id)
    character_data.sanity_point = max(character_data.sanity_point - santi_down, 0)
    change_data.sanity_point -= santi_down
    character_data.pl_ability.today_sanity_point_cost += santi_down
    # 结算催眠度增加
    hypnosis_degree_grow = originium_arts.hypnosis_degree_calculation(character_data.target_character_id)
    # debug下催眠增加到999
    if cache.debug_mode:
        hypnosis_degree_grow = 999
    new_hypnosis_degree = target_character_data.hypnosis.hypnosis_degree + hypnosis_degree_grow
    # 赋予到角色数据
    target_character_data.hypnosis.hypnosis_degree = min(new_hypnosis_degree, originium_arts.hypnosis_degree_limit_calculation())
    target_change.hypnosis_degree += hypnosis_degree_grow
    # 判断催眠完成
    originium_arts.evaluate_hypnosis_completion(character_data.target_character_id)
    # 判断是否理智已耗尽导致催眠结束
    if character_data.sanity_point == 0 and target_character_data.sp_flag.unconscious_h:
        # 空气催眠则重置催眠地点和解开门锁
        if target_character_data.sp_flag.unconscious_h == 5:
            character_data.pl_ability.air_hypnosis_position = ""
        target_character_data.sp_flag.unconscious_h = 0
        now_draw = draw.NormalDraw()
        now_draw.text = _("\n{0}的理智耗尽，催眠结束\n\n").format(character_data.name)
        now_draw.draw()

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HYPNOSIS_ALL)
def handle_hypnosis_all(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    集体催眠（含理智消耗）
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
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    scene_character_list = scene_data.character_list.copy()
    # 催眠角色列表
    hypnosis_character_list = []
    # 去掉里的自己
    if character_id in scene_character_list:
        scene_character_list.remove(character_id)
    # 基础理智消耗
    sanity_point_cost = 10
    # 遍历角色列表
    for target_id in scene_character_list:
        # 计算理智消耗
        santi_down = originium_arts.calculate_hypnosis_sanity_cost(target_id)
        sanity_point_cost += santi_down
        hypnosis_character_list.append(target_id)
        # 如果超出了现有理智，则取现有理智
        if sanity_point_cost >= character_data.sanity_point:
            sanity_point_cost = min(sanity_point_cost, character_data.sanity_point)
            break
    # 结算理智消耗
    character_data.sanity_point = max(character_data.sanity_point - sanity_point_cost, 0)
    change_data.sanity_point -= sanity_point_cost
    character_data.pl_ability.today_sanity_point_cost += sanity_point_cost
    # 遍历催眠角色列表
    for target_id in hypnosis_character_list:
        target_character_data = cache.character_data[target_id]
        change_data.target_change.setdefault(target_character_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_character_data.cid]
        if target_character_data.dead:
            continue
        # 结算催眠度增加
        hypnosis_degree_grow = originium_arts.hypnosis_degree_calculation(target_id)
        # debug下催眠增加到999
        if cache.debug_mode:
            hypnosis_degree_grow = 999
        new_hypnosis_degree = target_character_data.hypnosis.hypnosis_degree + hypnosis_degree_grow
        # 赋予到角色数据
        target_character_data.hypnosis.hypnosis_degree = min(new_hypnosis_degree, originium_arts.hypnosis_degree_limit_calculation())
        target_change.hypnosis_degree += hypnosis_degree_grow
        # 判断催眠完成
        originium_arts.evaluate_hypnosis_completion(target_id)
    # 判断是否理智已耗尽导致催眠结束
    if character_data.sanity_point == 0:
        for target_id in scene_character_list:
            target_character_data = cache.character_data[target_id]
            # 空气催眠则重置催眠地点和解开门锁
            if target_character_data.sp_flag.unconscious_h == 5:
                character_data.pl_ability.air_hypnosis_position = ""
            target_character_data.sp_flag.unconscious_h = 0
            now_draw = draw.NormalDraw()
            now_draw.text = _("\n{0}的理智耗尽，催眠结束\n\n").format(character_data.name)
            now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HYPNOSIS_CANCEL)
def handle_hypnosis_cancel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    解除交互对象的催眠
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
     """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    if target_character_data.sp_flag.unconscious_h >= 4:
        target_character_data.sp_flag.unconscious_h = 0
    # 空气催眠则重置催眠地点和解开门锁
    if target_character_data.sp_flag.unconscious_h == 5:
        character_data.pl_ability.air_hypnosis_position = ""
    # 去掉大部分的心体催眠状态
    target_character_data.hypnosis.increase_body_sensitivity = False
    target_character_data.hypnosis.blockhead = False
    target_character_data.hypnosis.active_h = False
    target_character_data.hypnosis.roleplay = 0
    # 结算二段行为
    handle_npc_ai_in_h.settle_unconscious_semen_and_cloth(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_INCREASE_BODY_SENSITIVITY_ON)
def handle_target_hypnosis_increase_body_sensitivity_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方开启体控-敏感度提升（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
     """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    santi_down = 10
    target_character_data.hypnosis.increase_body_sensitivity = True
    character_data.sanity_point = max(character_data.sanity_point - santi_down, 0)
    change_data.sanity_point -= santi_down
    character_data.pl_ability.today_sanity_point_cost += santi_down


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_INCREASE_BODY_SENSITIVITY_OFF)
def handle_target_hypnosis_increase_body_sensitivity_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方关闭体控-敏感度提升
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
     """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.hypnosis.increase_body_sensitivity = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_FORCE_CLIMAX)
def handle_target_hypnosis_force_climax(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方开启体控-强制高潮（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
     """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    character_data.sanity_point = max(character_data.sanity_point - 50, 0)
    change_data.sanity_point -= 50
    character_data.pl_ability.today_sanity_point_cost += 50

    base_chara_climix_common_settle(character_data.target_character_id, 4, change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_FORCE_OVULATION_ON)
def handle_target_hypnosis_force_ovulation_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方开启体控-强制排卵（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
     """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    santi_down = 10
    target_character_data.hypnosis.force_ovulation = True
    character_data.sanity_point = max(character_data.sanity_point - santi_down, 0)
    change_data.sanity_point -= santi_down
    character_data.pl_ability.today_sanity_point_cost += santi_down


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_FORCE_OVULATION_OFF)
def handle_target_hypnosis_force_ovulation_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方关闭体控-强制排卵
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
     """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.hypnosis.force_ovulation = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_BLOCKHEAD_SWITCH_CHANGE)
def handle_target_hypnosis_blockhead_switch_change(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方切换体控-木头人开关（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    if target_character_data.hypnosis.blockhead:
        target_character_data.hypnosis.blockhead = False
    else:
        target_character_data.hypnosis.blockhead = True
        santi_down = 10
        character_data.sanity_point = max(character_data.sanity_point - santi_down, 0)
        change_data.sanity_point -= santi_down
        character_data.pl_ability.today_sanity_point_cost += santi_down


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_BLOCKHEAD_OFF)
def handle_target_hypnosis_blockhead_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方关闭体控-木头人
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.hypnosis.blockhead = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_ACTIVE_H_SWITCH_CHANGE)
def handle_target_hypnosis_active_h_switch_change(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方切换体控-逆推开关（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    if target_character_data.hypnosis.active_h:
        target_character_data.hypnosis.active_h = False
        target_character_data.h_state.npc_active_h = False
    else:
        target_character_data.hypnosis.active_h = True
        target_character_data.h_state.npc_active_h = True
        santi_down = 10
        character_data.sanity_point = max(character_data.sanity_point - santi_down, 0)
        change_data.sanity_point -= santi_down
        character_data.pl_ability.today_sanity_point_cost += santi_down
        handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_H)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_ACTIVE_H_OFF)
def handle_target_hypnosis_active_h_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方关闭体控-逆推
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.hypnosis.active_h = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_PAIN_AS_PLEASURE_SWITCH_CHANGE)
def handle_target_hypnosis_pain_as_pleasure_switch_change(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方切换心控-苦痛快感化开关（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    if target_character_data.hypnosis.pain_as_pleasure:
        target_character_data.hypnosis.pain_as_pleasure = False
    else:
        target_character_data.hypnosis.pain_as_pleasure = True
        santi_down = 10
        character_data.sanity_point = max(character_data.sanity_point - santi_down, 0)
        change_data.sanity_point -= santi_down
        character_data.pl_ability.today_sanity_point_cost += santi_down


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HYPNOSIS_PAIN_AS_PLEASURE_OFF)
def handle_target_hypnosis_active_h_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方关闭心控-苦痛快感化
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.hypnosis.pain_as_pleasure = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TIME_STOP_ON)
def handle_time_stop_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    开启时停
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    cache.time_stop_mode = True
    for chara_id in cache.npc_id_got:
        chara_data = cache.character_data[chara_id]
        chara_data.sp_flag.unconscious_h = 3
        # 重置时停中的角色的时停高潮计数
        for body_part in game_config.config_body_part:
            chara_data.h_state.time_stop_orgasm_count[body_part] = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TIME_STOP_OFF)
def handle_time_stop_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    关闭时停
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    cache.time_stop_mode = False
    for chara_id in cache.npc_id_got:
        chara_data = cache.character_data[chara_id]
        chara_data.sp_flag.unconscious_h = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_BE_CARRIED_IN_TIME_STOP)
def handle_target_be_carried_in_time_stop(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象变成被时停搬运状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id == character_id:
        return
    character_data.pl_ability.carry_chara_id_in_time_stop = character_data.target_character_id


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NOT_BE_CARRIED_IN_TIME_STOP)
def handle_target_not_be_carried_in_time_stop(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    清零自己的当前时停搬运对象
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.pl_ability.carry_chara_id_in_time_stop = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_BE_FREE_IN_TIME_STOP)
def handle_target_be_free_in_time_stop(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    将交互对象设为时停中自由状态（含理智消耗）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.pl_ability.free_in_time_stop_chara_id = character_data.target_character_id
    character_data.sanity_point = max(character_data.sanity_point - 50, 0)
    change_data.sanity_point -= 50
    character_data.pl_ability.today_sanity_point_cost += 50


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NOT_BE_FREE_IN_TIME_STOP)
def handle_target_not_be_free_in_time_stop(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    清零自己的让某人时停中自由状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.pl_ability.free_in_time_stop_chara_id = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NPC_ACTIVE_H_ON)
def handle_npc_active_h_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己开启主动H
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
    character_data.h_state.npc_active_h = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NPC_ACTIVE_H_OFF)
def handle_npc_active_h_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己关闭主动H
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
    character_data.h_state.npc_active_h = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NPC_ACTIVE_H_ON)
def handle_target_npc_active_h_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方开启主动H
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.h_state.npc_active_h = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NPC_ACTIVE_H_OFF)
def handle_target_npc_active_h_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    对方关闭主动H
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.h_state.npc_active_h = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PL_JUST_SHOOT_ON)
def handle_pl_just_shoot_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    玩家变为前指令刚刚射精状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    pl_character_data: game_type.Character = cache.character_data[0]
    pl_character_data.h_state.just_shoot = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PL_JUST_SHOOT_OFF)
def handle_pl_just_shoot_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    玩家清零前指令刚刚射精状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    pl_character_data: game_type.Character = cache.character_data[0]
    pl_character_data.h_state.just_shoot = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PL_CONDOM_USE_RESET)
def handle_pl_condom_use_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    重置玩家的避孕套使用状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    pl_character_data: game_type.Character = cache.character_data[0]
    pl_character_data.h_state.condom_count = [0, 0]


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_CONDOM_INFO_SHOW_FLAG_ON)
def handle_self_condom_info_show_flag_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己开启避孕套信息显示
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.h_state.condom_info_show_flag = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TAGET_CONDOM_INFO_SHOW_FLAG_ON)
def handle_target_condom_info_show_flag_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象开启避孕套信息显示
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_self_condom_info_show_flag_on(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_CONDOM_INFO_SHOW_FLAG_ON)
def handle_scene_all_characters_condom_info_show_flag_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有角色开启避孕套信息显示
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        # 遍历非玩家的角色
        if chara_id:
            handle_target_condom_info_show_flag_on(chara_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_ORGASM_EDGE_ON)
def handle_self_orgasm_edge_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己开启绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.h_state.orgasm_edge = 1
    for body_part in game_config.config_body_part:
        character_data.h_state.orgasm_edge_count[body_part] = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_ORGASM_EDGE_OFF)
def handle_self_orgasm_edge_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己关闭绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.h_state.orgasm_edge = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ORGASM_EDGE_ON)
def handle_target_orgasm_edge_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象开启绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_self_orgasm_edge_on(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ORGASM_EDGE_OFF)
def handle_target_orgasm_edge_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象关闭绝顶寸止
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_self_orgasm_edge_off(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ALL_GROUP_SEX_TEMPLE_ON)
def handle_all_group_sex_temple_run_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    开启全群交模板，进行轮流群交
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.all_group_sex_temple_run = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ALL_GROUP_SEX_TEMPLE_OFF)
def handle_all_group_sex_temple_run_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    关闭全群交模板，进行单轮群交
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.all_group_sex_temple_run = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_JOIN_GROUP_SEX_ON)
def handle_self_join_group_sex_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己开始加入群交
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.go_to_join_group_sex = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_JOIN_GROUP_SEX_OFF)
def handle_self_join_group_sex_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己停止加入群交
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.go_to_join_group_sex = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_GET_WEEKNESSS_BY_DR)
def handle_target_get_weeknesss_by_dr(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象获得[被博士持有把柄]
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_character_data.talent[402] = 1
    now_draw = draw.NormalDraw()
    now_draw.width = width
    now_draw.text = _("\n{0}获得了【被博士持有把柄】\n").format(target_character_data.name)
    now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ENTER_WAITING_FOR_PHYSICAL_EXAM)
def handle_enter_waiting_for_physical_exam(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己进入等待体检状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id not in cache.rhodes_island.waiting_for_exam_operator_ids:
        cache.rhodes_island.waiting_for_exam_operator_ids.add(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.EXIT_WAITING_FOR_PHYSICAL_EXAM)
def handle_exit_waiting_for_physical_exam(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己退出等待体检状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id in cache.rhodes_island.waiting_for_exam_operator_ids:
        cache.rhodes_island.waiting_for_exam_operator_ids.remove(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WAIT_UNITL_TRAGET_ACTION_END)
def handle_wait_unitl_traget_action_end(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    玩家等待至交互对象行动结束
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    from Script.Design import update
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    if character_data.dead:
        return
    target_start_time = target_character_data.behavior.start_time
    target_end_time = game_time.get_sub_date(target_character_data.behavior.duration, old_date=target_start_time)
    # 到结束时间还有多少分钟
    add_time = int((target_end_time.timestamp() - now_time.timestamp()) / 60)
    character_data: game_type.Character = cache.character_data[0]
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.state = constant.CharacterStatus.STATUS_WAIT
    character_data.behavior.duration = add_time
    update.game_update_flow(add_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WAIT_UNITL_PLAYER_ACTION_END)
def handle_wait_unitl_player_action_end(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己等待至玩家行动结束
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data = cache.character_data[0]
    if character_data.dead:
        return
    player_action_start_time = pl_character_data.behavior.start_time
    player_action_end_time = game_time.get_sub_date(pl_character_data.behavior.duration, old_date=player_action_start_time)
    # 到结束时间还有多少分钟
    add_time = int((player_action_end_time.timestamp() - now_time.timestamp()) / 60)
    character_data.behavior.behavior_id = constant.Behavior.WAIT
    character_data.state = constant.CharacterStatus.STATUS_WAIT
    character_data.behavior.duration = add_time + 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SET_TARGET_FOOD_FROM_BAG_LAST)
def handle_set_target_food_from_bag_last(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    将自己行为目标食物指定为背包里的最后一个食物
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if len(character_data.food_bag) == 0:
        return
    # 获取背包最后一个食物
    last_key = list(character_data.food_bag.keys())[-1]
    now_food = character_data.food_bag[last_key]
    character_data.behavior.food_name = now_food.name
    character_data.behavior.food_seasoning = now_food.special_seasoning
    character_data.behavior.food_quality = now_food.quality
    character_data.behavior.target_food = now_food


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FACILITY_DAMAGE_CHECK)
def handle_facility_damage_check(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    几率判定自己所在地点是否造成损坏
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 获取当前位置
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    # 计算已损坏次数
    damage_count = 0
    if scene_path_str in cache.rhodes_island.facility_damage_data:
        damage_count = cache.rhodes_island.facility_damage_data[scene_path_str]
    # 计算损坏几率
    damage_rate = 1 / (2 ** damage_count)
    damage_rate = max(damage_rate, 0)
    # 掷骰子
    if random.random() < (damage_rate / 100):
        # 损坏
        damage_count += 1
        cache.rhodes_island.facility_damage_data[scene_path_str] = damage_count


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_MEDIUM_HIT_POINT)
def handle_add_medium_hit_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加中量体力
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
    add_hit_point = add_time * (20 + character_data.hit_point_max * 0.01)
    character_data.hit_point += add_hit_point
    if character_data.hit_point > character_data.hit_point_max:
        add_hit_point -= character_data.hit_point - character_data.hit_point_max
        character_data.hit_point = character_data.hit_point_max
    change_data.hit_point += add_hit_point


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_MEDIUM_MANA_POINT)
def handle_add_medium_mana_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加中量气力
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
    add_mana_point = add_time * (30 + character_data.hit_point_max * 0.02)
    character_data.mana_point += add_mana_point
    if character_data.mana_point > character_data.mana_point_max:
        add_mana_point -= character_data.mana_point - character_data.mana_point_max
        character_data.mana_point = character_data.mana_point_max
    change_data.mana_point += add_mana_point


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.INTERRUPT_TARGET_ACTIVITY)
def handle_interrupt_target_activity(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    打断交互目标活动
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
    if target_data.dead:
        return
    if character_data.target_character_id == 0:
        return
    # if target_data.behavior.behavior_id == constant.Behavior.DEAD:
    #     return
    if target_data.behavior.behavior_id:
        if target_data.behavior.start_time <= character_data.behavior.start_time:
            target_end_time = game_time.get_sub_date(
                target_data.behavior.duration, old_date=target_data.behavior.start_time
            )
            if target_end_time >= character_data.behavior.start_time:
                if target_data.behavior.behavior_id == constant.Behavior.MOVE:
                    target_data.behavior = game_type.Behavior()
                    target_data.state = constant.CharacterStatus.STATUS_ARDER
                    instuct_judege.init_character_behavior_start_time(
                        target_data.cid, character_data.behavior.start_time
                    )
                else:
                    settle_behavior.handle_settle_behavior(
                        target_data.cid, character_data.behavior.start_time
                    )


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.OPTION_FATER)
def handle_option_fater(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    开启子选项面板
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    event_option_panel.line_feed.draw()
    now_draw = event_option_panel.Event_option_Panel(character_id, width)
    now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_TO_PLAYER)
def handle_target_to_player(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象设为对玩家交互
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.OPEN_INSTRUCT_FILTER_H)
def handle_open_instruct_filter_h(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    开启H面板过滤器（已弃用）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    handle_instruct.instruct_filter_H_change(True)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CLOSE_INSTRUCT_FILTER_H)
def handle_close_instruct_filter_h(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    关闭H面板过滤器（已弃用）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    handle_instruct.instruct_filter_H_change(False)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_THIS_EVENT_TO_TRIGGERED_RECORD)
def handle_add_this_event_to_already_triggered(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    将玩家当前触发的事件加入总次数已触发记录
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    player_character_data: game_type.Character = cache.character_data[0]
    if player_character_data.event.son_event_id:
        cache.taiggered_event_record.add(player_character_data.event.son_event_id)
    else:
        cache.taiggered_event_record.add(player_character_data.event.event_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_THIS_EVENT_TO_TODAY_TRIGGERED_RECORD)
def handle_add_this_event_to_today_already_triggered(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    将玩家当前触发的事件加入今日已触发记录
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    player_character_data: game_type.Character = cache.character_data[0]
    if player_character_data.event.son_event_id:
        cache.today_taiggered_event_record.add(player_character_data.event.son_event_id)
    else:
        cache.today_taiggered_event_record.add(player_character_data.event.event_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GROUP_SEX_MODE_ON)
def handle_group_sex_mode_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    开启群交模式
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    cache.group_sex_mode = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GROUP_SEX_MODE_OFF)
def handle_group_sex_mode_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    关闭群交模式
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    cache.group_sex_mode = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PL_TARGET_TO_ME)
def handle_pl_target_to_me(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    将玩家的交互对象设为自己
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    pl_character_data: game_type.Character = cache.character_data[0]
    pl_character_data.target_character_id = character_id


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_TO_SELF)
def handle_target_to_self(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    将交互对象设为对自己交互
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.target_character_id = character_id


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_TO_MASTUREBATE)
def handle_target_to_masturebate(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    将交互对象设为对当前场景中的首位自慰角色
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data = cache.character_data[character_id]
    now_position = character_data.position
    now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_scene_str]
    if len(now_scene_data.character_list) >= 2:
        # 遍历当前角色列表
        for chara_id in now_scene_data.character_list:
            # 遍历非自己且非玩家的角色
            if chara_id != character_id and chara_id != 0:
                other_character_data: game_type.Character = cache.character_data[chara_id]
                # 检测是否在自慰
                if other_character_data.behavior.behavior_id == constant.Behavior.MASTUREBATE:
                    character_data.target_character_id = chara_id
                    break


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.NOT_TIRED)
def handle_not_tired(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    从疲劳中恢复
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.tired = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ITEM_OFF)
def handle_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    去掉身上所有的道具（含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    for i in range(len(character_data.h_state.body_item)):
        character_data.h_state.body_item[i][1] = False
        character_data.h_state.body_item[i][2] = None


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ITEM_OFF)
def handle_target_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉身上所有的道具（含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_item_off(character_data.target_character_id, add_time, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ITEM_OFF_EXCEPT_PILL)
def handle_item_off_except_pill(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    去掉身上所有的H道具（不含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    for i in range(len(character_data.h_state.body_item)):
        if i in {8,9,10,11,12}:
            continue
        character_data.h_state.body_item[i][1] = False
        character_data.h_state.body_item[i][2] = None


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ITEM_OFF_EXCEPT_PILL)
def handle_target_item_off_except_pill(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉身上所有的道具（不含药品）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_item_off_except_pill(character_data.target_character_id, add_time, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_B_ITEM_OFF)
def handle_target_b_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉B部位的道具
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
    for i in [0, 4]:
        target_data.h_state.body_item[i][1] = False
        target_data.h_state.body_item[i][2] = None


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_A_ITEM_OFF)
def handle_target_a_item_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象去掉A部位的道具
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
    for i in [3, 7]:
        target_data.h_state.body_item[i][1] = False
        target_data.h_state.body_item[i][2] = None


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_N_FEEL)
def handle_target_add_small_n_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｎ快（N感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    base_chara_state_common_settle(character_data.target_character_id, add_time, 0, 50, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_B_FEEL)
def handle_target_add_small_b_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｂ快（B感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    base_chara_state_common_settle(character_data.target_character_id, add_time, 1, 50, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_C_FEEL)
def handle_target_add_small_c_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｃ快（C感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    base_chara_state_common_settle(character_data.target_character_id, add_time, 2, 50, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_P_FEEL)
def handle_target_add_small_p_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｐ快（P感补正）
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(3, 0)
    now_lust = target_data.status_data[3]
    now_lust_multiple = 30
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[3])
    now_add_lust *= adjust
    target_data.eja_point += now_add_lust
    # change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    # target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    # target_change.eja_point.setdefault(3, 0)
    # target_change.eja_point += now_add_lust
    target_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_V_FEEL)
def handle_target_add_small_v_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｖ快（V感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    base_chara_state_common_settle(character_data.target_character_id, add_time, 4, 50, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_A_FEEL)
def handle_target_add_small_a_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ａ快（A感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    base_chara_state_common_settle(character_data.target_character_id, add_time, 5, 50, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_U_FEEL)
def handle_target_add_small_u_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｕ快（U感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    base_chara_state_common_settle(character_data.target_character_id, add_time, 6, 50, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_W_FEEL)
def handle_target_add_small_w_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｗ快（W感补正）
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    base_chara_state_common_settle(character_data.target_character_id, add_time, 7, 50, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_LUBRICATION)
def handle_target_add_small_lubrication(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量润滑（欲望补正）
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
    base_chara_state_common_settle(character_data.target_character_id, add_time, 8, ability_level = target_data.ability[33], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_BODY_LUBRICANT)
def handle_use_body_lubricant(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个润滑液
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[100] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_HUGE_LUBRICATION)
def handle_target_add_huge_lubrication(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加大量润滑（润滑液）
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(8, 0)
    now_lust = target_data.status_data[8]
    now_lust_multiple = 10000 - int(now_lust *0.1)
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    target_data.status_data[8] = min(99999, target_data.status_data[8])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_PHILTER)
def handle_use_philter(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个媚药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[103] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_HUGE_DESIRE_AND_SUBMIT)
def handle_target_add_huge_desire_and_submit(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加大量欲情和屈服和欲望值（媚药）
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
    if target_data.dead:
        return

    # 欲情
    target_data.status_data.setdefault(12, 0)
    now_lust = target_data.status_data[12]
    now_lust_multiple = 10000 - int(now_lust *0.016) 
    now_add_lust = now_lust_multiple
    target_data.status_data[12] += now_add_lust
    target_data.status_data[12] = min(99999, target_data.status_data[12])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(12, 0)
    target_change.status_data[12] += now_add_lust

    # 屈服
    target_data.status_data.setdefault(15, 0)
    now_lust = target_data.status_data[15]
    now_lust_multiple = 10000 - int(now_lust *0.016) 
    now_add_lust = now_lust_multiple
    target_data.status_data[15] += now_add_lust
    target_data.status_data[15] = min(99999, target_data.status_data[15])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(15, 0)
    target_change.status_data[15] += now_add_lust

    # 欲望值
    target_data.desire_point = 100

@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_ENEMAS)
def handle_use_enemas(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个灌肠液
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[104] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ENEMA)
def handle_target_enema(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象A灌肠并增加中量润滑
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
    if target_data.dead:
        return

    # 增加润滑
    target_data.status_data.setdefault(8, 0)
    now_lust = target_data.status_data[8]
    now_lust_multiple = 2500 - int(now_lust *0.04) 
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    target_data.status_data[8] = min(99999, target_data.status_data[8])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

    # 根据A扩张和当前灌肠液量来判定苦痛程度
    ability_lv = target_data.ability[10]
    ability_adjust = attr_calculation.get_ability_adjust(ability_lv)
    enema_capacity = target_data.dirty.enema_capacity
    enema_capacity_adjust = 2 ** (enema_capacity + 1)
    extra_adjust = enema_capacity_adjust / ability_adjust
    base_chara_state_common_settle(character_data.target_character_id, add_time, 17, base_value = 1000, ability_level = target_data.ability[15], extra_adjust = extra_adjust, change_data_to_target_change = change_data)

    # A灌肠
    target_data.dirty.a_clean = 1
    target_data.dirty.enema_capacity += 1
    target_data.dirty.enema_capacity = min(6, target_data.dirty.enema_capacity)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ENEMA_END)
def handle_target_enema_end(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象结束A灌肠并增加中量润滑
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
    if target_data.dead:
        return

    # 增加润滑
    target_data.status_data.setdefault(8, 0)
    now_lust = target_data.status_data[8]
    now_lust_multiple = 2500 - int(now_lust *0.04) 
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    target_data.status_data[8] = min(99999, target_data.status_data[8])
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

    # A灌肠结束
    if target_data.dirty.a_clean == 1:
        target_data.dirty.a_clean = 2
    elif target_data.dirty.a_clean == 3:
        target_data.dirty.a_clean = 4
        # 清空肠内精液量的90%
        now_semen_data = character_data.dirty.body_semen[8]
        semen_num = now_semen_data[1] * 0.9
        if semen_num > 1:
            now_semen_data[1] -= semen_num
            now_semen_data[2] = attr_calculation.get_semen_now_level(now_semen_data[1], 8, 0)
            # 绘制提示信息
            info_text  = _("{0}的后穴喷出了{1}ml的精液\n").format(target_data.name, int(semen_num))
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = width
            info_draw.draw()
    # 清空灌肠液量
    target_data.dirty.enema_capacity = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NIPPLE_CLAMP_ON)
def handle_target_nipple_clamp_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上乳头夹
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
    target_data.h_state.body_item[0][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NIPPLE_CLAMP_OFF)
def handle_target_nipple_clamp_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下乳头夹
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
    target_data.h_state.body_item[0][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_CLIT_CLAMP_ON)
def handle_target_clit_clamp_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上阴蒂夹
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
    target_data.h_state.body_item[1][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_CLIT_CLAMP_OFF)
def handle_target_clit_clamp_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下阴蒂夹
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
    target_data.h_state.body_item[1][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_VIBRATOR_ON)
def handle_target_vibrator_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象插入V震动棒
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
    target_data.h_state.body_item[2][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_VIBRATOR_OFF)
def handle_target_vibrator_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象拔出V震动棒
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
    target_data.h_state.body_item[2][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_VIBRATOR_ON)
def handle_target_anal_vibrator_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象插入A震动棒
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
    target_data.h_state.body_item[3][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_VIBRATOR_OFF)
def handle_target_anal_vibrator_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象拔出A震动棒
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
    target_data.h_state.body_item[3][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_BEADS_ON)
def handle_target_anal_beads_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象塞入肛门拉珠
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
    target_data.h_state.body_item[7][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANAL_BEADS_OFF)
def handle_target_anal_beads_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象拔出肛门拉珠
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
    target_data.h_state.body_item[7][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MILKING_MACHINE_ON)
def handle_target_milking_machine_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上搾乳机
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
    target_data.h_state.body_item[4][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MILKING_MACHINE_OFF)
def handle_target_milking_machine_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下搾乳机
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
    target_data.h_state.body_item[4][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_URINE_COLLECTOR_ON)
def handle_target_urine_collector_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上采尿器
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
    target_data.h_state.body_item[5][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_URINE_COLLECTOR_OFF)
def handle_target_urine_collector_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下采尿器
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
    target_data.h_state.body_item[5][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_PATCH_ON)
def handle_target_patch_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象戴上眼罩
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
    target_data.h_state.body_item[6][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_PATCH_OFF)
def handle_target_patch_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象取下眼罩
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
    target_data.h_state.body_item[6][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_GAG_ON)
def handle_target_gag_on(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象戴上口球
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
    target_data.h_state.body_item[14][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_GAG_OFF)
def handle_target_gag_off(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象取下口球
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
    target_data.h_state.body_item[14][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADJUST_BODY_MANAGE_DAY_ITEM)
def handle_adjust_body_manage_day_item(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    调整自己的身体管理_白天道具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id == 0:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 这里把交互对象设为自己是因为下面的装备/取下道具函数都是让交互对象结算的
    character_data.target_character_id = character_id
    # 身体管理_乳头夹
    if handle_premise.handle_ask_equp_nipple_clamp_in_day(character_id) and not handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_nipple_clamp_in_day(character_id) and handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_阴蒂夹
    if handle_premise.handle_ask_equp_clit_clamp_in_day(character_id) and not handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_clit_clamp_in_day(character_id) and handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_V振动棒
    if handle_premise.handle_ask_equp_v_bibrator_in_day(character_id) and not handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_v_bibrator_in_day(character_id) and handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_off(character_id, add_time, change_data, now_time)
    # 身体管理_A振动棒
    if handle_premise.handle_ask_equp_a_bibrator_in_day(character_id) and not handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_a_bibrator_in_day(character_id) and handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_off(character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADJUST_BODY_MANAGE_SLEEP_ITEM)
def handle_adjust_body_manage_sleep_item(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    调整自己的身体管理_睡觉道具
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id == 0:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 这里把交互对象设为自己是因为下面的装备/取下道具函数都是让交互对象结算的
    character_data.target_character_id = character_id
    # 身体管理_乳头夹
    if handle_premise.handle_ask_equp_nipple_clamp_in_sleep(character_id) and not handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_nipple_clamp_in_sleep(character_id) and handle_premise.handle_self_now_nipple_clamp(character_id):
        handle_target_nipple_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_阴蒂夹
    if handle_premise.handle_ask_equp_clit_clamp_in_sleep(character_id) and not handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_clit_clamp_in_sleep(character_id) and handle_premise.handle_self_now_clit_clamp(character_id):
        handle_target_clit_clamp_off(character_id, add_time, change_data, now_time)
    # 身体管理_V振动棒
    if handle_premise.handle_ask_equp_v_bibrator_in_sleep(character_id) and not handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_v_bibrator_in_sleep(character_id) and handle_premise.handle_self_now_vibrator_insertion(character_id):
        handle_target_vibrator_off(character_id, add_time, change_data, now_time)
    # 身体管理_A振动棒
    if handle_premise.handle_ask_equp_a_bibrator_in_sleep(character_id) and not handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_on(character_id, add_time, change_data, now_time)
    elif not handle_premise.handle_ask_equp_a_bibrator_in_sleep(character_id) and handle_premise.handle_self_now_vibrator_insertion_anal(character_id):
        handle_target_anal_vibrator_off(character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_DIURETICS_ONCE)
def handle_use_diuretics_once(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个一次性利尿剂
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[105] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_DIURETICS_PERSISTENT)
def handle_use_diuretics_persistent(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个持续性利尿剂
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[106] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_SLEEPING_PILLS)
def handle_use_sleeping_pills(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个安眠药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[107] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_OVULATION_PROMOTING_DRUGS)
def handle_use_ovulation_promoting_drugs(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个排卵促进药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[108] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_CONTRACEPTIVE_BEFORE)
def handle_use_contraceptive_before(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个事前避孕药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[101] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_CONTRACEPTIVE_AFTER)
def handle_use_contraceptive_after(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个事后避孕药
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[102] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_RING)
def handle_use_ring(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个戒指
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[201] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_COLLAR)
def handle_use_collar(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个项圈
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[202] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_BAG)
def handle_use_bag(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个干员携袋
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[151] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_CONDOM)
def handle_use_condom(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个避孕套
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[120] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_URETHRAL_SWAB)
def handle_use_urethral_swab(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个尿道棉棒
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[139] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.USE_SAFE_CANDLES)
def handle_use_safe_candles(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    使用了一个低温蜡烛
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 在爱情旅馆的顶级套房中H则不消耗
    if handle_premise.handle_h_in_love_hotel(character_id) and handle_premise.handle_love_hotel_room_v3(character_id):
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.item[136] -= 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_URINATE)
def handle_target_add_urinate(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象尿意值全满
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
    target_data.urinate_point = 240


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_DIURETICS_ON)
def handle_target_diuretics_on(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象获得利尿剂状态
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
    add_time = datetime.timedelta(hours=4)
    end_time = now_time + add_time
    target_data.h_state.body_item[8][1] = True
    target_data.h_state.body_item[8][2] = end_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_TIRED_TO_SLEEP)
def handle_target_add_tired_tosleep(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象疲劳值全满，进入8h的睡眠
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
    target_data.tired_point = 160
    target_data.sleep_point = 100
    target_data.h_state.body_item[9][1] = True
    target_data.h_state.body_item[9][2] = now_time + datetime.timedelta(hours=8)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_PREGNANCY_CHANCE)
def handle_target_add_pregnancy_chance(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    道具_使用效果 交互对象获得排卵促进药状态
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
    target_data.h_state.body_item[10][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NO_PREGNANCY_NEXT_DAY)
def handle_target_no_pregnancy_next_day(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象获得事前避孕药状态
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
    target_data.h_state.body_item[11][1] = True
    target_data.h_state.body_item[11][2] = now_time + datetime.timedelta(days=30)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_NO_PREGNANCY_FROM_LAST_H)
def handle_target_no_pregnancy_from_last_h(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象获得事后避孕药状态
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
    target_data.h_state.body_item[12][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.WEAR_CONDOM)
def handle_wear_condom(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己获得戴上避孕套状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.h_state.body_item[13][1] = True


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TAKE_CONDOM_OFF)
def handle_take_condom_off(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己去掉戴上避孕套状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.h_state.body_item[13][1] = False


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_LEARN)
def handle_target_add_small_learn(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量习得（技巧补正）
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
    base_chara_state_common_settle(character_data.target_character_id, add_time, 9, ability_level = target_data.ability[30], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_RESPECT)
def handle_target_add_small_repect(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量恭顺（顺从补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 10, ability_level = target_data.ability[31], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_FRIENDLY)
def handle_target_add_small_friendly(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量好意（亲密补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 11, ability_level = target_data.ability[32], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_DESIRE)
def handle_target_add_small_desire(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量欲情（欲望补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 12, ability_level = target_data.ability[33], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_HAPPY)
def handle_target_add_small_happy(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量快乐（快乐刻印补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 13, ability_level = target_data.ability[13], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_LEAD)
def handle_target_add_small_lead(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量先导（施虐补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 14, ability_level = target_data.ability[35], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_SUBMIT)
def handle_target_add_small_submit(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量屈服（屈服刻印补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 15, ability_level = target_data.ability[14], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_SHY)
def handle_target_add_small_shy(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量羞耻（露出补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 16, ability_level = target_data.ability[34], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_PAIN)
def handle_target_add_small_pain(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量苦痛（苦痛刻印补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 17, ability_level = target_data.ability[15], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_TERROR)
def handle_target_add_small_terror(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量恐怖（恐怖刻印补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 18, 10, ability_level = target_data.ability[17], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_DEPRESSION)
def handle_target_add_small_depression(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量抑郁
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 19, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_DISGUST)
def handle_target_add_small_disgust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量反感（反发刻印补正）
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
    if character_id != 0 and character_data.target_character_id != 0:
        return
    base_chara_state_common_settle(character_data.target_character_id, add_time, 20, 5, ability_level = target_data.ability[18], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_P_FEEL)
def handle_add_small_p_feel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身增加少量Ｐ快
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
    now_lust_multiple = 10
    now_add_lust = add_time + now_lust_multiple + character_data.eja_point * 0.4
    character_data.eja_point += now_add_lust
    change_data.eja_point += now_add_lust
    character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BOTH_ADD_SMALL_LEARN)
def handle_both_add_small_learn(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方增加少量习得（若没有交互对象则仅增加自己）
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
    base_chara_state_common_settle(character_id, add_time, 9, 10, change_data = change_data)
    # 交互对象也同样#
    if character_data.target_character_id != character_id:
        base_chara_state_common_settle(character_data.target_character_id, add_time, 9, 10, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_LEARN_OLD)
def handle_add_small_learn_old(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量习得
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    handle_add_small_learn(character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_LUBRICATION)
def handle_add_small_lubrication(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量润滑（欲望补正）
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
    base_chara_state_common_settle(character_id, add_time, 8, ability_level = character_data.ability[33], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_LEARN)
def handle_add_small_learn(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量习得（技巧补正）
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
    base_chara_state_common_settle(character_id, add_time, 9, ability_level = character_data.ability[30], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_RESPECT)
def handle_add_small_respect(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量恭顺（顺从补正）
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
    base_chara_state_common_settle(character_id, add_time, 10, ability_level = character_data.ability[31], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_FRIENDLY)
def handle_add_small_friendly(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量好意（亲密补正）
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
    base_chara_state_common_settle(character_id, add_time, 11, ability_level = character_data.ability[32], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_DESIRE)
def handle_add_small_desire(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量欲情（欲望补正）
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
    base_chara_state_common_settle(character_id, add_time, 12, ability_level = character_data.ability[33], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_HAPPY)
def handle_add_small_happy(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量快乐（快乐刻印补正）
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
    base_chara_state_common_settle(character_id, add_time, 13, ability_level = character_data.ability[13], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_LEAD)
def handle_add_small_lead(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量先导（施虐补正）
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
    base_chara_state_common_settle(character_id, add_time, 14, ability_level = character_data.ability[35], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_SUBMIT)
def handle_add_small_submit(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量屈服（屈服刻印补正）
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
    base_chara_state_common_settle(character_id, add_time, 15, ability_level = character_data.ability[14], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_SHY)
def handle_add_small_shy(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量羞耻（露出补正）
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
    base_chara_state_common_settle(character_id, add_time, 16, ability_level = character_data.ability[34], change_data = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DIRTY_RESET)
def handle_dirty_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    污浊情况(身体+衣服)归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.dirty = attr_calculation.get_dirty_reset(character_data.dirty)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ASSISTANT_RESET)
def handle_assistant_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    助理数据归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.assistant_services = attr_calculation.get_assistant_services_zero()
    pl_character_data = cache.character_data[0]
    if pl_character_data.assistant_character_id == character_id:
        pl_character_data.assistant_character_id = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOOR_CLOSE)
def handle_door_close(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前场景进入关门状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_position_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_position_str]
    now_scene_data.close_flag = now_scene_data.close_type


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DOOR_CLOSE_RESET)
def handle_door_close_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前场景取消关门状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    now_position = character_data.position
    now_position_str = map_handle.get_map_system_path_str_for_list(now_position)
    now_scene_data = cache.scene_data[now_position_str]
    now_scene_data.close_flag = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MOVE_TO_PRE_SCENE)
def handle_move_to_pre_scene(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    角色移动至前一场景
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
    if len(character_data.action_info.past_move_position_list) and not character_id:
        character_data.behavior.move_target = character_data.action_info.past_move_position_list[-1]
        # 删除掉前一场景的移动数据
        character_data.action_info.past_move_position_list.pop(-1)
        handle_move_to_target_scene(character_id, add_time, change_data, now_time)
        character_data.sp_flag.move_stop = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_MOVE_TO_PRE_SCENE)
def handle_target_move_to_pre_scene(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象移动至前一场景
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_move_to_pre_scene(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_H_STATE_RESET)
def handle_self_h_state_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己H状态结构体归零，同步高潮程度记录，清零H相关二段状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # H状态数据归零
    character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state)
    # 清零阴茎污浊
    character_data.dirty.penis_dirty_dict["semen"] = False
    # 清零自慰状态
    character_data.sp_flag.masturebate = 0
    # 清零前往群交
    character_data.sp_flag.go_to_join_group_sex = False
    # 清零隐奸模式
    character_data.sp_flag.hidden_sex_mode = 0
    # 记录高潮进度
    for orgasm in range(8):
        now_data = attr_calculation.get_status_level(character_data.status_data[orgasm])
        character_data.h_state.orgasm_level[orgasm] = now_data
    # 清零H相关二段状态
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0 and (second_behavior_id in range(1100,1120) or second_behavior_id in range(1200,1250)):
            character_data.second_behavior[second_behavior_id] = 0
    # 囚犯干员回到自己监牢
    if handle_premise.handle_imprisonment_1(character_id) and handle_premise.handle_not_in_dormitory(character_id):
        dormitory_list = map_handle.get_map_system_path_for_str(character_data.dormitory)
        map_handle.character_move_scene(character_data.position, dormitory_list, character_id)
    # 退出H模式
    character_data.sp_flag.is_h = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BOTH_H_STATE_RESET)
def handle_both_h_state_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方H状态结构体归零，同步高潮程度记录，清零H相关二段状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_self_h_state_reset(character_id, add_time, change_data, now_time)
    handle_self_h_state_reset(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UPDATE_ORGASM_LEVEL)
def handle_update_orgasm_level(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方同步高潮程度记录
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
    for orgasm in range(8):
        now_data = attr_calculation.get_status_level(character_data.status_data[orgasm])
        character_data.h_state.orgasm_level[orgasm] = now_data
        now_data = attr_calculation.get_status_level(target_data.status_data[orgasm])
        target_data.h_state.orgasm_level[orgasm] = now_data


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_UPDATE_ORGASM_LEVEL)
def handle_scene_all_characters_update_orgasm_level(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有角色同步高潮程度记录
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        now_character_data = cache.character_data[chara_id]
        for orgasm in range(8):
            now_data = attr_calculation.get_status_level(now_character_data.status_data[orgasm])
            now_character_data.h_state.orgasm_level[orgasm] = now_data


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_H_STATE_RESET)
def handle_scene_all_characters_h_state_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有角色H状态结构体归零，同步高潮程度记录，清零H相关二段状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list.copy():
        handle_self_h_state_reset(chara_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ALL_CHARACTERS_UNCONSCIOUS_SEMEN_RESET)
def handle_all_character_unconscious_semen_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    清零所有角色的无意识精液情况
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    for chara_id, character_data in cache.character_data.items():
        character_data.dirty.body_semen_in_unconscious = []
        character_data.dirty.cloth_semen_in_unconscious = []


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CHARA_OFF_LINE)
def handle_chara_off_line(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    角色离线，归零若干数据结构体，从当前干员列表中移除，离开地图
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.behavior = game_type.Behavior() # 行动数据归零
    character_data.event = game_type.Chara_Event() # 事件数据归零
    handle_assistant_reset(character_id, add_time, change_data, now_time) # 助理数据归零
    handle_dirty_reset(character_id, add_time, change_data, now_time) # 污浊情况归零
    character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state) # H状态数据归零
    # 清零跟随数据
    character_data.sp_flag.is_follow = 0
    # 从当前干员列表中移除
    if character_id in cache.npc_id_got:
        cache.npc_id_got.remove(character_id)
    # 离开地图
    old_scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if character_id in cache.scene_data[old_scene_path_str].character_list:
        cache.scene_data[old_scene_path_str].character_list.remove(character_id)
    character_data.position = ["0", "0"]


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CHARA_ON_LINE)
def handle_chara_on_line(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    角色上线，加入当前干员列表，进入地图
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 基础属性重置
    character_data.hit_point = character_data.hit_point_max
    character_data.mana_point = character_data.mana_point_max
    character_data.hunger_point = 0
    character_data.tired_point = 0
    character_data.sleep_point = 0
    character_data.urinate_point = 0
    # 清零各特殊状态flag
    if character_data.sp_flag.imprisonment == 1:
        character_data.sp_flag = game_type.SPECIAL_FLAG()
        character_data.sp_flag.imprisonment = 1
    else:
        character_data.sp_flag = game_type.SPECIAL_FLAG()
    # 赋予默认行动数据
    character_data.target_character_id = character_id
    character_data.behavior.behavior_id = constant.Behavior.SHARE_BLANKLY
    character_data.behavior.start_time = now_time
    character_data.behavior.duration = 1
    character_data.state = constant.CharacterStatus.STATUS_ARDER
    # 加入当前干员列表
    if character_id not in cache.npc_id_got:
        cache.npc_id_got.add(character_id)
    # 进入地图
    now_scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if character_id not in cache.scene_data[now_scene_path_str].character_list:
        cache.scene_data[now_scene_path_str].character_list.add(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.T_BE_BAGGED)
def handle_t_be_bagged(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象变成被装袋搬走状态
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
    target_data.sp_flag.be_bagged = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.T_BE_IMPRISONMENT)
def handle_t_be_imprisonment(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象变成被监禁状态
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
    target_data.sp_flag.imprisonment = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SHOWER_FLAG_TO_1)
def handle_shower_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要脱衣服（洗澡）状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.shower = 1


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


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SHOWER_FLAG_TO_0)
def handle_shower_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零洗澡状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.shower = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SHOWER_FLAG_TO_2)
def handle_shower_flag_to_2(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要洗澡状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.shower = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SHOWER_FLAG_TO_3)
def handle_shower_flag_to_3(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要披浴巾状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.shower = 3


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SHOWER_FLAG_TO_4)
def handle_shower_flag_to_4(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成洗完澡状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.shower = 4


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.EAT_FOOD_FLAG_TO_0)
def handle_eat_food_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零吃饭状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.eat_food = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.EAT_FOOD_FLAG_TO_1)
def handle_eat_food_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要取餐状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.eat_food = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.EAT_FOOD_FLAG_TO_2)
def handle_eat_food_flag_to_2(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要进食状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.eat_food = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SLEEP_FLAG_TO_0)
def handle_sleep_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零要睡眠状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.sleep = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SLEEP_FLAG_TO_1)
def handle_sleep_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要睡眠状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.sleep = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.REST_FLAG_TO_0)
def handle_rest_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零要休息状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.rest = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.REST_FLAG_TO_1)
def handle_rest_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要休息状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.rest = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PEE_FLAG_TO_0)
def handle_pee_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零要撒尿状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.pee = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PEE_FLAG_TO_1)
def handle_pee_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要撒尿状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.pee = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SWIM_FLAG_TO_1)
def handle_swim_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要换泳衣状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.swim = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SWIM_FLAG_TO_2)
def handle_swim_flag_to_2(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成要游泳状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.swim = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MAINTENANCE_FLAG_TO_0)
def handle_maintenance_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零要检修状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.work_maintenance = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CANCEL_ALL_WORK_AND_ENTERTAINMENT_FLAG)
def handle_cancel_all_work_and_entertainment_flag(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身取消所有工作和娱乐状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.swim = 0
    character_data.sp_flag.bathhouse_entertainment = 0
    character_data.sp_flag.work_maintenance = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.H_FLAG_TO_0)
def handle_h_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零H状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.is_h = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.H_FLAG_TO_1)
def handle_h_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成H状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.is_h = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.T_H_FLAG_TO_0)
def handle_t_h_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象清零H状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_h_flag_to_0(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.T_H_FLAG_TO_1)
def handle_t_h_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象变成H状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_h_flag_to_1(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_H_FLAG_TO_1)
def handle_scene_all_characters_h_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有角色变成H状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        if chara_id == 0:
            continue
        handle_h_flag_to_1(chara_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SELF_HIDDEN_SEX_FLAG_TO_0)
def handle_self_hidden_sex_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己清零隐奸状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.hidden_sex_mode = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HIDDEN_SEX_FLAG_TO_0)
def handle_target_hidden_sex_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象清零隐奸状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_self_hidden_sex_flag_to_0(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BOTH_HIDDEN_SEX_FLAG_TO_0)
def handle_both_hidden_sex_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    双方清零隐奸状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    handle_self_hidden_sex_flag_to_0(character_id, add_time, change_data, now_time)
    handle_self_hidden_sex_flag_to_0(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_0)
def handle_unconscious_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零无意识状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_1)
def handle_unconscious_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成无意识_睡眠状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_2)
def handle_unconscious_flag_to_2(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成无意识_醉酒状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_3)
def handle_unconscious_flag_to_3(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成无意识_时停状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 3


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_4)
def handle_unconscious_flag_to_4(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成无意识_空气状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 4


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_5)
def handle_unconscious_flag_to_5(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成无意识_平然状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 5


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_6)
def handle_unconscious_flag_to_6(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成无意识_心控状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 6


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.UNCONSCIOUS_FLAG_TO_7)
def handle_unconscious_flag_to_7(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成无意识_体控状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.unconscious_h = 7


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HELP_BUY_FOOD_FLAG_TO_0)
def handle_help_buy_food_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零要帮忙买午饭状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.help_buy_food = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BATHHOUSE_ENTERTAINMENT_FLAG_TO_0)
def handle_bathhouse_entertainment_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零大浴场娱乐状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.bathhouse_entertainment = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BATHHOUSE_ENTERTAINMENT_FLAG_TO_1)
def handle_bathhouse_entertainment_flag_to_1(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成大浴场娱乐_要更衣状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.bathhouse_entertainment = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BATHHOUSE_ENTERTAINMENT_FLAG_TO_2)
def handle_bathhouse_entertainment_flag_to_2(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身变成大浴场娱乐_要娱乐状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.bathhouse_entertainment = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MILK_FLAG_TO_0)
def handle_milk_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime, ):
    """
    自身清零要挤奶状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.milk = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HYPNOSIS_FLAG_TO_0)
def handle_hypnosis_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime, ):
    """
    自身清零催眠系的flag与催眠子项
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.unconscious_h in [4, 5, 6, 7]:
        character_data.sp_flag.unconscious_h = 0
    character_data.hypnosis.increase_body_sensitivity = False
    character_data.hypnosis.blockhead = False
    character_data.hypnosis.active_h = False
    character_data.hypnosis.pain_as_pleasure = False
    character_data.hypnosis.roleplay = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ANGRY_WITH_PLAYER_FLAG_TO_0)
def handle_target_angry_with_player_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象清零对玩家的愤怒状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character = cache.character_data[character_data.target_character_id]
    target_character.sp_flag.angry_with_player = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MASTUREBATE_FLAG_TO_0)
def handle_masturebate_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime, ):
    """
    自身清零要自慰状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.masturebate = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MASTUREBATE_BEFORE_SLEEP_FLAG_TO_0)
def handle_masturebate_before_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime, ):
    """
    自身清零要睡前自慰状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.masturebate_before_sleep = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MASTUREBATE_BEFORE_SLEEP_FLAG_TO_2)
def handle_masturebate_before_flag_to_2(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime, ):
    """
    自身变为已睡前自慰状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.masturebate_before_sleep = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HELP_MAKE_FOOD_FLAG_TO_0)
def handle_help_make_food_flag_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身清零做午饭状态
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sp_flag.help_make_food = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TALK_ADD_ADJUST)
def handle_talk_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （聊天用）根据发起者的话术技能进行双方的好感度、好意、快乐调整，并记录当前谈话时间
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if character_id != 0 and character_data.target_character_id != 0:
            return
        # 获取调整值#
        character_data.ability.setdefault(40, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[40])
        # 好感度变化#
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, adjust, change_data)
        # 好意变化#
        base_chara_state_common_settle(character_data.target_character_id, add_time, 11, ability_level = character_data.ability[40], change_data_to_target_change = change_data)
        # 快乐变化#
        base_chara_state_common_settle(character_data.target_character_id, add_time, 13, ability_level = character_data.ability[40], change_data_to_target_change = change_data)
        # 记录谈话时间#
        target_data.action_info.talk_time = now_time
        # print("聊天计数器时间变为 ：",target_data.action_info.talk_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.COFFEE_ADD_ADJUST)
def handle_coffee_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （泡咖啡用）根据发起者的料理技能进行好感度、信赖、好意调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if character_id != 0 and character_data.target_character_id != 0:
            return
        # 获取调整值#
        character_data.ability.setdefault(43, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[43])
        # 好感度变化#
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, adjust, change_data)
        # 信赖变化#
        base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, adjust, change_data)
        # 好意变化#
        base_chara_state_common_settle(character_data.target_character_id, add_time, 11, ability_level = character_data.ability[43], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_COFFEE_ADD_ADJUST)
def handle_target_coffee_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （泡咖啡用）根据交互对象的料理技能进行好感度、信赖、好意调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if character_id != 0 and character_data.target_character_id != 0:
            return
        # 获取调整值#
        target_data.ability.setdefault(43, 0)
        adjust = attr_calculation.get_ability_adjust(target_data.ability[43])
        # 好感度变化#
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, adjust, change_data)
        # 信赖变化#
        base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, adjust, change_data)
        # 好意变化#
        base_chara_state_common_settle(character_data.target_character_id, add_time, 11, ability_level = target_data.ability[43], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.OFFICIAL_WORK_ADD_ADJUST)
def handle_official_work_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （处理公务用）根据自己（如果有的话再加上交互对象）的学识以及办公室等级来处理当前的剩余工作量
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    from Script.Design import basement
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    if character_data.dead:
        return
    if target_data.dead:
        return
    now_draw_text = ""
    # 获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[45])
    # 如果有交互对象，且对方不在无意识状态下，则算上对方的学识加成
    if character_data.target_character_id != character_id and handle_premise.handle_unconscious_flag_0(character_data.target_character_id):
        adjust_target = attr_calculation.get_ability_adjust(target_data.ability[45])
        adjust += adjust_target
        now_draw_text += _("在{0}的帮助下，").format(target_data.name)
    # 根据博士办公室的房间等级来调整
    now_level = cache.rhodes_island.facility_level[22]
    facility_cid = game_config.config_facility_effect_data[_("博士办公室")][int(now_level)]
    facility_effect = game_config.config_facility_effect[facility_cid].effect
    adjust *= (1 + facility_effect / 100)
    # 处理工作
    finish_work = int(add_time * adjust)
    cache.rhodes_island.office_work = int(max(cache.rhodes_island.office_work - finish_work, 0))
    # 输出处理结果
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw_text += _("共处理了{0}公务，").format(finish_work)
        if cache.rhodes_island.office_work > 0:
            now_draw_text += _("还有{0}需要处理\n").format(cache.rhodes_island.office_work)
        else:
            now_draw_text += _("已经全部处理完毕\n\n")
        now_draw.text = now_draw_text
        now_draw.width = width
        now_draw.draw()
    # 输出待办事项
    basement.draw_todo()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CURE_PATIENT_ADD_ADJUST)
def handle_cure_patient_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （诊疗病人用）根据发起者(如果有的话再加上交互对象)的医疗技能治愈了一名病人，并获得一定的龙门币
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
    if target_data.dead:
        return
    # 获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[46])
    # 如果有交互对象，则算上对方的医疗加成
    if character_data.target_character_id != character_id:
        adjust_target = attr_calculation.get_ability_adjust(target_data.ability[46])
        adjust = (adjust + adjust_target) / 1.5
    # 获得加成 #
    now_add_lust = add_time * adjust * 50
    now_add_lust = int(now_add_lust * random.uniform(0.5, 1.5))

    cache.rhodes_island.cure_income += now_add_lust
    cache.rhodes_island.patient_now -= 1
    cache.rhodes_island.patient_cured += 1

    # 如果是玩家在诊疗或玩家与诊疗者在同一位置的话，显示诊疗情况
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.width = width
        now_draw.text = _("\n在{0}的努力下，医治了一名病人，支付了{1}龙门币的医疗费。（今日剩余病人数：{2}人）\n").format(character_data.name, now_add_lust, cache.rhodes_island.patient_now)
        now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.RECRUIT_ADD_ADJUST)
def handle_recruit_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （招募干员用）根据发起者的话术技能增加招募槽
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    from Script.UI.Panel import recruit_panel

    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    if character_data.dead:
        return
    if target_data.dead:
        return
    # 获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[40])
    # 获得加成 #
    now_add_lust = adjust * 2 * random.uniform(0.8, 1.2)
    # debug下直接拉满
    if cache.debug_mode:
        now_add_lust += 100

    select_index = -1
    # 如果角色已经确定招募栏位，则直接使用
    for recruit_line_id in cache.rhodes_island.recruit_line:
        if character_id in cache.rhodes_island.recruit_line[recruit_line_id][2]:
            select_index = recruit_line_id
            break
    # 如果角色没有确定招募栏位或是玩家来招募，则随机一个指派过去
    if select_index == -1 or character_id == 0:
        line_id_list = list(cache.rhodes_island.recruit_line.keys())
        select_index = random.choice(line_id_list)

    # 如果该招募槽的策略为11号停止招募，则直接返回
    if cache.rhodes_island.recruit_line[select_index][1] == 11:
        return

    # 如果是玩家在招募或玩家与招募者在同一位置的话，显示招募进度的增加情况
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.width = width
        now_draw.text = _("\n在{0}的努力下，{1}号招募位进度+{2}%，现在为{3}%\n").format(character_data.name, select_index, round(now_add_lust,1), round(cache.rhodes_island.recruit_line[select_index][0] + now_add_lust,1))
        now_draw.draw()

    # 增加对应槽的招募值，并进行结算
    cache.rhodes_island.recruit_line[select_index][0] += now_add_lust
    recruit_panel.update_recruit()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.INVITE_VISITOR_ADD_ADJUST)
def handle_invite_visitor_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （邀请访客用）根据发起者(如果有的话再加上交互对象)的话术技能增加邀请槽
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    from Script.UI.Panel import invite_visitor_panel

    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    if character_data.dead:
        return
    if target_data.dead:
        return

    # 如果没有选择目标则直接返回
    if cache.rhodes_island.invite_visitor[0] == 0:
        # 玩家使用时显示提示
        if character_id == 0:
            now_draw = draw.NormalDraw()
            now_draw.width = width
            now_draw.text = _("\n请先使用邀请系统选择邀请的对象，再进行邀请\n")
            now_draw.draw()
        return

    # 获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[40])
    # 获得加成 #
    now_add_lust = adjust * 2 * random.uniform(0.8, 1.2)
    # debug下直接拉满
    if cache.debug_mode:
        now_add_lust += 100

    # 如果是玩家在邀请或玩家与邀请者在同一位置的话，显示进度的增加情况
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.width = width
        now_draw.text = _("\n在{0}的努力下，邀请进度+{1}%，现在为{2}%\n").format(character_data.name, round(now_add_lust,1), round(cache.rhodes_island.invite_visitor[1] + now_add_lust,1))
        now_draw.draw()

    # 增加对应槽的邀请值，并进行结算
    cache.rhodes_island.invite_visitor[1] += now_add_lust
    invite_visitor_panel.update_invite_visitor()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MILK_ADD_ADJUST)
def handle_milk_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （挤奶用）把交互对象的乳汁转移到厨房的冰箱里
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
    pl_character_data: game_type.Character = cache.character_data[0]

    now_milk = target_data.pregnancy.milk
    character_data.behavior.milk_ml += now_milk
    cache.rhodes_island.milk_in_fridge.setdefault(character_data.target_character_id, 0)
    cache.rhodes_island.milk_in_fridge[character_data.target_character_id] += now_milk
    pl_character_data.pl_collection.milk_total.setdefault(character_data.target_character_id, 0)
    pl_character_data.pl_collection.milk_total[character_data.target_character_id] += now_milk
    target_data.pregnancy.milk = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SALUTATION_3_ADD_ADJUST)
def handle_salutation_3_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （早安咬与晚安咬）触发交互对象一次射精，射到发起者嘴里
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    ejaculation_panel.ejaculation_flow(2, 0, character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.AROMATHERAPY_ADD_ADJUST)
def handle_aromatherapy_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （香薰疗愈用）对各配方结算各效果
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]

    # 如果没有选择配方则直接返回
    if target_character_data.sp_flag.aromatherapy == 0:
        return

    # 回复
    if target_character_data.sp_flag.aromatherapy == 1:
        target_character_data.hit_point = target_character_data.hit_point_max
        target_character_data.mana_point = target_character_data.mana_point_max


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.URETHRAL_SWAB_ADD_ADJUST)
def handle_urethral_swab_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的U属性(润滑+扩张)对其进行苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 润滑调整
        target_data.status_data.setdefault(8, 0)
        pain_adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])

        # 扩长等级相对于插入等级的调整，棉棒默认为无影响
        dilate_level = target_data.ability[11]
        size_adjust = attr_calculation.get_pain_adjust(dilate_level, level_flag = True)

        # 最终调整值
        final_adjust = pain_adjust * size_adjust

        base_chara_state_common_settle(character_data.target_character_id, add_time, 17,base_value = 100, ability_level = target_data.ability[15], extra_adjust = final_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.URETHRAL_FINGER_INSERTION_ADD_ADJUST)
def handle_urethral_finger_insertion_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的U属性(润滑+扩张)对其进行苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 润滑调整
        target_data.status_data.setdefault(8, 0)
        pain_adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])

        # 扩长等级相对于插入等级的调整，手指为-2级扩张
        dilate_level = target_data.ability[11] - 2
        size_adjust = attr_calculation.get_pain_adjust(dilate_level, level_flag = True)

        # 最终调整值
        final_adjust = pain_adjust * size_adjust

        base_chara_state_common_settle(character_data.target_character_id, add_time, 17,base_value = 400, ability_level = target_data.ability[15], extra_adjust = final_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MASTUREBATE_ADD_ADJUST)
def handle_masturebate_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （自慰用）选择自己最高感度的部位，增加该部位快感和经验
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 根据NPC的部位喜好，选择一个部位
    part_id = handle_npc_ai_in_h.evaluate_npc_body_part_prefs(character_id)
    # 增加快感
    base_chara_state_common_settle(character_id, add_time, part_id, 50, ability_level = character_data.ability[30], change_data = change_data)
    # 增加经验
    character_data.experience.setdefault(part_id, 0)
    character_data.experience[part_id] += 1
    change_data.experience.setdefault(part_id, 0)
    change_data.experience[part_id] += 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DIRTY_RESET_IN_SHOWER)
def handle_dirty_reset_in_shower(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自身部分部位污浊保留一定比例，其他污浊体归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 保留比例
    keep_rate_dict = {6 : 0.2, 7 : 0.7, 8 : 0.3}
    # 身体管理被要求不洗精液时则上调比例
    if handle_premise.handle_ask_not_wash_semen(character_id):
        keep_rate_dict[6] = 0.8
        keep_rate_dict[7] = 0.9
    # 保留数据
    keep_data = {6 : 0, 7 : 0, 8 : 0}
    # 保留部位
    for body_cid in [6, 7, 8]:
        body_dirty = character_data.dirty.body_semen[body_cid].copy()
        keep_rate = keep_rate_dict[body_cid]
        new_dirty = body_dirty[1] * keep_rate
        # 如果保留后小于5，则归零
        if new_dirty < 5:
            new_dirty = 0
        new_lv = attr_calculation.get_semen_now_level(new_dirty, body_cid, 0)
        body_dirty[1] = new_dirty
        body_dirty[2] = new_lv
        keep_data[body_cid] = body_dirty

    # 数据归零后再赋值
    character_data.dirty = attr_calculation.get_dirty_reset(character_data.dirty)
    character_data.dirty.body_semen[6] = keep_data[6]
    character_data.dirty.body_semen[7] = keep_data[7]
    character_data.dirty.body_semen[8] = keep_data[8]


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ORGASM_EDGE_RELEASE)
def handle_orgasm_edge_release(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （绝顶解放）交互对象变为寸止解放状态，将寸止计数转化为绝顶
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
    # 如果没有交互对象
    if character_data.target_character_id == character_id:
        return
    # 如果对方没有在寸止
    if target_data.h_state.orgasm_edge == 0:
        return
    change_data.target_change.setdefault(character_data.target_character_id, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[character_data.target_character_id]
    # 变为寸止解放状态
    target_data.h_state.orgasm_edge = 2
    # 将寸止计数转化为绝顶
    settle_behavior.orgasm_settle(character_data.target_character_id, target_change, un_count_orgasm_dict = target_data.h_state.orgasm_edge_count)
    # 清零寸止计数
    for body_part in game_config.config_body_part:
        target_data.h_state.orgasm_edge_count[body_part] = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TIME_STOP_ORGASM_RELEASE)
def handle_time_stop_orgasm_release(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （解除时停）交互对象变为时停解放状态，结算时停绝顶和时停精液
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    for chara_id in cache.npc_id_got:
        if chara_id == 0:
            continue
        character_data = cache.character_data[chara_id]
        # 变为时停解放状态
        character_data.h_state.time_stop_release = True
        # 将时停绝顶计数转化为绝顶
        settle_behavior.orgasm_settle(chara_id, change_data, un_count_orgasm_dict = character_data.h_state.time_stop_orgasm_count)
        # 清零时停绝顶计数
        for body_part in game_config.config_body_part:
            character_data.h_state.time_stop_orgasm_count[body_part] = 0
        # 触发角色的二段行为
        handle_npc_ai_in_h.settle_unconscious_semen_and_cloth(chara_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.END_H_ADD_HPMP_MAX)
def handle_end_h_add_hpmp_max(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （结束H）自己和交互对象根据本次H中的绝顶次数增加体力气力上限
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    id_list = [character_id]
    if character_data.target_character_id != character_id:
        id_list.append(character_data.target_character_id)
    for chara_id in id_list:
        now_character_data: game_type.Character = cache.character_data[chara_id]
        # 如果有精液寸止，则射出
        if now_character_data.h_state.endure_not_shot_count > 0:
            settle_behavior.orgasm_judge(chara_id, change_data, skip_undure = True)
            settle_behavior.second_behavior_effect(chara_id, change_data)
        # 统计绝顶次数
        orgasm_count = 0
        for body_part in game_config.config_body_part:
            orgasm_count += now_character_data.h_state.orgasm_count[body_part][0]
        # 如果有绝顶，则增加体力气力上限
        if orgasm_count > 0:
            now_character_data.hit_point_max += orgasm_count * 2
            now_character_data.mana_point_max += orgasm_count * 3
            info_text = _("在激烈的H之后，{0}的体力上限增加了{1}，气力上限增加了{2}").format(now_character_data.name, orgasm_count * 2, orgasm_count * 3)
            # 玩家则额外增加精液量上限
            if chara_id == 0 and now_character_data.semen_point_max < 999:
                now_character_data.semen_point_max += orgasm_count
                now_character_data.semen_point_max = min(now_character_data.semen_point_max, 999)
                info_text += _("，精液量上限增加了{0}").format(orgasm_count)
            info_text += "\n"
            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = width
            info_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GROUP_SEX_END_H_ADD_HPMP_MAX)
def handle_group_sex_end_h_add_hpmp_max(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （群交结束H）在场全部角色根据本次H中的绝顶次数增加体力气力上限
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        now_character_data: game_type.Character = cache.character_data[chara_id]
        orgasm_count = 0
        for body_part in game_config.config_body_part:
            orgasm_count += now_character_data.h_state.orgasm_count[body_part][0]
        if orgasm_count > 0:
            now_character_data.hit_point_max += orgasm_count * 2
            now_character_data.mana_point_max += orgasm_count * 3
            info_text = _("在激烈的H之后，{0}的体力上限增加了{1}，气力上限增加了{2}").format(now_character_data.name, orgasm_count * 2, orgasm_count * 3)
            # 玩家则额外增加精液量上限
            if chara_id == 0 and now_character_data.semen_point_max < 999:
                now_character_data.semen_point_max += orgasm_count
                now_character_data.semen_point_max = min(now_character_data.semen_point_max, 999)
                info_text += _("，精液量上限增加了{0}").format(orgasm_count)
            info_text += "\n"
            # 输出提示信息
            info_draw = draw.NormalDraw()
            info_draw.text = info_text
            info_draw.width = width
            info_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.GROUP_SEX_FAIL_ADD_JUST)
def handle_group_sex_fail_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （群交失败）在场全部角色减体力气力，拒绝者进行邀请H失败结算
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    original_target_character_id = character_data.target_character_id
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 遍历场景内所有角色
    for chara_id in scene_data.character_list:
        handle_sub_self_small_mana_point(chara_id, add_time, change_data, now_time)
        handle_sub_self_small_hit_point(chara_id, add_time, change_data, now_time)
        # 跳过玩家
        if chara_id == 0:
            continue
        # 如果是拒绝者，则进行邀请H失败结算
        if handle_premise.handle_group_sex_fail_and_self_refuse(chara_id):
            character_data.target_character_id = chara_id
            handle_do_h_failed_adjust(0, add_time, change_data, now_time)
    character_data.target_character_id = original_target_character_id


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BOARD_GAME_WIN_ADD_ADJUST)
def handle_board_game_win_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （桌游获胜用）根据游戏难度获得好感度、信赖、习得、粉红凭证
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
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change = change_data.target_change[target_data.cid]

    ai_level = character_data.behavior.board_game_ai_difficulty
    # 好感
    base_chara_favorability_and_trust_common_settle(character_data.target_character_id, add_time * 2, True, 0, ai_level, target_change)
    # 信赖
    base_chara_favorability_and_trust_common_settle(character_data.target_character_id, add_time * 2, False, 0, ai_level, target_change)
    # 习得
    base_chara_state_common_settle(character_id, add_time, 9, ability_level = character_data.ability[45], extra_adjust = ai_level, change_data = change_data)
    base_chara_state_common_settle(character_data.target_character_id, add_time, 9, ability_level = character_data.ability[45], extra_adjust = ai_level, change_data = target_change)
    # 粉红凭证
    add_pink_certificates = int(add_time // 2 * ai_level)
    cache.rhodes_island.materials_resouce[4] += add_pink_certificates
    # 输出提示信息
    game_name = game_config.config_board_game[character_data.behavior.board_game_type].name
    info_draw = draw.NormalDraw()
    info_draw.text = _("{0}在{1}中获胜，获得了{2}粉红凭证\n\n").format(character_data.name, game_name, add_pink_certificates)
    info_draw.width = width
    info_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BOARD_GAME_LOSE_ADD_ADJUST)
def handle_board_game_lose_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （桌游输了用）根据游戏难度获得好感度、习得
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
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change = change_data.target_change[target_data.cid]

    ai_level = character_data.behavior.board_game_ai_difficulty
    # 好感
    base_chara_favorability_and_trust_common_settle(character_data.target_character_id, add_time * 2, True, 0, ai_level, target_change)
    # 习得
    base_chara_state_common_settle(character_id, add_time, 9, ability_level = character_data.ability[45], extra_adjust = ai_level, change_data = change_data)
    base_chara_state_common_settle(character_data.target_character_id, add_time, 9, ability_level = character_data.ability[45], extra_adjust = ai_level, change_data = target_change)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.MAINTENANCE_ADD_ADJUST)
def handle_maintenance_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （维护设施用）修复当前地点的损坏设施
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    # 获取当前位置
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    # 检查是否在损坏设施数据中
    if scene_path_str in cache.rhodes_island.facility_damage_data:
        repair_num = character_data.ability[48]
        cache.rhodes_island.facility_damage_data[scene_path_str] -= repair_num
        # 修复后如果小于等于0则去掉
        if cache.rhodes_island.facility_damage_data[scene_path_str] <= 0:
            cache.rhodes_island.facility_damage_data.pop(scene_path_str)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TRAIN_PRISONERS_ADD_ADJUST)
def handle_train_prisoners_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （训练囚犯用）对所有被关押的囚犯进行日常训练
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    from Script.Core import value_handle
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    now_train_id = cache.rhodes_island.confinement_training_setting.get(1, 0)
    all_prisoner_data = cache.rhodes_island.current_prisoners
    # 如果未设定训练则返回
    if now_train_id == 0:
        return
    # 如果没有囚犯则返回
    if len(all_prisoner_data) == 0:
        return
    # 部位快感训练
    if now_train_id == 1:
        # 根据部位感度等级进行加权选择目标部位
        all_part_data = {}
        for part_id in range(8):
            # 跳过P
            if part_id == 3:
                continue
            all_part_data[part_id] = character_data.ability[part_id]
            all_part_data[part_id] = max(all_part_data[part_id], 1)
        # 选择部位
        target_part_id = value_handle.get_random_for_weight(all_part_data)
        def now_tarin(now_prisoner_cid):
            base_chara_state_common_settle(now_prisoner_cid, add_time, target_part_id, 0, ability_level = character_data.ability[target_part_id], change_data_to_target_change = change_data)
            exp_id = target_part_id
            base_chara_experience_common_settle(now_prisoner_cid, exp_id, change_data_to_target_change = change_data)
    # 部位扩张训练
    elif now_train_id == 2:
        # 根据部位扩张等级进行加权选择目标部位
        all_part_data = {}
        for part_id in [9,10,11,12]:
            all_part_data[part_id] = character_data.ability[part_id]
            all_part_data[part_id] = max(all_part_data[part_id], 1)
        # 选择部位
        target_part_id = value_handle.get_random_for_weight(all_part_data)
        def now_tarin(now_prisoner_cid):
            base_chara_state_common_settle(now_prisoner_cid, add_time, target_part_id - 5, 0, ability_level = character_data.ability[target_part_id], change_data_to_target_change = change_data)
            exp_id = target_part_id + 56
            base_chara_experience_common_settle(now_prisoner_cid, exp_id, change_data_to_target_change = change_data)
    # 苦痛快感训练
    elif now_train_id == 3:
        def now_tarin(now_prisoner_cid):
            base_chara_state_common_settle(now_prisoner_cid, add_time, 0, 0, ability_level = character_data.ability[36], change_data_to_target_change = change_data)
            base_chara_state_common_settle(now_prisoner_cid, add_time, 17, 0, change_data_to_target_change = change_data)
            exp_id = 32
            base_chara_experience_common_settle(now_prisoner_cid, exp_id, change_data_to_target_change = change_data)
    # 性爱技巧训练
    elif now_train_id == 4:
        # 根据性爱技巧等级进行加权选择目标部位
        all_part_data = {}
        for part_id in [70,71,72,73,74,75,76]:
            all_part_data[part_id] = character_data.ability[part_id]
            all_part_data[part_id] = max(all_part_data[part_id], 1)
        # 选择部位
        target_part_id = value_handle.get_random_for_weight(all_part_data)
        def now_tarin(now_prisoner_cid):
            base_chara_state_common_settle(now_prisoner_cid, add_time, 9, 0, ability_level = character_data.ability[target_part_id], change_data_to_target_change = change_data)
            base_chara_state_common_settle(now_prisoner_cid, add_time, 9, 0, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
    # 身体锻炼训练
    elif now_train_id == 5:
        def now_tarin(now_prisoner_cid):
            handle_add_hpmp_max(now_prisoner_cid, add_time, change_data, now_time)
    # 心理服从训练
    elif now_train_id == 6:
        def now_tarin(now_prisoner_cid):
            base_chara_state_common_settle(now_prisoner_cid, add_time, 11, 0, ability_level = character_data.ability[32], change_data_to_target_change = change_data)
            base_chara_state_common_settle(now_prisoner_cid, add_time, 15, 0, ability_level = character_data.ability[14], change_data_to_target_change = change_data)

    # 遍历犯人
    for key, value in all_prisoner_data.items():
        now_prisoner_cid = key
        # 1异常或睡觉中的角色不进行训练
        if not handle_premise.handle_normal_1(now_prisoner_cid) or handle_premise.handle_action_sleep(now_prisoner_cid):
            continue
        now_tarin(now_prisoner_cid)
        base_chara_hp_mp_common_settle(now_prisoner_cid, add_time, hp_value=-1, mp_value=-1, dregree=1, change_data_to_target_change=change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.RECOVER_FROM_UNCONSCIOUS_ADD_ADJUST)
def handle_recover_from_unconscious_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象从无意识H中恢复意识的结算
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 如果交互对象是在H中，则进行恢复意识结算
    character_data: game_type.Character = cache.character_data[character_id]
    if handle_premise.handle_is_h(character_data.target_character_id):
        handle_npc_ai_in_h.recover_from_unconscious_h(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.READ_ADD_ADJUST)
def handle_read_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （读书用）根据书的不同对发起者(如果有的话再加上交互对象)获得对应的知识，并进行NPC的还书判定
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    from Script.UI.Panel import borrow_book_panel

    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    if character_data.dead:
        return
    book_id = character_data.behavior.book_id
    book_data = game_config.config_book[book_id]
    book_type = book_data.type
    experience_index_set = set()
    experience_index_set.add(92)
    # 技能书籍的额外经验增长
    if book_type == 11:
        experience_index_set.add(80)
    elif book_type == 12:
        experience_index_set.add(87)
    elif book_type == 13:
        experience_index_set.add(81)
    elif book_type == 14:
        experience_index_set.add(83)
    elif book_type == 15:
        experience_index_set.add(85)
    elif book_type == 16:
        experience_index_set.add(82)
    elif book_type == 17:
        experience_index_set.add(88)
    elif book_type == 18:
        experience_index_set.add(89)
    elif book_type == 19:
        experience_index_set.add(90)
    elif book_type == 20:
        experience_index_set.add(91)
    # 色情书籍额外加色情阅读经验
    elif 31 <= book_type <= 59:
        experience_index_set.add(93)

    # 遍历集合增加对应经验
    for experience_index in experience_index_set:
        character_data.experience[experience_index] += 1
        change_data.experience.setdefault(experience_index, 0)
        change_data.experience[experience_index] += 1
        # 如果有交互对象，则交互对象也加
        if character_data.target_character_id != character_id:
            target_data.experience[experience_index] += 1
            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            target_change.experience.setdefault(experience_index, 0)
            target_change.experience[experience_index] += 1

    # NPC的还书判定
    if character_id:
        return_rate = 20 + random.randint(1,20)
        character_data.entertainment.book_return_possibility += return_rate
        borrow_book_panel.check_return_book(character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TEACH_ADD_ADJUST)
def handle_teach_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （教学用）自己增加习得和学识经验，所有当前场景里状态是上课的角色增加习得和学识经验，如果玩家是老师则再加好感和信赖，最后结束
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]

    # 获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[45])
    # 获得加成 #
    now_add_lust = adjust * add_time * random.uniform(0.5, 1.5)

    # 增加自己的习得和学识经验
    base_chara_state_common_settle(character_id, add_time, 9, ability_level = character_data.ability[45], change_data = change_data)
    base_chara_experience_common_settle(character_id, 82)

    # 遍历当前场景的其他角色
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 场景角色数大于等于2时进行检测
    if len(scene_data.character_list) >= 2:
        # 遍历当前角色列表
        for chara_id in scene_data.character_list:
            # 跳过自己
            if chara_id == character_id:
                continue
            else:
                other_character_data: game_type.Character = cache.character_data[chara_id]
                # 如果对方在听课
                if other_character_data.behavior.behavior_id == constant.Behavior.ATTENT_CLASS:

                    # 增加习得和学识经验
                    base_chara_state_common_settle(chara_id, add_time, 9, ability_level = character_data.ability[45], change_data_to_target_change = change_data)
                    base_chara_experience_common_settle(chara_id, 82)

                    # 如果老师是玩家
                    if character_id == 0:
                        # 加好感
                        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, other_character_data.ability[32], change_data, other_character_data.cid)
                        # 加信赖
                        base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, other_character_data.ability[32], change_data, other_character_data.cid)

                    # 手动结算该状态
                    character_behavior.judge_character_status(chara_id)
                    # other_character_data.state = constant.CharacterStatus.STATUS_ARDER


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BAGGING_AND_MOVING_ADD_ADJUST)
def handle_bagging_and_moving_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （装袋搬走用）交互对象获得装袋搬走flag，玩家增加搬运人id，对方离线
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    # 玩家数据结算
    character_data.sp_flag.bagging_chara_id = character_data.target_character_id
    # 对方数据结算
    target_data.sp_flag.be_bagged = 1
    handle_chara_off_line(character_data.target_character_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PUT_INTO_PRISON_ADD_ADJUST)
def handle_put_into_prison_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （投入监牢用）被搬运对象上线，成为囚犯并结算，玩家失去搬运人id
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    from Script.UI.Panel import confinement_and_training
    if not add_time:
        return
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[0]
    target_id = character_data.sp_flag.bagging_chara_id
    target_data: game_type.Character = cache.character_data[target_id]
    # 玩家数据结算
    character_data.sp_flag.bagging_chara_id = 0
    # 对方位置结算
    target_data.position = character_data.position
    target_data.behavior.move_src = character_data.position
    target_data.behavior.move_target = character_data.position
    # 对方数据结算
    confinement_and_training.chara_become_prisoner(target_id)
    # 角色上线
    handle_chara_on_line(target_id, add_time, change_data, now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SET_FREE_ADD_ADJUST)
def handle_set_free_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （解除囚禁）交互对象失去监禁flag，从囚犯数据中删除
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    target_data.sp_flag.imprisonment = 0
    # 回到旧宿舍
    if target_data.pre_dormitory != "":
        target_data.dormitory = target_data.pre_dormitory
        target_data.pre_dormitory = ""
    # 从囚犯数据中删除
    if character_data.target_character_id in cache.rhodes_island.current_prisoners:
        cache.rhodes_island.current_prisoners.pop(character_data.target_character_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.EAT_ADD_ADJUST)
def handle_eat_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （进食）食物结算。会根据有无交互目标，食物的调味来自动判别食用对象和结算内容
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[character_id]

    # 判断是谁要吃食物
    eat_food_chara_id_list = []
    if character_data.behavior.food_seasoning == 0:
        eat_food_chara_id_list.append(character_id)
        if character_data.target_character_id != character_id:
            eat_food_chara_id_list.append(character_data.target_character_id)
    else:
        eat_food_chara_id_list.append(character_data.target_character_id)

    # 根据食物品质获得调整系数
    food_quality = character_data.behavior.food_quality
    # 品质最小为1
    food_quality = max(food_quality, 1)
    quality_adjust = (food_quality / 5) ** 2
    # 高品质食物额外加系数
    if food_quality == 8:
        quality_adjust *= 2
    elif food_quality >= 7:
        quality_adjust += 1

    # 检测是否是手制的食物
    pl_make_flag = False
    if character_data.behavior.target_food:
        food_maker = character_data.behavior.target_food.maker
        if len(food_maker):
            # 手动制作的食物则额外加成
            quality_adjust *= 2
            # 检测是否是玩家制作的食物
            pl_character_name = cache.character_data[0].name
            if food_maker == pl_character_name:
                pl_make_flag = True

    # 吃掉该食物
    handle_delete_food(character_id,add_time=add_time,change_data=change_data,now_time=now_time)
    # 对要吃食物的人进行结算
    for chara_id in eat_food_chara_id_list:
        target_data: game_type.Character = cache.character_data[chara_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]

        # 加好感
        if chara_id:
            now_add = int(add_time * quality_adjust)
            base_chara_favorability_and_trust_common_settle(character_id, now_add, True, 0, 0, change_data, chara_id)
            # 玩家做的饭的情况下，额外加信赖
            if pl_make_flag:
                base_chara_favorability_and_trust_common_settle(character_id, now_add, False, 0, 0, change_data, chara_id)
            # 高品质食物则变为好心情
            if food_quality >= 7:
                handle_mood_to_good(chara_id, add_time, change_data, now_time)

        # 加体力气力，清零饥饿值和进食状态
        # 为了增加更多的体力气力，将时间设为25
        now_add = int(25 * quality_adjust)
        handle_add_small_hit_point(chara_id,add_time=now_add,change_data=target_change,now_time=now_time)
        handle_add_small_mana_point(chara_id,add_time=now_add,change_data=target_change,now_time=now_time)
        handle_hunger_point_zero(chara_id,add_time=add_time,change_data=target_change,now_time=now_time)
        handle_eat_food_flag_to_0(chara_id,add_time=add_time,change_data=target_change,now_time=now_time)

        # 精液食物则将精液加到口腔污浊，并加精液经验
        if character_data.behavior.food_seasoning in {11,12}:
            # 加精液经验和饮精经验
            base_chara_experience_common_settle(chara_id, 24, change_data=target_change)
            base_chara_experience_common_settle(chara_id, 25, change_data=target_change)
            # 获取精液量
            now_food = character_data.behavior.target_food
            semen_ml = now_food.special_seasoning_amount
            # 加精液到口腔
            cache.shoot_position = 2    # 口腔
            ejaculation_panel.update_semen_dirty(chara_id, 2, 0, semen_ml, update_shoot_position_flag=False)
        # 药物食物则获得对应药物效果
        elif character_data.behavior.food_seasoning == 102: # 事后避孕药
            handle_target_no_pregnancy_from_last_h(0,add_time=add_time,change_data=change_data,now_time=now_time)
        elif character_data.behavior.food_seasoning == 103: # 媚药
            handle_target_add_huge_desire_and_submit(0,add_time=add_time,change_data=change_data,now_time=now_time)
        elif character_data.behavior.food_seasoning == 105: # 一次性利尿剂
            handle_target_add_urinate(0,add_time=add_time,change_data=change_data,now_time=now_time)
        elif character_data.behavior.food_seasoning == 106: # 持续性利尿剂
            handle_target_diuretics_on(0,add_time=add_time,change_data=change_data,now_time=now_time)
        elif character_data.behavior.food_seasoning == 107: # 安眠药
            handle_target_add_tired_tosleep(0,add_time=add_time,change_data=change_data,now_time=now_time)
        elif character_data.behavior.food_seasoning == 108: # 排卵促进药
            handle_target_add_pregnancy_chance(0,add_time=add_time,change_data=change_data,now_time=now_time)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_HPMP_MAX)
def handle_add_hpmp_max(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （锻炼身体用）增加体力气力上限
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
    # 设施效率
    now_level = cache.rhodes_island.facility_level[9]
    facility_cid = game_config.config_facility_effect_data[_("训练场")][int(now_level)]
    facility_effect = game_config.config_facility_effect[facility_cid].effect
    facility_adjust = 1 + facility_effect / 100

    # 指数曲线，x = [1000, 2000, 4000, 5000, 10000]， y = [50, 25, 15, 10, 5]
    add_hp = 128.961 * math.exp(-0.0016 * character_data.hit_point_max) + 28.578 * math.exp(-1.8453e-04 * character_data.hit_point_max)
    add_mp = 128.961 * math.exp(-0.0016 * character_data.mana_point_max) + 28.578 * math.exp(-1.8453e-04 * character_data.mana_point_max)

    # 最终增加值
    add_hp = int(add_hp * facility_adjust * random.uniform(0.8, 1.2))
    add_mp = int(add_mp * facility_adjust * random.uniform(0.8, 1.5))
    # 增加上限
    character_data.hit_point_max += add_hp
    character_data.mana_point_max += add_mp
    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = _("\n{0}的体力上限增加{1},气力上限增加{2}").format(character_data.name, str(add_hp), str(add_mp))
        now_draw.width = width
        now_draw.draw()
    # 交互对象也同样#
    if character_data.target_character_id != character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        add_hp = 128.961 * math.exp(-0.0016 * target_data.hit_point_max) + 28.578 * math.exp(-1.8453e-04 * target_data.hit_point_max * 2)
        add_mp = 128.961 * math.exp(-0.0016 * target_data.mana_point_max) + 28.578 * math.exp(-1.8453e-04 * target_data.mana_point_max * 2)
        add_hp = int(add_hp * facility_adjust * random.uniform(0.8, 1.2))
        add_mp = int(add_mp * facility_adjust * random.uniform(0.8, 1.5))
        target_data.hit_point_max += add_hp
        target_data.mana_point_max += add_mp
        # 如果和玩家位于同一地点，则输出提示信息
        if character_data.position == cache.character_data[0].position:
            now_draw = draw.NormalDraw()
            now_draw.text = _("\n{0}的体力上限增加{1},气力上限增加{2}\n").format(target_data.name, str(add_hp), str(add_mp))
            now_draw.width = width
            now_draw.draw()
    else:
        now_draw = draw.NormalDraw()
        now_draw.text = "\n"
        now_draw.width = 1
        now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SING_ADD_ADJUST)
def handle_sing_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （唱歌用）根据自己的音乐技能进行好感度、信赖、好意、恐怖、抑郁、反感调整
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
    # print(f"debug 唱歌，角色 = {character_data.name}，目标= {target_data.name}")

    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if character_id != 0 and character_data.target_character_id != 0:
            return
        # 获取调整值#
        character_data.ability.setdefault(44, 0)
        # 如果水平在2级及以下则扣好感信赖，如果是NPC执行则跳过
        good_flag = True
        if character_data.ability[44] <= 2 and character_id == 0:
            good_flag = False
        adjust = attr_calculation.get_ability_adjust(character_data.ability[44])

        # print(f"debug 唱歌，adjust = {adjust}，add_favorability = {add_favorability}")

        # 对在场的全部角色起效
        for chara_id in cache.scene_data[map_handle.get_map_system_path_str_for_list(character_data.position)].character_list:
            # 跳过玩家自己
            if chara_id == character_id:
                continue
            target_data: game_type.Character = cache.character_data[chara_id]

            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            # 好感与信赖变化#
            if good_flag:
                base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, adjust, change_data, chara_id)
                base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, adjust, change_data, chara_id)
            else:
                base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, adjust - 1, change_data, chara_id)
                base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, adjust - 1, change_data, chara_id)

            # 好意变化#
            target_data.status_data.setdefault(11, 0)
            now_lust = target_data.status_data[11]
            now_lust_multiple = 30
            now_add_lust = add_time + now_lust_multiple
            if good_flag:
                now_add_lust *= adjust
                now_add_lust += now_lust / 10
            else:
                now_add_lust *= (adjust - 1)
            target_data.status_data[11] += now_add_lust
            target_data.status_data[11] = min(99999, target_data.status_data[11])
            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            target_change.status_data.setdefault(11, 0)
            target_change.status_data[11] += now_add_lust

            # 恐怖、抑郁、反感变化
            if not good_flag:
                for i in {18, 19, 20}:
                    now_lust = target_data.status_data[i]
                    now_lust_multiple = 100
                    now_add_lust = add_time + now_lust_multiple
                    if good_flag:
                        now_add_lust *= (1.5 - adjust)
                    else:
                        now_add_lust *= (5 - adjust)
                        now_add_lust += now_lust / 10
                    target_data.status_data[i] += now_add_lust
                    target_data.status_data[i] = min(99999, target_data.status_data[i])
                    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
                    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
                    target_change.status_data.setdefault(i, 0)
                    target_change.status_data[i] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PLAY_INSTRUMENT_ADD_ADJUST)
def handle_play_instrument_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （演奏乐器用）根据自己的音乐技能进行好感度、信赖、好意、恐怖、抑郁、反感调整
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
    # print(f"debug 演奏，角色 = {character_data.name}，目标= {target_data.name}")
    # 对着自己演奏乐器不进行该结算
    if character_data.target_character_id == character_id:
        return
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if character_id != 0 and character_data.target_character_id != 0:
            return
        # 获取调整值#
        character_data.ability.setdefault(44, 0)
        # 如果水平在2级及以下则扣好感信赖，如果是NPC执行则跳过
        good_flag = True
        if character_data.ability[44] <= 2 and character_id == 0:
            good_flag = False
        adjust = attr_calculation.get_ability_adjust(character_data.ability[44])

        # print(f"debug 乐器，角色 = {character_data.name}，目标= {target_data.name}，good_flag = {good_flag}，add_favorability = {add_favorability}")

        # 对在场的全部角色起效
        for chara_id in cache.scene_data[map_handle.get_map_system_path_str_for_list(character_data.position)].character_list:
            # 跳过玩家自己
            if chara_id == character_id:
                continue
            target_data: game_type.Character = cache.character_data[chara_id]

            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]

            # 好感与信赖变化#
            if good_flag:
                base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, adjust * 2, change_data, chara_id)
                base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, adjust * 2, change_data, chara_id)
            else:
                base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, (adjust - 1) * 2, change_data, chara_id)
                base_chara_favorability_and_trust_common_settle(character_id, add_time, False, 0, (adjust - 1) * 2, change_data, chara_id)

            # 好意变化#
            target_data.status_data.setdefault(11, 0)
            now_lust = target_data.status_data[11]
            now_lust_multiple = 30
            now_add_lust = add_time + now_lust_multiple
            if good_flag:
                now_add_lust *= adjust
                now_add_lust += now_lust / 8
            else:
                now_add_lust *= (adjust - 1)
            target_data.status_data[11] += now_add_lust
            target_data.status_data[11] = min(99999, target_data.status_data[11])
            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            target_change.status_data.setdefault(11, 0)
            target_change.status_data[11] += now_add_lust

            # 恐怖、抑郁、反感变化
            if not good_flag:
                for i in {18, 19, 20}:
                    now_lust = target_data.status_data[i]
                    now_lust_multiple = 150
                    now_add_lust = add_time + now_lust_multiple
                    if good_flag:
                        now_add_lust *= (1.5 - adjust)
                    else:
                        now_add_lust *= (5 - adjust)
                        now_add_lust += now_lust / 8
                    target_data.status_data[i] += now_add_lust
                    target_data.status_data[i] = min(99999, target_data.status_data[i])
                    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
                    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
                    target_change.status_data.setdefault(i, 0)
                    target_change.status_data[i] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_N_ADJUST)
def handle_tech_add_n_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，和交互对象的感度，对交互对象进行N快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 0, 50, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[0], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_B_ADJUST)
def handle_tech_add_b_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，对交互对象进行B快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 1, 50, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[1], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_C_ADJUST)
def handle_tech_add_c_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，对交互对象进行C快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 2, 50, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[2], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_P_ADJUST)
def handle_tech_add_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，对交互对象进行P快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        character_data.ability.setdefault(19, 0)
        abi_adjust = attr_calculation.get_ability_adjust(character_data.ability[30])
        feel_adjust = attr_calculation.get_ability_adjust(character_data.ability[3])
        adjust = math.sqrt(abi_adjust * feel_adjust)
        # P快变化#
        target_data.status_data.setdefault(3, 0)
        now_lust = target_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        target_data.eja_point += now_add_lust
        # change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        # target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        # target_change.status_data.setdefault(3, 0)
        # target_change.status_data[3] += now_add_lust
        target_data.action_info.last_eaj_add_time = now_time
        # 欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 6
        target_data.status_data[12] += now_add_lust
        target_data.status_data[12] = min(99999, target_data.status_data[12])
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_V_ADJUST)
def handle_tech_add_v_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，对交互对象进行V快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 4, 50, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[4], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_A_ADJUST)
def handle_tech_add_a_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，对交互对象进行A快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 5, 50, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[5], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_U_ADJUST)
def handle_tech_add_u_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，对交互对象进行U快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 6, 50, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[6], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_W_ADJUST)
def handle_tech_add_w_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能和交互对象的感度，对交互对象进行W快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 7, 50, ability_level = character_data.ability[30], change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[7], change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TECH_ADD_PL_P_ADJUST)
def handle_tech_add_pl_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据对交互对象的技巧技能对发起者进行P快调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(target_data.ability[30])
        # P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust
        character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_LUBRICATION_ADJUST_ADD_PAIN)
def handle_target_lubrication_adjust_add_pain(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的润滑情况对其进行苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.status_data.setdefault(8, 0)
        pain_adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])
        base_chara_state_common_settle(character_data.target_character_id, add_time, 17, ability_level = target_data.ability[15], extra_adjust = pain_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_V_ADJUST_ADD_PAIN)
def handle_target_v_adjust_add_pain(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的V属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 润滑调整
        target_data.status_data.setdefault(8, 0)
        pain_adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) - 1

        # 扩长等级相对于阴茎等级的调整，因为阴茎等级默认为1，所以再加1
        jj_size = character_data.pl_ability.jj_size
        dilate_level = target_data.ability[9]
        final_level = dilate_level - jj_size + 1
        size_adjust = attr_calculation.get_pain_adjust(final_level, level_flag = True)

        # 最终调整值
        final_adjust = max(pain_adjust - waist_adjust, 0) * size_adjust

        base_chara_state_common_settle(character_data.target_character_id, add_time, 17, ability_level = target_data.ability[15], extra_adjust = final_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_A_ADJUST_ADD_PAIN)
def handle_target_a_adjust_add_pain(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的A属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 润滑调整
        target_data.status_data.setdefault(8, 0)
        pain_adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) - 1

        # 扩长等级相对于阴茎等级的调整，因为阴茎等级默认为1，所以再加1
        jj_size = character_data.pl_ability.jj_size
        dilate_level = target_data.ability[10]
        final_level = dilate_level - jj_size + 1
        size_adjust = attr_calculation.get_pain_adjust(final_level, level_flag = True)

        # 最终调整值
        final_adjust = max(pain_adjust - waist_adjust, 0) * size_adjust

        base_chara_state_common_settle(character_data.target_character_id, add_time, 17, ability_level = target_data.ability[15], extra_adjust = final_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_U_ADJUST_ADD_PAIN)
def handle_target_u_adjust_add_pain(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的U属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 润滑调整
        target_data.status_data.setdefault(8, 0)
        pain_adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) - 1

        # 扩长等级相对于阴茎等级的调整，因为尿道非常小，所以相对于V和A，初始+1-4 = -3
        jj_size = character_data.pl_ability.jj_size
        dilate_level = target_data.ability[11]
        final_level = dilate_level - jj_size - 3
        size_adjust = attr_calculation.get_pain_adjust(final_level, level_flag = True)

        # 最终调整值
        final_adjust = max(pain_adjust - waist_adjust, 0) * size_adjust

        base_chara_state_common_settle(character_data.target_character_id, add_time, 17, base_value = 1000, ability_level = target_data.ability[15], extra_adjust = final_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_W_ADJUST_ADD_PAIN)
def handle_target_w_adjust_add_pain(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的W属性(润滑+腰技+扩张+阴茎大小)对其进行苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 润滑调整
        target_data.status_data.setdefault(8, 0)
        pain_adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) - 1

        # 扩长等级相对于阴茎等级的调整，因为子宫较小，所以相对于V和A，初始+1-2=-1
        jj_size = character_data.pl_ability.jj_size
        dilate_level = target_data.ability[12]
        final_level = dilate_level - jj_size - 1
        size_adjust = attr_calculation.get_pain_adjust(final_level, level_flag = True)

        # 最终调整值
        final_adjust = max(pain_adjust - waist_adjust, 0) * size_adjust

        base_chara_state_common_settle(character_data.target_character_id, add_time, 17, base_value = 100, ability_level = target_data.ability[15], extra_adjust = final_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_V_ADJUST_ADD_BY_SEX)
def handle_tech_add_v_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧+腰技+阴茎大小对交互目标进行V快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return

        # 阴茎大小的调整
        jj_size = character_data.pl_ability.jj_size
        size_adjust = attr_calculation.get_ability_adjust(jj_size) / 2
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) / 2
        # 最终调整值
        extra_adjust = size_adjust + waist_adjust

        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 4, 50, ability_level = character_data.ability[30], extra_adjust = extra_adjust, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[4], extra_adjust = extra_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_A_ADJUST_ADD_BY_SEX)
def handle_tech_add_a_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧+腰技+阴茎大小对交互目标进行A快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return

        # 阴茎大小的调整
        jj_size = character_data.pl_ability.jj_size
        size_adjust = attr_calculation.get_ability_adjust(jj_size) / 2
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) / 2
        # 最终调整值
        extra_adjust = size_adjust + waist_adjust

        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 5, 50, ability_level = character_data.ability[30], extra_adjust = extra_adjust, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[5], extra_adjust = size_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_U_ADJUST_ADD_BY_SEX)
def handle_tech_add_u_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧+腰技+阴茎大小对交互目标进行U快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return

        # 阴茎大小的调整
        jj_size = character_data.pl_ability.jj_size
        size_adjust = attr_calculation.get_ability_adjust(jj_size) / 2
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) / 2
        # 最终调整值
        extra_adjust = size_adjust + waist_adjust

        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 6, 50, ability_level = character_data.ability[30], extra_adjust = extra_adjust, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[6], extra_adjust = extra_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_W_ADJUST_ADD_BY_SEX)
def handle_tech_add_w_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧+腰技+阴茎大小对交互目标进行W快、欲情调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return

        # 阴茎大小的调整
        jj_size = character_data.pl_ability.jj_size
        size_adjust = attr_calculation.get_ability_adjust(jj_size) / 2
        # 腰技的调整
        waist_tech = character_data.ability[76]
        waist_adjust = attr_calculation.get_ability_adjust(waist_tech) / 2
        # 最终调整值
        extra_adjust = size_adjust + waist_adjust

        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 7, 50, ability_level = character_data.ability[30], extra_adjust = extra_adjust, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[7], extra_adjust = extra_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_PAIN_TO_N_ADJUST)
def handle_pain_to_n_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据发起者的技巧、交互对象的受虐对其进行N快、欲情、苦痛调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return

        # 技巧大小的调整
        tech_lv = character_data.ability[30]
        tech_adjust = attr_calculation.get_ability_adjust(tech_lv)
        # 受虐的调整
        masochism_lv = target_data.ability[36]
        masochism_adjust = attr_calculation.get_ability_adjust(masochism_lv)
        # 最终调整值
        extra_adjust = tech_adjust + masochism_adjust

        # 快感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 0, 50, ability_level = character_data.ability[30], extra_adjust = masochism_adjust, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = target_data.ability[33], extra_adjust = extra_adjust, change_data_to_target_change = change_data)
        # 苦痛
        base_chara_state_common_settle(character_data.target_character_id, add_time, 17, 50, ability_level = target_data.ability[15], extra_adjust = extra_adjust, change_data_to_target_change = change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FINGER_TECH_ADD_PL_P_ADJUST)
def handle_finger_tech_add_pl_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的技巧+指技对发起者进行P快调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust_1 = attr_calculation.get_ability_adjust(target_data.ability[30])
        adjust_2 = attr_calculation.get_ability_adjust(target_data.ability[70])
        adjust = adjust_1 / 2 + adjust_2
        # P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust
        character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TONGUE_TECH_ADD_PL_P_ADJUST)
def handle_tongue_tech_add_pl_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的技巧+舌技对发起者进行P快调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust_1 = attr_calculation.get_ability_adjust(target_data.ability[30])
        adjust_2 = attr_calculation.get_ability_adjust(target_data.ability[71])
        adjust = adjust_1 / 2 + adjust_2
        # P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust
        character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.FEET_TECH_ADD_PL_P_ADJUST)
def handle_feet_tech_add_pl_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的技巧+足技对发起者进行P快调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust_1 = attr_calculation.get_ability_adjust(target_data.ability[30])
        adjust_2 = attr_calculation.get_ability_adjust(target_data.ability[72])
        adjust = adjust_1 / 2 + adjust_2
        # P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust
        character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.BREAST_TECH_ADD_PL_P_ADJUST)
def handle_breast_tech_add_pl_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的技巧+胸技对发起者进行P快调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust_1 = attr_calculation.get_ability_adjust(target_data.ability[30])
        adjust_2 = attr_calculation.get_ability_adjust(target_data.ability[73])
        adjust = adjust_1 / 2 + adjust_2
        # P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust
        character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.VAGINA_TECH_ADD_PL_P_ADJUST)
def handle_vagina_tech_add_pl_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的技巧+膣技对发起者进行P快调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust_1 = attr_calculation.get_ability_adjust(target_data.ability[30])
        adjust_2 = attr_calculation.get_ability_adjust(target_data.ability[74])
        adjust = adjust_1 / 2 + adjust_2
        # P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust
        character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ANUS_TECH_ADD_PL_P_ADJUST)
def handle_anus_tech_add_pl_p_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    根据交互对象的技巧+肛技对发起者进行P快调整
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
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        # 获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust_1 = attr_calculation.get_ability_adjust(target_data.ability[30])
        adjust_2 = attr_calculation.get_ability_adjust(target_data.ability[75])
        adjust = adjust_1 / 2 + adjust_2
        # P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 50
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        now_add_lust += now_lust / 8
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust
        character_data.action_info.last_eaj_add_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.LOW_OBSCENITY_FAILED_ADJUST)
def handle_low_obscenity_failed_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    轻度性骚扰失败的加反感、加愤怒、降好感度修正
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        # 不需要再进行该判断
        # if not character.calculation_instuct_judege(0,character_data.target_character_id,"初级骚扰"):

        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        # 加反感
        base_chara_state_common_settle(character_data.target_character_id, add_time, 20, 200, ability_level = target_data.ability[18], change_data_to_target_change = change_data)
        # 加愤怒
        target_data.angry_point += 50
        target_data.sp_flag.angry_with_player = True
        # 降好感
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, -1, change_data)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HIGH_OBSCENITY_FAILED_ADJUST)
def handle_high_obscenity_failed_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    重度性骚扰失败的加反感、加愤怒、降好感度修正
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        # 不需要再进行该判断
        # if not character.calculation_instuct_judege(0,character_data.target_character_id,"严重骚扰"):

        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        # 加反感
        target_data.status_data.setdefault(20, 0)
        now_lust = target_data.status_data[20]
        now_lust_multiple = 10000
        now_add_lust = add_time + now_lust_multiple
        adjust = attr_calculation.get_ability_adjust(target_data.ability[18])
        now_add_lust *= adjust
        now_add_lust += now_lust / 2
        target_data.status_data[20] += now_add_lust
        target_data.status_data[20] = min(99999, target_data.status_data[20])
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change.status_data.setdefault(20, 0)
        target_change.status_data[20] = now_add_lust
        # 加愤怒
        target_data.angry_point += 100
        target_data.sp_flag.angry_with_player = True
        # 降好感
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, -3, change_data)
        # 降信赖
        now_lust_multiple = target_data.trust * 0.2 + 2
        if now_lust_multiple < 0:
            now_lust_multiple *= -1
        target_data.trust -= now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust -= now_lust_multiple


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DO_H_FAILED_ADJUST)
def handle_do_h_failed_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    邀请H失败的加反感、加愤怒、降好感度、降信赖修正
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]

        # 高陷落不进行该判断
        chara_fall = attr_calculation.get_character_fall_level(character_data.target_character_id)
        if chara_fall >= 4:
            return

        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        # 加反感
        target_data.status_data.setdefault(20, 0)
        now_lust = target_data.status_data[20]
        now_lust_multiple = 20000
        now_add_lust = add_time + now_lust_multiple
        adjust = attr_calculation.get_ability_adjust(target_data.ability[18])
        now_add_lust *= adjust
        now_add_lust += now_lust / 2
        target_data.status_data[20] += now_add_lust
        target_data.status_data[20] = min(99999, target_data.status_data[20])
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change.status_data.setdefault(20, 0)
        target_change.status_data[20] = now_add_lust
        # 加愤怒
        target_data.angry_point += 100
        target_data.sp_flag.angry_with_player = True
        # 降好感
        base_chara_favorability_and_trust_common_settle(character_id, add_time, True, 0, -15, change_data)
        # 降信赖
        now_lust_multiple = target_data.trust * 0.4 + 5
        if now_lust_multiple < 0:
            now_lust_multiple *= -1
        target_data.trust -= now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust -= now_lust_multiple


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SLEEP_ADD_ADJUST)
def handle_sleep_add_adjust(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （睡觉用）如果在自己宿舍，则换睡衣并有一定几率关门
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if handle_premise.handle_in_dormitory(character_id):
        # 换睡衣
        clothing.get_sleep_cloth(character_id)
        # 被要求不关门则不关门
        if handle_premise.handle_ask_not_lock_door_bedore_sleeping(character_id):
            pass
        # 否则判定是否关门
        elif random.random() < 0.5:
            handle_door_close(character_id, add_time, change_data, now_time)
            # print(F"debug : {cache.character_data[character_id].name} 在{cache.character_data[character_id].dormitory}关门睡觉")
        # else:
            # print(F"debug : {cache.character_data[character_id].name} 在{cache.character_data[character_id].dormitory}不关门睡觉")


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.URINATE_POINT_ZERO)
def handle_urinate_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    尿意值归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.urinate_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_URINATE_POINT_ZERO)
def handle_target_urinate_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象尿意值归零
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
    target_data.urinate_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HUNGER_POINT_ZERO)
def handle_hunger_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    饥饿值归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.hunger_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_HUNGER_POINT_ZERO)
def handle_target_hunger_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象饥饿值归零
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
    target_data.hunger_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SLEEP_POINT_ZERO)
def handle_sleep_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    熟睡值归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.sleep_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_SLEEP_POINT_ZERO)
def handle_target_sleep_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象熟睡值归零
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
    target_data.sleep_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_URINATE_POINT)
def handle_add_small_urinate_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己增加少量尿意值
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.urinate_point += 60


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_ADD_SMALL_URINATE_POINT)
def handle_target_add_small_urinate_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象增加少量尿意值
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
    target_data.urinate_point += 60


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_DESIRE_POINT_ZERO)
def handle_target_desire_point_zero(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象欲望值归零
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
    target_data.desire_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DESIRE_POINT_TO_79)
def handle_desire_point_to_79(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己欲望值调为79
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.desire_point = 79


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.TARGET_DESIRE_POINT_TO_79)
def handle_target_desire_point_to_79(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    交互对象欲望值调为79
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
    target_data.desire_point = 79


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DESIRE_POINT_TO_0)
def handle_desire_point_to_0(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    自己欲望值归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.desire_point = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_SANITY_POINT)
def handle_add_small_sanity_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加少量理智值(15%/h)
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    add_sanity_point = int(add_time / 60 * 0.15 * character_data.sanity_point_max)
    character_data.sanity_point += add_sanity_point
    # 如果超过最大值则=最大值
    if character_data.sanity_point >= character_data.sanity_point_max:
        character_data.sanity_point = character_data.sanity_point_max


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_SEMEN_POINT)
def handle_add_small_semen_point(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    增加少量精液值(15%/h)
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    if character_id > 0:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    add_semen_point = int(add_time / 60 * 0.15 * character_data.semen_point_max)
    character_data.semen_point += add_semen_point
    # 如果超过最大值则=最大值
    if character_data.semen_point >= character_data.semen_point_max:
        character_data.semen_point = character_data.semen_point_max


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.RECORD_TRAINING_TIME)
def handle_record_training_time(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    记录当前训练时间
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.action_info.last_training_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.RECORD_SHOWER_TIME)
def handle_record_shower_time(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    记录当前淋浴时间
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.action_info.last_shower_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.RECORD_WAKE_TIME)
def handle_record_wake_time(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    角色记录并刷新起床时间
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.action_info.wake_time = now_time


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_RESET)
def handle_penis_in_t_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_双方归零
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
    target_data.h_state.insert_position = -1
    character_data.h_state.insert_position = -1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SCENE_ALL_CHARACTERS_PENIS_IN_RESET)
def handle_scene_all_characters_penis_in_reset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    场景内所有角色的当前阴茎位置归零
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    for chara_id in scene_data.character_list:
        now_character_data: game_type.Character = cache.character_data[chara_id]
        now_character_data.h_state.insert_position = -1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_HAIR)
def handle_penis_in_t_hair(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_发交中
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
    target_data.h_state.insert_position = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_FACE)
def handle_penis_in_t_face(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_阴茎蹭脸中
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
    target_data.h_state.insert_position = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_MOUSE)
def handle_penis_in_t_mouse(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_口交中
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
    target_data.h_state.insert_position = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_BREAST)
def handle_penis_in_t_breast(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_乳交中
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
    target_data.h_state.insert_position = 3


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_AXILLA)
def handle_penis_in_t_axilla(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_腋交中
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
    target_data.h_state.insert_position = 4


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_HAND)
def handle_penis_in_t_hand(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_手交中
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
    target_data.h_state.insert_position = 5


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_VAGINA)
def handle_penis_in_t_vagina(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_V插入中
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
    target_data.h_state.insert_position = 6


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_WOMB)
def handle_penis_in_t_womb(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_W插入中
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
    target_data.h_state.insert_position = 7


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_ANAL)
def handle_penis_in_t_anal(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_A插入中
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
    target_data.h_state.insert_position = 8


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_URETHRAL)
def handle_penis_in_t_urethral(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_U插入中
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
    target_data.h_state.insert_position = 9


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_LEG)
def handle_penis_in_t_leg(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_腿交中
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
    target_data.h_state.insert_position = 10


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_FOOT)
def handle_penis_in_t_foot(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_足交中
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
    target_data.h_state.insert_position = 11


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_TAIL)
def handle_penis_in_t_tail(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_尾交中
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
    target_data.h_state.insert_position = 12


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_HORN)
def handle_penis_in_t_horn(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_阴茎蹭角中
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
    target_data.h_state.insert_position = 13


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_EARS)
def handle_penis_in_t_ears(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    当前阴茎位置为交互对象_阴茎蹭耳朵中
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
    target_data.h_state.insert_position = 14


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_HAT)
def handle_penis_in_t_hat(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_帽子交中
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
    target_data.h_state.insert_position = 20


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_GLASSES)
def handle_penis_in_t_classes(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_眼镜交中
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
    target_data.h_state.insert_position = 21


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_EAR_ORNAMENT)
def handle_penis_in_t_ear_ornament(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_耳饰交中
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
    target_data.h_state.insert_position = 22


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_NECK_ORNAMENT)
def handle_penis_in_t_neck_ornament(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_脖饰交中
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
    target_data.h_state.insert_position = 23


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_MOUTH_ORNAMENT)
def handle_penis_in_t_mouth_ornament(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_口罩交中
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
    target_data.h_state.insert_position = 24


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_TOP)
def handle_penis_in_t_top(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_上衣交中
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
    target_data.h_state.insert_position = 25


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_CORSET)
def handle_penis_in_t_corset(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_胸衣交中
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
    target_data.h_state.insert_position = 26


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_GLOVES)
def handle_penis_in_t_gloves(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_手套交中
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
    target_data.h_state.insert_position = 27


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_SKIRT)
def handle_penis_in_t_skirt(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_裙子交中
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
    target_data.h_state.insert_position = 28


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_UNDERWEAR)
def handle_penis_in_t_underwear(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_内裤交中
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
    target_data.h_state.insert_position = 29


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_SOCKS)
def handle_penis_in_t_socks(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_袜子交中
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
    target_data.h_state.insert_position = 30


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_SHOES)
def handle_penis_in_t_shoes(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_鞋子交中
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
    target_data.h_state.insert_position = 31


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_WEAPONS)
def handle_penis_in_t_weapoms(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_武器交中
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
    target_data.h_state.insert_position = 32


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PENIS_IN_T_TROUSERS)
def handle_penis_in_t_trousers(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    改变当前阴茎位置为交互对象_裤子交中
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
    target_data.h_state.insert_position = 28


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.CANCEL_PENIS_IN_FACE_OR_MOUSE)
def handle_cancel_penis_in_face_or_mouse(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    取消为阴茎位置交互对象_阴茎蹭脸中和口交中
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
    if target_data.h_state.insert_position in {1,2}:
        target_data.h_state.insert_position = -1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_NORMAL)
def handle_dr_position_normal(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    博士体位数据变成正常体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 1


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_BACK)
def handle_dr_position_back(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    博士体位数据变成后背体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 2


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_FACE_RIDE)
def handle_dr_position_face_ride(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成对面骑乘体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 3


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_BACK_RIDE)
def handle_dr_position_back_ride(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成背面骑乘体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 4


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_FACE_SEAT)
def handle_dr_position_face_seat(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成对面座体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 5


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_BACK_SEAT)
def handle_dr_position_back_seat(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成背面座体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 6


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_FACE_STAND)
def handle_dr_position_face_stand(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成对面立体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 7


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_BACK_STAND)
def handle_dr_position_back_stand(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成背面立体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 8


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_FACE_HUG)
def handle_dr_position_face_hug(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成对面抱体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 9


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_BACK_HUG)
def handle_dr_position_back_hug(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成背面抱体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 10


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_FACE_LIE)
def handle_dr_position_face_lie(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成对面卧体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 11


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.DR_POSITION_BACK_LIE)
def handle_dr_position_back_lie(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    博士体位数据变成背面卧体位
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[0]
    character_data.h_state.current_sex_position = 12


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.H_IN_LOVE_HOTEL_TO_FALSE)
def handle_h_in_love_hotel_to_false(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    取消自己和交互对象正在爱情旅馆中H的状态
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
    character_data.h_state.h_in_love_hotel = False
    target_data.h_state.h_in_love_hotel = False
