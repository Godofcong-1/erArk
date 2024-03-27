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
from Script.UI.Panel import draw_event_text_panel, ejaculation_panel
from Script.Config import game_config, normal_config

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1


def init_character_behavior():
    """
    角色行为树总控制
    """
    cache.over_behavior_character = set()
    new_day_flag = True
    while 1:
        # 先结算玩家部分
        while 0 not in cache.over_behavior_character:
            pl_start_time = cache.character_data[0].behavior.start_time
            character_behavior(0, cache.game_time, pl_start_time)
        id_list = cache.npc_id_got.copy()
        id_list.discard(0)
        # 后结算其他NPC部分
        while len(cache.over_behavior_character) <= len(id_list):
            for character_id in id_list:
                if character_id in cache.over_behavior_character:
                    continue
                character_behavior(character_id, cache.game_time, pl_start_time)
                # logging.debug(f'当前已完成结算的角色有{cache.over_behavior_character}')
        # 新一天刷新
        # print(f"debug new_day_flag = {new_day_flag}， cache.game_time.day = {cache.game_time.day}， cache.pre_game_time.day = {cache.pre_game_time.day}")
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


def character_behavior(character_id: int, now_time: datetime.datetime, pl_start_time: datetime.datetime):
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

    # 处理特殊模式
    if character_id != 0:
        judge_character_tired_sleep(character_id) # 判断疲劳和睡眠
        judge_character_cant_move(character_id) # 无法自由移动的角色
        judge_character_follow(character_id) # 跟随模式
        judge_character_h_and_obscenity(character_id) # H与猥亵

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
            cache.over_behavior_character.add(character_id)
            # logging.debug(f'角色编号{character_id}空闲，执行可用行动，到结算为止耗时为{end_judge - start_character}')
            # print(f"debug 玩家空闲")
        # 非空闲活动下结算当前状态#
        else:
            # 结算玩家在移动时同场景里的NPC的跟随情况
            if character_data.state == constant.CharacterStatus.STATUS_MOVE:
                judge_same_position_npc_follow()
            judge_character_status(character_id)
            # 刷新会根据时间即时增加的角色数值
            character_aotu_change_value(character_id, now_time, pl_start_time)
            # 睡觉刷新
            if character_data.behavior.behavior_id == constant.Behavior.SLEEP:
                update_sleep()
            # 结算角色的状态是否会持续
            change_character_persistent_state(character_id)
            time_judge = judge_character_status_time_over(character_id, now_time)
            if time_judge:
                cache.over_behavior_character.add(character_id)
        #         print(f"debug time_judge")
        # 最后结算疲劳
        judge_character_tired_sleep(character_id)
        # print(f"debug 玩家结算完毕")

    # 再处理NPC部分
    if character_id:
        # if character_data.name == "阿米娅":
        #     print(f"debug 前：{character_data.name}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}")
        # 空闲状态下寻找、执行、结算可用行动
        if character_data.state == constant.CharacterStatus.STATUS_ARDER:
            # 寻找可用行动
            find_character_target(character_id, now_time)
            # 结算状态与事件
            judge_character_status(character_id)
        # 移动情况下也直接结算
        elif character_data.state == constant.CharacterStatus.STATUS_MOVE:
            # 结算状态与事件
            judge_character_status(character_id)
        # 刷新会根据时间即时增加的角色数值
        character_aotu_change_value(character_id, now_time, pl_start_time)
        # 结算角色的状态是否会持续
        change_character_persistent_state(character_id)
        # 判断是否需要打断角色的当前行动
        judge_interrupt_character_behavior(character_id)
        time_judge = judge_character_status_time_over(character_id, now_time)
        if time_judge or character_data.state == constant.CharacterStatus.STATUS_WAIT:
            cache.over_behavior_character.add(character_id)
        # if character_data.name == "阿米娅":
        #     print(f"debug 后：{character_data.name}，time_judge = {time_judge}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}")

    # 自动获得对应素质和能力
    handle_talent.gain_talent(character_id,now_gain_type = 0)


