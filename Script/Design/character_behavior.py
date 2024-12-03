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
)
from Script.Design import (
    settle_behavior,
    game_time,
    character,
    handle_premise,
    handle_premise_place,
    event,
    talk,
    map_handle,
    cooking,
    attr_calculation,
    character_move,
    pregnancy,
    handle_talent,
    handle_ability,
    update,
)
from Script.UI.Moudle import draw
from Script.UI.Panel import ejaculation_panel, field_commission_panel
from Script.Config import game_config, normal_config
from Script.Settle import default

game_path = game_path_config.game_path
cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """
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
            pl_duration = cache.character_data[0].behavior.duration
            character_behavior(0, cache.game_time, pl_start_time)
        # 如果当前是时停模式，则回退时间，然后结束循环
        if cache.time_stop_mode:
            game_time.sub_time_now(minute = -pl_duration)
            break
        field_commission_panel.update_field_commission() # 刷新委托任务
        id_list = cache.npc_id_got.copy()
        id_list.discard(0)
        # 后结算其他NPC部分
        # now_time = datetime.datetime.now()
        # print(f"开始循环NPC部分: {now_time}")
        while len(cache.over_behavior_character) <= len(id_list):
            # print(f"debug 还差{len(id_list) - len(cache.over_behavior_character)}个NPC结算")
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
        # 玩家睡觉存档
        if cache.pl_sleep_save_flag:
            cache.pl_sleep_save_flag = False
            update_save()
        # 结束循环
        if len(cache.over_behavior_character) >= len(id_list) + 1:
            break


def update_cafeteria():
    """刷新食堂内食物"""
    max_people = len(cache.npc_id_got)
    # food_judge = 1
    food_count = 0
    for food_type in cache.rhodes_island.dining_hall_data:
        food_list: Dict[UUID, game_type.Food] = cache.rhodes_island.dining_hall_data[food_type]
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
        cooking.init_food_shop_data()


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
        judge_character_h_obscenity_unconscious(character_id) # H状态、猥亵与无意识

    # 处理公共资源
    # update_cafeteria() # 刷新食堂的饭，不需要了，改为NPC在没有饭的时候自动刷新

    # 先处理玩家部分
    if character_id == 0:
        # 记录玩家的指令文本
        cache.daily_intsruce += character_instruct_record(0)
        cache.pl_pre_status_instruce.append(character_data.state)
        if len(cache.pl_pre_status_instruce) > 10:
            cache.pl_pre_status_instruce.pop(0)

        if character_data.state == constant.CharacterStatus.STATUS_ARDER:
            cache.over_behavior_character.add(character_id)
            # print(f"debug 玩家空闲")
        # 非空闲活动下结算当前状态#
        else:
            # 结算玩家在移动时同场景里的NPC的跟随情况
            if character_data.state == constant.CharacterStatus.STATUS_MOVE:
                judge_same_position_npc_follow()
            # 在玩家行动前的前置结算
            judge_before_pl_behavior()
            # 结算状态与事件
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
        judge_character_tired_sleep(character_id) # 结算疲劳
        judge_character_h_obscenity_unconscious(character_id) # H状态、猥亵与无意识
        judge_pl_real_time_data() # 玩家实时数据结算
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
        if time_judge:
            cache.over_behavior_character.add(character_id)
        # if character_data.name == "阿米娅":
        #     print(f"debug 后：{character_data.name}，time_judge = {time_judge}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}, duration = {character_data.behavior.duration}, end_time = {game_time.get_sub_date(minute=character_data.behavior.duration, old_date=character_data.behavior.start_time)}")

    # 自动获得对应素质和能力
    handle_talent.gain_talent(character_id,now_gain_type = 0)


def find_character_target(character_id: int, now_time: datetime.datetime):
    """
    查询角色可用目标活动并赋给角色
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    start_time = character_data.behavior.start_time
    all_target_list = list(game_config.config_target.keys())
    premise_data = {}
    target_weight_data = {}
    null_target_set = set()

    # 如果该NPC在H模式，则不赋予新活动，且直接加入结束列表
    if character_data.sp_flag.is_h:
        cache.over_behavior_character.add(character_id)
        return

    # 如果玩家在对该NPC交互，则等待flag=1，此操作暂时不进行
    # safe_instruct = [constant.CharacterStatus.STATUS_WAIT,constant.CharacterStatus.STATUS_REST,constant.CharacterStatus.STATUS_SLEEP]
    # if PC_character_data.target_character_id == character_id:
    #     # print(f"debug character_id = {character_data.name}，state = {PC_character_data.state}")
    #     if character_data.state not in safe_instruct:
    #         character_data.sp_flag.wait_flag = 1

    # 首先判定是否有高优先级的行动
    type_0_target_list = game_config.config_target_type_index[0]
    target, weight, judge, new_premise_data = search_target(character_id, type_0_target_list, null_target_set, premise_data, target_weight_data)
    # 将行动列表加到null_target中，将新的前提数据加到premise_data中
    null_target_set.update(type_0_target_list)
    premise_data = new_premise_data
    # 然后判断需求，先判断需求链中的需求，再判断非链中的需求，最后判断是否需要进入需求链
    if judge == 0 and not handle_premise.handle_normal_1(character_id):
        now_target_list = game_config.config_target_type_index[12]
        target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
        null_target_set.update(now_target_list)
        premise_data = new_premise_data
    # 非链中的需求
    if judge == 0 and handle_premise.handle_unnormal_27(character_id):
        now_target_list = game_config.config_target_type_index[13]
        target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
        null_target_set.update(now_target_list)
        premise_data = new_premise_data
    # 进入需求链
    if judge == 0:
        now_target_list = game_config.config_target_type_index[11]
        target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
        null_target_set.update(now_target_list)
        premise_data = new_premise_data
    # 然后判断助理，先判断助理服务链，再判断非链中的助理服务，最后判断是否要进入助理服务链
    if judge == 0 and handle_premise.handle_is_assistant(character_id):
        # 是否正在助理服务链中
        if judge == 0 and handle_premise.handle_assistant_salutation_of_ai_disable(character_id):
            now_target_list = game_config.config_target_type_index[42]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 是否进行非链的助理服务
        if judge == 0:
            now_target_list = game_config.config_target_type_index[43]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 是否进入助理服务链
        if judge == 0:
            now_target_list = game_config.config_target_type_index[41]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
    # 然后判断工作，需要有工作，且在工作时间或到岗时间
    if judge == 0 and handle_premise.handle_have_work(character_id) and handle_premise.handle_to_work_time_or_work_time(character_id):
        # 进行工作
        if judge == 0:
            now_target_list = game_config.config_target_type_index[22]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 工作准备
        if judge == 0:
            now_target_list = game_config.config_target_type_index[21]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
    # 然后判断娱乐，需要在娱乐时间
    if judge == 0 and handle_premise.handle_all_entertainment_time(character_id):
        # 进行娱乐
        if judge == 0:
            now_target_list = game_config.config_target_type_index[32]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 娱乐后处理
        if judge == 0:
            now_target_list = game_config.config_target_type_index[33]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data
        # 娱乐准备
        if judge == 0:
            now_target_list = game_config.config_target_type_index[31]
            target, weight, judge, new_premise_data = search_target(character_id, now_target_list, null_target_set, premise_data, target_weight_data)
            null_target_set.update(now_target_list)
            premise_data = new_premise_data

    # 如果以上都没有，则开始遍历各大类的目标行动
    if judge == 0:
        now_target_list = []
        target_type_list = []

        # 如果已经有now_target_list了，则直接使用
        if len(now_target_list):
            now_target_list = now_target_list
        # 或者有target_type_list，则遍历后加入now_target_list
        elif len(target_type_list):
            for target_type in target_type_list:
                now_target_list.extend(game_config.config_target_type_index[target_type])
        # 如果还是没有，则遍历所有大类
        else:
            now_target_list = all_target_list

        target, weight, judge, new_premise_data = search_target(
            character_id,
            now_target_list,
            null_target_set,
            premise_data,
            target_weight_data,
        )
        # if character_data.name == "阿米娅":
        #     print(f"\ndebug 阿米娅的target = {target},weight = {weight},now_time = {now_time}")
        #     if 5 <= int(target) <= 30:
        #         print(f"debug position = {character_data.position},move_final_target = {character_data.behavior.move_final_target}")
    if judge:
        # print(f"debug {character_data.name}")
        # print(f"debug null_target_set = {null_target_set}")
        # print(f"debug premise_data = {premise_data}")
        # if character_data.name == "阿米娅":
        #     print(f"debug {character_data.name}的target = {target},weight = {weight},now_time = {now_time}")
        target_config = game_config.config_target[target]
        state_machine_id = target_config.state_machine_id
        #如果上个AI行动是普通交互指令，则将等待flag设为1
        # if state_machine_id >= 100:
        #     character_data.sp_flag.wait_flag = 1
            # print(f"debug 前一个状态机id = ",state_machine_id,",flag变为1,character_name =",character_data.name)
        constant.handle_state_machine_data[state_machine_id](character_id)
        # if character_data.name == "阿米娅":
        #     print(f"debug 中：{character_data.name}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}")
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
    from Script.Design import handle_instruct

    character_data: game_type.Character = cache.character_data[character_id]
    #交互对象结算
    if character_id:
        # 疲劳判定
        if character_data.hit_point <= 1 and not character_data.sp_flag.tired:
            character_data.sp_flag.tired = True
        # 仅在H或跟随模式下再进行结算
        if character_data.sp_flag.is_h or character_data.sp_flag.is_follow:
            # 如果疲劳了
            if character_data.sp_flag.tired or (attr_calculation.get_tired_level(character_data.tired_point) >= 2):
                pl_character_data: game_type.Character = cache.character_data[0]
                # 输出基础文本
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                # 跟随时，忽略H后停留的情况
                if character_data.sp_flag.is_follow and character_data.behavior.behavior_id != constant.Behavior.WAIT:
                    draw_text = _("太累了，无法继续跟随\n") if character_data.sp_flag.tired else _("太困了，无法继续跟随\n")
                    now_draw.text = character_data.name + draw_text
                    now_draw.draw()
                    character_data.sp_flag.is_follow = 0
                # H时，在无意识模式下则不检测疲劳，只检测HP
                elif character_data.sp_flag.is_h and (not character_data.sp_flag.unconscious_h or (character_data.sp_flag.unconscious_h and character_data.hit_point <= 1)):
                    character_data.sp_flag.is_h = False
                    pl_character_data.behavior.behavior_id = constant.Behavior.T_H_HP_0
                    pl_character_data.state = constant.CharacterStatus.STATUS_T_H_HP_0
                    pl_character_data.behavior.duration = 5
                    # 调用结束H的指令
                    handle_instruct.handle_end_h()

    # 玩家计算
    else:
        # 玩家只进行HP1的疲劳判定
        if character_data.hit_point <= 1:
            target_data = cache.character_data[character_data.target_character_id]
            # 如果是在H时
            if target_data.sp_flag.is_h:
                character_data.behavior.behavior_id = constant.Behavior.H_HP_0
                character_data.state = constant.CharacterStatus.STATUS_H_HP_0
                character_data.behavior.duration = 5
                target_data.sp_flag.is_h = False
                character_data.sp_flag.tired = False
                # 绘制文本
                now_draw = draw.WaitDraw()
                now_draw.width = window_width
                draw_text = _("太累了，无法继续H\n")
                now_draw.text = character_data.name + draw_text
                now_draw.draw()
                # 调用结束H的指令
                handle_instruct.handle_end_h()


