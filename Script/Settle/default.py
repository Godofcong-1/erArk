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
    handle_instruct,
    character_behavior,
)
from Script.Core import cache_control, constant, game_type, get_text
from Script.Config import game_config, normal_config
from Script.UI.Moudle import draw

import random


_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.NOTHING)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_SMALL_HIT_POINT)
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
    add_hit_point = add_time * 40
    character_data.hit_point += add_hit_point
    if character_data.hit_point > character_data.hit_point_max:
        add_hit_point -= character_data.hit_point - character_data.hit_point_max
        character_data.hit_point = character_data.hit_point_max
    change_data.hit_point += add_hit_point


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_SMALL_MANA_POINT)
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
    add_mana_point = add_time * 60
    character_data.mana_point += add_mana_point
    if character_data.mana_point > character_data.mana_point_max:
        add_mana_point -= character_data.mana_point - character_data.mana_point_max
        character_data.mana_point = character_data.mana_point_max
    change_data.mana_point += add_mana_point


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_INTERACTION_FAVORABILITY)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if target_data.dead:
            return
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
        )


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_SMALL_TRUST)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if target_data.dead:
            return
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change = change_data.target_change[target_data.cid]
        now_lust_multiple = 1
        adjust = attr_calculation.get_ability_adjust(target_data.ability[21])
        now_lust_multiple *= adjust
        target_data.trust += now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple
        if (character_id != 0) and (character_data.target_character_id == 0):
            character_data.trust += now_lust_multiple
            change_data.trust += now_lust_multiple


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.DOWN_BOTH_SMALL_HIT_POINT)
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
    sub_hit = add_time * 5
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
            # H时单独结算
            if target_data.is_h:
                character_behavior.judge_character_tired_sleep(0)
                handle_instruct.handle_end_h()
            else:
                now_draw = draw.NormalDraw()
                now_draw.width = width
                now_draw.text = "\n" + character_data.name + "太累了\n"
                now_draw.draw()
    #交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        sub_hit = add_time * 5
        #气力为0时体力消耗3倍
        if target_data.mana_point == 0:
            sub_hit *= 3
        #体力不足0时锁为1
        if target_data.hit_point >= sub_hit:
            target_data.hit_point -= sub_hit
            target_change.hit_point -= sub_hit
        else:
            target_change.hit_point -= target_data.hit_point
            target_data.hit_point = 1
            if not target_data.tired:
                target_data.tired = 1
                # H时单独结算
                if target_data.is_h:
                    character_behavior.judge_character_tired_sleep(character_data.target_character_id)
                    handle_instruct.handle_end_h()
                else:
                    now_draw = draw.NormalDraw()
                    now_draw.width = width
                    now_draw.text = "\n" + target_data.name + "太累了\n"
                    now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.DOWN_BOTH_SMALL_MANA_POINT)
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
    sub_mana = add_time * 7.5
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
                now_draw.width = width
                now_draw.text = "\n" + character_data.name + "太累了\n"
                now_draw.draw()
    #交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        sub_mana = add_time * 7.5
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
                if not target_data.tired:
                    target_data.tired = 1
                    now_draw = draw.NormalDraw()
                    now_draw.width = width
                    now_draw.text = "\n" + target_data.name + "太累了\n"
                    now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.DOWN_SELF_SMALL_HIT_POINT)
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
    sub_hit = add_time * 5
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
            now_draw.width = width
            now_draw.text = "\n" + character_data.name + "太累了\n"
            now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.DOWN_SELF_SMALL_MANA_POINT)
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
    sub_mana = add_time * 7.5
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
                now_draw.width = width
                now_draw.text = "\n" + character_data.name + "太累了\n"
                now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_BOTH_SMALL_HIT_POINT)
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
    add_hit_point = add_time * 15
    character_data.hit_point += add_hit_point
    if character_data.hit_point > character_data.hit_point_max:
        add_hit_point -= character_data.hit_point - character_data.hit_point_max
        character_data.hit_point = character_data.hit_point_max
    change_data.hit_point += add_hit_point
    #交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        add_hit_point = add_time * 15
        #如果气力=0则恢复减半
        if target_data.mana_point == 0:
            add_hit_point /= 2
        target_data.hit_point += add_hit_point
        target_change.hit_point += add_hit_point
        #如果超过最大值则=最大值
        if target_data.hit_point >= target_data.hit_point_max:
            target_data.hit_point = target_data.hit_point_max


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_BOTH_SMALL_MANA_POINT)
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
    add_mana_point = add_time * 20
    character_data.mana_point += add_mana_point
    if character_data.mana_point > character_data.mana_point_max:
        add_mana_point -= character_data.mana_point - character_data.mana_point_max
        character_data.mana_point = character_data.mana_point_max
    change_data.mana_point += add_mana_point
    #交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        add_mana_point = add_time * 20
        #如果气力=0则恢复减半
        if target_data.mana_point == 0:
            add_mana_point /= 2
        target_data.mana_point += add_mana_point
        target_change.mana_point += add_mana_point
        #如果超过最大值则=最大值
        if target_data.mana_point >= target_data.mana_point_max:
            target_data.mana_point = target_data.mana_point_max


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.MOVE_TO_TARGET_SCENE)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.EAT_FOOD)
def handle_eat_food(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    食用指定食物
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
    if character_data.behavior.eat_food is not None:
        food: game_type.Food = character_data.behavior.eat_food
        food_name = ""
        food_name = cache.recipe_data[food.recipe].name
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        if target_data.cid:
            change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
            target_change = change_data.target_change[target_data.cid]
            add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
            character_handle.add_favorability(
                character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
        character_data.behavior.food_name = food_name
        # if character_data.food_bag[food.uid]:
        # print(f"debug food.uid = {food.uid}")
        # print(f"debug character_data.food_bag = {character_data.food_bag}")
        if food.uid in character_data.food_bag:
            del character_data.food_bag[food.uid]


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.MAKE_FOOD)
def handle_make_food(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    制作指定食物
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
    if character_data.behavior.eat_food is not None:
        food: game_type.Food = character_data.behavior.eat_food
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


# @settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_SOCIAL_FAVORABILITY)
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


# @settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_INTIMACY_FAVORABILITY)
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


# @settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_INTIMATE_FAVORABILITY)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.FIRST_KISS)
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
    target_data.social_contact_data.setdefault(character_id, 0)

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
            #初吻的二段结算
            target_data.second_behavior[1050] = 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.FIRST_HAND_IN_HAND)
def handle_first_hand_in_hand(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    记录初次牵手
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
    target_data.social_contact_data.setdefault(character_id, 0)
    social = 0
    if character_id in target_data.social_contact_data:
        social = target_data.social_contact_data[character_id]
    if social >= 2:
        if character_data.first_hand_in_hand == -1:
            character_data.first_kiss = target_data.cid
        if target_data.first_hand_in_hand == -1:
            target_data.first_kiss = character_id


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.FIRST_SEX)
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
    target_data.social_contact_data.setdefault(character_id, 0)

    # 判定是否为道具性交
    item_flag = False
    if cache.input_cache[len(cache.input_cache)-1] == str(constant.Instruct.VIBRATOR_INSERTION):
        item_flag = True

    # 遍历指令列表，获得指令的中文名
    i = 0
    for k in constant.Instruct.__dict__:
        # print(f"debug i = {i}，k = {k}")
        # print(f"debug 上指令 = {cache.input_cache[len(cache.input_cache)-1]}")
        if int(cache.input_cache[len(cache.input_cache)-1]) + 2 == i:
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
        if len(target_data.cloth[9]):
            pan_id = target_data.cloth[9][-1]
        elif len(target_data.cloth_off[9]):
            pan_id = target_data.cloth_off[9][-1]
        elif len(character_data.pl_collection.npc_panties_tem[character_data.target_character_id]):
            pan_id = character_data.pl_collection.npc_panties_tem[character_data.target_character_id][-1]
        else:
            no_pan_flag = True
        if not no_pan_flag:
            pan_name = game_config.config_clothing_tem[pan_id].name
            target_data.cloth[9] = []
            now_draw.text = f"\n获得了{target_data.name}穿着的{pan_name}(沾有处子血)，已自动存入收藏品列表，可在藏物馆查看\n"
            now_draw.draw()
            character_data.pl_collection.first_panties[character_data.target_character_id] =  f"{pan_name}(沾有处子血)"
        else:
            now_draw.text = f"\n{target_data.name}的处子血滴了下去，被你谨慎地用试管接了一滴，已自动存入收藏品列表，可在藏物馆查看\n"
            character_data.pl_collection.first_panties[character_data.target_character_id] = f"一滴{target_data.name}的处子血"
            now_draw.draw()

        # 道具破处
        if item_flag:
            target_data.first_record.first_sex_item = 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.FIRST_A_SEX)
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
    target_data.social_contact_data.setdefault(character_id, 0)

    # 判定是否为道具性交
    item_flag = False
    if cache.input_cache[len(cache.input_cache)-1] == str(constant.Instruct.VIBRATOR_INSERTION_ANAL):
        item_flag = True

    # 遍历指令列表，获得指令的中文名
    i = 0
    for k in constant.Instruct.__dict__:
        if int(cache.input_cache[len(cache.input_cache)-1]) + 2 == i:
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
            #处女的二段结算
            target_data.second_behavior[1052] = 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_MEDIUM_HIT_POINT)
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
    add_hit_point = add_time * 100
    character_data.hit_point += add_hit_point
    if character_data.hit_point > character_data.hit_point_max:
        add_hit_point -= character_data.hit_point - character_data.hit_point_max
        character_data.hit_point = character_data.hit_point_max
    change_data.hit_point += add_hit_point


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_MEDIUM_MANA_POINT)
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
    add_mana_point = add_time * 150
    character_data.mana_point += add_mana_point
    if character_data.mana_point > character_data.mana_point_max:
        add_mana_point -= character_data.mana_point - character_data.mana_point_max
        character_data.mana_point = character_data.mana_point_max
    change_data.mana_point += add_mana_point


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.INTERRUPT_TARGET_ACTIVITY)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.NOT_TIRED)
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
    character_data.tired = 0


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ITEM_OFF)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ITEM_OFF)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_N_FEEL)
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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(0, 0)
    now_lust = target_data.status_data[0]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[0])
    now_add_lust *= adjust
    target_data.status_data[0] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(0, 0)
    target_change.status_data[0] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_B_FEEL)
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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(1, 0)
    now_lust = target_data.status_data[1]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[1])
    now_add_lust *= adjust
    target_data.status_data[1] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(1, 0)
    target_change.status_data[1] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_C_FEEL)
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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(2, 0)
    now_lust = target_data.status_data[2]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[2])
    now_add_lust *= adjust
    target_data.status_data[2] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(2, 0)
    target_change.status_data[2] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_P_FEEL)
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
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[3])
    now_add_lust *= adjust
    target_data.eja_point += now_add_lust
    # change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    # target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    # target_change.eja_point.setdefault(3, 0)
    # target_change.eja_point += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_V_FEEL)
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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(4, 0)
    now_lust = target_data.status_data[4]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[4])
    now_add_lust *= adjust
    target_data.status_data[4] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(4, 0)
    target_change.status_data[4] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_A_FEEL)
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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(5, 0)
    now_lust = target_data.status_data[5]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[5])
    now_add_lust *= adjust
    target_data.status_data[5] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(5, 0)
    target_change.status_data[5] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_U_FEEL)
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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(6, 0)
    now_lust = target_data.status_data[6]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[6])
    now_add_lust *= adjust
    target_data.status_data[6] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(6, 0)
    target_change.status_data[6] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_W_FEEL)
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
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    target_data.status_data.setdefault(7, 0)
    now_lust = target_data.status_data[7]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[7])
    now_add_lust *= adjust
    target_data.status_data[7] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(7, 0)
    target_change.status_data[7] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_LUBRICATION)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(8, 0)
    now_lust = target_data.status_data[8]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[22])
    now_add_lust *= adjust
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.USE_BODY_LUBRICANT)
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

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_HUGE_LUBRICATION)
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
    now_lust_multiple = 2000 + int(now_lust*0.5)
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.USE_PHILTER)
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

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_HUGE_DESIRE_AND_SUBMIT)
def handle_target_add_huge_desire_and_submit(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加大量好意和欲情（媚药）
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
    now_lust_multiple = 2000 + int(now_lust*0.5)
    now_add_lust = now_lust_multiple
    target_data.status_data[12] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(12, 0)
    target_change.status_data[12] += now_add_lust
    target_change.status_data[12] += now_add_lust

    # 屈服
    target_data.status_data.setdefault(15, 0)
    now_lust = target_data.status_data[15]
    now_lust_multiple = 2000 + int(now_lust*0.5)
    now_add_lust = now_lust_multiple
    target_data.status_data[15] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(15, 0)
    target_change.status_data[15] += now_add_lust
    target_change.status_data[15] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.USE_ENEMAS)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ENEMA)
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
    now_lust_multiple = 500 + int(now_lust*0.1)
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

    # A灌肠
    target_data.dirty.a_clean = 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ENEMA_END)
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
    now_lust_multiple = 500 + int(now_lust*0.1)
    now_add_lust = now_lust_multiple
    target_data.status_data[8] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(8, 0)
    target_change.status_data[8] += now_add_lust

    # A灌肠结束
    target_data.dirty.a_clean = 2


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_NIPPLE_CLAMP_ON)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_NIPPLE_CLAMP_OFF)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_CLIT_CLAMP_ON)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_CLIT_CLAMP_OFF)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_VIBRATOR_ON)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_VIBRATOR_OFF)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ANAL_VIBRATOR_ON)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ANAL_VIBRATOR_OFF)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ANAL_BEADS_ON)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ANAL_BEADS_OFF)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.USE_DIURETICS_ONCE)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.USE_DIURETICS_PERSISTENT)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_URINATE)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_DIURETICS_ON)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_LEARN)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(9, 0)
    now_lust = target_data.status_data[9]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[19])
    now_add_lust *= adjust
    target_data.status_data[9] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(9, 0)
    target_change.status_data[9] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_RESPECT)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(10, 0)
    now_lust = target_data.status_data[10]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[20])
    now_add_lust *= adjust
    target_data.status_data[10] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(10, 0)
    target_change.status_data[10] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_FRIENDLY)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(11, 0)
    now_lust = target_data.status_data[11]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[21])
    now_add_lust *= adjust
    target_data.status_data[11] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(11, 0)
    target_change.status_data[11] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_DESIRE)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(12, 0)
    now_lust = target_data.status_data[12]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[22])
    now_add_lust *= adjust
    target_data.status_data[12] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(12, 0)
    target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_HAPPY)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(13, 0)
    now_lust = target_data.status_data[13]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_mark_debuff_adjust(target_data.ability[13])
    now_add_lust *= adjust
    target_data.status_data[13] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(13, 0)
    target_change.status_data[13] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_LEAD)