def find_character_target(character_id: int, now_time: datetime.datetime):
    """
    查询角色可用目标活动并赋给角色
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    PC_character_data: game_type.Character = cache.character_data[0]
    start_time = character_data.behavior.start_time
    target_list = list(game_config.config_target.keys())
    premise_data = {}
    target_weight_data = {}

    # 如果该NPC在H模式，则不赋予新活动，且直接加入结束列表
    if character_data.sp_flag.is_h:
        cache.over_behavior_character.add(character_id)
        return

    # 如果玩家在对该NPC交互，则等待flag=1，此操作暂时不进行
    safe_instruct = [constant.CharacterStatus.STATUS_WAIT,constant.CharacterStatus.STATUS_REST,constant.CharacterStatus.STATUS_SLEEP]
    # if PC_character_data.target_character_id == character_id:
    #     # print(f"debug character_id = {character_data.name}，state = {PC_character_data.state}")
    #     if character_data.state not in safe_instruct:
    #         character_data.sp_flag.wait_flag = 1

    target, weight, judge = search_target(
        character_id,
        target_list,
        set(),
        premise_data,
        target_weight_data,
    )
    # if character_data.name == "阿米娅":
    #     print(f"\ndebug 阿米娅的target = {target},weight = {weight},now_time = {now_time}")
    #     if 5 <= int(target) <= 30:
    #         print(f"debug position = {character_data.position},move_final_target = {character_data.behavior.move_final_target}")
    if judge:
        target_config = game_config.config_target[target]
        state_machine_id = target_config.state_machine_id
        #如果上个AI行动是普通交互指令，则将等待flag设为1
        # if state_machine_id >= 100:
        #     character_data.sp_flag.wait_flag = 1
            # print(f"debug 前一个状态机id = ",state_machine_id,",flag变为1,character_name =",character_data.name)
        constant.handle_state_machine_data[state_machine_id](character_id)
    else:
        now_judge = game_time.judge_date_big_or_small(start_time, now_time)
        if now_judge:
            cache.over_behavior_character.add(character_id)
        else:
            next_time = game_time.get_sub_date(minute=1, old_date=start_time)
            cache.character_data[character_id].behavior.start_time = next_time


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

    # 玩家疲劳计算
    else:
        target_data = cache.character_data[character_data.target_character_id]
        if character_data.sp_flag.tired and target_data.sp_flag.is_h:
            character_data.behavior.behavior_id = constant.Behavior.H_HP_0
            character_data.state = constant.CharacterStatus.STATUS_H_HP_0
            character_data.sp_flag.tired = 0


def judge_character_status(character_id: int) -> int:
    """
    校验并结算角色状态\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    bool -- 本次update时间切片内活动是否已完成\n
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
            # end_time = now_time # 这里本来是游戏实际时间，架构改了之后大概不需要了，姑且先保留着
            end_time = end_time
    # print(f"debug {character_data.name}的end_time = {end_time}")

    # 跳过指令和指令后置类型的事件触发
    # print(f"debug 跳过指令和指令后置类型的事件触发")
    start_event_draw = event.handle_event(character_id)
    event_type_now = 1
    if start_event_draw != None:
        event_id = start_event_draw.event_id
        character_data.event.event_id = event_id
        event_config = game_config.config_event[event_id]
        event_type_now = event_config.type
        # 如果是父事件的话，则先输出文本
        if "10001" in event_config.effect:
            start_event_draw.draw()

    # if not character_id:
    #     print(f"debug 1 move_src = {character_data.behavior.move_src},position = {character_data.position}")
    now_panel = settle_behavior.handle_settle_behavior(character_id, end_time, event_type_now)
    # if not character_id:
    #     print(f"debug 2 move_src = {character_data.behavior.move_src},position = {character_data.position}")

    end_event_draw = event.handle_event(character_id)
    if end_event_draw != None and start_event_draw == None:
        end_event_id = end_event_draw.event_id
        end_event_type = end_event_draw.event_type
        event_config = game_config.config_event[end_event_id]
        # 指令前置类型的事件触发
        if end_event_type == 1:
            # print(f"debug 指令前置类型的事件触发")

            # 先绘制指令文本
            talk.handle_talk(character_id)

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
        son_event_draw = draw_event_text_panel.DrawEventTextPanel(son_event_id,character_id, event_config.type)
        if start_event_draw != None:
            start_event_draw = son_event_draw
        else:
            end_event_draw = son_event_draw

    # 如果有事件则显示事件，否则显示口上
    if start_event_draw != None:
        start_event_draw.draw()
    elif end_event_draw != None:
        end_event_draw.draw()
    else:
        talk.handle_talk(character_id)
    # 指令后置类型的事件，在最后输出指令的口上
    if event_type_now == 2:
        talk.handle_talk(character_id)
    if now_panel != None:
        now_panel.draw()
        #进行一次暂停以便玩家看输出信息
        if character_id == 0:
            wait_draw = draw.LineFeedWaitDraw()
            wait_draw.text = "\n"
            wait_draw.width = normal_config.config_normal.text_width
            wait_draw.draw()

    return 1

