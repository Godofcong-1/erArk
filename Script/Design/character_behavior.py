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
    event,
    talk,
    map_handle,
    cooking,
    attr_calculation,
    character_move,
    pregnancy,
    basement,
    handle_talent,
    handle_ability,
    update,
)
from Script.UI.Moudle import draw
from Script.UI.Panel import draw_event_text_panel
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
    cache.over_behavior_character = set()
    sleep_flag,new_day_flag = True,True
    while 1:
        id_list = cache.npc_id_got.copy()
        id_list.discard(0)
        # 先结算其他NPC部分
        while len(cache.over_behavior_character) < len(id_list):
            for character_id in id_list:
                if character_id in cache.over_behavior_character:
                    continue
                character_behavior(character_id, cache.game_time)
                # logging.debug(f'当前已完成结算的角色有{cache.over_behavior_character}')
        # 后结算玩家部分
        while 0 not in cache.over_behavior_character:
            character_behavior(0, cache.game_time)
        # 睡觉刷新
        PL_data: game_type.Character = cache.character_data[0]
        if PL_data.behavior.behavior_id == constant.Behavior.SLEEP and sleep_flag:
            sleep_flag = False
            update_sleep()
        # 新一天刷新
        if cache.game_time.day != cache.pre_game_time.day and new_day_flag:
            new_day_flag = False
            update_new_day()
        # 结束循环
        if len(cache.over_behavior_character) >= len(id_list) + 1:
            break


def update_cafeteria():
    """刷新食堂内食物"""
    max_people = len(cache.npc_id_got)
    # food_judge = 1
    food_count = 0
    for food_type in cache.restaurant_data:
        food_list: Dict[UUID, game_type.Food] = cache.restaurant_data[food_type]
        food_count += len(food_list)
    #     for food_id in food_list:
    #         food: game_type.Food = food_list[food_id]
    #         # if food.eat:
    #             # food_judge = 0
    #         food_judge = 0
    #         break
    #     if not food_judge:
    #         break
    # if food_judge:
    # 食物数量不足且当前时间在饭点时，刷新食物
    if food_count <= max_people * 3 and handle_premise.handle_eat_time(0):
        cooking.init_restaurant_data()

def update_recruit():
    """刷新招募栏位"""

    # 遍历全招募栏
    for key in cache.base_resouce.recruit_now:

        # 如果超过100则进行结算
        if cache.base_resouce.recruit_now[key] >= 100:
            cache.base_resouce.recruit_now[key] = 0

            # 开始随机获得招募npc的id
            wait_id_set = []
            for i in range(len(cache.npc_tem_data)):
                id = i + 1
                if id not in cache.npc_id_got:
                    wait_id_set.append(id)
            if len(wait_id_set):
                choice_id = random.choice(wait_id_set)
                cache.base_resouce.recruited_id.add(choice_id)

                now_draw = draw.WaitDraw()
                now_draw.width = width
                now_draw.text = _(f"\n\n   ※ 招募到了新的干员，请前往博士办公室确认 ※\n\n")
                now_draw.style = "nowmap"
                now_draw.draw()

            # 之前做该栏位工作的HR，也把栏位数据清零
            for id in cache.base_resouce.all_work_npc_set[71]:
                character_data = cache.character_data[id]
                if character_data.work.recruit_index == key:
                    character_data.work.recruit_index = -1


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
    # 刷新会根据时间即时增加的角色数值
    character_aotu_change_value(character_id, now_time)

    # 处理特殊模式
    if character_id != 0:
        judge_character_first_meet(character_id) # 初见和每日招呼
        judge_character_tired_sleep(character_id) # 判断疲劳和睡眠
        judge_character_cant_move(character_id) # 无法自由移动的角色
        judge_character_follow(character_id) # 跟随模式
        judge_character_h(character_id) # H模式

    # 处理公共资源
    update_cafeteria() # 刷新食堂的饭

    # 先处理玩家部分
    if character_id == 0:
        # 判断玩家的开始事件
        # now_event = event.handle_event(0,1)
        # if now_event != None:
        #     now_event.draw()
        #     character_data.event.event_id = now_event.event_id
        #     start_time = character_data.behavior.start_time
        #     end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
        #     now_panel = settle_behavior.handle_settle_behavior(character_id, end_time, start_flag = True)
        #     if now_panel != None:
        #         now_panel.draw()

        if character_data.state == constant.CharacterStatus.STATUS_ARDER:
            cache.over_behavior_character.add(0)
            # logging.debug(f'角色编号{character_id}空闲，执行可用行动，到结算为止耗时为{end_judge - start_character}')
        # 非空闲活动下结算当前状态#
        else:
            status_judge = judge_character_status(character_id, now_time)
            if status_judge:
                cache.over_behavior_character.add(character_id)
        # 最后结算疲劳
        judge_character_tired_sleep(character_id)

    # 再处理NPC部分
    if character_id:
        # print(f"debug 前：{character_data.name}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}")
        # 空闲状态下执行可用行动#
        if character_data.state == constant.CharacterStatus.STATUS_ARDER:
            if character_id:
                character_target_judge(character_id, now_time)
            else:
                cache.over_behavior_character.add(0)
        # 非空闲活动下结算当前状态#
        else:
            status_judge = judge_character_status(character_id, now_time)
            if status_judge:
                cache.over_behavior_character.add(character_id)
        # print(f"debug 后：{character_data.name}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}")