def handle_target_add_small_lead(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量先导（受虐补正）
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
    target_data.status_data.setdefault(14, 0)
    now_lust = target_data.status_data[14]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[25])
    now_add_lust *= adjust
    target_data.status_data[14] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(14, 0)
    target_change.status_data[14] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_SUBMIT)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(15, 0)
    now_lust = target_data.status_data[15]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_mark_debuff_adjust(target_data.ability[14])
    now_add_lust *= adjust
    target_data.status_data[15] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(15, 0)
    target_change.status_data[15] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_SHY)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(16, 0)
    now_lust = target_data.status_data[16]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(target_data.ability[23])
    now_add_lust *= adjust
    target_data.status_data[16] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(16, 0)
    target_change.status_data[16] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_PAIN)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(17, 0)
    now_lust = target_data.status_data[17]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
    now_add_lust *= adjust
    target_data.status_data[17] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(17, 0)
    target_change.status_data[17] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_TERROR)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(18, 0)
    now_lust = target_data.status_data[18]
    now_lust_multiple = 10 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_mark_debuff_adjust(character_data.ability[15])
    now_add_lust *= adjust
    target_data.status_data[18] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(18, 0)
    target_change.status_data[18] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_DEPRESSION)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(19, 0)
    now_lust = target_data.status_data[19]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status_data[19] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(19, 0)
    target_change.status_data[19] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_DISGUST)
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
    if target_data.dead:
        return
    target_data.status_data.setdefault(20, 0)
    now_lust = target_data.status_data[20]
    now_lust_multiple = 10 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_mark_debuff_adjust(target_data.ability[18])
    now_add_lust *= adjust
    target_data.status_data[20] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status_data.setdefault(20, 0)
    target_change.status_data[20] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_SMALL_P_FEEL)
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
    now_add_lust = add_time + now_lust_multiple + character_data.eja_point*0.4
    character_data.eja_point += now_add_lust
    change_data.eja_point += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.BOTH_ADD_SMALL_LEARN)
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
    now_lust_multiple = 10
    now_add_lust = add_time + now_lust_multiple
    character_data.status_data[9] += now_add_lust
    change_data.status_data.setdefault(9, 0)
    change_data.status_data[9] += now_add_lust
    #交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(9, 0)
        target_change.status_data[9] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_SMALL_LEARN)
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
    now_lust_multiple = 10
    now_add_lust = add_time + now_lust_multiple
    character_data.status_data[9] += now_add_lust
    change_data.status_data.setdefault(9, 0)
    change_data.status_data[9] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.DIRTY_RESET)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.DOOR_CLOSE_RESET)
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TALK_ADD_ADJUST)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(40, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[40])
        #好感度变化#
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        add_favorability *= adjust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
        #好意变化#
        target_data.status_data.setdefault(11, 0)
        now_lust = target_data.status_data[11]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[11] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(11, 0)
        target_change.status_data[11] += now_add_lust
        #快乐变化#
        target_data.status_data.setdefault(13, 0)
        now_lust = target_data.status_data[13]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[13] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(13, 0)
        target_change.status_data[13] += now_add_lust
        #记录谈话时间#
        target_data.action_info.talk_time = now_time
        # print("聊天计数器时间变为 ：",target_data.action_info.talk_time)


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.COFFEE_ADD_ADJUST)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(43, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[43])
        #好感度变化#
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        add_favorability *= adjust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
        #信赖变化#
        now_lust_multiple = 1
        # adjust = attr_calculation.get_ability_adjust(character_data.ability[21])
        now_lust_multiple *= adjust
        target_data.trust += now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple
        if (character_id != 0) and (character_data.target_character_id == 0):
            character_data.trust += now_lust_multiple
            change_data.trust += now_lust_multiple
        #好意变化#
        target_data.status_data.setdefault(11, 0)
        now_lust = target_data.status_data[11]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[11] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(11, 0)
        target_change.status_data[11] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_COFFEE_ADD_ADJUST)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        target_data.ability.setdefault(43, 0)
        adjust = attr_calculation.get_ability_adjust(target_data.ability[43])
        #好感度变化#
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        add_favorability *= adjust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
        #信赖变化#
        now_lust_multiple = 1
        # adjust = attr_calculation.get_ability_adjust(character_data.ability[21])
        now_lust_multiple *= adjust
        target_data.trust += now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple
        if (character_id != 0) and (character_data.target_character_id == 0):
            character_data.trust += now_lust_multiple
            change_data.trust += now_lust_multiple
        #好意变化#
        target_data.status_data.setdefault(11, 0)
        now_lust = target_data.status_data[11]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[11] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(11, 0)
        target_change.status_data[11] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.KONWLEDGE_ADD_PINK_MONEY)