def judge_character_status(character_id: int) -> int:
    """
    校验并结算角色状态\n
    Keyword arguments:\n
    character_id -- 角色id\n
    Return arguments:\n
    int -- 结算是否成功
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
    start_event_draw = event.handle_event(character_id, event_before_instrust_flag = True)
    event_type_now = 1
    if start_event_draw != None:
        event_id = start_event_draw.event_id
        character_data.event.event_id = event_id
        event_config = game_config.config_event[event_id]
        event_type_now = event_config.type
        # 事件绘制
        start_event_draw.draw()

    # if not character_id:
    #     print(f"debug 1 move_src = {character_data.behavior.move_src},position = {character_data.position}")
    # 指令与指令前事件的数值结算
    first_settle_panel = settle_behavior.handle_settle_behavior(character_id, end_time, event_type_now)
    second_settle_panel = None
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
            character_data.event.event_id = end_event_id
            # 事件绘制
            end_event_draw.draw()
            # 事件的数值结算
            second_settle_panel = settle_behavior.handle_settle_behavior(character_id, end_time, 0)

    # if not character_id:
    #     print(f"debug 3 move_src = {character_data.behavior.move_src},position = {character_data.position}")

    # 绘制数值变化
    if first_settle_panel != None:
        first_settle_panel.draw()
        if second_settle_panel != None:
            second_settle_panel.draw()
        #进行一次暂停以便玩家看输出信息
        if character_id == 0:
            wait_draw = draw.LineFeedWaitDraw()
            wait_draw.text = "\n"
            wait_draw.width = window_width
            wait_draw.draw()

    return 1

def judge_character_status_time_over(character_id: int, now_time: datetime.datetime, end_now = 0) -> int:
    """
    结算角色状态是否本次行动已经结束
    Keyword arguments:
    character_id -- 角色id
    end_now -- 是否要强制结算，1为当前时间大于行动结束时间，2为当前时间等于行动结束时间
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data = cache.character_data[0]
    scene_path_str = map_handle.get_map_system_path_str_for_list(character_data.position)
    scene_data: game_type.Scene = cache.scene_data[scene_path_str]
    # 如果行动起始时间大于当前时间，则初始化行动起始时间为当前时间
    if game_time.judge_date_big_or_small(character_data.behavior.start_time, now_time):
        character_data.behavior.start_time = now_time
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
    # 如果本次行动的持续时间为0
    if not add_time:
        # 如果是H状态，则直接可以跳出
        if handle_premise.handle_is_h(character_id):
            return 1
        character_data.behavior = game_type.Behavior()
        character_data.behavior.start_time = now_time
        character_data.behavior.duration = 1
        # 等待状态下则不转为空闲状态，直接跳出
        if character_data.state == constant.CharacterStatus.STATUS_WAIT:
            return 1
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        # print(f"debug {character_data.name}的add_time = 0，已重置为当前时间：start_time = {character_data.behavior.start_time}")
        return 0
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
                    pass
                    # 暂时不用该功能
                    """
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
                    """
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
            # 如果权重已经大于100，则直接返回
            if now_weight >= 100:
                # print(f"debug now_weight = {now_weight}")
                return target, now_weight, 1, premise_data
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
        return final_target, value_weight, 1, premise_data
    return "", 0, 0, premise_data

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
        draw_text = _("\n当前共{0}反发珠，抵消了：").format(character_data.juel[20])
        for i in [15, 10, 11, 12, 13]:
            # 1好意抵消2反发
            if character_data.juel[i] > 0:
                juel_down = min(character_data.juel[20], character_data.juel[i] * 2)
                character_data.juel[20] -= juel_down
                character_data.juel[i] -= juel_down // 2
                draw_text += _(" {0}个{1} ").format(juel_down//2, game_config.config_juel[i].name)
        draw_text += _("，剩余{0}个反发珠\n").format(character_data.juel[20])
        now_draw = draw.NormalDraw()
        now_draw.text = draw_text
        # now_draw.draw()
    return 1


def character_instruct_record(character_id: int) -> str:
    """
    角色的指令记录\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    str -- 指令记录文本
    """
    character_data: game_type.Character = cache.character_data[character_id]
    name = character_data.name
    instruct_text = ""
    # 记录时间的小时数和分钟数
    now_time = character_data.behavior.start_time.strftime("%H:%M")
    instruct_text += _("{0}在{1}，").format(name, now_time)
    # 移动指令则记录移动路径
    if character_data.state == constant.CharacterStatus.STATUS_MOVE:
        move_src = character_data.behavior.move_src[-1]
        if move_src == "0":
            move_src =  character_data.behavior.move_src[-2] + "出口"
        move_target = character_data.behavior.move_target[-1]
        if move_target == "0":
            move_target =  character_data.behavior.move_target[-2] + "出口"
        if move_target:
            instruct_text += _("从{0}移动至{1}\n").format(move_src, move_target)
    # 其他指令则记录状态
    else:
        now_chara_state = game_config.config_status[character_data.state].name
        # 如果是交互指令则记录交互对象
        if character_data.target_character_id != character_id:
            target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
            target_name = target_character_data.name
            instruct_text += _("对{0}进行了{1}\n").format(target_name, now_chara_state)
        else:
            instruct_text += _("进行了{0}\n").format(now_chara_state)
    return instruct_text


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
    return cant_move_flag


def judge_character_follow(character_id: int) -> int:
    """
    处理跟随模式
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 正常状态下的助理跟随，未智能跟随则变成智能跟随
    if (
        handle_premise.handle_not_follow(character_id) and
        handle_premise.handle_is_assistant(character_id) and
        handle_premise.handle_assistant_follow_1(character_id) and
        handle_premise.handle_action_not_sleep(character_id) and
        handle_premise.handle_normal_1(character_id)
        ):
        character_data.sp_flag.is_follow = 1

    # 智能跟随
    if character_data.sp_flag.is_follow == 1:
        # 取消所有工作和娱乐状态
        default.handle_cancel_all_work_and_entertainment_flag(character_id, 1, game_type.CharacterStatusChange, datetime.datetime)

    # 维持强制跟随的状态
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


def judge_character_h_obscenity_unconscious(character_id: int) -> int:
    """
    判断H状态、猥亵与无意识\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 玩家部分
    if character_id == 0:
        # 清空空气催眠位置
        if character_data.position != character_data.pl_ability.air_hypnosis_position:
            character_data.pl_ability.air_hypnosis_position = ""
        # 如果前指令是口交类型则重置所有阴茎污浊状态
        if handle_premise.handle_last_cmd_blowjob_type(0):
            for dirty_key in character_data.dirty.penis_dirty_dict:
                character_data.dirty.penis_dirty_dict[dirty_key] = False
        # 刚刚射精状态下，用计数的方式来判断是否重置
        if character_data.h_state.just_shoot == 1:
            character_data.h_state.just_shoot = 2
        else:
            character_data.h_state.just_shoot = 0
        # 二次确认H意外结束的归零结算
        special_end_list = constant.special_end_H_list
        if len(cache.pl_pre_status_instruce) and cache.pl_pre_status_instruce[-1] in special_end_list and character_data.behavior.behavior_id not in special_end_list:
            default.handle_both_h_state_reset(0, 1, change_data=game_type.CharacterStatusChange, now_time=datetime.datetime)
        # 如果在时停中搬运角色，则直接移动到玩家同一地点
        if (
            handle_premise.handle_time_stop_on(character_id) and 
            handle_premise.handle_carry_somebody_in_time_stop(character_id)
            ):
            now_carry_chara_id = pl_character_data.pl_ability.carry_chara_id_in_time_stop
            now_carry_character_data = cache.character_data[now_carry_chara_id]
            map_handle.character_move_scene(now_carry_character_data.position, pl_character_data.position, now_carry_chara_id)


    # 玩家部分终止，以下为NPC部分
    if character_id == 0:
        return 1

    # 将绝顶解放状态改为关闭绝顶寸止
    if handle_premise.handle_self_orgasm_edge_relase(character_id):
        default.handle_self_orgasm_edge_off(character_id, 1, change_data=game_type.CharacterStatusChange, now_time=datetime.datetime)
    # 将时停解放状态改为False
    if handle_premise.handle_self_time_stop_orgasm_relase(character_id):
        character_data.h_state.time_stop_release = False

    # H状态或木头人时，行动锁死为等待不动
    if character_data.sp_flag.is_h or character_data.hypnosis.blockhead:
        # 睡奸时例外
        if character_data.state == constant.CharacterStatus.STATUS_SLEEP:
            return 1
        character_data.behavior.behavior_id = constant.Behavior.WAIT
        character_data.state = constant.CharacterStatus.STATUS_WAIT
        character_data.behavior.start_time = pl_character_data.behavior.start_time
        character_data.behavior.duration = pl_character_data.behavior.duration
        character_data.target_character_id = character_id

    # 如果不在同一位置
    if handle_premise_place.handle_not_in_player_scene(character_id):

        # 如果不在同一位置，则结束H状态和无意识状态
        if character_data.sp_flag.is_h:
            character_data.sp_flag.is_h = False
            character_data.sp_flag.unconscious_h = 0
            character_data.behavior.behavior_id = constant.Behavior.END_H
            character_data.state = constant.CharacterStatus.STATUS_END_H
            character_data.behavior.start_time = pl_character_data.behavior.start_time
            character_data.behavior.duration = pl_character_data.behavior.duration
            character_data.target_character_id = character_id

        # 如果不在同一位置，则结束睡眠猥亵状态
        elif character_data.sp_flag.unconscious_h == 1:
            character_data.sp_flag.unconscious_h = 0

        # 如果不在同一位置，则结束空气催眠
        elif character_data.sp_flag.unconscious_h == 5 and character_data.position != pl_character_data.pl_ability.air_hypnosis_position:
            character_data.sp_flag.unconscious_h = 0

    return 1


def judge_pl_real_time_data() -> int:
    """
    玩家实时数据结算\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """

    pl_character_data: game_type.Character = cache.character_data[0]

    # 酒店退房时间到了则退房
    if cache.rhodes_island.love_hotel_room_lv > 0:
        if game_time.judge_date_big_or_small(cache.game_time, pl_character_data.action_info.check_out_time) > 0:
            # 输出提示信息
            room_name = [_("标间"),_("情趣主题房"),_("顶级套房")]
            now_draw = draw.NormalDraw()
            now_draw.text = _("\n您入住的{0}到退房时间了，已自动退房\n").format(room_name[cache.rhodes_island.love_hotel_room_lv - 1])
            now_draw.draw()
            # 结算
            cache.rhodes_island.love_hotel_room_lv = 0
            pl_character_data.action_info.check_out_time = datetime.datetime(1, 1, 1)


def judge_before_pl_behavior():
    """
    玩家角色行动前的判断\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    if pl_character_data.target_character_id != 0:
        target_character_data: game_type.Character = cache.character_data[pl_character_data.target_character_id]
        # 重置交互对象的射精部位
        if target_character_data.h_state.shoot_position_body != -1:
            target_character_data.h_state.shoot_position_body = -1
        if target_character_data.h_state.shoot_position_cloth != -1:
            target_character_data.h_state.shoot_position_cloth = -1

    else:
        # 睡眠时间在6h及以上的额外恢复
        if pl_character_data.state == constant.CharacterStatus.STATUS_SLEEP and pl_character_data.behavior.duration >= 360:
            refresh_temp_semen_max() # 刷新玩家临时精液上限

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
    now_draw.text = _("\n博士入睡，开始结算各种数据\n")
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
            character_data.eja_point = 0 # 清零射精槽
            # 如果此时助理在睡眠中，则清零助理晚安问候
            assistant_id = character_data.assistant_character_id
            assistant_character_data: game_type.Character = cache.character_data[assistant_id]
            if handle_premise.handle_assistant_night_salutation_on(assistant_id) and handle_premise.handle_action_sleep(assistant_id):
                assistant_character_data.sp_flag.night_salutation = 0
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
            character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state)
            # 清零催眠状态
            if character_data.sp_flag.unconscious_h >= 4:
                character_data.sp_flag.unconscious_h = 0
            character_data.hypnosis.increase_body_sensitivity = False
            character_data.hypnosis.blockhead = False
            character_data.hypnosis.active_h = False
            character_data.hypnosis.pain_as_pleasure = False
            character_data.hypnosis.roleplay = 0
            # 清零睡奸中醒来状态
            character_data.sp_flag.sleep_h_awake = 0


    # 非角色部分
    cache.pl_sleep_save_flag = True


def update_new_day():
    """
    新一天的刷新\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    from Script.Design import basement, clothing
    from Script.UI.Panel import nation_diplomacy_panel, navigation_panel

    now_draw = draw.NormalDraw()
    now_draw.width = window_width
    now_draw.text = _("\n已过24点，开始结算各种数据\n\n")
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
            if character_data.sp_flag.morning_salutation == 2 or character_data.assistant_services[5] == 0:
                character_data.sp_flag.morning_salutation = 0
            if character_data.sp_flag.night_salutation == 2 or character_data.assistant_services[6] == 0:
                character_data.sp_flag.night_salutation = 0
            # 清零香薰疗愈的flag
            if character_data.sp_flag.aromatherapy != 0:
                character_data.sp_flag.aromatherapy = 0
            # 清零食物不对劲的flag
            if character_data.sp_flag.find_food_weird != 0:
                character_data.sp_flag.find_food_weird = 0
            # 增加欲望值
            character_data.desire_point += random.randint(5, 15)
            # 每周一次，如果已陷落则提供粉红凭证
            if cache.game_time.weekday() == 6:
                fall_chara_give_pink_voucher(character_id)

    # 非角色部分
    basement.update_base_resouce_newday() # 更新基础资源
    cooking.init_food_shop_data() # 初始化餐厅数据
    navigation_panel.judge_arrive() # 判断是否到达目的地
    # 每周一次
    if cache.game_time.weekday() == 6:
        nation_diplomacy_panel.judge_diplomatic_policy() # 结算外交政策
    cache.pre_game_time = cache.game_time
    cache.daily_intsruce.append('\n\n' + game_time.get_date_until_day() + '\n\n')
    # update_save()


def update_save():
    """
    自动存档\n
    Keyword arguments:
    无\n
    Return arguments:
    无
    """
    from Script.Core import save_handle

    now_draw = draw.WaitDraw()
    now_draw.width = window_width
    now_draw.text = _("\n全部结算完毕，开始自动保存\n")
    # 播放一条提示信息
    info_list = []
    for i in game_config.config_tip_data:
        info_list.append(i)
    info_id = random.choice(info_list)
    info_text = game_config.config_tip_data[info_id].info
    now_draw.text += _("\n请博士在保存时阅读今日的小贴士：\n\n  {0}\n\n\n").format(info_text)
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
    if now_character_data.target_character_id not in cache.character_data:
        now_character_data.target_character_id = character_id
    target_data: game_type.Character = cache.character_data[now_character_data.target_character_id]
    add_time = now_character_data.behavior.duration
    # 真实的开始时间是当前角色行动开始时间和玩家行动开始时间中更晚的那个
    now_character_behavior_start_time = now_character_data.behavior.start_time
    true_start_time = max(now_character_behavior_start_time, pl_start_time)
    # 真实的结束时间是当前角色行动结束时间和当前时间中更早的那个
    now_character_end_time = game_time.get_sub_date(minute=add_time, old_date=now_character_behavior_start_time)
    true_end_time = min(now_character_end_time, now_time)
    # 真实的行动时间是真实的结束时间减去真实的开始时间
    true_add_time = int((true_end_time.timestamp() - true_start_time.timestamp()) / 60)
    # 避免负数
    true_add_time = max(true_add_time, 0)

    # 结算疲劳值
    tired_change = int(true_add_time / 6)
    # 基础行动结算1疲劳值
    if true_add_time == 5:
        tired_change = 1
    # 不睡觉时、且不是时停中，结算疲劳值
    if now_character_data.state not in {constant.CharacterStatus.STATUS_SLEEP} and handle_premise.handle_time_stop_off(character_id):
        now_character_data.tired_point += tired_change
        now_character_data.tired_point = min(now_character_data.tired_point,160)

    # 休息时回复体力、气力
    if now_character_data.state == constant.CharacterStatus.STATUS_REST:
        final_adjust = 1
        # 休息室等级对回复效果的影响
        now_level = cache.rhodes_island.facility_level[31]
        facility_cid = game_config.config_facility_effect_data[_("休息室")][int(now_level)]
        facility_effect = game_config.config_facility_effect[facility_cid].effect
        facility_effect_adjust = 1 + facility_effect / 100
        final_adjust *= facility_effect_adjust
        # 素质对回复效果的影响
        if now_character_data.talent[351]: # 回复慢
            final_adjust *= 0.7
        elif now_character_data.talent[352]: # 回复快
            final_adjust *= 1.5
        # 回复体力、气力
        hit_point_add_base = now_character_data.hit_point_max * 0.003 + 10
        hit_point_add = int(hit_point_add_base * true_add_time * final_adjust)
        now_character_data.hit_point += hit_point_add
        now_character_data.hit_point = min(now_character_data.hit_point, now_character_data.hit_point_max)
        mana_point_add_base = now_character_data.mana_point_max * 0.006 + 20
        mana_point_add = int(mana_point_add_base * true_add_time * final_adjust)
        now_character_data.mana_point += mana_point_add
        now_character_data.mana_point = min(now_character_data.mana_point, now_character_data.mana_point_max)

    # 睡觉时大量减少疲劳值，增加熟睡值，回复体力、气力
    elif now_character_data.state == constant.CharacterStatus.STATUS_SLEEP:
        # 减少疲劳值
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
            add_sleep = random.randint(int(true_add_time * -0.3),int(true_add_time * 0.6))
            now_character_data.sleep_point += add_sleep
        # 最高上限100
        now_character_data.sleep_point = min(now_character_data.sleep_point,100)
        # print(f"debug {now_character_data.name}疲劳值-{tired_change}={now_character_data.tired_point}，熟睡值+{add_sleep}={now_character_data.sleep_point}，当前时间={cache.game_time}")
        final_adjust = 1
        # 素质对回复效果的影响
        if now_character_data.talent[351]: # 回复慢
            final_adjust *= 0.7
        elif now_character_data.talent[352]: # 回复快
            final_adjust *= 1.5
        # 回复体力、气力
        hit_point_add_base = now_character_data.hit_point_max * 0.0025 + 3
        hit_point_add = int(hit_point_add_base * true_add_time * final_adjust)
        now_character_data.hit_point += hit_point_add
        now_character_data.hit_point = min(now_character_data.hit_point, now_character_data.hit_point_max)
        mana_point_add_base = now_character_data.mana_point_max * 0.005 + 6
        mana_point_add = int(mana_point_add_base * true_add_time * final_adjust)
        now_character_data.mana_point += mana_point_add
        now_character_data.mana_point = min(now_character_data.mana_point, now_character_data.mana_point_max)

    # 结算尿意值
    if character_id == 0 and not cache.system_setting[5]:
        pass
    else:
        add_urinate = random.randint(int(true_add_time * 0.8), int(true_add_time * 1.2))
        add_urinate *= cache.system_setting[6] / 2
        now_character_data.urinate_point += int(add_urinate)
        now_character_data.urinate_point = min(now_character_data.urinate_point,300)

    # 结算饥饿值
    add_hunger = random.randint(int(true_add_time * 0.8), int(true_add_time * 1.2))
    now_character_data.hunger_point += add_hunger
    now_character_data.hunger_point = min(now_character_data.hunger_point,240)

    # 结算有意识、周围有其他人、羞耻没有超限、状态1256正常下，不穿胸衣和内裤时的羞耻值增加
    exposure_adjust = 0
    if (
        handle_premise.handle_not_wear_bra_or_pan(character_id) and 
        handle_premise.handle_unconscious_flag_0(character_id) and 
        handle_premise_place.handle_scene_over_two(character_id) and 
        handle_premise.handle_self_shy_ge_100000(character_id) and 
        handle_premise.handle_normal_1(character_id) and 
        handle_premise.handle_normal_2(character_id) and
        handle_premise.handle_normal_5(character_id) and
        handle_premise.handle_normal_6(character_id)
        ):
        if handle_premise.handle_not_wear_bra(character_id):
            exposure_adjust += 1
        if handle_premise.handle_not_wear_pan(character_id):
            exposure_adjust += 2
    if exposure_adjust:
        feel_adjust = attr_calculation.get_ability_adjust(now_character_data.ability[34])
        exposure_add = true_add_time * feel_adjust * exposure_adjust
        now_character_data.status_data[16] += exposure_add
        now_character_data.status_data[16] = min(now_character_data.status_data[16],100000)

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
            # 上次射精时间距离现在超过30分钟则射精值减少
            last_time = now_character_data.action_info.last_eaj_add_time
            if (cache.game_time - last_time) > datetime.timedelta(minutes=30):
                now_character_data.eja_point -= true_add_time * 10
                now_character_data.eja_point = max(now_character_data.eja_point,0)

        # 玩家缓慢恢复精液量
        now_character_data.semen_point += int(true_add_time / 20)
        now_character_data.semen_point = min(now_character_data.semen_point,now_character_data.semen_point_max)

        # 结算玩家源石技艺的理智值消耗
        # 视觉系
        if now_character_data.pl_ability.visual:
            down_sp = max(int(true_add_time / 12),1)
            # 倍率计算
            multiple = now_character_data.talent[307] + now_character_data.talent[308] + now_character_data.talent[309]
            down_sp *= max(multiple, 1)
            # 用于消耗的理智值不得超过当前理智值
            down_sp = min(down_sp, now_character_data.sanity_point)
            now_character_data.sanity_point -= down_sp
            now_character_data.pl_ability.today_sanity_point_cost += down_sp
        # 时停系
        if handle_premise.handle_time_stop_on(character_id):
            down_sp = max(true_add_time * 2, 1)
            # 用于消耗的理智值不得超过当前理智值
            down_sp = min(down_sp, now_character_data.sanity_point)
            now_character_data.sanity_point -= down_sp
            now_character_data.pl_ability.today_sanity_point_cost += down_sp
        # 理智值不足则归零并中断所有开启中的源石技艺
        if handle_premise.handle_at_least_one_arts_on(character_id) and now_character_data.sanity_point <= 0:
            # 输出提示信息
            now_draw = draw.WaitDraw()
            now_draw.width = window_width
            now_draw.style = "red"
            now_draw.text = _("\n理智值不足，开启的源石技艺已全部中断\n")
            now_draw.draw()
            # 开始结算
            now_character_data.sanity_point = 0
            now_character_data.pl_ability.visual = False
            # 解除目标的催眠
            if target_data.sp_flag.unconscious_h >= 4:
                default.handle_hypnosis_cancel(0,1,game_type.CharacterStatusChange,datetime.datetime)
            # 时停中则进入时停解除状态
            if handle_premise.handle_time_stop_on(character_id):
                from Script.Design import handle_instruct
                handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_TIME_STOP_OFF)

        # 结算对无意识对象的结算
        if target_data.sp_flag.unconscious_h:
            # 睡奸判定
            if target_data.state == constant.CharacterStatus.STATUS_SLEEP and target_data.sp_flag.unconscious_h == 1:
                # 如果是等待指令或安眠药中则无事发生
                if (
                    now_character_data.state == constant.CharacterStatus.STATUS_WAIT or
                    now_character_data.h_state.body_item[9][1] == 1
                ):
                    # 赋值为2来规避吵醒判定
                    sleep_level = 2
                # 如果是其他行动则判定是否吵醒
                else:
                    # 双倍扣除原本会增加的熟睡值
                    down_sleep = int(true_add_time * 3)
                    target_data.sleep_point -= down_sleep
                    # 计算当前熟睡等级
                    sleep_level,tem = attr_calculation.get_sleep_level(target_data.sleep_point)
                # 熟睡等级小于等于1时判定是否吵醒
                if sleep_level <= 1:
                    judge_weak_up_in_sleep_h(character_id)

    # 结算非玩家部分
    else:
        # 结算精液流动
        if len(now_character_data.dirty.semen_flow):
            settle_semen_flow(character_id, true_add_time)


