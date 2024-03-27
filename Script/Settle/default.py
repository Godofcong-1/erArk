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
    handle_instruct,
    character_behavior,
    basement,
)
from Script.Core import cache_control, constant, constant_effect, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw
from Script.UI.Panel import event_option_panel, originium_arts, ejaculation_panel
from Script.Settle import default_experience

import random, math

_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """


def chara_base_state_adjust(character_id: int, state_id: int, ability_level: int = 0):
    """
    角色状态系数获得的共用函数
    Keyword arguments:
    character_id -- 角色id
    state_id -- 状态id
    ability_level -- 系数修正用能力等级
    """

    character_data: game_type.Character = cache.character_data[character_id]

    # 系数加成
    final_adjust = 0
    # 能力修正
    if ability_level in [13,14,15,16,17,18,19]:
        feel_adjust = attr_calculation.get_mark_debuff_adjust(ability_level)
    else:
        feel_adjust = attr_calculation.get_ability_adjust(ability_level)
    final_adjust += feel_adjust
    # 调香
    if character_data.sp_flag.aromatherapy == 2 and state_id == 9:
        final_adjust += 1
    elif character_data.sp_flag.aromatherapy == 3 and state_id in [17, 18, 19, 20]:
        final_adjust -= 0.5
    elif character_data.sp_flag.aromatherapy == 4 and state_id ==12:
        final_adjust += 1
    final_adjust = max(0, final_adjust)

    return final_adjust


def chara_feel_state_adjust(character_id: int, state_id: int, ability_level: int = 0):
    """
    角色快感系数获得的共用函数
    Keyword arguments:
    character_id -- 角色id
    state_id -- 状态id
    ability_level -- 系数修正用能力等级
    """

    character_data: game_type.Character = cache.character_data[character_id]

    # 系数加成
    final_adjust = 0
    # 部位感觉
    feel_adjust = attr_calculation.get_ability_adjust(character_data.ability[state_id])
    final_adjust += feel_adjust
    # 技巧
    if ability_level:
        tech_adjust = attr_calculation.get_ability_adjust(ability_level)
        final_adjust = math.sqrt(feel_adjust * tech_adjust)
    # 调香
    if character_data.sp_flag.aromatherapy == 4:
        final_adjust += 1

    return final_adjust


def base_chara_state_common_settle(
        character_id: int,
        add_time: int,
        state_id: int,
        base_value: int = 30,
        ability_level: int = 0,
        extra_adjust: float = 0,
        change_data: game_type.CharacterStatusChange = None,
        change_data_to_target_change: game_type.CharacterStatusChange = None,
        ):
    """
    基础角色状态通用结算函数\n
    Keyword arguments:\n
    character_id -- 角色id\n
    add_time -- 结算时间\n
    state_id -- 状态id\n
    base_value -- 基础固定值\n
    ability_level -- 系数修正用能力等级\n
    extra_adjust -- 额外系数\n
    change_data_to_target_change -- 结算信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return

    # 基础固定值
    time_base_value = add_time + base_value

    # 系数加成，区分快感状态和普通状态
    if state_id <= 7:
        final_adjust = chara_feel_state_adjust(character_id, state_id, ability_level) + extra_adjust
    else:
        final_adjust = chara_base_state_adjust(character_id, state_id, ability_level) + extra_adjust

    # 最终值
    final_value = time_base_value * final_adjust + character_data.status_data[state_id] / 10

    # 结算最终值
    character_data.status_data[state_id] += final_value
    character_data.status_data[state_id] = min(99999, character_data.status_data[state_id])

    # 结算信息记录对象
    if change_data != None:
        change_data.status_data.setdefault(state_id, 0)
        change_data.status_data[state_id] += final_value
    if change_data_to_target_change != None:
        change_data_to_target_change.target_change.setdefault(character_id, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data_to_target_change.target_change[character_id]
        target_change.status_data.setdefault(state_id, 0)
        target_change.status_data[state_id] += final_value


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
    add_hit_point = add_time * 20
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
    add_mana_point = add_time * 30
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
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if target_data.dead:
            return
        if target_data.sp_flag.unconscious_h:
            return
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
        )


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
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if target_data.dead:
            return
        if target_data.sp_flag.unconscious_h:
            return
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time) * -1
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
        )


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
    character_data: game_type.Character = cache.character_data[character_id]
    # 首先需要有交互对象，然后要么是玩家发起指令，要么是NPC对玩家发起指令
    if character_data.target_character_id != character_id and (
            character_id != 0 or character_data.target_character_id != 0):
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if character_id != 0 and character_data.target_character_id != 0:
            return
        if target_data.sp_flag.unconscious_h:
            return
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        now_lust_multiple = character.calculation_trust(character_id, target_data.cid, add_time)
        if now_lust_multiple < 0:
            now_lust_multiple = 0
        target_data.trust += now_lust_multiple
        target_data.trust = min(300, target_data.trust)
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple
        # NPC对玩家发起指令的情况
        if (character_id != 0) and (character_data.target_character_id == 0):
            character_data.trust += now_lust_multiple
            change_data.trust += now_lust_multiple


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
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.target_character_id != character_id and (
            not character_id or not character_data.target_character_id):
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if character_id != 0 and character_data.target_character_id != 0:
            return
        if target_data.sp_flag.unconscious_h:
            return
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        now_lust_multiple = character.calculation_trust(character_id, target_data.cid, add_time)
        if now_lust_multiple > 0:
            now_lust_multiple *= -1
        target_data.trust += now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple
        if (character_id != 0) and (character_data.target_character_id == 0):
            character_data.trust += now_lust_multiple
            change_data.trust += now_lust_multiple


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
    if not add_time:
        return
    sub_hit = add_time * 3
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    # 气力为0时体力消耗3倍#
    if character_data.mana_point == 0:
        sub_hit *= 3
    # 体力不足0时锁为1#
    if character_data.hit_point >= sub_hit:
        character_data.hit_point -= sub_hit
        change_data.hit_point -= sub_hit
    else:
        change_data.hit_point -= character_data.hit_point
        character_data.hit_point = 1
        if not character_data.sp_flag.tired:
            character_data.sp_flag.tired = 1
            # H时单独结算
            target_data: game_type.Character = cache.character_data[character_data.target_character_id]
            if target_data.sp_flag.is_h:
                character_behavior.judge_character_tired_sleep(0)
                handle_instruct.handle_end_h()
            else:
                # 如果和玩家位于同一地点，则输出提示信息
                if character_data.position == cache.character_data[0].position:
                    now_draw = draw.NormalDraw()
                    now_draw.width = width
                    now_draw.text = "\n" + character_data.name + "太累了\n"
                    now_draw.draw()
    # 交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        sub_hit = add_time * 3
        # 气力为0时体力消耗3倍
        if target_data.mana_point == 0:
            sub_hit *= 3
        # 体力不足0时锁为1
        if target_data.hit_point >= sub_hit:
            target_data.hit_point -= sub_hit
            target_change.hit_point -= sub_hit
        else:
            target_change.hit_point -= target_data.hit_point
            target_data.hit_point = 1
            if not target_data.sp_flag.tired:
                target_data.sp_flag.tired = 1
                # H时单独结算
                if target_data.sp_flag.is_h:
                    character_behavior.judge_character_tired_sleep(character_data.target_character_id)
                    handle_instruct.handle_end_h()
                else:
                    # 如果和玩家位于同一地点，则输出提示信息
                    if character_data.position == cache.character_data[0].position:
                        now_draw = draw.NormalDraw()
                        now_draw.width = width
                        now_draw.text = "\n" + target_data.name + "太累了\n"
                        now_draw.draw()


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
    if not add_time:
        return
    sub_mana = add_time * 6
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
                # H时单独结算
                target_data: game_type.Character = cache.character_data[character_data.target_character_id]
                if target_data.sp_flag.is_h:
                    character_behavior.judge_character_tired_sleep(0)
                    handle_instruct.handle_end_h()
                else:
                    # 如果和玩家位于同一地点，则输出提示信息
                    if character_data.position == cache.character_data[0].position:
                        now_draw = draw.NormalDraw()
                        now_draw.width = width
                        now_draw.text = "\n" + character_data.name + "太累了\n"
                        now_draw.draw()
    # 交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        sub_mana = add_time * 6
        if target_data.mana_point >= sub_mana:
            target_data.mana_point -= sub_mana
            target_change.mana_point -= sub_mana
        else:
            target_change.mana_point -= target_data.mana_point
            sub_mana -= target_data.mana_point
            target_data.mana_point = 0
            target_data.hit_point -= sub_mana
            target_change.hit_point -= sub_mana
            if target_data.hit_point <= 0:
                target_data.hit_point = 1

                if not target_data.sp_flag.tired:
                    target_data.sp_flag.tired = 1
                    # H时单独结算
                    if target_data.sp_flag.is_h:
                        character_behavior.judge_character_tired_sleep(character_data.target_character_id)
                        handle_instruct.handle_end_h()
                    else:
                        # 如果和玩家位于同一地点，则输出提示信息
                        if character_data.position == cache.character_data[0].position:
                            now_draw = draw.NormalDraw()
                            now_draw.width = width
                            now_draw.text = "\n" + target_data.name + "太累了\n"
                            now_draw.draw()


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
    if not add_time:
        return
    sub_hit = add_time * 3
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    # 气力为0时体力消耗3倍#
    if character_data.mana_point == 0:
        sub_hit *= 3
    # 体力不足0时锁为1#
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
                now_draw.width = width
                now_draw.text = "\n" + character_data.name + "太累了\n"
                now_draw.draw()


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
    if not add_time:
        return
    sub_mana = add_time * 6
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
                    now_draw.width = width
                    now_draw.text = "\n" + character_data.name + "太累了\n"
                    now_draw.draw()


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
    add_hit_point = add_time * 20
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
    add_mana_point = add_time * 25
    character_data.mana_point += add_mana_point
    change_data.mana_point += add_mana_point
    if character_data.mana_point > character_data.mana_point_max:
        character_data.mana_point = character_data.mana_point_max
    # 交互对象也同样#
    if character_data.target_character_id != character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        add_mana_point = add_time * 20
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
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if target_data.cid:
            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change = change_data.target_change[target_data.cid]
            add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
            character_handle.add_favorability(
                character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )


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
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[character_id]
    while 1:
        recipes_id_list = list(cache.recipe_data.keys())
        recipes_id = random.choice(recipes_id_list)
        if cache.recipe_data[recipes_id].difficulty <= character_data.ability[43]:
            break
    food_recipe: game_type.Recipes = cache.recipe_data[recipes_id]
    food_list = {}
    new_food = cooking.cook(food_list, recipes_id, character_data.ability[43], character_data.name)
    cache.restaurant_data.setdefault(str(recipes_id), {})
    cache.restaurant_data[str(recipes_id)][new_food.uid] = new_food
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
    while 1:
        recipes_id_list = list(cache.recipe_data.keys())
        recipes_id = random.choice(recipes_id_list)
        if cache.recipe_data[recipes_id].difficulty <= character_data.ability[43]:
            break
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

    # 判定是否为道具性交
    item_flag = False
    if cache.input_cache[len(cache.input_cache) - 1] == str(constant.Instruct.VIBRATOR_INSERTION):
        item_flag = True

    # 遍历指令列表，获得指令的中文名
    i = 0
    for k in constant.Instruct.__dict__:
        # print(f"debug i = {i}，k = {k}")
        # print(f"debug 上指令 = {cache.input_cache[len(cache.input_cache)-1]}")
        if int(cache.input_cache[len(cache.input_cache) - 1]) + 2 == i:
            instruct_name = constant.instruct_en2cn[k]
            break
        i += 1

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
            now_draw.text = f"\n获得了{target_data.name}穿着的{pan_name}(沾有处子血)，已自动存入收藏品列表，可在藏物馆查看\n\n"
            now_draw.draw()
            character_data.pl_collection.first_panties[character_data.target_character_id] = f"{pan_name}(沾有处子血)"
        else:
            now_draw.text = f"\n{target_data.name}的处子血滴了下去，被你谨慎地用试管接了一滴，已自动存入收藏品列表，可在藏物馆查看\n\n"
            character_data.pl_collection.first_panties[
                character_data.target_character_id] = f"一滴{target_data.name}的处子血"
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

    # 遍历指令列表，获得指令的中文名
    i = 0
    for k in constant.Instruct.__dict__:
        if int(cache.input_cache[len(cache.input_cache) - 1]) + 2 == i:
            instruct_name = constant.instruct_en2cn[k]
            break
        i += 1

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
    character_data.sanity_point = max(character_data.sanity_point - 5, 0)
    change_data.sanity_point -= 5
    character_data.pl_ability.today_sanity_point_cost += 5


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
    character_data.sanity_point = max(character_data.sanity_point - 20, 0)
    change_data.sanity_point -= 20
    character_data.pl_ability.today_sanity_point_cost += 20
    # 结算催眠度增加
    hypnosis_degree_addition = attr_calculation.hypnosis_degree_calculation(character_data.target_character_id)
    hypnosis_degree_grow = 10 * hypnosis_degree_addition
    # debug下催眠增加到999
    if cache.debug_mode:
        hypnosis_degree_grow = 999
    new_hypnosis_degree = target_character_data.hypnosis.hypnosis_degree + hypnosis_degree_grow
    # 赋予到角色数据
    target_character_data.hypnosis.hypnosis_degree = min(new_hypnosis_degree, attr_calculation.hypnosis_degree_limit_calculation())
    target_change.hypnosis_degree += hypnosis_degree_grow
    # 判断催眠完成
    originium_arts.evaluate_hypnosis_completion(character_data.target_character_id)


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
    # 去掉里的自己
    if character_id in scene_character_list:
        scene_character_list.remove(character_id)
    # 结算理智消耗
    sanity_point_cost = 10 + 10 * len(scene_character_list)
    character_data.sanity_point = max(character_data.sanity_point - sanity_point_cost, 0)
    change_data.sanity_point -= sanity_point_cost
    character_data.pl_ability.today_sanity_point_cost += sanity_point_cost
    # 遍历角色列表
    for target_id in scene_character_list:
        target_character_data = cache.character_data[target_id]
        change_data.target_change.setdefault(target_character_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_character_data.cid]
        if target_character_data.dead:
            continue
        # 结算催眠度增加
        hypnosis_degree_addition = attr_calculation.hypnosis_degree_calculation(target_id)
        hypnosis_degree_grow = 10 * hypnosis_degree_addition
        # debug下催眠增加到999
        if cache.debug_mode:
            hypnosis_degree_grow = 999
        new_hypnosis_degree = target_character_data.hypnosis.hypnosis_degree + hypnosis_degree_grow
        # 赋予到角色数据
        target_character_data.hypnosis.hypnosis_degree = min(new_hypnosis_degree, attr_calculation.hypnosis_degree_limit_calculation())
        target_change.hypnosis_degree += hypnosis_degree_grow
        # 判断催眠完成
        originium_arts.evaluate_hypnosis_completion(target_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.HYPNOSIS_CANCEL)