def handle_knowledge_add_pink_money(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据自己（再加上交互对象的）学识获得少量粉色凭证
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
    #获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[45])
    # 获得粉色凭证 #
    now_add_lust = add_time * adjust
    now_add_lust = int(now_add_lust)

    # 如果有交互对象，则算上对方的学识加成
    if character_data.target_character_id != 0:
        adjust_target = attr_calculation.get_ability_adjust(target_data.ability[45])
        now_add_lust += int (add_time * adjust_target)
    cache.base_resouce.pink_certificate += now_add_lust
    now_draw = draw.NormalDraw()
    now_draw.text = f"\n  获得{str(now_add_lust)}粉色凭证\n"
    now_draw.width = width
    now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.CURE_PATIENT_ADD_ADJUST)
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
    #获取调整值#
    adjust = attr_calculation.get_ability_adjust(character_data.ability[46])
    # 获得加成 #
    now_add_lust = add_time * adjust * 1000
    now_add_lust = int(now_add_lust * random.uniform(0.5,1.5))

    # 如果有交互对象，则算上对方的医疗加成
    if character_data.target_character_id != character_id:
        adjust_target = attr_calculation.get_ability_adjust(target_data.ability[46])
        now_add_lust += int (add_time * adjust_target)
    cache.base_resouce.money += now_add_lust
    cache.base_resouce.cure_income += now_add_lust
    cache.base_resouce.all_income += now_add_lust
    cache.base_resouce.patient_now -= 1
    cache.base_resouce.patient_cured += 1


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.ADD_HPMP_MAX)
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
    add_hp = int(10 * random.uniform(0.75,1.25))
    add_mp = int(20 * random.uniform(0.75,1.25))
    character_data.hit_point_max += add_hp
    character_data.mana_point_max += add_mp
    now_draw = draw.NormalDraw()
    now_draw.text = f"\n{character_data.name}博士的体力上限增加{str(add_hp)},气力上限增加{str(add_mp)}"
    now_draw.width = width
    now_draw.draw()
    #交互对象也同样#
    if character_data.target_character_id:
        target_data: game_type.Character = cache.character_data[character_data.target_character_id]
        add_hp = 10 * random.uniform(0.75,1.25)
        add_mp = 20 * random.uniform(0.75,1.25)
        target_data.hit_point_max += add_hp
        target_data.mana_point_max += add_mp
        now_draw = draw.NormalDraw()
        now_draw.text = f"\n{target_data.name}的体力上限增加{str(add_hp)},气力上限增加{str(add_mp)}\n"
        now_draw.width = width
        now_draw.draw()
    else:
        now_draw = draw.NormalDraw()
        now_draw.text = "\n"
        now_draw.width = 1
        now_draw.draw()


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.SING_ADD_ADJUST)
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

    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(44, 0)
        # 如果水平在3级及以下则扣好感信赖，如果是NPC执行则跳过
        good_flag = True
        if character_data.ability[44] <= 3 and character_id == 0:
            good_flag = False
        adjust = attr_calculation.get_ability_adjust(character_data.ability[44])
        #好感度变化#
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        if good_flag:
            add_favorability *= adjust
        else:
            add_favorability *= (adjust - 1)

        # print(f"debug 唱歌，角色 = {character_data.name}，目标= {target_data.name}，good_flag = {good_flag}，add_favorability = {add_favorability}")

        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
        #信赖变化#
        now_lust_multiple = 1
        # adjust = attr_calculation.get_ability_adjust(character_data.ability[21])
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

        #好意变化#
        target_data.status_data.setdefault(11, 0)
        now_lust = target_data.status_data[11]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        if good_flag:
            now_add_lust *= adjust
        else:
            now_add_lust *= (adjust - 1)
        target_data.status_data[11] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(11, 0)
        target_change.status_data[11] += now_add_lust

        # 恐怖、抑郁、反感变化
        if not good_flag:
            for i in {18,19,20}:
                now_lust = target_data.status_data[i]
                now_lust_multiple = 100 + now_lust / 10
                now_add_lust = add_time + now_lust_multiple
                if good_flag:
                    now_add_lust *= adjust
                else:
                    now_add_lust *= 10
                target_data.status_data[i] += now_add_lust
                change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
                target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
                target_change.status_data.setdefault(i, 0)
                target_change.status_data[i] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.PLAY_INSTRUMENT_ADD_ADJUST)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(44, 0)
        # 如果水平在3级及以下则扣好感信赖，如果是NPC执行则跳过
        good_flag = True
        if character_data.ability[44] <= 3 and character_id == 0:
            good_flag = False
        adjust = attr_calculation.get_ability_adjust(character_data.ability[44])
        #好感度变化#
        add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
        if good_flag:
            add_favorability *= adjust
        else:
            add_favorability *= (adjust - 1)

        # print(f"debug 乐器，角色 = {character_data.name}，目标= {target_data.name}，good_flag = {good_flag}，add_favorability = {add_favorability}")

        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        character_handle.add_favorability(
            character_id, target_data.cid, add_favorability, change_data, target_change, now_time
            )
        #信赖变化#
        now_lust_multiple = 2
        # adjust = attr_calculation.get_ability_adjust(character_data.ability[21])
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

        #好意变化#
        target_data.status_data.setdefault(11, 0)
        now_lust = target_data.status_data[11]
        now_lust_multiple = 150 + now_lust / 8
        now_add_lust = add_time + now_lust_multiple
        if good_flag:
            now_add_lust *= adjust
        else:
            now_add_lust *= (adjust - 1)
        target_data.status_data[11] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(11, 0)
        target_change.status_data[11] += now_add_lust

        # 恐怖、抑郁、反感变化
        if not good_flag:
            for i in {18,19,20}:
                now_lust = target_data.status_data[i]
                now_lust_multiple = 150 + now_lust / 8
                now_add_lust = add_time + now_lust_multiple
                if good_flag:
                    now_add_lust *= adjust
                else:
                    now_add_lust *= 10
                target_data.status_data[i] += now_add_lust
                change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
                target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
                target_change.status_data.setdefault(i, 0)
                target_change.status_data[i] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_N_ADJUST)
