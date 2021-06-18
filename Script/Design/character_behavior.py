import random
import datetime
from uuid import UUID
from types import FunctionType
from typing import Dict
from Script.Core import (
    cache_control,
    game_path_config,
    game_type,
    constant,
    value_handle,
    get_text,
)
from Script.Design import (
    settle_behavior,
    game_time,
    character,
    handle_premise,
    talk,
    map_handle,
    cooking,
)
from Script.Config import game_config, normal_config

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def init_character_behavior():
    """
    角色行为树总控制
    """
    while 1:
        if len(cache.over_behavior_character) >= len(cache.character_data):
            break
        for character_id in cache.character_data:
            if character_id in cache.over_behavior_character:
                continue
            character_behavior(character_id, cache.game_time)
            # judge_character_dead(character_id)
        update_cafeteria()
    cache.over_behavior_character = set()


def update_cafeteria():
    """刷新食堂内食物"""
    food_judge = 1
    for food_type in cache.restaurant_data:
        food_list: Dict[UUID, game_type.Food] = cache.restaurant_data[food_type]
        for food_id in food_list:
            food: game_type.Food = food_list[food_id]
            if food.eat:
                food_judge = 0
            break
        if not food_judge:
            break
    if food_judge:
        cooking.init_restaurant_data()


def character_behavior(character_id: int, now_time: datetime.datetime):
    """
    角色行为控制
    Keyword arguments:
    character_id -- 角色id
    now_time -- 指定时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.dead:
        return
    if character_data.behavior.start_time is None:
        character.init_character_behavior_start_time(character_id, now_time)
    if character_data.state == constant.CharacterStatus.STATUS_ARDER:
        if character_id:
            character_target_judge(character_id, now_time)
        else:
            cache.over_behavior_character.add(0)
    else:
        status_judge = judge_character_status(character_id, now_time)
        if status_judge:
            cache.over_behavior_character.add(character_id)


def character_target_judge(character_id: int, now_time: datetime.datetime):
    """
    查询角色可用目标活动并执行
    Keyword arguments:
    character_id -- 角色id
    """
    premise_data = {}
    target_weight_data = {}
    target, _, judge = search_target(
        character_id,
        list(game_config.config_target.keys()),
        set(),
        premise_data,
        target_weight_data,
    )
    if judge:
        target_config = game_config.config_target[target]
        constant.handle_state_machine_data[target_config.state_machine_id](character_id)
    else:
        start_time = cache.character_data[character_id].behavior.start_time
        now_judge = game_time.judge_date_big_or_small(start_time, now_time)
        if now_judge:
            cache.over_behavior_character.add(character_id)
        else:
            next_time = game_time.get_sub_date(minute=1, old_date=start_time)
            cache.character_data[character_id].behavior.start_time = next_time


# def judge_character_dead(character_id: int):
#     """
#     校验角色状态并处死角色
#     Keyword arguments:
#     character_id -- 角色id
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     if character_data.dead:
#         if character_id not in cache.over_behavior_character:
#             cache.over_behavior_character.add(character_id)
#         return
#     character_data.status.setdefault(27, 0)
#     character_data.status.setdefault(28, 0)
#     if (
#         character_data.status[27] >= 100
#         or character_data.status[28] >= 100
#         or character_data.hit_point <= 0
#     ):
#         character_data.dead = 1
#         character_data.state = 13
#         if character_id not in cache.over_behavior_character:
#             cache.over_behavior_character.add(character_id)


def judge_character_status(character_id: int, now_time: datetime.datetime) -> int:
    """
    校验并结算角色状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    start_time = character_data.behavior.start_time
    end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
    if (
        character_data.target_character_id != character_id
        and character_data.target_character_id not in scene_data.character_list
    ):
        end_time = now_time
    time_judge = game_time.judge_date_big_or_small(now_time, end_time)
    add_time = (end_time.timestamp() - start_time.timestamp()) / 60
    if not add_time:
        character_data.behavior = game_type.Behavior()
        character_data.behavior.start_time = end_time
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        return 1
    # last_hunger_time = start_time
    # if character_data.last_hunger_time is not None:
    #     last_hunger_time = character_data.last_hunger_time
    # hunger_time = int((now_time - last_hunger_time).seconds / 60)
    # character_data.status.setdefault(27, 0)
    # character_data.status.setdefault(28, 0)
    # character_data.status[27] += hunger_time * 0.02
    # character_data.status[28] += hunger_time * 0.02
    # character_data.last_hunger_time = now_time
    if time_judge:
        now_panel = settle_behavior.handle_settle_behavior(character_id, end_time)
        talk.handle_talk(character_id)
        if now_panel != None:
            now_panel.draw()
        character_data.behavior = game_type.Behavior()
        character_data.state = constant.CharacterStatus.STATUS_ARDER
    if time_judge == 1:
        character_data.behavior.start_time = end_time
        return 0
    elif time_judge == 2:
        character.init_character_behavior_start_time(character_id, now_time)
        return 0
    return 1


def search_target(
    character_id: int,
    target_list: list,
    null_target: set,
    premise_data: Dict[int, int],
    target_weight_data: Dict[int, int],
) -> (int, int, bool):
    """
    查找可用目标
    Keyword arguments:
    character_id -- 角色id
    target_list -- 检索的目标列表
    null_target -- 被排除的目标
    premise_data -- 已算出的前提权重
    target_weight_data -- 已算出权重的目标列表
    Return arguments:
    int -- 目标id
    int -- 目标权重
    bool -- 前提是否能够被满足
    """
    target_data = {}
    for target in target_list:
        if target in null_target:
            continue
        if target in target_weight_data:
            target_data.setdefault(target_weight_data[target], set())
            target_data[target_weight_data[target]].add(target)
            continue
        if target not in game_config.config_target_premise_data:
            target_data.setdefault(1, set())
            target_data[1].add(target)
            target_weight_data[target] = 1
            continue
        target_premise_list = game_config.config_target_premise_data[target]
        now_weight = 0
        now_target_pass_judge = 0
        now_target_data = {}
        premise_judge = 1
        for premise in target_premise_list:
            premise_judge = 0
            if premise in premise_data:
                premise_judge = premise_data[premise]
            else:
                premise_judge = handle_premise.handle_premise(premise, character_id)
                premise_data[premise] = premise_judge
            if premise_judge:
                now_weight += premise_judge
            else:
                if premise in game_config.config_effect_target_data and premise not in premise_data:
                    now_target_list = game_config.config_effect_target_data[premise] - null_target
                    now_target, now_target_weight, now_judge = search_target(
                        character_id,
                        now_target_list,
                        null_target,
                        premise_data,
                        target_weight_data,
                    )
                    if now_judge:
                        now_target_data.setdefault(now_target_weight, set())
                        now_target_data[now_target_weight].add(now_target)
                        now_weight += now_target_weight
                    else:
                        now_target_pass_judge = 1
                        break
                else:
                    now_target_pass_judge = 1
                    break
        if now_target_pass_judge:
            null_target.add(target)
            target_weight_data[target] = 0
            continue
        if premise_judge:
            target_data.setdefault(now_weight, set())
            target_data[now_weight].add(target)
            target_weight_data[target] = now_weight
        else:
            now_value_weight = value_handle.get_rand_value_for_value_region(now_target_data.keys())
            target_data.setdefault(now_weight, set())
            target_data[now_weight].add(random.choice(list(now_target_data[now_value_weight])))
    if len(target_data):
        value_weight = value_handle.get_rand_value_for_value_region(target_data.keys())
        return random.choice(list(target_data[value_weight])), value_weight, 1
    return "", 0, 0
