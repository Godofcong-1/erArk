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
            character_id, target_data.cid, add_favorability, target_change, now_time
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
        adjust = attr_calculation.get_ability_adjust(character_data.ability[21])
        now_lust_multiple *= adjust
        target_data.trust += now_lust_multiple
        change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
        target_change.trust += now_lust_multiple


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.SUB_SMALL_HIT_POINT)
def handle_sub_small_hit_point(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    减少少量体力
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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.SUB_SMALL_MANA_POINT)
def handle_sub_small_mana_point(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    减少少量气力
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
        character_data.hit_point -= sub_mana / 15
        change_data.hit_point -= sub_mana / 15


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
                character_id, target_data.cid, add_favorability, target_change, now_time
            )
        del character_data.food_bag[food.uid]
        character_data.behavior.food_name = food_name


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
                character_id, target_data.cid, add_favorability, target_change, now_time
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
#                     character_id, target_data.cid, add_favorability, target_change, now_time
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
#                 character_id, target_data.cid, add_favorability, target_change, now_time
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
#                 character_id, target_data.cid, add_favorability, target_change, now_time
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
#                 character_id, target_data.cid, add_favorability, target_change, now_time
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
#                 character_id, target_data.cid, add_favorability, target_change, now_time
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
    if target_data.social_contact_data[character_id] >= 3:
        if character_data.first_kiss == -1:
            character_data.first_kiss = target_data.cid
            if (not character_id) or (not target_data.cid):
                now_draw = draw.NormalDraw()
                now_draw.text = _("{character_name}失去了初吻\n").format(character_name=character_data.name)
                now_draw.width = window_width
                now_draw.draw()
        if target_data.first_kiss == -1:
            target_data.first_kiss = character_id
            if (not character_id) or (not target_data.cid):
                now_draw = draw.NormalDraw()
                now_draw.text = _("{character_name}失去了初吻\n").format(character_name=target_data.name)
                now_draw.width = window_width
                now_draw.draw()


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


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_N_FEEL)
def handle_target_add_small_n_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｎ快
    Keyword arguments:
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
    target_data.status.setdefault(0, 0)
    now_lust = target_data.status[0]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[0] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(0, 0)
    target_change.status[0] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_B_FEEL)
def handle_target_add_small_b_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｂ快
    Keyword arguments:
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
    target_data.status.setdefault(1, 0)
    now_lust = target_data.status[1]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[1] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(1, 0)
    target_change.status[1] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_V_FEEL)
def handle_target_add_small_v_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｖ快
    Keyword arguments:
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
    target_data.status.setdefault(2, 0)
    now_lust = target_data.status[2]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[2] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(2, 0)
    target_change.status[2] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_C_FEEL)
def handle_target_add_small_c_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｃ快
    Keyword arguments:
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
    target_data.status.setdefault(3, 0)
    now_lust = target_data.status[3]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[3] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(3, 0)
    target_change.status[3] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_A_FEEL)
def handle_target_add_small_a_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ａ快
    Keyword arguments:
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
    target_data.status.setdefault(4, 0)
    now_lust = target_data.status[4]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[4] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(4, 0)
    target_change.status[4] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_P_FEEL)
def handle_target_add_small_p_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｐ快
    Keyword arguments:
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
    target_data.status.setdefault(5, 0)
    now_lust = target_data.status[5]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[5] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(5, 0)
    target_change.status[5] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_U_FEEL)
def handle_target_add_small_u_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｕ快
    Keyword arguments:
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
    target_data.status.setdefault(6, 0)
    now_lust = target_data.status[6]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[6] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(6, 0)
    target_change.status[6] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_W_FEEL)
def handle_target_add_small_w_feel(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量Ｗ快
    Keyword arguments:
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
    target_data.status.setdefault(7, 0)
    now_lust = target_data.status[7]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[7] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(7, 0)
    target_change.status[7] += now_add_lust

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
    target_data.status.setdefault(8, 0)
    now_lust = target_data.status[8]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[8] += now_add_lust
    adjust = attr_calculation.get_ability_adjust(character_data.ability[22])
    now_add_lust *= adjust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(8, 0)
    target_change.status[8] += now_add_lust


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
    target_data.status.setdefault(9, 0)
    now_lust = target_data.status[9]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
    now_add_lust *= adjust
    target_data.status[9] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(9, 0)
    target_change.status[9] += now_add_lust

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
    target_data.status.setdefault(10, 0)
    now_lust = target_data.status[10]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[20])
    now_add_lust *= adjust
    target_data.status[10] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(10, 0)
    target_change.status[10] += now_add_lust

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
    target_data.status.setdefault(11, 0)
    now_lust = target_data.status[11]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[21])
    now_add_lust *= adjust
    target_data.status[11] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(11, 0)
    target_change.status[11] += now_add_lust

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
    target_data.status.setdefault(12, 0)
    now_lust = target_data.status[12]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[22])
    now_add_lust *= adjust
    target_data.status[12] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(12, 0)
    target_change.status[12] += now_add_lust

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
    target_data.status.setdefault(13, 0)
    now_lust = target_data.status[13]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[13])
    now_add_lust *= adjust
    target_data.status[13] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(13, 0)
    target_change.status[13] += now_add_lust