def judge_character_status_time_over(character_id: int, now_time: datetime.datetime, end_now = 0) -> int:
    """
    结算角色状态是否本次行动已经结束
    Keyword arguments:
    character_id -- 角色id
    end_now -- 是否要强制结算
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data = cache.character_data[0]
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
    # if character_data.name == "阿米娅":
    #     print(f"debug {character_data.name}的time_judge = {time_judge}，add_time = {add_time}")
    if not add_time:
        character_data.behavior = game_type.Behavior()
        character_data.behavior.start_time = now_time
        character_data.behavior.duration = 1
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        return 0
    # 助理的特殊判断
    if character_id and character_id == pl_character_data.assistant_character_id:
        if not time_judge:
            # 早安服务
            if character_data.assistant_services[5] and character_data.sp_flag.morning_salutation == 0:
                judge_wake_up_time = game_time.get_sub_date(minute=-30, old_date=pl_character_data.action_info.wake_time) # 醒来之前半小时
                # 当前时间在醒来之前半小时内
                if game_time.judge_date_big_or_small(end_time, judge_wake_up_time) and not game_time.judge_date_big_or_small(end_time, pl_character_data.action_info.wake_time):
                    # print(f"debug {character_data.name}刷新早安服务判断，state = {character_data.state}")
                    time_judge = 3
                    new_start_time = judge_wake_up_time
    if end_now:
        time_judge = end_now
    if time_judge:
        # 记录并刷新旧状态列表
        character_data.last_state.append(character_data.state)
        if len(character_data.last_state) > 5:
            character_data.last_state.pop(0)
        # 移动状态下则不完全重置行动数据，保留最终目标数据
        if character_data.state == constant.CharacterStatus.STATUS_MOVE:
            tem_move_final_target = character_data.behavior.move_final_target
            character_data.behavior = game_type.Behavior()
            character_data.behavior.move_final_target = tem_move_final_target
        else:
            character_data.behavior = game_type.Behavior()
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        character_data.event.event_id = ""
        character_data.event.son_event_id = ""
        # 当前时间大于行动结束时间
        if time_judge == 1:
            character_data.behavior.start_time = end_time
            return 0
        # 当前时间等于行动结束时间
        elif time_judge == 2:
            character.init_character_behavior_start_time(character_id, now_time)
            return 1
        # 特殊情况下提前终止
        elif time_judge == 3:
            character_data.behavior.start_time = new_start_time
            return 0
    return 1


def search_target(
    character_id: int,
    target_list: list,
    null_target: set,
    premise_data: Dict[int, int],
    target_weight_data: Dict[int, int],
):
    """
    查找可用目标\n
    Keyword arguments:\n
    character_id -- 角色id\n
    target_list -- 检索的目标列表\n
    null_target -- 被排除的目标\n
    premise_data -- 已算出的前提权重\n
    target_weight_data -- 已算出权重的目标列表\n
    Return arguments:\n
    int -- 目标id\n
    int -- 目标权重\n
    bool -- 前提是否能够被满足\n
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
        final_target = random.choice(list(target_data[value_weight]))
        # if character_id == 1:
        #     print(f"debug target_data = {target_data} , final_target = {final_target} , value_weight = {value_weight}")
        #     if final_target == "531":
        #         print(f"debug value_weight = {value_weight}")
        #     print(f"debug value_weight = {value_weight}")
        return final_target, value_weight, 1
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
            if status_id in [17, 18, 19]:
                character_data.juel[20] += add_juel // 2
            else:
                character_data.juel[status_id] += add_juel
            # juel_text = game_config.config_juel[status_id].name
            # print("宝珠名：",juel_text,"。增加了 :",add_juel)
    # 当反感珠大于0时，计算和其他珠的抵消
    if character_data.juel[20] > 0:
        draw_text = f"\n当前共{character_data.juel[20]}反发珠，抵消了："
        for i in [15, 10, 11, 12, 13]:
            # 1好意抵消2反发
            if character_data.juel[i] > 0:
                juel_down = min(character_data.juel[20], character_data.juel[i] * 2)
                character_data.juel[20] -= juel_down
                character_data.juel[i] -= juel_down // 2
                draw_text += f" {juel_down//2}个{game_config.config_juel[i].name} "
        draw_text += f"，剩余{character_data.juel[20]}个反发珠\n"
        now_draw = draw.NormalDraw()
        now_draw.text = draw_text
        # now_draw.draw()
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
    维持强制跟随状态
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 维持跟随的状态
    if character_data.sp_flag.is_follow == 2:
        character.init_character_behavior_start_time(character_id, cache.game_time)
        character_data.behavior.behavior_id = constant.Behavior.FOLLOW
        character_data.state = constant.CharacterStatus.STATUS_FOLLOW
        if character_data.position != cache.character_data[0].position:
            # print("检测到跟随，NPC编号为：",character_id)
            to_dr = cache.character_data[0].position
            tem_1, tem_2, move_path, move_time = character_move.character_move(character_id, to_dr)
            # print("开始移动，路径为：",move_path,"，时间为：",move_time)
            character_data.behavior.behavior_id = constant.Behavior.MOVE
            character_data.behavior.move_target = move_path
            character_data.behavior.duration = move_time
            character_data.state = constant.CharacterStatus.STATUS_MOVE
    return 1