def handle_hypnosis_cancel(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    解除催眠
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
    add_hit_point = add_time * 80
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
    add_mana_point = add_time * 100
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
    # if target_data.state == constant.CharacterStatus.STATUS_DEAD:
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
                    character.init_character_behavior_start_time(
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
    去掉身上所有的道具
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
    交互对象去掉身上所有的道具
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
    # print(f"debug 触发去掉身上所有的道具 target_data.h_state.body_item = {target_data.h_state.body_item}")
    for i in range(len(target_data.h_state.body_item)):
        # print(f"debug i = {i}")
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
    交互对象增加大量欲情和屈服（媚药）
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

    # A灌肠
    target_data.dirty.a_clean = 1


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
    target_data.dirty.a_clean = 2


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


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.ADD_SMALL_LEARN)
def handle_add_small_learn(
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
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    base_chara_state_common_settle(character_id, add_time, 9, 20, change_data = change_data)


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
    character_data.dirty = attr_calculation.get_dirty_zero()


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
    if len(character_data.behavior.move_src) and not character_id:
        character_data.behavior.move_target = character_data.behavior.move_src
        handle_move_to_target_scene(character_id, add_time, change_data, now_time)
        character_data.sp_flag.move_stop = 1


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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    character_data.h_state = attr_calculation.get_h_state_zero(character_data.h_state)
    target_data.h_state = attr_calculation.get_h_state_zero(target_data.h_state)
    for orgasm in range(8):
        now_data = attr_calculation.get_status_level(target_data.status_data[orgasm])
        target_data.h_state.orgasm_level[orgasm] = now_data
    # 清零H相关二段状态
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0 and (second_behavior_id in range(1000,1025) or second_behavior_id in range(1200,1250)):
            character_data.second_behavior[second_behavior_id] = 0
    for second_behavior_id, behavior_data in target_data.second_behavior.items():
        if behavior_data != 0 and (second_behavior_id in range(1000,1025) or second_behavior_id in range(1200,1250)):
            target_data.second_behavior[second_behavior_id] = 0


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
    target_character = cache.character_data[character_data.target_character_id]
    target_character.sp_flag.is_h = 0


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.T_H_FLAG_TO_1)
def handle_t_h_flag_to_1(
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
    target_character = cache.character_data[character_data.target_character_id]
    target_character.sp_flag.is_h = 1


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
    自身清零催眠系的flag状态
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
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        add_favorability *= adjust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
        )
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
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        add_favorability *= adjust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
        )
        # 信赖变化#
        now_lust_multiple = character.calculation_trust(character_id, target_data.cid, add_time)
        now_lust_multiple *= adjust * 0.4
        target_data.trust += now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple
        if (character_id != 0) and (character_data.target_character_id == 0):
            character_data.trust += now_lust_multiple
            change_data.trust += now_lust_multiple
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
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        add_favorability *= adjust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
        )
        # 信赖变化#
        now_lust_multiple = character.calculation_trust(character_id, target_data.cid, add_time)
        now_lust_multiple *= adjust * 0.4
        target_data.trust += now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple
        if (character_id != 0) and (character_data.target_character_id == 0):
            character_data.trust += now_lust_multiple
            change_data.trust += now_lust_multiple
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
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]

    if character_data.dead:
        return
    if target_data.dead:
        return
    now_draw_text = ""
    # 获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[45])
    # 如果有交互对象，则算上对方的学识加成
    if character_data.target_character_id != character_id:
        adjust_target = attr_calculation.get_ability_adjust(target_data.ability[45])
        adjust += adjust_target
        now_draw_text += _(f"在{target_data.name}的帮助下，")
    # 根据博士办公室的房间等级来调整
    now_level = cache.rhodes_island.facility_level[22]
    facility_cid = game_config.config_facility_effect_data["博士办公室"][int(now_level)]
    facility_effect = game_config.config_facility_effect[facility_cid].effect
    adjust *= (1 + facility_effect / 100)
    # 处理工作
    finish_work = int(add_time * adjust)
    cache.rhodes_island.office_work = int(max(cache.rhodes_island.office_work - finish_work, 0))
    # 输出处理结果
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw_text += _(f"共处理了{finish_work}公务，")
        if cache.rhodes_island.office_work > 0:
            now_draw_text += _(f"还有{cache.rhodes_island.office_work}需要处理\n")
        else:
            now_draw_text += _(f"已经全部处理完毕\n\n")
        now_draw.text = now_draw_text
        now_draw.width = width
        now_draw.draw()


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
    # 获得加成 #
    now_add_lust = add_time * adjust * 200
    now_add_lust = int(now_add_lust * random.uniform(0.5, 1.5))

    # 如果有交互对象，则算上对方的医疗加成
    if character_data.target_character_id != character_id:
        adjust_target = attr_calculation.get_ability_adjust(target_data.ability[46])
        now_add_lust += int(add_time * adjust_target)
    cache.rhodes_island.cure_income += now_add_lust
    cache.rhodes_island.patient_now -= 1
    cache.rhodes_island.patient_cured += 1

    # 如果是玩家在诊疗或玩家与诊疗者在同一位置的话，显示诊疗情况
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.width = width
        now_draw.text = _(f"\n在{character_data.name}的努力下，医治了一名病人，支付了{now_add_lust}龙门币的医疗费。（今日剩余病人数：{cache.rhodes_island.patient_now}人）\n")
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

    # 如果是玩家在招募或玩家与招募者在同一位置的话，显示招募进度的增加情况
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.width = width
        now_draw.text = _(f"\n在{character_data.name}的努力下，{select_index}号招募位进度+{round(now_add_lust,1)}%，现在为{round(cache.rhodes_island.recruit_line[select_index][0] + now_add_lust,1)}%\n")
        now_draw.draw()

    # 增加对应槽的招募值，并进行结算
    cache.rhodes_island.recruit_line[select_index][0] += now_add_lust
    basement.update_recruit()


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
            now_draw.text = _(f"\n请先使用邀请系统选择邀请的对象，再进行邀请\n")
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
        now_draw.text = _(f"\n在{character_data.name}的努力下，邀请进度+{round(now_add_lust,1)}%，现在为{round(cache.rhodes_island.invite_visitor[1] + now_add_lust,1)}%\n")
        now_draw.draw()

    # 增加对应槽的邀请值，并进行结算
    cache.rhodes_island.invite_visitor[1] += now_add_lust
    basement.update_invite_visitor()


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

    now_milk = target_data.pregnancy.milk
    character_data.behavior.milk_ml += now_milk
    cache.rhodes_island.milk_in_fridge.setdefault(character_data.target_character_id, 0)
    cache.rhodes_island.milk_in_fridge[character_data.target_character_id] += now_milk
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
    character_data: game_type.Character = cache.character_data[character_id]
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
        basement.check_return_book(character_id)


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
    default_experience.handle_add_1_learn_experience(character_id, add_time, change_data, now_time)

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
                if other_character_data.state == constant.CharacterStatus.STATUS_ATTENT_CLASS:

                    # 增加习得和学识经验
                    base_chara_state_common_settle(chara_id, add_time, 9, ability_level = character_data.ability[45], change_data_to_target_change = change_data)
                    default_experience.handle_add_1_learn_experience(chara_id, add_time, change_data, now_time)

                    # 如果老师是玩家
                    if character_id == 0:
                        change_data.target_change.setdefault(other_character_data.cid, game_type.TargetChange())
                        target_change: game_type.TargetChange = change_data.target_change[other_character_data.cid]

                        # 加好感
                        add_favorability = character.calculation_favorability(character_id, other_character_data.cid, add_time)
                        character_handle.add_favorability(
                            character_id, other_character_data.cid, add_favorability, change_data, target_change, now_time
                        )

                        # 加信赖
                        now_lust_multiple = character.calculation_trust(character_id, other_character_data.cid, add_time)
                        now_lust_multiple *= attr_calculation.get_ability_adjust(other_character_data.ability[32])
                        other_character_data.trust += now_lust_multiple
                        change_data.target_change.setdefault(other_character_data.cid, game_type.TargetChange())
                        target_change.trust += now_lust_multiple

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
    （装袋搬走用）交互对象获得装袋搬走flag，清除跟随和助理状态。并从当前场景移除角色id，玩家增加搬运人id
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
    if character_data.assistant_character_id == character_data.target_character_id:
        character_data.assistant_character_id = 0
    # 对方数据结算
    target_data.sp_flag.be_bagged = 1
    target_data.sp_flag.is_follow = 0
    cache.npc_id_got.remove(character_data.target_character_id)
    # 地图数据结算
    old_scene_path_str = map_handle.get_map_system_path_str_for_list(target_data.position)
    if character_data.target_character_id in cache.scene_data[old_scene_path_str].character_list:
        cache.scene_data[old_scene_path_str].character_list.remove(character_data.target_character_id)
    target_data.position = ["0", "0"]


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.PUT_INTO_PRISON_ADD_ADJUST)
def handle_put_into_prison_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （投入监牢用）玩家失去搬运人id，玩家搬运的角色失去装袋搬走flag，获得监禁flag，获得屈服1，反发2和恐怖1，并从当前场景增加角色id，清零各特殊状态flag
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    # 获取角色数据
    character_data: game_type.Character = cache.character_data[0]
    target_id = character_data.sp_flag.bagging_chara_id
    target_data: game_type.Character = cache.character_data[target_id]
    # 玩家数据结算
    character_data.sp_flag.bagging_chara_id = 0
    # 对方数据结算
    target_data.sp_flag.be_bagged = 0
    target_data.sp_flag.imprisonment = 1
    cache.npc_id_got.add(target_id)
    # 屈服1，恐怖1，反发2
    if target_data.ability[14] <= 0:
        target_data.ability[14] = 1
        target_data.second_behavior[1033] = 1
    if target_data.ability[17] <= 0:
        target_data.ability[17] = 1
        target_data.second_behavior[1042] = 1
    if target_data.ability[18] <= 1:
        target_data.ability[18] = 2
        target_data.second_behavior[1046] = 1
    # 对方位置结算
    target_data.position = character_data.position
    target_data.behavior.move_src = character_data.position
    target_data.behavior.move_target = character_data.position
    # 清零各特殊状态flag
    target_data.sp_flag.is_follow = 0
    target_data.sp_flag.sleep = 0
    target_data.sp_flag.rest = 0
    target_data.sp_flag.pee = 0
    target_data.sp_flag.milk = 0
    target_data.sp_flag.shower = 0
    target_data.sp_flag.eat_food = 0
    # 地图数据结算
    old_scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    if target_id not in cache.scene_data[old_scene_path_str].character_list:
        cache.scene_data[old_scene_path_str].character_list.add(target_id)


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.SET_FREE_ADD_ADJUST)
def handle_set_free_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （解除囚禁）交互对象失去监禁flag
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


