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
    get_text,
)
from Script.Design import (
    settle_behavior,
    game_time,
    character,
    handle_premise,
    handle_premise_place,
    event,
    handle_npc_ai,
    map_handle,
    cooking,
    attr_calculation,
    pregnancy,
    handle_talent,
    handle_ability,
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
        handle_npc_ai.judge_character_tired_sleep(character_id) # 判断疲劳和睡眠
        handle_npc_ai.judge_character_cant_move(character_id) # 无法自由移动的角色
        handle_npc_ai.judge_character_follow(character_id) # 跟随模式
        handle_npc_ai.judge_character_h_obscenity_unconscious(character_id) # H状态、猥亵与无意识

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
                handle_npc_ai.judge_same_position_npc_follow()
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
        handle_npc_ai.judge_character_tired_sleep(character_id) # 结算疲劳
        handle_npc_ai.judge_character_h_obscenity_unconscious(character_id) # H状态、猥亵与无意识
        judge_pl_real_time_data() # 玩家实时数据结算
        # print(f"debug 玩家结算完毕")

    # 再处理NPC部分
    if character_id:
        # if character_data.name == "阿米娅":
        #     print(f"debug 前：{character_data.name}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}")
        # 空闲状态下寻找、执行、结算可用行动
        if character_data.state == constant.CharacterStatus.STATUS_ARDER:
            # 寻找可用行动
            handle_npc_ai.find_character_target(character_id, now_time)
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
        handle_npc_ai.judge_interrupt_character_behavior(character_id)
        time_judge = judge_character_status_time_over(character_id, now_time)
        if time_judge:
            cache.over_behavior_character.add(character_id)
        # if character_data.name == "阿米娅":
        #     print(f"debug 后：{character_data.name}，time_judge = {time_judge}，behavior_id = {game_config.config_status[character_data.state].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}, duration = {character_data.behavior.duration}, end_time = {game_time.get_sub_date(minute=character_data.behavior.duration, old_date=character_data.behavior.start_time)}")

    # 自动获得对应素质和能力
    handle_talent.gain_talent(character_id,now_gain_type = 0)


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
    if first_settle_panel != None and len(first_settle_panel.draw_list):
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

    # 结算上次进行聊天的时间，以重置聊天计数器#
    settle_behavior.change_character_talkcount_for_time(0, pl_character_data.behavior.start_time)


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
            handle_npc_ai.get_chara_entertainment(character_id)
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
                    handle_npc_ai.judge_weak_up_in_sleep_h(character_id)

    # 结算非玩家部分
    else:
        # 结算精液流动
        if len(now_character_data.dirty.semen_flow):
            settle_semen_flow(character_id, true_add_time)


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