def character_target_judge(character_id: int, now_time: datetime.datetime):
    """
    查询角色可用目标活动并执行
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    PC_character_data: game_type.Character = cache.character_data[0]
    start_time = character_data.behavior.start_time
    premise_data = {}
    target_weight_data = {}

    # 如果玩家在对该NPC交互，则等待flag=1
    safe_instruct = [constant.CharacterStatus.STATUS_WAIT,constant.CharacterStatus.STATUS_REST,constant.CharacterStatus.STATUS_SLEEP]
    if PC_character_data.target_character_id == character_id:
        # print(f"debug character_id = {character_data.name}，state = {PC_character_data.state}")
        if character_data.state not in safe_instruct:
            character_data.sp_flag.wait_flag = 1

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
        #如果上个AI行动是普通交互指令，则将等待flag设为1
        # if state_machine_id >= 100:
        #     character_data.sp_flag.wait_flag = 1
            # print(f"debug 前一个状态机id = ",state_machine_id,",flag变为1,character_name =",character_data.name)
        constant.handle_state_machine_data[state_machine_id](character_id)
        # event_draw = event.handle_event(character_id, 1)
        # if (not character_id) or (PC_character_data.target_character_id == character_id):
        #     if event_draw is not None:
        #         event_draw.draw()
        #         # 进行开始结算的数值结算
        #         end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
        #         if character_data.target_character_id != character_id:
        #             end_time = now_time
        #         now_panel = settle_behavior.handle_settle_behavior(character_id, end_time, start_flag = True)
        #         if now_panel != None:
        #             now_panel.draw()
    else:
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
    #交互对象结算
    if character_id:
        if character_data.sp_flag.is_h or character_data.sp_flag.is_follow:
            
            if character_data.sp_flag.tired or (attr_calculation.get_tired_level(character_data.tired_point) >= 2):
                pl_character_data: game_type.Character = cache.character_data[0]
                # 输出基础文本
                now_draw = draw.NormalDraw()
                now_draw.width = width
                # 跟随和H的分歧，忽略H后停留的情况
                if character_data.sp_flag.is_follow and character_data.behavior.behavior_id != constant.Behavior.WAIT:
                    draw_text = "太累了，无法继续跟随\n" if character_data.sp_flag.tired else "太困了，无法继续跟随\n"
                    now_draw.text = character_data.name + draw_text
                    now_draw.draw()
                    character_data.sp_flag.is_follow = 0
                # H时
                elif character_data.sp_flag.is_h and not character_data.sp_flag.unconscious_h:
                    pl_character_data.behavior.behavior_id = constant.Behavior.T_H_HP_0
                    pl_character_data.state = constant.CharacterStatus.STATUS_T_H_HP_0

                # 新：交给指令里的end_h结算(旧：数据结算)
                # character_data.sp_flag.is_h = False
                # character_data.sp_flag.is_follow = 0

                # 新：暂时注释，保持跟随状态（旧：助手取消助手栏里的跟随）
                # if character_id == pl_character_data.assistant_character_id:
                #     character_data.assistant_state.always_follow = 0
    # 玩家疲劳计算
    else:
        target_data = cache.character_data[character_data.target_character_id]
        if character_data.sp_flag.tired and target_data.sp_flag.is_h:
            character_data.behavior.behavior_id = constant.Behavior.H_HP_0
            character_data.state = constant.CharacterStatus.STATUS_H_HP_0
            character_data.sp_flag.tired = 0


def judge_character_status(character_id: int, now_time: datetime.datetime, end_now = 0) -> int:
    """
    校验并结算角色状态
    Keyword arguments:
    character_id -- 角色id
    end_now -- 是否要强制结算
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
        # 例外：玩家在搬运该角色
        if character_data.target_character_id != character_data.sp_flag.bagging_chara_id:
            end_time = now_time
    # print(f"debug {character_data.name}的end_time = {end_time}")
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
    if end_now:
        time_judge = end_now
    if time_judge:
        # 查询当前玩家是否触发了事件
        start_event_draw = None if character_id else event.handle_event(character_id)
        event_type_now = 1
        if start_event_draw != None:
            event_id = start_event_draw.event_id
            character_data.event.event_id = event_id
            event_type_now = start_event_draw.event_type

        # if not character_id:
        #     print(f"debug 1 move_src = {character_data.behavior.move_src},position = {character_data.position}")
        now_panel = settle_behavior.handle_settle_behavior(character_id, end_time, event_type_now)
        # if not character_id:
        #     print(f"debug 2 move_src = {character_data.behavior.move_src},position = {character_data.position}")

        # 如果是二类
        end_event_draw = event.handle_event(character_id)
        if end_event_draw != None:
            end_event_id = end_event_draw.event_id
            end_event_type = end_event_draw.event_type
            event_config = game_config.config_event[end_event_id]
            if end_event_type == 2:

                # 如果是父事件的话，则先输出文本
                if "10001" in event_config.effect:
                    end_event_draw.draw()

                character_data.event.event_id = end_event_id
                now_panel = settle_behavior.handle_settle_behavior(character_id, end_time, 0)

        # if not character_id:
        #     print(f"debug 3 move_src = {character_data.behavior.move_src},position = {character_data.position}")

        # 如果触发了子事件的话则把文本替换为子事件文本
        if character_data.event.son_event_id != "":
            son_event_id = character_data.event.son_event_id
            event_config = game_config.config_event[son_event_id]
            start_event_draw = draw_event_text_panel.DrawEventTextPanel(son_event_id,character_id, event_config.type)

        # 如果有事件则显示事件，否则显示口上
        if start_event_draw != None:
            start_event_draw.draw()
        elif end_event_draw != None:
            end_event_draw.draw()
        else:
            talk.handle_talk(character_id)
        if now_panel != None:
            now_panel.draw()
            #进行一次暂停以便玩家看输出信息
            if character_id == 0:
                wait_draw = draw.LineFeedWaitDraw()
                wait_draw.text = "\n"
                wait_draw.width = normal_config.config_normal.text_width
                wait_draw.draw()
        character_data.behavior = game_type.Behavior()
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        character_data.event.event_id = ""
        character_data.event.son_event_id = ""
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
                premise_judge = max(premise_judge, 0)
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
            now_value_weight = value_handle.get_rand_value_for_value_region(list(now_target_data.keys()))
            target_data.setdefault(now_weight, set())
            target_data[now_weight].add(random.choice(list(now_target_data[now_value_weight])))
    if len(target_data):
        value_weight = value_handle.get_rand_value_for_value_region(list(target_data.keys()))
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