@settle_behavior.add_settle_behavior_effect(constant_effect.BehaviorEffect.EAT_ADD_ADJUST)
def handle_eat_add_just(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    （进食）根据当前场景的有无目标，以及食物的调味来区分进行食用人的判断和相应的结算
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

    # 吃掉该食物
    handle_delete_food(character_id,add_time=add_time,change_data=change_data,now_time=now_time)
    # 对要吃食物的人进行结算
    for chara_id in eat_food_chara_id_list:
        target_data: game_type.Character = cache.character_data[chara_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]

        # 加好感
        if chara_id:
            add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
            character_handle.add_favorability(
                    character_id, target_data.cid, add_favorability, change_data, target_change, now_time
                )

        # 加体力气力，清零饥饿值和进食状态
        handle_add_small_hit_point(chara_id,add_time=add_time,change_data=target_change,now_time=now_time)
        handle_add_small_mana_point(chara_id,add_time=add_time,change_data=target_change,now_time=now_time)
        handle_hunger_point_zero(chara_id,add_time=add_time,change_data=target_change,now_time=now_time)
        handle_eat_food_flag_to_0(chara_id,add_time=add_time,change_data=target_change,now_time=now_time)

        # 精液食物则将精液加到口腔污浊，并加精液经验
        if character_data.behavior.food_seasoning in {11,12}:
            # 加精液经验
            default_experience.handle_target_add_1_cumsdrink_experience(0,add_time=add_time,change_data=change_data,now_time=now_time)
            default_experience.handle_target_add_1_cums_experience(0,add_time=add_time,change_data=change_data,now_time=now_time)
            # 获取精液量
            now_food = character_data.behavior.target_food
            semen_ml = now_food.special_seasoning_amount
            # 加精液到口腔
            cache.shoot_position = 2    # 口腔
            ejaculation_panel.update_semen_dirty(chara_id, 2, 0, semen_ml)
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
    add_hp = int(character_data.hit_point_max * 0.005 * random.uniform(0.8, 1.2))
    add_mp = int(character_data.mana_point_max * 0.01 * random.uniform(0.5, 1.2))
    character_data.hit_point_max += add_hp
    character_data.mana_point_max += add_mp
    # 如果和玩家位于同一地点，则输出提示信息
    if character_data.position == cache.character_data[0].position:
        now_draw = draw.NormalDraw()
        now_draw.text = f"\n{character_data.name}的体力上限增加{str(add_hp)},气力上限增加{str(add_mp)}"
        now_draw.width = width
        now_draw.draw()
    # 交互对象也同样#
    if character_data.target_character_id != character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        add_hp = int(target_data.hit_point_max * 0.005 * random.uniform(0.8, 1.2))
        add_mp = int(target_data.mana_point_max * 0.01 * random.uniform(0.5, 1.2))
        target_data.hit_point_max += add_hp
        target_data.mana_point_max += add_mp
        # 如果和玩家位于同一地点，则输出提示信息
        if character_data.position == cache.character_data[0].position:
            now_draw = draw.NormalDraw()
            now_draw.text = f"\n{target_data.name}的体力上限增加{str(add_hp)},气力上限增加{str(add_mp)}\n"
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
        # 好感度变化#
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        # print(f"debug 唱歌，角色 = {character_data.name}，目标= {target_data.name}，add_favorability = {add_favorability}")
        if good_flag or add_favorability < 0:
            add_favorability *= adjust
        else:
            add_favorability *= (adjust - 1)

        # print(f"debug 唱歌，adjust = {adjust}，add_favorability = {add_favorability}")

        # 对在场的全部角色起效
        for chara_id in cache.scene_data[map_handle.get_map_system_path_str_for_list(character_data.position)].character_list:
            # 跳过玩家自己
            if chara_id == character_id:
                continue
            target_data: game_type.Character = cache.character_data[chara_id]

            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            character_handle.add_favorability(
                character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
            # 信赖变化#
            now_lust_multiple = character.calculation_trust(character_id, target_data.cid, add_time)
            if good_flag:
                now_lust_multiple *= adjust
            else:
                now_lust_multiple *= (adjust - 1)
            target_data.trust += now_lust_multiple
            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            target_change.trust += now_lust_multiple
            if (character_id != 0) and (character_data.target_character_id == 0):
                character_data.trust += now_lust_multiple
                change_data.trust += now_lust_multiple

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
        # 好感度变化#
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        if good_flag or add_favorability < 0:
            add_favorability *= adjust
        else:
            add_favorability *= (adjust - 1)

        # print(f"debug 乐器，角色 = {character_data.name}，目标= {target_data.name}，good_flag = {good_flag}，add_favorability = {add_favorability}")

        # 对在场的全部角色起效
        for chara_id in cache.scene_data[map_handle.get_map_system_path_str_for_list(character_data.position)].character_list:
            # 跳过玩家自己
            if chara_id == character_id:
                continue
            target_data: game_type.Character = cache.character_data[chara_id]

            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            character_handle.add_favorability(
                character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
            # 信赖变化#
            now_lust_multiple = character.calculation_trust(character_id, target_data.cid, add_time)
            now_lust_multiple *= 2
            if good_flag:
                now_lust_multiple *= adjust
            else:
                now_lust_multiple *= (adjust - 1)
            target_data.trust += now_lust_multiple
            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
            target_change.trust += now_lust_multiple
            if (character_id != 0) and (character_data.target_character_id == 0):
                character_data.trust += now_lust_multiple
                change_data.trust += now_lust_multiple

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
        base_chara_state_common_settle(character_data.target_character_id, add_time, 0, 50, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = character_data.ability[0], change_data_to_target_change = change_data)


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
        base_chara_state_common_settle(character_data.target_character_id, add_time, 1, 50, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = character_data.ability[1], change_data_to_target_change = change_data)


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
        base_chara_state_common_settle(character_data.target_character_id, add_time, 2, 50, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = character_data.ability[2], change_data_to_target_change = change_data)


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
        base_chara_state_common_settle(character_data.target_character_id, add_time, 4, 50, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = character_data.ability[4], change_data_to_target_change = change_data)


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
        base_chara_state_common_settle(character_data.target_character_id, add_time, 5, 50, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = character_data.ability[5], change_data_to_target_change = change_data)


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
        base_chara_state_common_settle(character_data.target_character_id, add_time, 6, 50, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = character_data.ability[6], change_data_to_target_change = change_data)


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
        base_chara_state_common_settle(character_data.target_character_id, add_time, 7, 50, change_data_to_target_change = change_data)
        # 欲情
        base_chara_state_common_settle(character_data.target_character_id, add_time, 12, 50, ability_level = character_data.ability[7], change_data_to_target_change = change_data)


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
        adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])
        # 苦痛变化#
        target_data.status_data.setdefault(17, 0)
        now_lust = target_data.status_data[17]
        now_lust_multiple = 30
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[17] += now_add_lust
        target_data.status_data[17] = min(99999, target_data.status_data[17])
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(17, 0)
        target_change.status_data[17] += now_add_lust


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
        target_change = change_data.target_change[target_data.cid]
        # 加反感
        target_data.status_data.setdefault(20, 0)
        now_lust = target_data.status_data[20]
        now_lust_multiple = 200
        now_add_lust = add_time + now_lust_multiple
        adjust = attr_calculation.get_ability_adjust(target_data.ability[18])
        now_add_lust *= adjust
        now_add_lust += now_lust / 10
        target_data.status_data[20] += now_add_lust
        target_data.status_data[20] = min(99999, target_data.status_data[20])
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change.status_data.setdefault(20, 0)
        target_change.status_data[20] += now_add_lust
        # 加愤怒
        target_data.angry_point += 50
        target_data.sp_flag.angry_with_player = True
        # 降好感
        minus_favorability = character.calculation_favorability(character_id, target_data.cid, add_time) * -1
        character_handle.add_favorability(
            character_id, target_data.cid, minus_favorability, change_data, target_change, now_time
        )


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
        minus_favorability = character.calculation_favorability(character_id, target_data.cid, add_time) * -1
        minus_favorability *= 3
        character_handle.add_favorability(
            character_id, target_data.cid, minus_favorability, change_data, target_change, now_time
        )
        # 降信赖
        now_lust_multiple = target_data.trust * 0.2 + 2
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

        # 不需要再进行该判断
        # if not character.calculation_instuct_judege(0,character_data.target_character_id,"严重骚扰"):

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
        minus_favorability = character.calculation_favorability(character_id, target_data.cid, add_time) * -1
        minus_favorability *= 15
        character_handle.add_favorability(
            character_id, target_data.cid, minus_favorability, change_data, target_change, now_time
        )
        # 降信赖
        now_lust_multiple = target_data.trust * 0.4 - 5
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
    （睡觉用）清零熟睡值
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