def judge_character_h_and_obscenity(character_id: int) -> int:
    """
    维持H状态与猥亵\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 如果不在同一位置，则结束H状态
    if character_data.sp_flag.is_h and character_data.position != pl_character_data.position:
        character_data.sp_flag.is_h = False
        character_data.sp_flag.unconscious_h = 0
        character_data.behavior.behavior_id = constant.Behavior.END_H
        character_data.state = constant.CharacterStatus.STATUS_END_H
        character_data.behavior.start_time = pl_character_data.behavior.start_time
        character_data.behavior.duration = pl_character_data.behavior.duration
        character_data.target_character_id = character_id

    # 如果不在同一位置，则结束睡眠猥亵状态
    if character_data.sp_flag.unconscious_h == 1 and character_data.position != pl_character_data.position:
        character_data.sp_flag.unconscious_h = 0

    # 维持H状态，行动锁死为等待不动
    if character_data.sp_flag.is_h:
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        character_data.behavior.start_time = pl_character_data.behavior.start_time
        character_data.behavior.duration = pl_character_data.behavior.duration
        character_data.target_character_id = character_id
    return 1


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
    now_draw.text = "\n博士入睡，开始结算各种数据\n"
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
            sanity_point_grow() # 玩家理智成长
            refresh_temp_semen_max() # 刷新玩家临时精液上限
            character_data.eja_point = 0 # 清零射精槽
            character_data.sanity_point = character_data.sanity_point_max # 恢复理智槽
            character_data.semen_point = character_data.semen_point_max # 恢复精液量
            # 检查是否有可以升级的能力
            if cache.system_setting[2]:
                handle_ability.gain_ability(character_id)
            line_feed.draw()
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
            if cache.system_setting[3]:
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
            # 清零助理服务的flag
            if character_data.sp_flag.morning_salutation == 2:
                character_data.sp_flag.morning_salutation = 0
            if character_data.sp_flag.night_salutation == 2:
                character_data.sp_flag.night_salutation = 0
            # 清零香薰疗愈的flag
            if character_data.sp_flag.aromatherapy != 0:
                character_data.sp_flag.aromatherapy = 0

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


def character_aotu_change_value(character_id: int, now_time: datetime.datetime, pl_start_time: datetime.datetime):
    """
    结算角色随时间自动增加的数值
    Keyword arguments:
    character_id -- 角色id
    now_time -- 指定时间
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[now_character_data.target_character_id]
    add_time = now_character_data.behavior.duration
    # 真实的开始时间是当前角色行动开始时间和玩家行动开始时间中更晚的那个
    now_character_behavior_start_time = now_character_data.behavior.start_time
    true_start_time = max(now_character_behavior_start_time, pl_start_time)
    # print(f"debug {now_character_data.name}的now_character_behavior_start_time = {now_character_behavior_start_time}，pl_start_time = {pl_start_time}，start_time = {true_start_time}")
    # 真实的结束时间是当前角色行动结束时间和当前时间中更早的那个
    now_character_end_time = game_time.get_sub_date(minute=add_time, old_date=now_character_behavior_start_time)
    true_end_time = min(now_character_end_time, now_time)
    # print(f"debug {now_character_data.name}的now_character_end_time = {now_character_end_time}，now_time = {now_time}，end_time = {true_end_time}")
    # if true_end_time == true_start_time:
    #     print(f"debug {now_character_data.name}，behavior_id = {game_config.config_status[now_character_data.state].name}, duration = {add_time}")
    # 真实的行动时间是真实的结束时间减去真实的开始时间
    true_add_time = int((true_end_time.timestamp() - true_start_time.timestamp()) / 60)
    # print(f"debug {now_character_data.name}的true_add_time = {true_add_time}，true_start_time = {true_start_time}，true_end_time = {true_end_time}\n")
    # 最少为1分钟，以免随机取值函数出错
    true_add_time = max(true_add_time, 0)

    tired_change = int(true_add_time / 6)
    # 仅计算在不睡觉时的正常行动结算疲劳值
    if game_config.config_status[now_character_data.state].name not in {"睡觉","休息"}:
        now_character_data.tired_point += tired_change
        now_character_data.tired_point = min(now_character_data.tired_point,160)

    # 休息时小幅度减少疲劳值
    elif now_character_data.state == constant.CharacterStatus.STATUS_REST:
        now_character_data.tired_point -= tired_change
        now_character_data.tired_point = max(now_character_data.tired_point,0) # 最少为0

        # 疲劳归零则直接结算当前行动
        # if now_character_data.tired_point <= 0:
        #     judge_character_status_time_over(character_id, cache.game_time, end_now = 2)

    # 睡觉时大量减少疲劳值
    elif now_character_data.state == constant.CharacterStatus.STATUS_SLEEP:
        tired_change *= 2
        now_character_data.tired_point -= tired_change
        now_character_data.tired_point = max(now_character_data.tired_point,0) # 最少为0
        # 熟睡值在到熟睡之前快速增加
        sleep_level,tem = attr_calculation.get_sleep_level(now_character_data.sleep_point)
        if sleep_level <= 1:
            add_sleep = int(true_add_time * 1.5)
            now_character_data.sleep_point += add_sleep
        # 熟睡值到熟睡后上下波动，加的可能性比减的可能性大一点点
        else:
            add_sleep = random.randint(int(true_add_time * -0.5),int(true_add_time * 0.6))
            now_character_data.sleep_point += add_sleep
        # 最高上限100
        now_character_data.sleep_point = min(now_character_data.sleep_point,100)
        # print(f"debug {now_character_data.name}疲劳值-{tired_change}={now_character_data.tired_point}，熟睡值+{add_sleep}={now_character_data.sleep_point}，当前时间={cache.game_time}")

    # 结算尿意值
    if character_id == 0 and not cache.system_setting[5]:
        pass
    else:
        add_urinate = random.randint(int(true_add_time * 0.8), int(true_add_time * 1.2))
        add_urinate *= cache.system_setting[6] / 2
        now_character_data.urinate_point += int(add_urinate)
        now_character_data.urinate_point = min(now_character_data.urinate_point,240)

    # 结算饥饿值
    add_hunger = random.randint(int(true_add_time * 0.8), int(true_add_time * 1.2))
    now_character_data.hunger_point += add_hunger
    now_character_data.hunger_point = min(now_character_data.hunger_point,240)

    # print(f"debug character_id = {character_id}，target_character_id = {player_character_data.target_character_id}，now_character_data.hunger_point = {now_character_data.hunger_point}")

    # 结算乳汁量，仅结算有泌乳素质的
    if now_character_data.talent[27]:
        milk_change = int(true_add_time * 2 / 3)
        add_milk = random.randint(int(milk_change * 0.8), int(milk_change * 1.2))
        now_character_data.pregnancy.milk += add_milk
        now_character_data.pregnancy.milk = min(now_character_data.pregnancy.milk,now_character_data.pregnancy.milk_max)

    # 结算玩家部分
    if character_id == 0:

        # 非H模式下结算玩家的射精值减少
        if not now_character_data.sp_flag.is_h:
            # 上次射精时间距离现在超过一小时则射精值减少
            last_time = now_character_data.action_info.last_eaj_add_time
            if (cache.game_time - last_time) > datetime.timedelta(minutes=30):
                now_character_data.eja_point -= true_add_time * 10
                now_character_data.eja_point = max(now_character_data.eja_point,0)

        # 玩家缓慢恢复精液量
        now_character_data.semen_point += int(true_add_time / 6)
        now_character_data.semen_point = min(now_character_data.semen_point,now_character_data.semen_point_max)

        # 结算玩家源石技艺的理智值消耗
        # 激素系，改为不消耗理智
        # if now_character_data.pl_ability.hormone:
        #     down_sp = max(int(true_add_time / 6),1)
        #     now_character_data.sanity_point -= down_sp
        #     now_character_data.pl_ability.today_sanity_point_cost += down_sp
        # 视觉系
        if now_character_data.pl_ability.visual:
            down_sp = max(int(true_add_time / 12),1)
            # 倍率计算
            multiple = now_character_data.talent[307] + now_character_data.talent[308] + now_character_data.talent[309]
            down_sp *= max(multiple, 1)
            now_character_data.sanity_point -= down_sp
            now_character_data.pl_ability.today_sanity_point_cost += down_sp
        # 理智值不足则归零并中断所有开启中的源石技艺
        if now_character_data.sanity_point < 0:
            now_character_data.sanity_point = 0
            now_character_data.pl_ability.visual = False
            # 输出提示信息
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.text = "\n理智值不足，开启的源石技艺已全部中断\n"
            now_draw.draw()

        # 结算对无意识对象的结算
        if target_data.sp_flag.unconscious_h:
            # 睡奸判定
            if target_data.state == constant.CharacterStatus.STATUS_SLEEP and now_character_data.behavior.behavior_id >= 301:
                # 双倍扣除原本会增加的熟睡值
                down_sleep = int(true_add_time * 3)
                target_data.sleep_point -= down_sleep
                # 计算当前熟睡等级
                sleep_level,tem = attr_calculation.get_sleep_level(target_data.sleep_point)
                # print(f"debug {target_data.name}熟睡值={target_data.sleep_point}，熟睡等级{sleep_level}")
                # 熟睡等级小于等于1时判定是否吵醒
                if sleep_level <= 1:
                    # 浅睡和半梦半醒时递增苏醒概率
                    weak_rate = game_config.config_sleep_level[1].sleep_point - target_data.sleep_point
                    if target_data.sleep_point <= game_config.config_sleep_level[0].sleep_point:
                        weak_rate += game_config.config_sleep_level[0].sleep_point - target_data.sleep_point
                    # 判定是否吵醒，吵醒则先结算当前行动然后进入重度性骚扰失败状态
                    if weak_rate >= random.randint(1,100):
                        target_data.tired_point = 0
                        target_data.sleep_point = 0
                        # 输出提示信息
                        now_draw = draw.WaitDraw()
                        now_draw.width = window_width
                        now_draw.text = f"\n因为{now_character_data.name}的动作，{target_data.name}从梦中惊醒过来\n"
                        now_draw.draw()
                        judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
                        now_character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
                        now_character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
                        now_character_data.behavior.duration = 10
                        judge_character_status(character_id)
                        # TODO 测试惊醒是否正常运作，是否需要时间推进十分钟
                        # update.game_update_flow(10)

    # 结算非玩家部分
    else:

        # 结算精液流动
        if len(now_character_data.dirty.semen_flow):
            # 计算流动的精液量
            flow_semen_max = int(true_add_time * 2)
            # print(f"debug {now_character_data.name}的精液流动最大量为{flow_semen_max}，add_time = {true_add_time}")

            new_flow_list = []
            # 遍历每个部位的精液流动
            for all_flow_dict in now_character_data.dirty.semen_flow:
                # 实际流动的精液总量
                all_real_flow = 0
                # 源头数据
                source_id = all_flow_dict["source"]["id"]
                source_type = all_flow_dict["source"]["type"]
                new_target_list = []
                # 如果all_flow_dict没有键"targets"，则跳过
                if "targets" not in all_flow_dict:
                    continue
                # 遍历每个流动的目标
                for now_flow_dict in all_flow_dict["targets"]:
                    if now_flow_dict["remaining_volume"] > 0:
                        # 计算该部位的精液流动
                        now_flow = min(flow_semen_max, now_flow_dict["remaining_volume"])
                        all_real_flow += now_flow
                        now_flow_dict["remaining_volume"] -= now_flow
                        now_part_cid = now_flow_dict["id"]
                        # print(f"debug {now_character_data.name}，{now_flow_dict['type']}的{now_part_cid}部位，精液流动{now_flow}，剩余{now_flow_dict['remaining_volume']}")
                        # 目标部位的精液增加
                        ejaculation_panel.update_semen_dirty(character_id=character_id, part_cid=now_part_cid, part_type=now_flow_dict["type"], semen_count=now_flow, update_shoot_position_flag=False)
                        # 如果目标部位的精液流动完毕，则将其从流动列表中移除
                        if now_flow_dict["remaining_volume"] > 0:
                            new_target_list.append(now_flow_dict)
                # 更新流动的目标列表
                all_flow_dict["targets"] = new_target_list
                # 遍历完全目标后，如果实际流动的精液总量大于0，则在源头部位减少相应的精液量
                if all_real_flow > 0:
                    ejaculation_panel.update_semen_dirty(character_id=character_id, part_cid=source_id, part_type=source_type, semen_count=-all_real_flow, update_shoot_position_flag=False)
                # 如果源头部位的精液流动完毕，则将其从流动列表中移除，否则将其加入新的流动列表
                if len(all_flow_dict["targets"]):
                    new_flow_list.append(all_flow_dict)
            # 更新流动的源头列表
            now_character_data.dirty.semen_flow = new_flow_list
            # print(f"debug {now_character_data.name}的精液流动完毕，剩余流动列表为{now_character_data.dirty.semen_flow}")