@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TARGET_ADD_SMALL_LEAD)
def handle_target_add_small_lead(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    交互对象增加少量先导（侍奉补正）
    Keyword arguments:
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
    target_data.status.setdefault(14, 0)
    now_lust = target_data.status[14]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[23])
    now_add_lust *= adjust
    target_data.status[14] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(14, 0)
    target_change.status[14] += now_add_lust

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
    target_data.status.setdefault(15, 0)
    now_lust = target_data.status[15]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[14])
    now_add_lust *= adjust
    target_data.status[15] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(15, 0)
    target_change.status[15] += now_add_lust

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
    target_data.status.setdefault(16, 0)
    now_lust = target_data.status[16]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[24])
    now_add_lust *= adjust
    target_data.status[16] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(16, 0)
    target_change.status[16] += now_add_lust

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
    target_data.status.setdefault(17, 0)
    now_lust = target_data.status[17]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[15])
    now_add_lust *= adjust
    target_data.status[17] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(17, 0)
    target_change.status[17] += now_add_lust

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
    target_data.status.setdefault(18, 0)
    now_lust = target_data.status[18]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[15])
    now_add_lust *= adjust
    target_data.status[18] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(18, 0)
    target_change.status[18] += now_add_lust

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
    target_data.status.setdefault(19, 0)
    now_lust = target_data.status[19]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    target_data.status[19] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(19, 0)
    target_change.status[19] += now_add_lust

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
    target_data.status.setdefault(20, 0)
    now_lust = target_data.status[20]
    now_lust_multiple = 10 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    adjust = attr_calculation.get_ability_adjust(character_data.ability[18])
    now_add_lust *= adjust
    target_data.status[20] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(20, 0)
    target_change.status[20] += now_add_lust

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
        return
    if character_data.dead:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    #获取调整值#
    character_data.ability.setdefault(25, 0)
    adjust = attr_calculation.get_ability_adjust(character_data.ability[25])
    #好感度变化#
    add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
    add_favorability *= adjust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    character_handle.add_favorability(
        character_id, target_data.cid, add_favorability, target_change, now_time
        )
    #好意变化#
    target_data.status.setdefault(11, 0)
    now_lust = target_data.status[11]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    now_add_lust *= adjust
    target_data.status[11] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(11, 0)
    target_change.status[11] += now_add_lust
    #快乐变化#
    target_data.status.setdefault(13, 0)
    now_lust = target_data.status[13]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    now_add_lust *= adjust
    target_data.status[13] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(13, 0)
    target_change.status[13] += now_add_lust
    #记录谈话时间#
    target_data.talk_time = now_time
    # print("聊天计数器时间变为 ：",target_data.talk_time)


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
        return
    if character_data.dead:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    #获取调整值#
    character_data.ability.setdefault(28, 0)
    adjust = attr_calculation.get_ability_adjust(character_data.ability[28])
    #好感度变化#
    add_favorability = character.calculation_favorability(character_id, target_data.cid, add_time)
    add_favorability *= adjust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    character_handle.add_favorability(
        character_id, target_data.cid, add_favorability, target_change, now_time
        )
    #信赖变化#
    now_lust_multiple = 1
    # adjust = attr_calculation.get_ability_adjust(character_data.ability[21])
    now_lust_multiple *= adjust
    target_data.trust += now_lust_multiple
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.trust += now_lust_multiple
    #好意变化#
    target_data.status.setdefault(11, 0)
    now_lust = target_data.status[11]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    now_add_lust *= adjust
    target_data.status[11] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(11, 0)
    target_change.status[11] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_N_ADJUST)
def handle_tech_add_n_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能进行N快、欲情调整
    Keyword arguments:
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
        return
    if character_data.dead:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    #获取调整值#
    character_data.ability.setdefault(19, 0)
    adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
    #B快变化#
    target_data.status.setdefault(0, 0)
    now_lust = target_data.status[0]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    now_add_lust *= adjust
    target_data.status[0] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(0, 0)
    target_change.status[0] += now_add_lust
    #欲情变化#
    target_data.status.setdefault(12, 0)
    now_lust = target_data.status[12]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    now_add_lust *= adjust
    target_data.status[12] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(12, 0)
    target_change.status[12] += now_add_lust


@settle_behavior.add_settle_behavior_effect(constant.BehaviorEffect.TECH_ADD_B_ADJUST)
def handle_tech_add_b_adjust(
    character_id: int,
    add_time: int,
    change_data: game_type.CharacterStatusChange,
    now_time: datetime.datetime,
):
    """
    根据发起者的技巧技能进行B快、欲情调整
    Keyword arguments:
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
        return
    if character_data.dead:
        return
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if target_data.dead:
        return
    #获取调整值#
    character_data.ability.setdefault(19, 0)
    adjust = attr_calculation.get_ability_adjust(character_data.ability[19])
    #B快变化#
    target_data.status.setdefault(1, 0)
    now_lust = target_data.status[1]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    now_add_lust *= adjust
    target_data.status[1] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(1, 0)
    target_change.status[1] += now_add_lust
    #欲情变化#
    target_data.status.setdefault(12, 0)
    now_lust = target_data.status[12]
    now_lust_multiple = 100 + now_lust / 10
    now_add_lust = add_time + now_lust_multiple
    now_add_lust *= adjust
    target_data.status[12] += now_add_lust
    change_data.target_change.setdefault(target_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_data.cid]
    target_change.status.setdefault(12, 0)
    target_change.status[12] += now_add_lust
