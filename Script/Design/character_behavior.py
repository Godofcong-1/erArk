import logging
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
    save_handle,
)
from Script.Design import (
    settle_behavior,
    game_time,
    character,
    handle_premise,
    talk,
    map_handle,
    cooking,
    attr_calculation,
    character_move
)
from Script.UI.Moudle import draw
from Script.Config import game_config, normal_config
import time

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """


def init_character_behavior():
    """
    角色行为树总控制
    """
    start_before = time.time()
    while 1:
        if len(cache.over_behavior_character) >= len(cache.character_data):
            start_after = time.time()
            # logging.debug(f'全部角色的总行为树时间为{start_after - start_before}')
            break
        for character_id in cache.character_data:
            start_all = time.time()
            if character_id in cache.over_behavior_character:
                continue
            character_behavior(character_id, cache.game_time)
            # judge_character_dead(character_id)
            judge_character_tired_sleep(character_id)
            end_all = time.time()
            # logging.debug(f'角色编号{character_id}的总行为树时间为{end_all - start_all}')
            # logging.debug(f'当前已完成结算的角色有{cache.over_behavior_character}')
        # update_cafeteria()
    cache.over_behavior_character = set()


def update_cafeteria():
    """刷新食堂内食物"""
    food_judge = 1
    for food_type in cache.restaurant_data:
        food_list: Dict[UUID, game_type.Food] = cache.restaurant_data[food_type]
        for food_id in food_list:
            food: game_type.Food = food_list[food_id]
            # if food.eat:
                # food_judge = 0
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
    # 处理跟随与H模式#
    if character_id != 0:
        judge_character_follow(character_id)
        judge_character_h(character_id)
    # 空闲状态下执行可用行动#
    start_character = time.time()
    if character_data.state == constant.CharacterStatus.STATUS_ARDER:
        if character_id:
            character_target_judge(character_id, now_time)
        else:
            cache.over_behavior_character.add(0)
        end_judge = time.time()
        # logging.debug(f'角色编号{character_id}空闲，执行可用行动，到结算为止耗时为{end_judge - start_character}')
    # 非空闲活动下结算当前状态#
    else:
        status_judge = judge_character_status(character_id, now_time)
        if status_judge:
            cache.over_behavior_character.add(character_id)
        end_judge = time.time()
        # logging.debug(f'角色编号{character_id}非空闲，结算当前状态，到结算为止耗时为{end_judge - start_character}')

    #24点之后的结算#
    if character.judge_character_time_over_24(character_id):
        #1.结算数值为珠
        settle_character_juel(character_id)
        #2.清零射精槽
        if character_id == 0:
            character_data.eja_point = 0
        #3.清零高潮程度
        character_data.orgasm_level = attr_calculation.get_orgasm_level_zero(character_data.orgasm_level)
        #4.清零并随机重置生气程度
        character_data.angry_point = random.randrange(1,35)
        #5.自动存档，用玩家id来限制只存一次
        if character_id == 0:
            save_handle.establish_save("auto")
        #6.清零污浊状态
        character_data.dirty = attr_calculation.get_dirty_zero()
    end_last = time.time()
    # logging.debug(f'角色编号{character_id}结算完24点和跟随H为止耗时为{end_last - start_character}')


def character_target_judge(character_id: int, now_time: datetime.datetime):
    """
    查询角色可用目标活动并执行
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
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
        state_machine_id = target_config.state_machine_id
        #如果上个AI行动不是原地等待5分钟，则将等待flag设为1
        # 不会被打断的指令列表
        safe_instruct = [10,11,12,13,14,15] # 移动系
        safe_instruct += [30,31,32,33,34,35] # 有事中断处理系
        if state_machine_id != 0 and state_machine_id not in safe_instruct:
            character_data.wait_flag = 1
        #     print(f"debug 前一个状态机id = ",state_machine_id,",flag变为1,character_id =",character_id)
        constant.handle_state_machine_data[state_machine_id](character_id)
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

def judge_character_tired_sleep(character_id : int):
    """
    校验角色是否疲劳或困倦
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    #疲劳结算
    if character_data.is_h or character_data.is_follow:
        
        if character_data.tired or attr_calculation.get_sleep_level(character_data.sleep_point) >= 2:
            character_data.is_h = False
            character_data.is_follow = 0
            now_draw = draw.NormalDraw()
            now_draw.width = width
            draw_text = "太累了，决定回房间睡觉 " if character_data.tired else "太困了，决定回房间睡觉"
            now_draw.text = character_data.name + draw_text
            now_draw.draw()


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
            #进行一次暂停以便玩家看输出信息
            wait_draw = draw.LineFeedWaitDraw()
            wait_draw.text = "\n"
            wait_draw.width = normal_config.config_normal.text_width
            wait_draw.draw()
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

def settle_character_juel(character_id: int) -> int:
    """
    校验角色状态并结算为珠
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    type_set = game_config.config_character_state_type_data[0]
    for status_id in type_set:
        # print("status_type :",status_type)
        # print("status_id :",status_id)
        # print("game_config.config_character_state[status_id] :",game_config.config_character_state[status_id])
        # print("game_config.config_character_state[status_id].name :",game_config.config_character_state[status_id].name)
        #去掉性别里不存在的状态
        if character_data.sex == 0:
            if status_id in {2, 4, 7, 8}:
                continue
        elif character_data.sex == 1:
            if status_id == 3:
                continue
        status_value = 0
        #获得状态值并清零
        if status_id in character_data.status_data:
            status_value = character_data.status_data[status_id]
            cache.character_data[character_id].status_data[status_id] = 0
            # print("status_value :",status_value)
        #只要状态值不为0就结算为对应珠
        if status_value != 0:
            add_juel = attr_calculation.get_juel(status_value)
            character_data.juel[status_id] += add_juel
            # juel_text = game_config.config_juel[status_id].name
            # print("宝珠名：",juel_text,"。增加了 :",add_juel)
    return 1

def judge_character_follow(character_id: int) -> int:
    """
    维持跟随状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 锁定助理的跟随状态
    if character_data.assistant_state.always_follow == 1 or character_data.assistant_state.always_follow == 2:
        character_data.is_follow = character_data.assistant_state.always_follow

    # 维持跟随的状态
    if character_data.is_follow == 2:
        character_data.behavior.behavior_id = constant.Behavior.FOLLOW
        character_data.state = constant.CharacterStatus.STATUS_FOLLOW
        if character_data.position != cache.character_data[0].position:
            # print("检测到跟随，NPC编号为：",character_id)
            to_dr = cache.character_data[0].position
            _, _, move_path, move_time = character_move.character_move(character_id, to_dr)
            # print("开始移动，路径为：",move_path,"，时间为：",move_time)
            character_data.behavior.behavior_id = constant.Behavior.MOVE
            character_data.behavior.move_target = move_path
            character_data.behavior.duration = move_time
            character_data.state = constant.CharacterStatus.STATUS_MOVE
    return 1

def judge_character_h(character_id: int) -> int:
    """
    维持H状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.is_h:
        character_data.behavior.behavior_id = constant.Behavior.H
        character_data.state = constant.CharacterStatus.STATUS_H
    return 1