def judge_weak_up_in_sleep_h(character_id: int):
    """
    判断睡奸中是否醒来\n
    Keyword arguments:\n
    character_id -- 角色id\n
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[now_character_data.target_character_id]

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
        now_draw.text = _("\n因为{0}的动作，{1}从梦中惊醒过来\n").format(now_character_data.name, target_data.name)
        now_draw.draw()
        # 终止对方的睡眠
        judge_character_status_time_over(now_character_data.target_character_id, cache.game_time, end_now = 2)
        # 停止对方的无意识状态与H状态
        target_data.sp_flag.unconscious_h = 0
        target_data.sp_flag.is_h = False
        # 对方获得睡奸醒来状态
        target_data.sp_flag.sleep_h_awake = True
        # 重置双方H结构体和相关数据
        default.handle_both_h_state_reset(0, 1, game_type.CharacterStatusChange, datetime.datetime)
        # 检测是否满足高级性骚扰的实行值需求
        if handle_premise.handle_instruct_judge_high_obscenity(0):
            # 如果已经陷落的话
            if handle_premise.handle_target_fall(character_id):
            # 爱情线会变成轻度性骚扰
                if handle_premise.handle_target_love_ge_1(character_id):
                    now_character_data.behavior.behavior_id = constant.Behavior.LOW_OBSCENITY_ANUS
                    now_character_data.state = constant.CharacterStatus.STATUS_LOW_OBSCENITY_ANUS
                # 隶属线会愤怒生气
                elif handle_premise.handle_target_obey_ge_1(character_id):
                    target_data.angry_point += 100
                    target_data.sp_flag.angry_with_player = True
                # 如果没有陷落的话，会变成高级性骚扰
                else:
                    now_character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
                    now_character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
            # 如果没有陷落的话，会变成高级性骚扰
            else:
                now_character_data.behavior.behavior_id = constant.Behavior.HIGH_OBSCENITY_ANUS
                now_character_data.state = constant.CharacterStatus.STATUS_HIGH_OBSCENITY_ANUS
        # 不满足的话，设为H失败
        else:
            now_character_data.behavior.behavior_id = constant.Behavior.DO_H_FAIL
            now_character_data.state = constant.CharacterStatus.STATUS_DO_H_FAIL
        now_character_data.behavior.duration = 10
        # 为了让惊醒正常运作，需要时间推进十分钟
        update.game_update_flow(10)


def settle_semen_flow(character_id: int, true_add_time: int):
    """
    结算精液流动\n
    Keyword arguments:\n
    character_id -- 角色id\n
    true_add_time -- 实际行动时间\n
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
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
    # 因为睡眠时间很长，会导致持续状态的时间超过了当前时间，所以改为使用当前时间
    # start_time = now_character_data.behavior.start_time
    # now_time = game_time.get_sub_date(minute=now_character_data.behavior.duration, old_date=start_time)
    now_time = cache.game_time

    # H下结算全部持续状态
    if now_character_data.sp_flag.is_h:
        # 结算H状态的持续时间
        for i in range(len(now_character_data.h_state.body_item)):
            if now_character_data.h_state.body_item[i][1]:
                end_time = now_character_data.h_state.body_item[i][2]
                if end_time != None and game_time.judge_date_big_or_small(now_time,end_time):
                    now_character_data.h_state.body_item[i][1] = False
                    now_character_data.h_state.body_item[i][2] = None
    # 非H下结算部分药物
    else:
        for i in [8, 9]:
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
            # 幼女只能进行过家家的娱乐活动
            if handle_premise.handle_self_is_child(character_id):
                for i in range(3):
                    character_data.entertainment.entertainment_type[i] = 151
                return
            entertainment_list = [i for i in game_config.config_entertainment]
            entertainment_list.remove(0)
            # 循环获得上午、下午、晚上的三个娱乐活动
            for i in range(3):

                # 进入主循环
                while 1:
                    # 开始随机
                    choice_entertainment_id = random.choice(entertainment_list)
                    entertainment_data = game_config.config_entertainment[choice_entertainment_id]
                    # if choice_entertainment_id in {92, 151}:
                    #     print(f"debug {character_data.name}: {choice_entertainment_id}")
                    # 首先检查娱乐地点的场所是否开放
                    if entertainment_data.palce in game_config.config_facility_open_name_set:
                        facility_open_cid = game_config.config_facility_open_name_to_cid[entertainment_data.palce]
                        # 如果该娱乐活动的场所未开放，则去掉该id后重新随机
                        if cache.rhodes_island.facility_open[facility_open_cid] == 0:
                            entertainment_list.remove(choice_entertainment_id)
                            continue
                    # 检查该娱乐活动是否需要特定的条件
                    if entertainment_data.need == "无":
                        break
                    else:
                        need_data_all = entertainment_data.need
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