def handle_tech_add_n_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行N快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #B快变化#
        target_data.status_data.setdefault(0, 0)
        now_lust = target_data.status_data[0]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[0] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(0, 0)
        target_change.status_data[0] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_B_ADJUST)
def handle_tech_add_b_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行B快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #B快变化#
        target_data.status_data.setdefault(1, 0)
        now_lust = target_data.status_data[1]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[1] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(1, 0)
        target_change.status_data[1] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_C_ADJUST)
def handle_tech_add_c_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行C快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #C快变化#
        target_data.status_data.setdefault(2, 0)
        now_lust = target_data.status_data[2]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[2] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(2, 0)
        target_change.status_data[2] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_P_ADJUST)
def handle_tech_add_p_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行P快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #P快变化#
        target_data.status_data.setdefault(3, 0)
        now_lust = target_data.status_data[3]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.eja_point += now_add_lust
        # change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        # target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        # target_change.status_data.setdefault(3, 0)
        # target_change.status_data[3] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_V_ADJUST)
def handle_tech_add_v_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行V快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #V快变化#
        target_data.status_data.setdefault(4, 0)
        now_lust = target_data.status_data[4]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[4] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(4, 0)
        target_change.status_data[4] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_A_ADJUST)
def handle_tech_add_a_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行A快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #A快变化#
        target_data.status_data.setdefault(5, 0)
        now_lust = target_data.status_data[5]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[5] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(5, 0)
        target_change.status_data[5] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_U_ADJUST)
