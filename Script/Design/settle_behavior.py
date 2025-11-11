import datetime
import random
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type, get_text, text_handle, rich_text
from Script.Design import attr_text, attr_calculation, handle_premise, handle_instruct, talk, game_time, second_behavior
from Script.Config import game_config, normal_config
from Script.UI.Panel import hypnosis_panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """


def handle_settle_behavior(character_id: int, now_time: datetime.datetime, event_flag = 1):
    """
    处理结算角色行为并输出对应文本
    Keyword arguments:
    character_id -- 角色id
    now_time -- 结算时间
    event_flag -- 事件结算变量，0只事件不指令，1只指令不事件，2均结算
    """
    from Script.UI.Panel import group_sex_panel

    now_character_data: game_type.Character = cache.character_data[character_id]
    player_character_data: game_type.Character = cache.character_data[0]
    change_data = game_type.CharacterStatusChange()
    start_time = now_character_data.behavior.start_time
    add_time = int((now_time - start_time).seconds / 60)

    behavior_id = now_character_data.behavior.behavior_id
    if event_flag > 0:
        # 玩家在群P模式的结算
        if (
            character_id == 0 and
            handle_premise.handle_group_sex_mode_on(character_id) and
            behavior_id not in {constant.Behavior.GROUP_SEX_TO_H, constant.Behavior.GROUP_SEX_END} and
            behavior_id not in constant.special_end_H_list
            ):
            # 记录初始的交互对象id
            first_target_character_id = now_character_data.target_character_id
            # 统计要执行的指令列表
            group_sex_instruct_list, full_list_of_target_id_and_state_id = group_sex_panel.count_group_sex_instruct_list()
            # 判定是否要进行当前行为的结算
            # 当前行为不在群P行为列表中，且不是等待行为时结算
            if behavior_id not in group_sex_instruct_list and behavior_id != constant.Behavior.WAIT:
                change_data = handle_instruct_data(character_id, behavior_id, now_time, add_time, change_data)
            # 不满足上述条件且也没有群P行为时也结算
            elif len(group_sex_instruct_list) == 0:
                change_data = handle_instruct_data(character_id, behavior_id, now_time, add_time, change_data)
            # 进行群P行为的计算
            if len(group_sex_instruct_list):
                for now_behavior_list in full_list_of_target_id_and_state_id:
                    # 获取当前行为的交互目标id和状态id
                    target_chara_id_list = now_behavior_list[0]
                    state_id = now_behavior_list[1]
                    for target_chara_id in target_chara_id_list:
                        # 将玩家的交互对象设为当前目标
                        now_character_data.target_character_id = target_chara_id
                        # 更改玩家的当前行为id
                        now_character_data.behavior.behavior_id = state_id
                        # 进行指令相关数据的结算
                        change_data = handle_instruct_data(character_id, state_id, now_time, add_time, change_data)
            # 回到初始的交互对象id
            now_character_data.target_character_id = first_target_character_id
            # 监狱长的性爱助手开启中，且当前交互目标不是监狱长
            if handle_premise.handle_sex_assistant_on(character_id) and handle_premise.handle_t_work_is_not_warden(character_id):
                from Script.UI.Panel import confinement_and_training
                # 进行性爱助手结算
                state_id = confinement_and_training.get_behavior_id_of_sex_assistant()
                if state_id != '0':
                    warden_character_id = cache.rhodes_island.current_warden_id
                    warden_character_data = cache.character_data[warden_character_id]
                    warden_character_data.behavior.behavior_id = state_id
                    warden_character_data.state = state_id
                    warden_character_data.behavior.duration = now_character_data.behavior.duration
                    warden_character_data.behavior.start_time = now_character_data.behavior.start_time
                    warden_character_data.target_character_id = now_character_data.target_character_id
                    warden_character_data.h_state.sex_assist = True
        # 正常情况下则直接执行结算
        else:
            # 进行指令相关数据的结算
            change_data = handle_instruct_data(character_id, behavior_id, now_time, add_time, change_data)

    if event_flag != 1:
        # 主事件
        event_id = now_character_data.event.event_id
        change_data = handle_event_data(event_id, character_id, add_time, change_data, now_time)

        # 子事件
        son_event_id = now_character_data.event.son_event_id
        # 如果触发了子事件的话
        if son_event_id != "":
            from Script.UI.Panel import draw_event_text_panel
            # 将子事件id归零
            now_character_data.event.son_event_id = ""
            # 绘制子事件文本
            event_config = game_config.config_event[son_event_id]
            son_event_draw = draw_event_text_panel.DrawEventTextPanel(son_event_id,character_id, event_config.type)
            son_event_draw.draw()
            # 进行子事件结算
            change_data = handle_event_data(son_event_id, character_id, add_time, change_data, now_time)

    # target_data = game_type.Character = cache.character_data[player_character_data.target_character_id]
    # print("target_data.name :",target_data.name)
    # 注释掉了会按不交流的时间自动扣好感的系统#
    # change_character_favorability_for_time(character_id, now_time)
    # 注释掉了社交关系#
    # change_character_social(character_id, status_data)
    now_judge = False
    exchange_flag = False # 玩家和NPC输出互换的flag
    PC_information_flag = 0  # 0初始，1PC输出，2不输出
    # NPC触发且不和玩家在同一地图时则跳过
    if character_id != 0 and now_character_data.position != player_character_data.position:
        return
    # 当NPC对玩家交互时，互相替换双方的输出内容
    if character_id != 0 and now_character_data.target_character_id == 0:
        exchange_flag = True
        change_data.target_change.setdefault(0, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[0]
        target_change.target_change[character_id] = change_data

        # 开始互换
        # print(f"debug 前target_change.hit_point = {target_change.hit_point}")
        change_data, target_change = target_change, change_data
        now_character_data, target_data = player_character_data, now_character_data
        character_id = 0
        # print(f"debug 后target_change.hit_point = {target_change.hit_point}")
    # elif character_id:
    #     return
    if change_data is None:
        return
    if change_data.mana_point:
        now_judge = True
        PC_information_flag = 1
    if change_data.hit_point:
        now_judge = True
        PC_information_flag = 1
    if change_data.eja_point:
        now_judge = True
        PC_information_flag = 1
    if len(change_data.status_data):
        now_judge = True
    if len(change_data.experience):
        now_judge = True
        PC_information_flag = 1
    if len(change_data.target_change) and not character_id:
        for target_character_id in change_data.target_change:
            # print(f"debug target_now_judge,character_id = {character_id},target_character_id = {target_character_id}")
            if character_id == target_character_id:
                continue
            else:
                now_judge = True
                PC_information_flag = 1 if PC_information_flag == 1 else 2
                break
    if now_judge:
        # print(f"debug now_judge")
        now_text_list = []
        if character_id == 0:
            now_text = "\n" + now_character_data.name + now_character_data.nick_name + ": "
        else:
            now_text = "\n" + now_character_data.name + ": "
            # 如果角色有口上颜色的话，则按口上颜色输出富文本的角色名
            if now_character_data.text_color:
                color_name = now_character_data.name
                now_text = f"\n<{color_name}>{now_character_data.name}:</{color_name}>"

        # 体力/气力/射精/理智的结算输出
        if change_data.hit_point and round(change_data.hit_point, 2) != 0:
            now_text += "\n  <hp_point>" + _("体力") + "　"*4 + text_handle.number_to_symbol_string(int(change_data.hit_point)) + "</hp_point>"
        if change_data.mana_point and round(change_data.mana_point, 2) != 0:
            now_text += "\n  <mp_point>" + _("气力") + "　"*4 + text_handle.number_to_symbol_string(int(change_data.mana_point)) + "</mp_point>"
        if change_data.eja_point and round(change_data.eja_point, 2) != 0:
            now_text += "\n  <semen>" + _("射精欲") + "　"*3 + text_handle.number_to_symbol_string(int(change_data.eja_point)) + "</semen>"
        if change_data.sanity_point and round(change_data.sanity_point, 2) != 0:
            now_text += "\n  <sanity>" + _("理智") + "　"*4 + text_handle.number_to_symbol_string(int(change_data.sanity_point)) + "</sanity>"

        # 状态的结算输出
        if len(change_data.status_data) and not exchange_flag:
            # 获取排序后的状态列表，按 type 排序（快感 type==0 在前）
            resort_state_list = [
                status_id
                for status_id in game_config.config_character_state
                if status_id in change_data.status_data and change_data.status_data[status_id] != 0
            ]
            resort_state_list.sort(key=lambda sid: game_config.config_character_state[sid].type)
            # 遍历排序后的状态列表进行输出
            for status_id in resort_state_list:
                # 获取状态对应的富文本颜色
                color_text = rich_text.get_chara_state_rich_color(status_id)
                now_text += f"\n  <{color_text}>"
                state_name = game_config.config_character_state[status_id].name
                # 快感则增加快感文字
                if game_config.config_character_state[status_id].type == 0:
                    state_name += _("快感")
                # 补全对齐
                state_name = f"{state_name.ljust(6,'　')}"
                now_text += (
                    state_name + 
                    attr_text.get_value_text(int(change_data.status_data[status_id]))
                )
                # 获取新旧状态等级
                new_state_level = attr_calculation.get_status_level(now_character_data.status_data[status_id])
                old_state_level = attr_calculation.get_status_level(now_character_data.status_data[status_id] - change_data.status_data[status_id])
                # 如果状态等级有变化则显示
                if new_state_level != old_state_level:
                    now_text += f" (lv{old_state_level}->{new_state_level})"
                now_text += f"</{color_text}>"

        # 经验的结算输出
        if len(change_data.experience):
            for experience_id in change_data.experience:
                experience_name = f"{game_config.config_experience[experience_id].name.ljust(6,'　')}"
                now_text += (
                    f"\n  <medium_spring_green>{experience_name}{attr_text.get_value_text(int(change_data.experience[experience_id]))}</medium_spring_green>"
                )

        # 非常见结算输出
        # if status_data.money:
        #     now_text_list.extend(
        #         [
        #             _("\n\n  获得龙门币:")
        #             + text_handle.number_to_symbol_string(status_data.money)
        #         ]
        #     )

        # 最后补个回车
        if now_text != "":
            now_text += "\n"

        if PC_information_flag == 1 and cache.all_system_setting.draw_setting[6] == 1:
            now_text_list.append(now_text)

        # 交互对象的结算输出
        if len(change_data.target_change):
            for target_character_id in change_data.target_change:
                # print(f"debug target_now_judge,character_id = {character_id},target_character_id = {target_character_id}")
                if character_id and target_character_id:
                    continue
                # 当NPC对玩家交互时，直接使用互相替换完的双方数据
                judge = 0
                if not exchange_flag:
                    target_change: game_type.TargetChange = change_data.target_change[target_character_id]
                    target_data: game_type.Character = cache.character_data[target_character_id]
                else:
                    judge = 1
                name = f"\n{target_data.name}"
                # 输出口上颜色的角色名
                color_name = 'standard'
                if target_data.text_color:
                    color_name = target_data.name
                name = f"\n<{color_name}>{target_data.name}</{color_name}>"
                # 输出无意识状态的提示信息
                now_unconscious_h = target_data.sp_flag.unconscious_h
                if now_unconscious_h:
                    # 催眠颜色
                    if handle_premise.handle_unconscious_hypnosis_flag(target_character_id):
                        unconscious_color = hypnosis_panel.get_hypnosis_degree_color(target_data.hypnosis.hypnosis_degree)
                    # 非催眠颜色
                    else:
                        unconscious_color = rich_text.get_chara_unconscious_rich_color(now_unconscious_h)
                    name += f"<{unconscious_color}>"
                    name += (" ({0}) ").format(hypnosis_panel.unconscious_list[now_unconscious_h])
                    name += f"</{unconscious_color}>"
                # 完整角色名抬头
                now_text = name + f"<{color_name}>:</{color_name}>"

                # 体力/气力/好感/信赖/催眠度的结算输出
                if target_change.hit_point and round(target_change.hit_point, 2) != 0:
                    now_text += _("\n  <hp_point>") + _("体力") + "　"*4 + text_handle.number_to_symbol_string(int(target_change.hit_point)) + "</hp_point>"
                    judge = 1
                if target_change.mana_point and round(target_change.mana_point, 2) != 0:
                    now_text += "\n  <mp_point>" + _("气力") + "　"*4 + text_handle.number_to_symbol_string(int(target_change.mana_point)) + "</mp_point>"
                    judge = 1
                if target_change.favorability:
                    now_text += "\n  <light_pink>" + _("好感") + "　"*4 + text_handle.number_to_symbol_string(int(target_change.favorability)) + "</light_pink>"
                    judge = 1
                if target_change.trust:
                    now_text += "\n  <summer_green>" + _("信赖") + "　"*4 + text_handle.number_to_symbol_string(float(format(target_change.trust, '.2f'))) + "%</summer_green>"
                    judge = 1
                if target_change.hypnosis_degree:
                    hypnosis_color = hypnosis_panel.get_hypnosis_degree_color(target_data.hypnosis.hypnosis_degree)
                    now_text += f"\n  <{hypnosis_color}>" + _("催眠度") + "　"*3 + text_handle.number_to_symbol_string(float(format(target_change.hypnosis_degree, '.1f'))) + f"%</{hypnosis_color}>"
                    judge = 1
                # if target_change.new_social != target_change.old_social:
                #     now_text += (
                #         " "
                #         + game_config.config_social_type[target_change.old_social].name
                #         + "->"
                #         + game_config.config_social_type[target_change.new_social].name
                #     )
                #     judge = 1
                # 状态的结算输出
                if len(target_change.status_data):
                    # 获取排序后的状态列表，按 type 排序（快感 type==0 在前）
                    resort_state_list = [
                        status_id
                        for status_id in game_config.config_character_state
                        if status_id in target_change.status_data and target_change.status_data[status_id] != 0
                    ]
                    resort_state_list.sort(key=lambda sid: game_config.config_character_state[sid].type)
                    # 遍历排序后的状态列表进行输出
                    for status_id in resort_state_list:
                        # 获取状态对应的富文本颜色
                        color_text = rich_text.get_chara_state_rich_color(status_id)
                        now_text += f"\n  <{color_text}>"
                        state_name = game_config.config_character_state[status_id].name
                        # 快感则增加快感文字
                        if game_config.config_character_state[status_id].type == 0:
                            state_name += _("快感")
                        # 补全对齐
                        state_name = f"{state_name.ljust(6,'　')}"
                        now_text += (
                            state_name + 
                            text_handle.number_to_symbol_string(int(target_change.status_data[status_id]))
                        )
                        # 获取新旧状态等级
                        new_state_level = attr_calculation.get_status_level(target_data.status_data[status_id])
                        old_state_level = attr_calculation.get_status_level(target_data.status_data[status_id] - target_change.status_data[status_id])
                        # 如果状态等级有变化则显示
                        if new_state_level != old_state_level:
                            now_text += f" (lv{old_state_level}->{new_state_level})"
                        now_text += f"</{color_text}>"
                        judge = 1
                # 经验的结算输出
                if len(target_change.experience):
                    for experience_id in target_change.experience:
                        if target_change.experience[experience_id]:
                            experience_name = f"{game_config.config_experience[experience_id].name.ljust(6,'　')}"
                            now_text += (
                                    "\n  <medium_spring_green>"
                                    + experience_name
                                    + text_handle.number_to_symbol_string(
                                int(target_change.experience[experience_id])
                            )
                                    + "</medium_spring_green>"
                            )
                            judge = 1
                if judge and (now_text != name) and cache.all_system_setting.draw_setting[7] == 1:
                    now_text_list.append(now_text)
        if add_time > 0:
            if not exchange_flag:
                now_text_time = _("\n\n {0}分钟过去了\n").format(str(add_time))
            else:
                now_text_time = _("\n\n 该行动将持续{0}分钟\n").format(str(add_time))
        else:
            now_text_time = "\n"
        if now_text_list:
            now_text_list.append(now_text_time)
        # now_panel = panel.LeftDrawTextListPanel()
        now_text = "".join(now_text_list)
        now_panel = rich_text.get_rich_text_draw_panel(now_text)
        now_panel.width = width
        now_panel.column = 8
        # now_panel.draw()
        # line = draw.LineDraw("-", width)
        # line.draw()
        # wait_draw = draw.WaitDraw()
        # wait_draw.draw()
        return now_panel


def handle_instruct_data(
        character_id: int,
        behavior_id: str,
        now_time: datetime.datetime,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        ):
    """
    处理指令数据
    Keyword arguments:
    character_id -- 角色id
    behavior_id -- 行动id
    now_time -- 结算时间
    add_time -- 行动已经过时间
    change_data -- 状态变更信息记录对象
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    # 进行一段结算
    if behavior_id in game_config.config_behavior_effect_data:
        # 先结算口上，并判断是否需要跳过，跳过来源于事件的特殊结算
        if now_character_data.event.skip_instruct_talk == False:
            talk.handle_talk(character_id)
        else:
            now_character_data.event.skip_instruct_talk = False
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            # 综合数值结算判定
            # 如果effect_id是str类型，则说明是综合数值结算
            if isinstance(effect_id, str) and "CVE" in effect_id:
                effect_all_value_list = effect_id.split("_")[1:]
                handle_comprehensive_value_effect(character_id, effect_all_value_list, change_data)
            else:
                if effect_id not in constant.settle_behavior_effect_data:
                    print(f"error 不存在的结算 = {effect_id}")
                    continue
                constant.settle_behavior_effect_data[effect_id](character_id, add_time, change_data, now_time)
        # 如果是对他人的行为，则将自己的id与行动结束时间记录到对方的数据中
        if now_character_data.target_character_id != character_id:
            end_time = game_time.get_sub_date(minute=now_character_data.behavior.duration, old_date=now_character_data.behavior.start_time)
            target_character_data: game_type.Character = cache.character_data[now_character_data.target_character_id]
            target_character_data.action_info.interacting_character_end_info = [character_id, end_time]
        # 娱乐和工作类的指令则进行一次设施损坏检测
        if behavior_id in game_config.config_behavior:
            behavior_data = game_config.config_behavior[behavior_id]
            if _('娱乐') in behavior_data.tag or _('工作') in behavior_data.tag:
                constant.settle_behavior_effect_data[1751](character_id, add_time, change_data, now_time)
    # 进行二段结算
    second_behavior.check_second_effect(character_id, change_data)
    # 如果是玩家对NPC的行为，则额外进行对方的二段结算
    if character_id == 0 and now_character_data.target_character_id != 0:
        target_change: game_type.TargetChange = change_data.target_change[now_character_data.target_character_id]
        second_behavior.check_second_effect(now_character_data.target_character_id, target_change, pl_to_npc = True)
    # 进行额外经验结算
    extra_exp_settle(character_id, change_data)
    return change_data