def judge_character_cant_move(character_id: int) -> int:
    """
    无法自由移动的角色\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]

    cant_move_flag = False

    # 被囚禁
    if character_data.sp_flag.imprisonment:
        cant_move_flag = True
        # character.init_character_behavior_start_time(character_id, cache.game_time)
        # character_data.behavior.behavior_id = constant.Behavior.WAIT
        # character_data.state = constant.CharacterStatus.STATUS_WAIT

    # 临盆和产后
    if character_data.talent[22] == 1 or character_data.talent[23] == 1:
        cant_move_flag = True
        # character.init_character_behavior_start_time(character_id, cache.game_time)
        # character_data.behavior.behavior_id = constant.Behavior.WAIT
        # character_data.state = constant.CharacterStatus.STATUS_WAIT

        # 检测当前位置是否在医疗部的住院部，如果不在的话则移动至住院部
        now_position = character_data.position
        now_scene_str = map_handle.get_map_system_path_str_for_list(now_position)
        now_scene_data = cache.scene_data[now_scene_str]
        if "Inpatient_Department" not in now_scene_data.scene_tag:
            to_Inpatient_Department = map_handle.get_map_system_path_for_str(random.choice(constant.place_data["Inpatient_Department"]))
            map_handle.character_move_scene(character_data.position, to_Inpatient_Department, character_id)
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
    if character_data.assistant_state.always_follow in {1,2}:
        # 排除太累了和太困了的情况
        if character_data.sp_flag.tired or (attr_calculation.get_tired_level(character_data.tired_point) >= 2):
            pass
        else:
            character_data.sp_flag.is_follow = character_data.assistant_state.always_follow

    # 维持跟随的状态
    if character_data.sp_flag.is_follow == 2:
        character.init_character_behavior_start_time(character_id, cache.game_time)
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
    维持H状态\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    if character_data.sp_flag.is_h:
        character.init_character_behavior_start_time(character_id, cache.game_time)
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_WAIT
    return 1


def judge_character_first_meet(character_id: int) -> int:
    """
    判断初见和每日招呼\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 优先输出初见，次要输出每日招呼
    if character_data.first_record.first_meet:
        character_data.second_behavior[1331] = 1
        character_data.first_record.first_meet = 0
        character_data.first_record.day_first_meet = 0
    elif character_data.first_record.day_first_meet:
        character_data.first_record.day_first_meet = 0
        character_data.second_behavior[1332] = 1