def handle_tech_add_u_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行U快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #U快变化#
        target_data.status_data.setdefault(6, 0)
        now_lust = target_data.status_data[6]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[6] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(6, 0)
        target_change.status_data[6] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_W_ADJUST)
def handle_tech_add_w_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能对交互对象进行W快、欲情调整
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        character_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
        #W快变化#
        target_data.status_data.setdefault(7, 0)
        now_lust = target_data.status_data[7]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[7] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(7, 0)
        target_change.status_data[7] += now_add_lust
        #欲情变化#
        target_data.status_data.setdefault(12, 0)
        now_lust = target_data.status_data[12]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[12] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(12, 0)
        target_change.status_data[12] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_PL_P_ADJUST)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        target_data.ability.setdefault(19, 0)
        adjust = attr_calculation.get_ability_adjust(target_data.ability[19])
        #P快变化#
        character_data.status_data.setdefault(3, 0)
        now_lust = character_data.status_data[3]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        character_data.eja_point += now_add_lust
        change_data.eja_point += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_LUBRICATION_ADJUST_ADD_PAIN)
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
    if character_data.target_character_id != character_id and (not character_id or not character_data.target_character_id):

        if character_data.dead:
            return
        if target_data.dead:
            return
        #获取调整值#
        target_data.status_data.setdefault(8, 0)
        adjust = attr_calculation.get_pain_adjust(target_data.status_data[8])
        #苦痛变化#
        target_data.status_data.setdefault(17, 0)
        now_lust = target_data.status_data[17]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        now_add_lust *= adjust
        target_data.status_data[17] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.status_data.setdefault(17, 0)
        target_change.status_data[17] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.LOW_OBSCENITY_FAILED_ADJUST)
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
        #加反感
        target_data.status_data.setdefault(20, 0)
        now_lust = target_data.status_data[20]
        now_lust_multiple = 100 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        adjust = attr_calculation.get_ability_adjust(target_data.ability[18])
        now_add_lust *= adjust
        target_data.status_data[20] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change.status_data.setdefault(20, 0)
        target_change.status_data[20] += now_add_lust
        #加愤怒
        target_data.angry_point += 20
        target_data.angry_with_player = True
        #降好感
        minus_favorability = character.calculation_favorability(character_id, target_data.cid, add_time) * -1
        character_handle.add_favorability(
            character_id, target_data.cid, minus_favorability, change_data, target_change, now_time
        )


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.HIGH_OBSCENITY_FAILED_ADJUST)
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
        #加反感
        target_data.status_data.setdefault(20, 0)
        now_lust = target_data.status_data[20]
        now_lust_multiple = 500 + now_lust / 10
        now_add_lust = add_time + now_lust_multiple
        adjust = attr_calculation.get_ability_adjust(target_data.ability[18])
        now_add_lust *= adjust
        target_data.status_data[20] += now_add_lust
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change.status_data.setdefault(20, 0)
        target_change.status_data[20] = now_add_lust
        #加愤怒
        target_data.angry_point += 50
        target_data.angry_with_player = True
        #降好感
        minus_favorability = character.calculation_favorability(character_id, target_data.cid, add_time) * -1
        minus_favorability *= 5
        character_handle.add_favorability(
            character_id, target_data.cid, minus_favorability, change_data, target_change, now_time
        )
        #降信赖
        now_lust_multiple = 10
        adjust = attr_calculation.get_ability_adjust(target_data.ability[21])
        now_lust_multiple *= adjust
        target_data.trust -= now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust -= now_lust_multiple


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.SLEEP_POINT_DOWN)
def handle_sleep_point_down(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    睡觉时降低困倦值
    Keyword arguments:
    character_id -- 角色id
    add_time -- 结算时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算的时间
    """
    if not add_time:
        return
    character_data: game_type.Character = cache.character_data[character_id]

    value = int(add_time / 3)
    character_data.sleep_point -= value


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.URINATE_POINT_DOWN)
def handle_urinate_point_down(
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_URINATE_POINT_DOWN)
def handle_target_urinate_point_down(
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

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.HUNGER_POINT_DOWN)
def handle_hunger_point_down(
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_HUNGER_POINT_DOWN)
def handle_target_urinate_point_down(
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.RECORD_TRAINING_TIME)
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

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.RECORD_SHOWER_TIME)
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