def fall_chara_give_pink_voucher(character_id: int):
    """
    陷落角色给予粉红凭证\n
    Keyword arguments:\n
    character_id -- 角色id
    """
    # 如果已陷落则给予粉红凭证
    character_fall_level = attr_calculation.get_character_fall_level(character_id)
    if character_fall_level <= 3:
        cache.rhodes_island.week_fall_chara_pink_certificate_add += character_fall_level * 20
    else:
        cache.rhodes_island.week_fall_chara_pink_certificate_add += 100


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
        now_draw.text = _("\n在刻苦的锻炼下，博士理智最大值成长了{0}点\n").format(grow_value)
        now_draw.draw()


def judge_same_position_npc_follow():
    """
    判断同位置的NPC是否跟随玩家\n
    Keyword arguments:\n
    无
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    for character_id in cache.npc_id_got:
        character_data: game_type.Character = cache.character_data[character_id]
        # 跳过不在同一位置的NPC
        if character_data.position != pl_character_data.position:
            continue
        # 智能跟随、异常状态267正常
        if (
            character_data.sp_flag.is_follow == 1 and
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
    # 需要睡眠时长至少大于等于6h
    if now_semen and character_data.behavior.duration >= 360:
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
        draw_text = _("\n在充足的睡眠下，今日未消耗的 {0}ml 精液转化为了 {1}ml 次日额外精液").format(now_semen, int(now_semen / 2))
        if character_data.tem_extra_semen_point >= character_data.semen_point_max * 4:
            draw_text += _("，额外精液量已达上限，并获得了为期一天的[浓厚精液]")
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

    # 休息中的相关判断
    if handle_premise.handle_action_rest(character_id):
        # 疲劳归零，且HP、MP满值时，则立刻结束休息
        if (
            handle_premise.handle_tired_le_0(character_id) and
            handle_premise.handle_hp_max(character_id) and
            handle_premise.handle_mp_max(character_id)
        ):
            judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
            return 1

    # 睡觉中的相关判断，需要没有被安眠药
    elif handle_premise.handle_action_sleep(character_id) and handle_premise.handle_self_not_sleep_pills(character_id):
        # ①睡觉中，早安问候服务开启中，今日未问候，角色行动结束时间晚于游戏时间，则将行动结束时间设为问候时间
        if (
            handle_premise.handle_assistant_morning_salutation_on(character_id) and
            handle_premise.handle_morning_salutation_flag_0(character_id) and
            handle_premise.handle_chara_behavior_end_time_lateer_than_game_time(character_id)
        ):
            # 角色醒来时间
            start_time = character_data.behavior.start_time
            end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)
            # 玩家醒来时间
            pl_character_data = cache.character_data[0]
            plan_to_wake_time = pl_character_data.action_info.plan_to_wake_time
            wake_time_hour, wake_time_minute = plan_to_wake_time[0], plan_to_wake_time[1]
            # 正确的醒来时间是end_time的时间中小时和分钟被替换为玩家醒来时间的小时和分钟
            judge_wake_up_time = end_time.replace(hour=wake_time_hour, minute=wake_time_minute)
            # 如果角色的行动结束时间在玩家醒来时间之后，则将行动结束时间设为玩家醒来时间
            # 通过判定行动时间来限制只触发一次
            if game_time.judge_date_big_or_small(end_time, judge_wake_up_time) and character_data.behavior.duration == 480:
                new_duration = int((judge_wake_up_time - start_time).seconds / 60)
                # print(f"debug {character_data.name}早安问候服务开启中，今日未问候，将行动结束时间设为问候时间，玩家醒来时间={pl_character_data.action_info.wake_time}，角色行动结束时间={end_time},原行动时间={character_data.behavior.duration}分钟，新行动时间={new_duration}分钟")
                character_data.behavior.duration = new_duration

        # ②睡觉中，疲劳归零，且HP、MP满值时，当前非睡觉时间，角色行动结束时间晚于游戏时间，则立刻结束睡觉
        if (
            handle_premise.handle_tired_le_0(character_id) and
            handle_premise.handle_hp_max(character_id) and
            handle_premise.handle_mp_max(character_id) and
            not handle_premise.handle_game_time_is_sleep_time(character_id) and
            handle_premise.handle_chara_behavior_end_time_lateer_than_game_time(character_id)
        ):
            judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
            # print(f"debug {character_data.name}疲劳归零，结束睡觉，当前时间={cache.game_time}")
            return 1

    # 工作或娱乐中的相关判断
    elif handle_premise.handle_action_work_or_entertainment(character_id):
        # 今日未洗澡，到了淋浴时间，距离行动结束时间还有至少30分钟，正常状态下，则立刻结束工作或娱乐
        if (
            handle_premise.handle_shower_flag_0(character_id) and
            handle_premise.handle_shower_time(character_id) and
            handle_premise.handle_still_30_minutes_before_end(character_id) and
            handle_premise.handle_normal_all(character_id)
        ):
            judge_character_status_time_over(character_id, cache.game_time, end_now = 2)
            # print(f"debug {character_data.name}立刻结束工作或娱乐，当前时间={cache.game_time}")
            return 1

    return 0


def npc_active_h():
    """
    判断NPC的逆推ai\n
    Return arguments:
    bool -- 0为失败，1为正常逆推
    """
    pl_character_data: game_type.Character = cache.character_data[0]
    target_character_id = pl_character_data.target_character_id
    target_character_data = cache.character_data[target_character_id]

    # 如果目标不是NPC，则返回
    if target_character_id == 0:
        return 0

    # 如果对方不是主动H状态，则返回
    if target_character_data.hypnosis.active_h == False and target_character_data.h_state.npc_active_h == False:
        return 0

    # 按照部位统计权重，初始权重为1
    part_weight = {}
    for i in range(8):
        part_weight[i] = 1

    # 部位经验权重为1
    for experience_id in game_config.config_experience:
        # 去掉非部位的经验
        if (
            20 <= experience_id <= 60 or
            experience_id >= 78
        ):
            continue

        # 取除以10的余数
        part_id = experience_id % 10
        if experience_id in {61,65}:
            part_id = 4
        elif experience_id in {62,66}:
            part_id = 5
        elif experience_id in {63,67}:
            part_id = 6
        elif experience_id in {64,68}:
            part_id = 7
        now_exp = target_character_data.experience[experience_id]
        part_weight[part_id] += now_exp

    # 能力等级权重为20
    for ability_id in game_config.config_ability:
        # 去掉非部位的能力
        if ability_id >= 13:
            continue
        if ability_id <= 8:
            part_id = ability_id
        # 将扩张的序号转换为部位序号
        else:
            part_id = ability_id - 5
        now_ability = target_character_data.ability[ability_id]
        part_weight[part_id] += now_ability * 20

    # TODO 暂时不支持U和W的逆推
    part_weight[6] = 0
    part_weight[7] = 0

    # 在最后将阴茎的权重置为0
    part_weight[3] = 0

    # 根据权重，随机选择一个部位
    part_id = random.choices(list(part_weight.keys()), weights=list(part_weight.values()), k=1)[0]
    # print(f"debug {target_character_data.name}的逆推ai选择了{game_config.config_organ[part_id].name}部位，总权重为{part_weight}")

    # 以防万一，如果因为BUG选中了阴茎，则返回
    if part_id == 3:
        return 0

    # 遍历全状态
    all_stastus_list = []
    for status_id in game_config.config_status:
        # 获得各状态的tag
        status_data = game_config.config_status[status_id]
        status_tag_list = status_data.tag.split("|")
        # 跳过其中非性爱类，道具类、药物类、SM类、非逆推类
        if(
            _("性爱") not in status_tag_list or
            _("道具") in status_tag_list or
            _("药物") in status_tag_list or
            _("SM") in status_tag_list or
            _("非逆推") in status_tag_list
        ):
            continue
        # 如果NPC为处，则跳过破处类
        if part_id == 4 and target_character_data.talent[0] and _("破处") in status_tag_list:
            continue
        if part_id == 5 and target_character_data.talent[1] and _("破处") in status_tag_list:
            continue
        if part_id == 6 and target_character_data.talent[2] and _("破处") in status_tag_list:
            continue
        if part_id == 7 and target_character_data.talent[3] and _("破处") in status_tag_list:
            continue
        # 开始加入列表中
        if part_id == 0 and "N" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 1 and "B" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 2 and "C" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 4 and "V" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 5 and "A" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 6 and "U" in status_tag_list:
            all_stastus_list.append(status_id)
        elif part_id == 7 and "W" in status_tag_list:
            all_stastus_list.append(status_id)

    # 如果没有符合条件的状态，则返回
    if len(all_stastus_list) == 0:
        return 0

    # print(f"debug 全列表为{all_stastus_list}")

    # 随机选择一个状态
    status_id = random.choice(all_stastus_list)

    # 赋予给玩家
    character.init_character_behavior_start_time(0, cache.game_time)
    pl_character_data.behavior.behavior_id = status_id
    pl_character_data.state = status_id
    pl_character_data.behavior.duration = 10
    update.game_update_flow(10)