def change_character_persistent_state(character_id: int):
    """
    结算角色的状态是否会持续\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    start_time = now_character_data.behavior.start_time
    now_time = game_time.get_sub_date(minute=now_character_data.behavior.duration, old_date=start_time)

    # 结算H状态的持续时间
    for i in range(len(now_character_data.h_state.body_item)):
        if now_character_data.h_state.body_item[i][1]:
            end_time = now_character_data.h_state.body_item[i][2]
            if end_time != None and game_time.judge_date_big_or_small(now_time,end_time):
                now_character_data.h_state.body_item[i][1] = False
                now_character_data.h_state.body_item[i][2] = None


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
        if hasattr(cache.rhodes_island, 'party_day_of_week') and cache.rhodes_island.party_day_of_week[week_day]:
            for i in range(3):
                character_data.entertainment.entertainment_type[i] = cache.rhodes_island.party_day_of_week[week_day]
        
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


def sanity_point_grow():
    """
    玩家理智值的自然成长\n
    Keyword arguments:
    无
    """
    character_data: game_type.Character = cache.character_data[0]
    today_cost = character_data.pl_ability.today_sanity_point_cost
    character_data.pl_ability.today_sanity_point_cost = 0
    # 消耗超过90时进行成长
    if today_cost >= 50 and character_data.sanity_point_max < 9999:
        # 成长值为消耗值的1/50，四舍五入取整
        grow_value = round(today_cost / 50)
        character_data.sanity_point_max += grow_value
        character_data.sanity_point_max = min(character_data.sanity_point_max,9999)
        # 绘制说明信息
        now_draw = draw.WaitDraw()
        now_draw.width = window_width
        now_draw.text = f"\n在刻苦的锻炼下，博士理智最大值成长了{grow_value}点\n"
        now_draw.draw()


def judge_same_position_npc_follow():
    """
    判断同位置的NPC是否跟随玩家\n
    Keyword arguments:
    无
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        # 智能跟随、位置在玩家移动的出发地、异常状态267正常
        if (
            character_data.sp_flag.is_follow == 1 and
            character_data.position == pl_character_data.position and 
            handle_premise.handle_normal_267(character_id)
            ):

            # 变成移动状态，目标为玩家位置
            tem_1, tem_2, move_path, move_time = character_move.character_move(character_id, pl_character_data.behavior.move_final_target)
            move_flag, wait_flag = character_move.judge_character_move_to_private(character_id, move_path)
            if move_flag:
                character_data.behavior.behavior_id = constant.Behavior.MOVE
                character_data.state = constant.CharacterStatus.STATUS_MOVE
                character_data.behavior.move_target = move_path
                character_data.behavior.move_final_target = pl_character_data.behavior.move_final_target
                character_data.behavior.duration = move_time
                character_data.behavior.start_time = pl_character_data.behavior.start_time
                character_data.target_character_id = character_id
                character_data.action_info.follow_wait_time = 0
            elif wait_flag:
                character_data.state = constant.CharacterStatus.STATUS_WAIT
                character_data.behavior.behavior_id = constant.Behavior.WAIT
                character_data.behavior.duration = 5
                character_data.action_info.follow_wait_time += 5

            # print(f"debug {character_data.name}跟随玩家，当前位置为{character_data.position}，当前目标位置为{move_path}，最终目标位置为{pl_character_data.behavior.move_final_target}，行动时间为{move_time}分钟, start_time = {character_data.behavior.start_time}")