def update_sleep():
    """
    玩家睡觉时的刷新\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """

    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw.text = "\n博士入睡，开始结算各种数据\n\n"
    now_draw.draw()
    id_list = cache.npc_id_got.copy()
    id_list.add(0)

    # 角色刷新
    for character_id in id_list:
        character_data: game_type.Character = cache.character_data[character_id]
        # 结算数值为珠
        settle_character_juel(character_id)
        # 玩家结算
        if character_id == 0:
            character_data.eja_point = 0 # 清零射精槽
            character_data.sanity_point = character_data.sanity_point_max # 恢复理智槽
            character_data.action_info.sleep_time = cache.game_time
        else:
            # 清零并随机重置生气程度
            character_data.angry_point = random.randrange(1,35)
            # 清零H被撞破的flag
            character_data.action_info.h_interrupt = 0
            # 重置每天第一次见面
            character_data.first_record.day_first_meet = 1
            # 重置洗澡状态
            character_data.sp_flag.shower = 0
            # 新：改为洗澡时清零（清零污浊状态）
            # character_data.dirty = attr_calculation.get_dirty_zero()
            # 检查并处理受精怀孕部分
            pregnancy.check_all_pregnancy(character_id)
            # 检查是否有可以获得的素质
            handle_talent.gain_talent(character_id,now_gain_type = 3)
            # 检查是否有可以升级的能力
            handle_ability.gain_ability(character_id)
            # 清零H状态
            character_data.h_state = attr_calculation.get_h_state_zero(character_data.h_state)

    # 非角色部分
    update_save()