def handle_event_data(event_id, character_id, add_time, change_data, now_time):
    """
    处理事件数据
    Keyword arguments:
    event_id -- 事件id
    character_id -- 角色id
    add_time -- 行动已经过时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算时间
    """
    if event_id != "":
        # 进行事件结算
        # print(f"debug handle_settle_behavior event_id = {event_id}")
        event_data: game_type.Event = game_config.config_event[event_id]
        for effect in event_data.effect:
            # 综合数值结算判定
            if "CVE" in effect:
                effect_all_value_list = effect.split("_")[1:]
                handle_comprehensive_value_effect(character_id, effect_all_value_list, change_data)
            # 综合指令状态结算判定
            elif "CSE" in effect:
                effect_all_value_str = effect.split("_", 1)[1]
                A = effect_all_value_str.split("_", 1)[0]
                behavior_id = effect_all_value_str.split("_", 1)[1]
                effect_all_value_list = [A, behavior_id]
                handle_instruct.handle_comprehensive_state_effect(effect_all_value_list, character_id, add_time, change_data, now_time)
            # 其他结算判定
            else:
                constant.settle_behavior_effect_data[int(effect)](
                    character_id, add_time, change_data, now_time
                )
    return change_data


def add_settle_behavior_effect(behavior_effect_id: int):
    """
    添加行为结算处理
    Keyword arguments:
    behavior_id -- 行为id
    """

    def decorator(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.settle_behavior_effect_data[behavior_effect_id] = return_wrapper
        return return_wrapper

    return decorator


def add_settle_second_behavior_effect(second_behavior_effect_id: int):
    """
    添加二段行为结算处理
    Keyword arguments:
    second_behavior_effect_id -- 二段行为id
    """

    def decorator(func):
        @wraps(func)
        def return_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        constant.settle_second_behavior_effect_data[second_behavior_effect_id] = return_wrapper
        return return_wrapper

    return decorator


def get_cut_down_favorability_for_consume_time(consume_time: int):
    """
    从经过的时间计算出扣除的好感度
    Keyword arguments:
    consume_time -- 经过时间
    """
    if consume_time < 10:
        return consume_time
    elif 10 <= consume_time < 100:
        return (consume_time - 9) * 10 + 9
    elif 100 <= consume_time < 1000:
        return (consume_time - 99) * 100 + 909
    else:
        return (consume_time - 999) * 1000 + 90909


# def change_character_favorability_for_time(character_id: int, now_time: datetime.datetime):
#     """
#     按最后社交时间扣除角色好感度
#     Keyword arguments:
#     character_id -- 角色id
#     now_time -- 当前时间
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     for now_character in character_data.favorability:
#         if character_data.favorability[now_character] <= 500:
#             continue
#         character_data.social_contact_last_time.setdefault(now_character, now_time)
#         last_add_time: datetime.datetime = character_data.social_contact_last_time[now_character]
#         now_consume_time = int((now_time - last_add_time).seconds / 60)
#         if now_consume_time < 60:
#             continue
#         now_cut_down = get_cut_down_favorability_for_consume_time(int(now_consume_time / 60))
#         if now_character in character_data.social_contact_last_cut_down_time:
#             last_cut_down_time: datetime.datetime = character_data.social_contact_last_cut_down_time[
#                 now_character
#             ]
#             old_consume_time = int((last_cut_down_time - last_add_time).seconds / 60)
#             old_cut_down = get_cut_down_favorability_for_consume_time(int(old_consume_time / 60))
#             now_cut_down -= old_cut_down
#         character_data.favorability[now_character] -= now_cut_down
#         if character_data.favorability[now_character] < 0:
#             character_data.favorability[now_character] = 0
#         # change_character_social_now(now_character, character_id)


def change_character_talkcount_for_time(character_id: int, now_time: datetime.datetime):
    """
    结算上次进行聊天的时间，以重置聊天计数器
    Keyword arguments:
    character_id -- 角色id
    now_time -- 当前时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[character_data.target_character_id]
    if not target_data.action_info.talk_time:
        target_data.action_info.talk_time = now_time
    if now_time.day == target_data.action_info.talk_time.day and now_time.hour > target_data.action_info.talk_time.hour:
        target_data.action_info.talk_count -= now_time.hour - target_data.action_info.talk_time.hour
        target_data.action_info.talk_time = now_time
        # print("检测到时间前进了至少一小时，聊天计数器-1")
    elif now_time.day != target_data.action_info.talk_time.day:
        target_data.action_info.talk_count = 0
        target_data.action_info.talk_time = now_time
        # print("检测到时间前进了至少一天，聊天计数器归零")
    if target_data.action_info.talk_count < 0:
        target_data.action_info.talk_count = 0
    # print("target_data.action_info.talk_count :",target_data.action_info.talk_count)



# def change_character_social(character_id: int, change_data: game_type.CharacterStatusChange):
#     """
#     处理角色关系变化
#     Keyword argumenys:
#     character_id -- 状态变化数据所属角色id
#     change_data -- 状态变化数据
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     for now_character in change_data.target_change:
#         change_character_social_now(character_id, now_character, change_data)


# def change_character_social_now(
#     character_id: int,
#     target_id: int,
#     change_data: game_type.CharacterStatusChange = game_type.CharacterStatusChange(),
# ):
#     """
#     执行角色关系变化
#     Keyword arguments:
#     character_id -- 状态变化数据所属角色id
#     target_id -- 关系变化角色id
#     change_data -- 状态变化数据
#     """
#     if target_id in change_data.target_change:
#         target_change: game_type.TargetChange = change_data.target_change[target_id]
#     target_data: game_type.Character = cache.character_data[target_id]
#     old_social = 0
#     new_social = 0
#     if character_id in target_data.social_contact_data:
#         old_social = target_data.social_contact_data[character_id]
#     target_data.favorability.setdefault(character_id, 0)
#     now_favorability = target_data.favorability[character_id]
#     new_social = get_favorability_social(now_favorability)
#     if new_social != old_social:
#         if target_id in change_data.target_change:
#             target_change.old_social = old_social
#             target_change.new_social = new_social
#         target_data.social_contact.setdefault(old_social, set())
#         target_data.social_contact.setdefault(new_social, set())
#         if character_id in target_data.social_contact[old_social]:
#             target_data.social_contact[old_social].remove(character_id)
#         target_data.social_contact[new_social].add(character_id)
#         target_data.social_contact_data[character_id] = new_social


def get_favorability_social(favorability: int) -> int:
    """
    获取好感度对应社交关系
    Keyword arguments:
    favorability -- 好感度
    Return arguments:
    int -- 社交关系
    """
    if favorability < 500:
        return 0
    elif favorability < 10000:
        return 1
    elif favorability < 200000:
        return 2
    elif favorability < 4000000:
        return 3
    elif favorability < 80000000:
        return 4
    return 5

def extra_exp_settle(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
):
    """
    处理额外经验结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # 导入常用结算函数，避免循环导入
    from Script.Settle.common_default import base_chara_experience_common_settle

    character_data: game_type.Character = cache.character_data[character_id]

    # 自己在H中且群交已开启，则群交经验+1
    if handle_premise.handle_self_is_h(character_id) and handle_premise.handle_group_sex_mode_on(character_id):
        base_chara_experience_common_settle(0, 56, change_data=change_data)

    # 玩家隐奸中，猥亵或性爱指令，且非等待，则隐奸经验+1
    if character_id == 0 and handle_premise.handle_hidden_sex_mode_ge_1(character_id):
        # 获取当前行为
        now_behavior_id = character_data.behavior.behavior_id
        behavior_data = game_config.config_behavior[now_behavior_id]
        # 猥亵或性爱指令
        add_flag = False
        for tag in {_("猥亵"), _("性爱")}:
            if tag in behavior_data.tag:
                add_flag = True
                break
        # 非等待
        if now_behavior_id == constant.Behavior.WAIT:
            add_flag = False
        # 增加隐奸经验
        if add_flag:
            base_chara_experience_common_settle(0, 35, change_data=change_data)
            base_chara_experience_common_settle(0, 35, target_flag=True, change_data=change_data)


def handle_comprehensive_value_effect(character_id: int, effect_all_value_list: list, change_data: game_type.CharacterStatusChange = game_type.CharacterStatusChange()) -> int:
    """
    综合型基础数值结算
    Keyword arguments:
    character_id -- 角色id
    effect_all_value_list -- 结算的各项数值
    change_data -- 结算信息记录对象
    Return arguments:
    bool -- 是否结算成功
    """
    # 导入常用结算函数，避免循环导入
    from Script.Settle.common_default import base_chara_experience_common_settle, base_chara_climix_common_settle
    from Script.UI.Panel import event_option_panel
    from Script.Design import character

    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"debug character_id = {character_id}, effect_all_value_list = {effect_all_value_list}")

    # 进行主体A的判别，A1为自己，A2为交互对象，A3为指定id角色(格式为A3|15)
    if effect_all_value_list[0] == "A1":
        final_character_data = character_data
        final_change_data = change_data
        final_character_id = character_id
    elif effect_all_value_list[0] == "A2":
        # 如果没有交互对象，则返回0
        if character_data.target_character_id == character_id:
            return 0
        final_character_data = cache.character_data[character_data.target_character_id]
        change_data.target_change.setdefault(character_data.target_character_id, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[character_data.target_character_id]
        final_change_data = target_change
        final_character_id = character_data.target_character_id
    elif effect_all_value_list[0][:2] == "A3":
        final_character_adv = int(effect_all_value_list[0][3:])
        final_character_id = character.get_character_id_from_adv(final_character_adv)
        # 如果还没拥有该角色，则返回0
        if final_character_id not in cache.npc_id_got:
            return 0
        final_character_data = cache.character_data[final_character_id]

    # 进行数值B的判别,A能力,T素质,J宝珠,E经验,S状态,F好感度,X信赖
    if len(effect_all_value_list[1]) > 1:
        type_son_id = int(effect_all_value_list[1].split("|")[1])

    # 创建一个字典来映射属性名
    attribute_mapping = {
        "A": "ability",
        "T": "talent",
        "J": "juel",
        "E": "experience",
        "S": "status_data",
        "F": "favorability",
        "X": "trust",
        "Flag": "flag",
        "Climax": "climax",
        "Father": "father",
        "ChangeTargetId": "change_target_id",
        "Move": "move",
    }
    
    # 创建一个字典来映射操作
    operation_mapping = {
        "G": lambda x, y: x + y,
        "L": lambda x, y: x - y,
        "E": lambda x, y: y,
        "寻路": None,
        "瞬移": None,
    }
    
    # 获取属性名和操作
    if "|" in effect_all_value_list[1]:
        attribute = effect_all_value_list[1].split("|")[0]
    else:
        attribute = effect_all_value_list[1][0]
    operation = effect_all_value_list[2]
    
    # 检查属性名和操作是否在映射字典中
    if attribute in attribute_mapping and operation in operation_mapping:
        # 获取属性和操作
        attribute_name = attribute_mapping[attribute]
        operation_func = operation_mapping[operation]
        # print(f"debug attribute_name = {attribute_name}, operation = {operation}")
    
        # 特殊处理
        # 好感
        if attribute_name == "favorability":
            final_character_data.favorability[0] = operation_func(final_character_data.favorability[0], int(effect_all_value_list[3]))
        # 信赖
        elif attribute_name == "trust":
            final_character_data.trust = operation_func(final_character_data.trust, int(effect_all_value_list[3]))
        # 经验
        elif attribute_name == "experience" and operation in ["G", "L"]:
            exp_value = int(effect_all_value_list[3])
            if operation == "L":
                exp_value = -int(effect_all_value_list[3])
            base_chara_experience_common_settle(final_character_id, type_son_id, base_value = exp_value, change_data = final_change_data)
        # 角色口上flag
        elif attribute_name == "flag":
            final_character_data.author_flag.chara_int_flag_dict.setdefault(type_son_id, 0)
            final_character_data.author_flag.chara_int_flag_dict[type_son_id] = operation_func(final_character_data.author_flag.chara_int_flag_dict[type_son_id], int(effect_all_value_list[3]))
        # 绝顶
        elif attribute_name == "climax":
            if operation == "E":
                base_chara_climix_common_settle(final_character_id, type_son_id, degree = int(effect_all_value_list[3]))
            elif operation == "G":
                for i in range(int(effect_all_value_list[3]) + 1):
                    base_chara_climix_common_settle(final_character_id, type_son_id, degree = i)
        # 父子嵌套事件
        elif attribute_name == "father":
            # print(f"debug effect_all_value_list = {effect_all_value_list}")
            now_draw = event_option_panel.multi_layer_event_option_Panel(character_id, width, type_son_id, int(effect_all_value_list[3]))
            now_draw.draw()
        # 指定角色id为交互对象
        elif attribute_name == "change_target_id":
            # 检查目标角色是否与自己位于同一位置
            if character_data.position == final_character_data.position:
                character_data.target_character_id = final_character_id
                return 1
            return 0
        # 移动
        elif attribute_name == "move":
            from Script.Design import map_handle, character_move
            from Script.StateMachine import default
            # 获取目标地点的tag
            # 将序号3及之后的effect_all_value_list拼回一个str，中间用_连接
            move_tag = "_".join(effect_all_value_list[3:])
            if move_tag in constant.place_data:
                # 获取目标地点的系统路径
                to_place = map_handle.get_map_system_path_for_str(
                    random.choice(constant.place_data[move_tag])
                )
                # 判断是寻路移动还是瞬移
                if operation == "寻路":
                    # 玩家进行寻路移动
                    if final_character_id == 0:
                        character_move.own_charcter_move(to_place)
                    # NPC进行寻路移动
                    else:
                        default.general_movement_module(final_character_id, to_place)
                elif operation == "瞬移":
                    # 调用map_handle的character_move_scene方法，输入旧、新地点路径和角色id
                    map_handle.character_move_scene(final_character_data.position, to_place, final_character_id)
                return 1
            return 0
        else:
            # 对属性进行操作

            # 获取属性值
            attribute_value = getattr(final_character_data, attribute_name)
            # 对属性值进行操作
            attribute_value[type_son_id] = operation_func(attribute_value[type_son_id], int(effect_all_value_list[3]))
            # 将操作后的属性值重新设置到对象上
            setattr(final_character_data, attribute_name, attribute_value)

            # 记录结算数据
            if attribute_name not in ["flag", "talent"]:
                change_data_attribute_value = getattr(final_change_data, attribute_name)
                # 如果attribute_name没有type_son_id则创建一个
                change_data_attribute_value.setdefault(type_son_id, 0)
                change_data_attribute_value[type_son_id] = operation_func(change_data_attribute_value[type_son_id], int(effect_all_value_list[3]))
                setattr(final_change_data, attribute_name, change_data_attribute_value)

            # final_character_data[attribute_name][type_son_id] = operation_func(final_character_data[attribute_name][type_son_id], int(effect_all_value_list[3]))

        return 1

    return 0