def refresh_temp_semen_max():
    """
    刷新临时最大精液量\n
    """
    character_data: game_type.Character = cache.character_data[0]
    now_semen = character_data.semen_point
    if now_semen:
        # 最大额外精液量为正常上限的4倍
        character_data.tem_extra_semen_point += int(now_semen / 2)
        character_data.tem_extra_semen_point = min(character_data.tem_extra_semen_point, character_data.semen_point_max * 4)
        # 获得浓厚精液
        if character_data.tem_extra_semen_point >= character_data.semen_point_max * 4:
            character_data.talent[33] = 1
        else:
            character_data.talent[33] = 0
        # 绘制说明信息
        now_draw = draw.NormalDraw()
        now_draw.width = window_width
        draw_text = f"\n今日未消耗的 {now_semen}ml 精液转化为了 {int(now_semen / 2)}ml 次日额外精液"
        if character_data.tem_extra_semen_point >= character_data.semen_point_max * 4:
            draw_text += f"，额外精液量已达上限，并获得了为期一天的[浓厚精液]"
        draw_text += "\n"
        now_draw.text = draw_text
        now_draw.draw()


def judge_interrupt_character_behavior(character_id: int) -> int:
    """
    判断是否需要打断角色的当前行动\n
    Keyword arguments:
    character_id -- 角色id\n
    interrupt_type -- 打断类型\n
    Return arguments:
    bool -- 是否打断
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 睡觉中，疲劳归零，且HP、MP满值时，当前非睡觉时间，则立刻结束睡觉
    if (
        handle_premise.handle_action_sleep(character_id) and
        handle_premise.handle_tired_le_0(character_id) and
        handle_premise.handle_hp_max(character_id) and
        handle_premise.handle_mp_max(character_id) and
        not handle_premise.handle_game_time_is_sleep_time(character_id)
    ):
        judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
        # print(f"debug {character_data.name}疲劳归零，结束睡觉，当前时间={cache.game_time}")
        return 1

    # 睡觉中，早安问候服务开启中，今日未问候，则将行动结束时间设为问候时间
    if (
        handle_premise.handle_action_sleep(character_id) and
        handle_premise.handle_assistant_morning_salutation_on(character_id) and
        handle_premise.handle_morning_salutation_flag_0(character_id)
    ):
        # 玩家醒来时间
        pl_character_data = cache.character_data[0]
        judge_wake_up_time = game_time.get_sub_date(minute=-30, old_date=pl_character_data.action_info.wake_time)
        # 角色醒来时间
        start_time = character_data.behavior.start_time
        end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
        # 如果角色的行动结束时间在玩家醒来时间之后，则将行动结束时间设为玩家醒来时间
        # 通过判定行动时间来限制只触发一次
        if game_time.judge_date_big_or_small(end_time, judge_wake_up_time) and character_data.behavior.duration == 480:
            new_duration = int((judge_wake_up_time - start_time).seconds / 60)
            # print(f"debug {character_data.name}早安问候服务开启中，今日未问候，将行动结束时间设为问候时间，玩家醒来时间={pl_character_data.action_info.wake_time}，角色行动结束时间={end_time},原行动时间={character_data.behavior.duration}分钟，新行动时间={new_duration}分钟")
            character_data.behavior.duration = new_duration
            return 1

    return 0