def update_new_day():
    """
    新一天的刷新\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """

    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw.text = "\n已过24点，开始结算各种数据\n\n"
    now_draw.draw()

    # 角色刷新
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        if character_id:
            # 刷新娱乐活动
            get_chara_entertainment(character_id)
            # 刷新生理周期
            pregnancy.update_reproduction_period(character_id)

    # 非角色部分
    basement.update_base_resouce_newday()
    cache.pre_game_time = cache.game_time
    # update_save()


def update_save():
    """
    自动存档\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw.text = "\n全部结算完毕，开始自动保存\n"
    # 播放一条提示信息
    info_list = []
    for i in game_config.config_tip_tem:
        info_list.append(i)
    info_id = random.choice(info_list)
    info_text = game_config.config_tip_tem[info_id].info
    now_draw.text += f"\n请博士在保存时阅读今日的小贴士：\n\n  {info_text}\n\n\n"
    now_draw.draw()
    save_handle.establish_save("auto")


def character_aotu_change_value(character_id: int, now_time: datetime.datetime):
    """
    结算角色随时间自动增加的数值
    Keyword arguments:
    character_id -- 角色id
    now_time -- 指定时间
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    player_character_data: game_type.Character = cache.character_data[0]
    target_data: game_type.Character = cache.character_data[now_character_data.target_character_id]
    start_time = player_character_data.behavior.start_time
    add_time = int((now_time - start_time).seconds / 60)

    # 如果玩家视觉下的经过时间超过12分钟，则每12分钟结算一次
    past_time = 12
    while 1:
        if add_time <= 0:
            break

        if add_time <= past_time:
            past_time = add_time
        add_time -= past_time

        # 休息时小幅度减少疲劳值
        if now_character_data.state == constant.CharacterStatus.STATUS_REST:
            add_tired = int(past_time / 6)
            now_character_data.tired_point -= add_tired
            now_character_data.tired_point = max(now_character_data.tired_point,0) # 最少为0

            # 非睡觉时间内，疲劳归零则直接结算当前行动
            if now_character_data.tired_point <= 0 and (not handle_premise.handle_sleep_time(character_id)):
                judge_character_status(character_id, now_time, end_now = 2)

        # 睡觉时减少疲劳值
        if now_character_data.state == constant.CharacterStatus.STATUS_SLEEP:
            add_tired = int(past_time / 3)
            now_character_data.tired_point -= add_tired
            now_character_data.tired_point = max(now_character_data.tired_point,0) # 最少为0
            # 熟睡值在到熟睡之前快速增加
            sleep_level,tem = attr_calculation.get_sleep_level(now_character_data.sleep_point)
            if sleep_level <= 1:
                add_sleep = int(past_time * 1.5)
                now_character_data.sleep_point += add_sleep
            # 熟睡值到熟睡后上下波动，加的可能性比减的可能性大一点点
            else:
                add_sleep = random.randint(int(past_time * -0.5),int(past_time * 0.6))
                now_character_data.sleep_point += add_sleep
            # 最高上限100
            now_character_data.sleep_point = min(now_character_data.sleep_point,100)
            # print(f"debug {now_character_data.name}疲劳值-{add_tired}={now_character_data.tired_point}，熟睡值+{add_sleep}={now_character_data.sleep_point}")

            # 非睡觉时间内，疲劳归零则直接结算当前行动
            if now_character_data.tired_point <= 0 and (not handle_premise.handle_sleep_time(character_id)):
                judge_character_status(character_id, now_time, end_now = 2)

        if character_id == 0:
            # 结算玩家源石技艺的理智值消耗
            # 激素系
            if now_character_data.pl_ability.hormone > 0:
                down_sp = max(int(past_time / 6),1)
                now_character_data.sanity_point -= down_sp
            # 视觉系
            if now_character_data.pl_ability.visual:
                down_sp = max(int(past_time / 6),1)
                now_character_data.sanity_point -= down_sp
            # 理智值不足则归零并中断所有开启中的源石技艺
            if now_character_data.sanity_point < 0:
                now_character_data.sanity_point = 0
                now_character_data.pl_ability.hormone *= -1
                # 输出提示信息
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                now_draw.text = "\n理智值不足，开启的源石技艺已全部中断\n"
                now_draw.draw()
            
            # 结算对无意识对象的结算
            if target_data.sp_flag.unconscious_h:
                # 睡奸判定
                if target_data.state == constant.CharacterStatus.STATUS_SLEEP and now_character_data.behavior.behavior_id >= 301:
                    # 减少熟睡值
                    down_sleep = int(past_time * 1.5)
                    target_data.sleep_point -= down_sleep
                    # 计算当前熟睡等级
                    sleep_level,tem = attr_calculation.get_sleep_level(target_data.sleep_point)
                    # print(f"debug {target_data.name}熟睡值={target_data.sleep_point}，熟睡等级{sleep_level}")
                    # 熟睡等级小于等于1时判定是否吵醒
                    if sleep_level <= 1:
                        # 浅睡和随时醒来时递增苏醒概率
                        weak_rate = game_config.config_sleep_level[1].sleep_point - target_data.sleep_point
                        if target_data.sleep_point <= game_config.config_sleep_level[0].sleep_point:
                            weak_rate += game_config.config_sleep_level[0].sleep_point - target_data.sleep_point
                        # 判定是否吵醒，吵醒则先结算当前行动然后进入重度性骚扰失败状态
                        if weak_rate >= random.randint(1,100):
                            target_data.tired_point = 0
                            target_data.sleep_point = 0
                            judge_character_status(target_data.target_character_id, now_time, end_now = 2)
                            # 输出提示信息
                            now_draw = draw.WaitDraw()
                            now_draw.width = window_width
                            now_draw.text = f"\n因为你的动作，{target_data.name}从梦中惊醒过来\n"
                            now_draw.draw()
                            now_character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
                            now_character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
                            now_character_data.behavior.duration = 10
                            update.game_update_flow(10)


