import datetime
from types import FunctionType
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
    instuct_judege,
    handle_premise,
    event,
    handle_npc_ai,
    handle_npc_ai_in_h,
    map_handle,
    handle_talent,
)
from Script.UI.Moudle import draw
from Script.UI.Panel import field_commission_panel
from Script.Config import game_config, normal_config
from Script.Settle import sleep_settle, past_day_settle, realtime_settle

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
    from Script.UI.Panel import achievement_panel
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
            cache.achievement.time_stop_duration += pl_duration
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
            past_day_settle.update_new_day()
        # 玩家睡觉存档
        if cache.pl_sleep_save_flag:
            cache.pl_sleep_save_flag = False
            sleep_settle.update_save()
        # 结束循环
        if len(cache.over_behavior_character) >= len(id_list) + 1:
            break
    # 结算成就
    achievement_panel.achievement_flow(_("时停"))
    achievement_panel.achievement_flow(_("群交"))


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
        instuct_judege.init_character_behavior_start_time(character_id, pl_start_time)

    # 处理特殊模式
    if character_id != 0:
        handle_npc_ai.judge_character_tired_sleep(character_id) # 判断疲劳和睡眠
        handle_npc_ai.judge_character_cant_move(character_id) # 无法自由移动的角色
        handle_npc_ai.judge_assistant_character(character_id) # 助理
        handle_npc_ai.judge_character_follow(character_id) # 跟随模式
        handle_npc_ai_in_h.judge_character_h_obscenity_unconscious(character_id, pl_start_time) # H状态、猥亵与无意识

    # 处理公共资源
    # update_cafeteria() # 刷新食堂的饭，不需要了，改为NPC在没有饭的时候自动刷新

    # 先处理玩家部分
    if character_id == 0:
        # 记录玩家的指令文本
        cache.daily_intsruce += character_instruct_record(0)
        cache.pl_pre_behavior_instruce.append(character_data.behavior.behavior_id)
        if len(cache.pl_pre_behavior_instruce) > 10:
            cache.pl_pre_behavior_instruce.pop(0)

        if character_data.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY:
            cache.over_behavior_character.add(character_id)
            # print(f"debug 玩家空闲")
        # 非空闲活动下结算当前状态#
        else:
            # 结算玩家在移动时同场景里的NPC的跟随情况
            if character_data.behavior.behavior_id == constant.Behavior.MOVE:
                handle_npc_ai.judge_same_position_npc_follow()
            # 在玩家行动前的前置结算
            judge_before_pl_behavior()
            # 结算状态与事件
            judge_character_status(character_id)
            # 刷新会根据时间即时增加的角色数值
            realtime_settle.character_aotu_change_value(character_id, now_time, pl_start_time)
            # 睡觉刷新
            if character_data.behavior.behavior_id == constant.Behavior.SLEEP:
                sleep_settle.update_sleep()
            # 结算角色的状态是否会持续
            realtime_settle.change_character_persistent_state(character_id)
            time_judge = judge_character_status_time_over(character_id, now_time)
            if time_judge:
                cache.over_behavior_character.add(character_id)
        #         print(f"debug time_judge")
        handle_npc_ai.judge_character_tired_sleep(character_id) # 结算疲劳
        handle_npc_ai_in_h.judge_character_h_obscenity_unconscious(character_id, pl_start_time) # H状态、猥亵与无意识
        realtime_settle.judge_pl_real_time_data() # 玩家实时数据结算
        # print(f"debug 玩家结算完毕")

    # 再处理NPC部分
    if character_id:
        # if character_data.name == "阿米娅":
            # print(f"debug 前：{character_data.name}，behavior_id = {game_config.config_behavior[character_data.behavior.behavior_id].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}")
        # 空闲状态下寻找、执行、结算可用行动
        if character_data.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY:
            # 寻找可用行动
            handle_npc_ai.find_character_target(character_id, now_time)
            # 结算状态与事件
            judge_character_status(character_id)
        # 移动情况下也直接结算
        elif character_data.behavior.behavior_id == constant.Behavior.MOVE:
            # 结算状态与事件
            judge_character_status(character_id)
        # 刷新会根据时间即时增加的角色数值
        realtime_settle.character_aotu_change_value(character_id, now_time, pl_start_time)
        # 结算角色的状态是否会持续
        realtime_settle.change_character_persistent_state(character_id)
        # 判断是否需要打断角色的当前行动
        handle_npc_ai.judge_interrupt_character_behavior(character_id)
        time_judge = judge_character_status_time_over(character_id, now_time)
        if time_judge:
            cache.over_behavior_character.add(character_id)
        # if character_data.name == "阿米娅":
        #     print(f"debug 后：{character_data.name}，time_judge = {time_judge}，behavior_id = {game_config.config_behavior[character_data.behavior.behavior_id].name}，start_time = {character_data.behavior.start_time}, game_time = {now_time}, duration = {character_data.behavior.duration}, end_time = {game_time.get_sub_date(minute=character_data.behavior.duration, old_date=character_data.behavior.start_time)}")

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
        if handle_premise.handle_self_is_h(character_id):
            return 1
        character_data.behavior = game_type.Behavior()
        character_data.behavior.start_time = now_time
        character_data.behavior.duration = 1
        # 等待状态下则不转为空闲状态，直接跳出
        if character_data.behavior.behavior_id == constant.Behavior.WAIT:
            return 1
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        # print(f"debug {character_data.name}的add_time = 0，已重置为当前时间：start_time = {character_data.behavior.start_time}")
        return 0
    if end_now:
        time_judge = end_now
    if time_judge:
        # 记录并刷新旧行为列表
        character_data.last_behavior_id_list.append(character_data.behavior.behavior_id)
        if len(character_data.last_behavior_id_list) > 5:
            character_data.last_behavior_id_list.pop(0)
        # 保留移动的来源位置
        tem_move_src = character_data.behavior.move_src
        if len(character_data.action_info.past_move_position_list) == 0 or (len(character_data.action_info.past_move_position_list) and tem_move_src != character_data.action_info.past_move_position_list[-1]):
            character_data.action_info.past_move_position_list.append(tem_move_src)
            if len(character_data.action_info.past_move_position_list) > 10:
                character_data.action_info.past_move_position_list.pop(0)
        # 移动状态下则不完全重置行动数据，保留最终目标数据
        if character_data.behavior.behavior_id == constant.Behavior.MOVE:
            tem_move_final_target = character_data.behavior.move_final_target
            character_data.behavior = game_type.Behavior()
            character_data.behavior.move_final_target = tem_move_final_target
        else:
            character_data.behavior = game_type.Behavior()
        # 赋予移动来源
        character_data.behavior.move_src = tem_move_src
        character_data.state = constant.CharacterStatus.STATUS_ARDER
        character_data.event.event_id = ""
        character_data.event.son_event_id = ""
        # 当前时间大于行动结束时间
        if time_judge == 1:
            character_data.behavior.start_time = end_time
            return 0
        # 当前时间等于行动结束时间
        elif time_judge == 2:
            instuct_judege.init_character_behavior_start_time(character_id, now_time)
            return 1
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
    if character_data.behavior.behavior_id == constant.Behavior.MOVE:
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
        now_chara_behavior_name = game_config.config_behavior[character_data.behavior.behavior_id].name
        # 如果是交互指令则记录交互对象
        if character_data.target_character_id != character_id:
            target_character_data: game_type.Character = cache.character_data[character_data.target_character_id]
            target_name = target_character_data.name
            instruct_text += _("对{0}进行了{1}\n").format(target_name, now_chara_behavior_name)
        else:
            instruct_text += _("进行了{0}\n").format(now_chara_behavior_name)
    return instruct_text


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

    # 睡眠时间在6h及以上的额外恢复
    if pl_character_data.behavior.behavior_id == constant.Behavior.SLEEP and pl_character_data.behavior.duration >= 360:
        sleep_settle.refresh_temp_semen_max() # 刷新玩家临时精液上限

    # 结算上次进行聊天的时间，以重置聊天计数器#
    settle_behavior.change_character_talkcount_for_time(0, pl_character_data.behavior.start_time)

    # 隐奸的被察觉情况结算
    if handle_premise.handle_hidden_sex_mode_ge_1(0):
        from Script.UI.Panel import hidden_sex_panel
        hidden_sex_panel.handle_hidden_sex_flow()