def get_chara_entertainment(character_id: int):
    """
    刷新角色的娱乐活动\n
    Keyword arguments:\n
    character_id -- 角色id
    """
    week_day = cache.game_time.weekday()
    character_data: game_type.Character = cache.character_data[character_id]
    if character_id:
        # 重置基础数据
        character_data.sp_flag.swim = 0

        # 如果当天有派对的话，则全员当天娱乐为该娱乐
        if hasattr(cache.base_resouce, 'party_day_of_week') and cache.base_resouce.party_day_of_week[week_day]:
            for i in range(3):
                character_data.entertainment.entertainment_type[i] = cache.base_resouce.party_day_of_week[week_day]
        
        # 否则随机当天的娱乐活动
        else:
            entertainment_list = [i for i in game_config.config_entertainment]
            entertainment_list.remove(0)
            # 循环获得上午、下午、晚上的三个娱乐活动
            for i in range(3):

                # 进入主循环
                while 1:
                    # 开始随机
                    choice_entertainment_id = random.choice(entertainment_list)
                    # if choice_entertainment_id in {92, 151}:
                    #     print(f"debug {character_data.name}: {choice_entertainment_id}")
                    # 检查该娱乐活动是否需要特定的条件
                    if game_config.config_entertainment[choice_entertainment_id].need == "无":
                        break
                    else:
                        need_data_all = game_config.config_entertainment[choice_entertainment_id].need
                        # 整理需要的条件
                        if "&" not in need_data_all:
                            need_data_list = [need_data_all]
                        else:
                            need_data_list = need_data_all.split('&')
                        judge, reason = attr_calculation.judge_require(need_data_list, character_id)
                        # 如果满足条件则选择该娱乐活动，否则去掉该id后重新随机
                        if judge:
                            break
                        else:
                            entertainment_list.remove(choice_entertainment_id)
                            continue

                # 跳出循环后，将该娱乐活动赋值给角色
                character_data.entertainment.entertainment_type[i] = choice_entertainment_id
                entertainment_list.remove(choice_entertainment_id) # 从列表中去掉该娱乐活动，防止重复
