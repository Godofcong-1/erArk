import datetime
import random
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type, get_text, text_handle
from Script.Design import attr_text, attr_calculation, handle_premise, handle_instruct, talk
from Script.UI.Moudle import panel, draw
from Script.Config import game_config, normal_config
from Script.UI.Panel import ejaculation_panel, originium_arts

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """


def handle_settle_behavior(character_id: int, now_time: datetime.datetime, instruct_flag = 1):
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
    if instruct_flag > 0:
        # 玩家在群P模式的结算
        if character_id == 0 and handle_premise.handle_group_sex_mode_on:
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
        # 正常情况下则直接执行结算
        else:
            # 进行指令相关数据的结算
            change_data = handle_instruct_data(character_id, behavior_id, now_time, add_time, change_data)

    if instruct_flag != 1:
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
        now_draw = draw.NormalDraw()
        if character_id == 0:
            now_draw.text = "\n" + now_character_data.name + now_character_data.nick_name + ": "
        else:
            now_draw.text = "\n" + now_character_data.name + ": "
        now_draw.width = width
        # now_draw.draw()
        if PC_information_flag == 1:
            now_text_list.append(now_draw.text)

        # 体力/气力/射精/理智的结算输出
        if change_data.hit_point and round(change_data.hit_point, 2) != 0:
            now_text_list.append(
                _("\n  体力") + text_handle.number_to_symbol_string(int(change_data.hit_point))
            )
        if change_data.mana_point and round(change_data.mana_point, 2) != 0:
            now_text_list.append(
                _("\n  气力") + text_handle.number_to_symbol_string(int(change_data.mana_point))
            )
        if change_data.eja_point and round(change_data.eja_point, 2) != 0:
            now_text_list.append(
                _("\n  射精") + text_handle.number_to_symbol_string(int(change_data.eja_point))
            )
        if change_data.sanity_point and round(change_data.sanity_point, 2) != 0:
            now_text_list.append(
                _("\n  理智") + text_handle.number_to_symbol_string(int(change_data.sanity_point))
            )

        # 状态的结算输出
        if len(change_data.status_data) and not exchange_flag:
            now_text_list.extend(
                [
                    f"\n  {game_config.config_character_state[i].name}{attr_text.get_value_text(int(change_data.status_data[i]))}"
                    for i in change_data.status_data
                ]
            )

        # 经验的结算输出
        if len(change_data.experience):
            now_text_list.extend(
                [
                    _("\n  ")
                    + game_config.config_experience[i].name
                    + text_handle.number_to_symbol_string(change_data.experience[i])
                    for i in change_data.experience
                ]
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
        if now_text_list != []:
            now_text_list.extend("\n")

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
                # 输出无意识状态的提示信息
                if target_data.sp_flag.unconscious_h:
                    name += _("({0})").format(originium_arts.unconscious_list[target_data.sp_flag.unconscious_h])
                now_text = name + ":"

                # 体力/气力/好感/信赖/催眠度的结算输出
                if target_change.hit_point and round(target_change.hit_point, 2) != 0:
                    now_text += _("\n  体力") + text_handle.number_to_symbol_string(int(target_change.hit_point))
                    judge = 1
                if target_change.mana_point and round(target_change.mana_point, 2) != 0:
                    now_text += _("\n  气力") + text_handle.number_to_symbol_string(int(target_change.mana_point))
                    judge = 1
                if target_change.favorability:
                    now_text += _("\n  对{character_name}{character_nick_name}好感").format(
                        character_name=now_character_data.name,
                        character_nick_name=now_character_data.nick_name
                    ) + text_handle.number_to_symbol_string(int(target_change.favorability))
                    judge = 1
                if target_change.trust:
                    now_text += _("\n  对{character_name}{character_nick_name}信赖").format(
                        character_name=now_character_data.name,
                        character_nick_name=now_character_data.nick_name
                    ) + text_handle.number_to_symbol_string(float(format(target_change.trust, '.1f'))) + "%"
                    judge = 1
                if target_change.hypnosis_degree:
                    now_text += _("\n  催眠度") + text_handle.number_to_symbol_string(float(format(target_change.hypnosis_degree, '.1f'))) + "%"
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
                    for status_id in target_change.status_data:
                        if target_change.status_data[status_id]:
                            now_text += (
                                    "\n  "
                                    + game_config.config_character_state[status_id].name
                                    + text_handle.number_to_symbol_string(
                                int(target_change.status_data[status_id])
                            )
                            )
                            judge = 1
                # 经验的结算输出
                if len(target_change.experience):
                    for experience_id in target_change.experience:
                        if target_change.experience[experience_id]:
                            now_text += (
                                    "\n  "
                                    + game_config.config_experience[experience_id].name
                                    + text_handle.number_to_symbol_string(
                                int(target_change.experience[experience_id])
                            )
                            )
                            judge = 1
                if judge and (now_text != name):
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
        now_panel = panel.LeftDrawTextListPanel()
        now_panel.set(now_text_list, width, 8)
        # now_panel.draw()
        # line = draw.LineDraw("-", width)
        # line.draw()
        # wait_draw = draw.WaitDraw()
        # wait_draw.draw()
        return now_panel


def handle_instruct_data(
        character_id: int,
        behavior_id: int,
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
        # 先结算口上
        talk.handle_talk(character_id)
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            constant.settle_behavior_effect_data[effect_id](character_id, add_time, change_data, now_time)
    # 进行二段结算
    check_second_effect(character_id, change_data)
    # 如果是玩家对NPC的行为，则额外进行对方的二段结算
    if character_id == 0 and now_character_data.target_character_id != 0:
        target_change: game_type.TargetChange = change_data.target_change[now_character_data.target_character_id]
        check_second_effect(now_character_data.target_character_id, target_change, pl_to_npc = True)
    # 进行无意识结算
    check_unconscious_effect(character_id, add_time, change_data, now_time)
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
                effect_all_value_list = effect.split("_")[1:]
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


def change_character_favorability_for_time(character_id: int, now_time: datetime.datetime):
    """
    按最后社交时间扣除角色好感度
    Keyword arguments:
    character_id -- 角色id
    now_time -- 当前时间
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for now_character in character_data.favorability:
        if character_data.favorability[now_character] <= 500:
            continue
        character_data.social_contact_last_time.setdefault(now_character, now_time)
        last_add_time: datetime.datetime = character_data.social_contact_last_time[now_character]
        now_consume_time = int((now_time - last_add_time).seconds / 60)
        if now_consume_time < 60:
            continue
        now_cut_down = get_cut_down_favorability_for_consume_time(int(now_consume_time / 60))
        if now_character in character_data.social_contact_last_cut_down_time:
            last_cut_down_time: datetime.datetime = character_data.social_contact_last_cut_down_time[
                now_character
            ]
            old_consume_time = int((last_cut_down_time - last_add_time).seconds / 60)
            old_cut_down = get_cut_down_favorability_for_consume_time(int(old_consume_time / 60))
            now_cut_down -= old_cut_down
        character_data.favorability[now_character] -= now_cut_down
        if character_data.favorability[now_character] < 0:
            character_data.favorability[now_character] = 0
        # change_character_social_now(now_character, character_id)


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


def check_second_effect(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
        pl_to_npc: bool = False,
):
    """
    处理第二结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    pl_to_npc -- 玩家对NPC的行为结算
    """
    # print("进入第二结算")
    orgasm_list = [i for i in range(1000, 1024)]
    mark_list = [i for i in range(1030, 1048)]
    item_list = [i for i in range(1100, 1199)]

    # 玩家检测自己
    if character_id == 0:
        character_data = cache.character_data[0]
        # 高潮结算
        orgasm_judge(character_id, change_data)
        # 道具结算
        item_effect(character_id)
        # 进行结算
        second_behavior_effect(character_id, change_data)
        # NPC的刻印结算
        change_data.target_change.setdefault(character_data.target_character_id, game_type.TargetChange())
        target_change: game_type.TargetChange = change_data.target_change[character_data.target_character_id]
        mark_effect(character_data.target_character_id, target_change)
        # 单独遍历结算刻印
        second_behavior_effect(character_data.target_character_id, target_change, mark_list)


    # NPC自己检测自己
    if character_id != 0:
        # 初见和每日招呼结算
        judge_character_first_meet(character_id)
        # 阴茎位置结算
        insert_position_effect(character_id)
        # 道具结算
        item_effect(character_id, pl_to_npc)
        # 单独遍历道具
        second_behavior_effect(character_id, change_data, item_list)
        # 高潮结算
        orgasm_judge(character_id, change_data)
        # 素质结算

        # 进行结算
        second_behavior_effect(character_id, change_data)

        # 刻印结算
        mark_effect(character_id, change_data)
        # 单独遍历结算刻印
        second_behavior_effect(character_id, change_data, mark_list)


def second_behavior_effect(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
        second_behavior_list: list = None,
        ):
    """
    触发二段行为的口上与效果
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    second_behavior_list -- 仅计算该范围内的二段行为id列表，默认为None
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 检测是否与玩家处于同一位置#
    if (
            character_data.position != cache.character_data[0].position
            and character_data.behavior.move_src != cache.character_data[0].position
    ):
        talk.must_show_talk_check(character_id)
        must_settle_check(character_id)
        return

    # 遍历二段行为id，进行结算
    for behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            if second_behavior_list and behavior_id not in second_behavior_list:
                continue
            # 触发二段行为的口上
            talk.handle_second_talk(character_id, behavior_id)
            # 遍历该二段行为的所有结算效果，挨个触发
            for effect_id in game_config.config_second_behavior_effect_data[behavior_id]:
                constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
            # print(f"debug {character_data.name}触发二段行为效果，behavior_id = {behavior_id}")
            # 触发后该行为值归零
            character_data.second_behavior[behavior_id] = 0


def must_settle_check(character_id: int):
    """
    检查是否有必须计算但不必须显示的空白结算
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    for second_behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            # print(f"debug 检测到{second_behavior_id}可能需要显示")
            # 需要有必须计算
            if 997 in game_config.config_second_behavior_effect_data[second_behavior_id]:
                # 遍历该二段行为的所有结算效果，挨个触发，但因为不在结算阶段，所以不会显示具体的结算数据
                change_data = game_type.CharacterStatusChange()
                for effect_id in game_config.config_second_behavior_effect_data[second_behavior_id]:
                    constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
                # 触发后该行为值归零
                character_data.second_behavior[second_behavior_id] = 0


def check_unconscious_effect(
        character_id: int,
        add_time: int,
        change_data: game_type.CharacterStatusChange,
        now_time: datetime.datetime,
):
    """
    处理无意识结算
    Keyword arguments:
    character_id -- 角色id
    add_time -- 行动已经过时间
    change_data -- 状态变更信息记录对象
    now_time -- 结算时间
    """

    character_data: game_type.Character = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    target_character_data: game_type.Character = cache.character_data[target_character_id]
    change_data.target_change.setdefault(target_character_data.cid, game_type.TargetChange())
    target_change: game_type.TargetChange = change_data.target_change[target_character_id]
    # target_change: game_type.TargetChange = status_data.target_change[target_character_id]
    # print()
    # print("进入无意识结算")

    # 玩家对交互目标进行结算
    if character_id == 0 and target_character_id != 0:
        # 目标处于无意识状态
        if handle_premise.handle_unconscious_flag_ge_1(target_character_id) or handle_premise.handle_self_time_stop_orgasm_relase(target_character_id):
            # 经验结算
            for experience_id in target_change.experience.copy():
                # 普通部位
                if experience_id in range(0, 8):
                    # 根据经验序号转化为对应的结算序号
                    effect_id = experience_id + 270
                    constant.settle_behavior_effect_data[effect_id](character_id, add_time, change_data, now_time)
                # 绝顶经验
                elif experience_id in range(10, 18):
                    constant.settle_behavior_effect_data[278](character_id, add_time, change_data, now_time)
                # 性交经验
                elif experience_id in range(61, 65):
                    constant.settle_behavior_effect_data[279](character_id, add_time, change_data, now_time)
                    # 睡姦经验与被睡姦经验
                    if handle_premise.handle_unconscious_flag_1(target_character_id):
                        constant.settle_behavior_effect_data[352](character_id, add_time, change_data, now_time)
                        constant.settle_behavior_effect_data[354](character_id, add_time, change_data, now_time)
                    # 催眠姦经验与被催眠姦经验
                    elif handle_premise.handle_unconscious_hypnosis_flag(target_character_id):
                        constant.settle_behavior_effect_data[358](character_id, add_time, change_data, now_time)
                        constant.settle_behavior_effect_data[360](character_id, add_time, change_data, now_time)
                    # 时姦经验与被时姦经验
                    elif handle_premise.handle_unconscious_flag_3(target_character_id) or handle_premise.handle_self_time_stop_orgasm_relase(target_character_id):
                        constant.settle_behavior_effect_data[355](character_id, add_time, change_data, now_time)
                        constant.settle_behavior_effect_data[357](character_id, add_time, change_data, now_time)

    return target_character_data.sp_flag.unconscious_h


def judge_character_first_meet(character_id: int) -> int:
    """
    判断初见和每日招呼\n
    Keyword arguments:
    character_id -- 角色id\n
    Return arguments:
    bool -- 本次update时间切片内活动是否已完成
    """
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]

    # 需要状态6正常，且不是睡觉状态
    if handle_premise.handle_normal_6(character_id) and handle_premise.handle_action_not_sleep(character_id):
        # 优先输出初见，次要输出每日招呼
        if character_data.first_record.first_meet and character_data.position == pl_character_data.position:
            character_data.second_behavior[1331] = 1
            character_data.first_record.first_meet = 0
            character_data.first_record.day_first_meet = 0
        elif character_data.first_record.day_first_meet and character_data.position == pl_character_data.position:
            # 如果是要早安问候的助理，则不每日招呼
            if handle_premise.handle_assistant_morning_salutation_on(character_id):
                pass
            else:
                character_data.second_behavior[1332] = 1
            character_data.first_record.day_first_meet = 0
            # 判断上交内裤与袜子
            if handle_premise.handle_wear_socks(character_id) and handle_premise.handle_ask_give_pan_everyday(character_id):
                character_data.second_behavior[1455] = 1
            if handle_premise.handle_wear_pan(character_id) and handle_premise.handle_ask_give_socks_everyday(character_id):
                character_data.second_behavior[1456] = 1


def insert_position_effect(character_id: int):
    """
    处理第二结算中的阴茎位置结算
    Keyword arguments:
    character_id -- 角色id
    """

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    # 非群交模式，当前有阴茎插入、当前位置为玩家位置
    if (
        handle_premise.handle_group_sex_mode_off(character_id) and
        character_data.h_state.insert_position != -1 and
        character_data.position == pl_character_data.position
        ):
        # 身体部位与服装部位通用均为+1200
        position_index = 1201 + character_data.h_state.insert_position
        character_data.second_behavior[position_index] = 1


def orgasm_judge(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    判断第二结算中的高潮，都发生哪些高潮，各多少次
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    # print()
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"进入{character_data.name}的高潮结算")

    # 检测射精
    if character_id == 0:
        if character_data.eja_point >= character_data.eja_point_max:
            # 如果已经没有精液了则只能进行普通射精
            if handle_premise.handle_pl_semen_le_2(0):
                character_data.second_behavior[1009] = 1
            else:
                # 忍住射精
                endure_flag = ejaculation_panel.show_endure_ejaculation_panel()
                if endure_flag:
                    return
                # 普
                if character_data.h_state.endure_not_shot_count == 0:
                    character_data.second_behavior[1009] = 1
                # 超强
                elif character_data.h_state.endure_not_shot_count >= 4:
                    character_data.second_behavior[1011] = 1
                # 强
                else:
                    character_data.second_behavior[1010] = 1
            character_data.eja_point = 0
            now_draw = ejaculation_panel.Ejaculation_Panel(width)
            now_draw.draw()
            line = draw.LineDraw("-", width)
            line.draw()
    else:
        normal_orgasm_dict = {}  # 高潮结算字典
        extra_orgasm_dict = {}  # 额外高潮结算字典
        un_count_orgasm_dict = {}  # 不计数高潮结算字典
        for orgasm in range(8):
            # 跳过射精槽
            if orgasm == 3:
                continue
            # 10级前检测人物的各感度数据是否等于该人物的高潮记录程度数据
            # now_data -- 当前高潮程度
            # pre_data -- 记录里的前高潮程度
            # un_count_data -- 不计数的本次临时高潮数
            # extra_add -- 额外高潮次数
            now_data = attr_calculation.get_status_level(character_data.status_data[orgasm])
            pre_data = character_data.h_state.orgasm_level[orgasm]
            un_count_data = 0
            extra_add = 0
            # 字典初始化
            normal_orgasm_dict[orgasm] = 0
            extra_orgasm_dict[orgasm] = 0
            un_count_orgasm_dict[orgasm] = 0
            # 饮精绝顶
            if orgasm == 0 and character_data.talent[31]:
                if character_data.h_state.shoot_position_body in [2, 15]:
                    un_count_data += 1
            un_count_orgasm_dict[orgasm] = un_count_data
            # 如果已经到了10级，则进行额外高潮结算
            if pre_data >= 10:
                character_data.h_state.extra_orgasm_feel.setdefault(orgasm, 0)
                change_data.status_data.setdefault(orgasm, 0)
                character_data.h_state.extra_orgasm_feel[orgasm] += int(change_data.status_data[orgasm])
                # 额外高潮次数
                extra_count = pre_data - 10
                # 基础阈值为2w，每次高潮则乘以0.9的若干次方
                now_threshold = 20000 * (0.9 ** extra_count)
                now_threshold = max(1000, now_threshold)
                # 如果超过阈值，则进行额外高潮结算
                extra_add = int(character_data.h_state.extra_orgasm_feel[orgasm] // now_threshold)
                now_data = pre_data + extra_add
                character_data.h_state.extra_orgasm_feel[orgasm] -= extra_add * now_threshold
                character_data.h_state.extra_orgasm_count += extra_add
                extra_orgasm_dict[orgasm] = extra_add
            # 计算普通高潮次数
            normal_orgasm_dict[orgasm] = now_data - pre_data
        # 高潮结算函数
        orgasm_settle(character_id, change_data, normal_orgasm_dict, extra_orgasm_dict, un_count_orgasm_dict)
        # 寸止失败解放
        if character_data.h_state.orgasm_edge == 3:
            character_data.h_state.orgasm_edge = 2
            orgasm_settle(character_id, change_data, normal_orgasm_dict, extra_orgasm_dict, un_count_orgasm_dict)


def orgasm_settle(
    character_id: int,
    change_data: game_type.CharacterStatusChange,
    normal_orgasm_dict: dict = {},
    extra_orgasm_dict: dict = {},
    un_count_orgasm_dict: dict = {},
    ):
    """
    处理第二结算中的高潮结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    normal_orgasm_dict -- 普通高潮字典
    extra_orgasm_dict -- 额外高潮字典
    un_count_orgasm_dict -- 不计数高潮字典
    """

    character_data = cache.character_data[character_id]
    # print(f"进入{character_data.name}的高潮结算")

    part_count = 0  # 部位高潮计数
    tem_orgasm_set = set()  # 临时高潮部位集合
    for orgasm in range(8):
        # 跳过射精槽
        if orgasm == 3:
            continue

        pre_data = character_data.h_state.orgasm_level[orgasm] # 记录里的前高潮程度

        normal_orgasm_data = 0
        if orgasm in normal_orgasm_dict:
            normal_orgasm_data = normal_orgasm_dict[orgasm]
        extra_orgasm_data = 0
        if orgasm in extra_orgasm_dict:
            extra_orgasm_data = extra_orgasm_dict[orgasm]
        un_count_orgasm_data = 0
        if orgasm in un_count_orgasm_dict:
            un_count_orgasm_data = un_count_orgasm_dict[orgasm]

        # 如果已经进入额外高潮，则将额外高潮次数加入到高潮次数中
        if extra_orgasm_data > 0:
            now_data = pre_data + extra_orgasm_data
        # 否则加入普通高潮次数
        else:
            now_data = pre_data + normal_orgasm_data

        # 如果当前高潮程度大于记录的高潮程度，或者有额外高潮，则进行高潮结算
        if normal_orgasm_data > 0 or extra_orgasm_data > 0 or un_count_orgasm_data > 0:
            # 高潮次数统计
            climax_count = normal_orgasm_data + un_count_orgasm_data
            # 刷新记录
            character_data.h_state.orgasm_level[orgasm] = now_data
            # 时停状态下
            if handle_premise.handle_unconscious_flag_3(character_id):
                # 绝顶计入寸止计数
                character_data.h_state.time_stop_orgasm_count.setdefault(orgasm, 0)
                character_data.h_state.time_stop_orgasm_count[orgasm] += climax_count
                continue
            # 如果开启了绝顶寸止，则进行寸止结算，然后跳过
            if handle_premise.handle_self_orgasm_edge(character_id):
                # 根据技巧而绝顶的能够进行寸止的次数限制
                orgasm_edge_success_flag = judge_orgasm_edge_success(character_id)
                # 绝顶计入寸止计数
                character_data.h_state.orgasm_edge_count.setdefault(orgasm, 0)
                character_data.h_state.orgasm_edge_count[orgasm] += climax_count
                # 赋予寸止行为
                character_data.second_behavior[1250 + orgasm] = 1
                # 寸止失败记录
                if not orgasm_edge_success_flag:
                    character_data.h_state.orgasm_edge = 3
                continue
            # 该部位高潮计数+1
            part_count += 1
            # 加入高潮部位记录
            tem_orgasm_set.add(orgasm)
            # 判定触发哪些绝顶
            num = orgasm * 3 + 1000  # 通过num值来判断是二段行为记录的哪个位置
            # 开始根据概率计算
            for i in range(climax_count):
                # 判断高潮程度
                now_degree = judge_orgasm_degree(now_data)
                # 赋予二次行为
                character_data.second_behavior[num + now_degree] = 1
            # 绝顶解放状态下（含寸止解放与时停解放），如果次数大于等于3，则触发超强绝顶
            if handle_premise.handle_self_orgasm_edge_relase_or_time_stop_orgasm_relase(character_id) and climax_count >= 3:
                character_data.second_behavior[1090 + orgasm] = 1
            # B绝顶喷乳，需要乳汁量到80%
            if orgasm == 1 and handle_premise.handle_milk_ge_80(character_id):
                # now_draw.text += _("\n触发B绝顶喷乳\n")
                character_data.second_behavior[1071] = 1
            # U绝顶排尿，需要尿意条到80%
            if orgasm == 6 and handle_premise.handle_urinate_ge_80(character_id):
                # now_draw.text += _("\n触发U绝顶排尿\n")
                character_data.second_behavior[1072] = 1
            # 如果发生了额外高潮，则进行额外高潮结算
            if extra_orgasm_data > 0:
                # now_draw.text += _("\n触发额外高潮\n")
                character_data.second_behavior[1026] = 1
            # now_draw.draw()

    if part_count >= 1:
        # 饮精绝顶经验
        if character_data.h_state.shoot_position_body in [2, 15]:
            character_data.experience[111] += 1
            change_data.experience.setdefault(111, 0)
            change_data.experience[111] += 1
    # 如果部位高潮计数大于等于2，则结算多重绝顶
    if part_count >= 2:
        second_behavior_index = 1079 + part_count
        character_data.second_behavior[second_behavior_index] = 1
        character_data.h_state.plural_orgasm_set = tem_orgasm_set.copy()


def judge_orgasm_degree(level_count: int) -> int:
    """
    判断高潮程度
    Keyword arguments:
    level_count -- 高潮次数，10级以下为当前等级，以上则为10+额外高潮次数
    Return arguments:
    int -- 高潮程度，0小绝顶，1普通绝顶，2强绝顶，3超强绝顶
    """
    # 小、普、强的基础概率
    base_probability = [0.8, 0.15, 0.05]
    # 开始根据高潮次数计算概率
    for _ in range(level_count):
        # 前半段减少小的，增加普的和强的
        if base_probability[0] > 0:
            base_probability[0] -= 0.1
            base_probability[1] += 0.07
            base_probability[2] += 0.03
        # 后半段减少普的0.05，增加强的0.05
        else:
            base_probability[1] -= 0.05
            base_probability[2] += 0.05
    # 确保概率不为负数
    base_probability = [max(0, p) for p in base_probability]
    # 随机抽取概率
    random_num = random.uniform(0, sum(base_probability))
    # 判断高潮程度
    if random_num < base_probability[0]:
        return 0
    elif random_num < base_probability[0] + base_probability[1]:
        return 1
    else:
        return 2


def judge_orgasm_edge_success(character_id: int) -> bool:
    """
    判断高潮寸止是否成功
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    bool -- 是否成功
    """
    orgasm_edge_success_flag = False
    character_data: game_type.Character = cache.character_data[character_id]
    # 目前的高潮寸止数量
    all_orgasm_edge_count = 0
    for key, value in character_data.h_state.orgasm_edge_count.items():
        all_orgasm_edge_count += value
    # 玩家的高潮寸止技巧
    pl_character_data: game_type.Character = cache.character_data[0]
    skill_ability_lv = pl_character_data.ability[30]
    info_draw_text = "\n"
    over_count = skill_ability_lv * 3 - all_orgasm_edge_count
    # 如果次数小于技巧等级*3，则成功
    if over_count >= 0:
        orgasm_edge_success_flag = True
        if over_count <= 1:
            info_draw_text += _("成功寸止了{0}的绝顶，但差不多也到了能控制住的极限了，还是尽快释放出来比较好\n").format(character_data.name)
        else:
            info_draw_text += _("成功寸止了{0}的绝顶\n").format(character_data.name)
    # 否则，每超出一次，则有20%的概率失败
    else:
        fail_rate = 0.2 * over_count * -1
        random_num = random.uniform(0, 1)
        if random_num < fail_rate:
            orgasm_edge_success_flag = False
            info_draw_text += _("尝试寸止{0}的绝顶，但失败了\n").format(character_data.name)
        else:
            orgasm_edge_success_flag = True
            info_draw_text += _("成功寸止了{0}的绝顶，但已经超过了能控制住的极限，随时都可能释放出来\n").format(character_data.name)
    # 绘制提示信息
    info_draw = draw.NormalDraw()
    info_draw.text = info_draw_text
    info_draw.draw()
    return orgasm_edge_success_flag


def mark_effect(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    处理第二结算中的刻印结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """

    # print()
    # print("进入刻印结算")
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"name = {character_data.name},change_data.status_data = {change_data.status_data}")
    now_draw = draw.WaitDraw()
    now_draw_text = ""

    if character_id == 0:
        return

    # 快乐刻印检测单指令全部位总高潮次数，2次快乐1,8次快乐2,16次快乐3
    # 或检测单次H中总绝顶次数，5次快乐1,20次快乐2,50次快乐3
    single_happy_count = 0
    all_happy_count = 0
    for orgasm in range(8):
        single_happy_count += character_data.h_state.orgasm_count[orgasm][0]
        all_happy_count += character_data.h_state.orgasm_count[orgasm][1]
    # print(f"debug happy_count = {happy_count}")
    if character_data.ability[13] <= 0 and (single_happy_count >= 2 or all_happy_count >= 5):
        character_data.ability[13] = 1
        character_data.second_behavior[1030] = 1
        # 至少提升为欲望1
        if character_data.ability[33] < 0:
            character_data.ability[33] = 1
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至1级\n").format(character_data.name)
    if character_data.ability[13] <= 1 and (single_happy_count >= 8 or all_happy_count >= 20):
        character_data.ability[13] = 2
        character_data.second_behavior[1031] = 1
        # 至少提升为欲望3
        if character_data.ability[33] < 3:
            character_data.ability[33] = 3
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至3级\n").format(character_data.name)
    if character_data.ability[13] <= 2 and (single_happy_count >= 16 or all_happy_count >= 50):
        character_data.ability[13] = 3
        character_data.second_behavior[1032] = 1
        # 至少提升为欲望5
        if character_data.ability[33] < 5:
            character_data.ability[33] = 5
            now_draw_text += _("在快乐刻印的影响下，{0}的欲望提升至5级\n").format(character_data.name)

    # 屈服刻印检测屈服+恭顺+羞耻/5，30000屈服1，50000屈服2，100000屈服3
    yield_count = 0
    yield_count += character_data.status_data[10]
    yield_count += character_data.status_data[15]
    yield_count += character_data.status_data[16] / 5
    if yield_count >= 30000 and character_data.ability[14] <= 0:
        character_data.ability[14] = 1
        character_data.second_behavior[1033] = 1
        # 至少提升为顺从1
        if character_data.ability[31] < 1:
            character_data.ability[31] = 1
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至1级\n").format(character_data.name)
    if yield_count >= 50000 and character_data.ability[14] <= 1:
        character_data.ability[14] = 2
        character_data.second_behavior[1034] = 1
        # 至少提升为顺从3
        if character_data.ability[31] < 3:
            character_data.ability[31] = 3
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至3级\n").format(character_data.name)
    if yield_count >= 100000 and character_data.ability[14] <= 2:
        character_data.ability[14] = 3
        character_data.second_behavior[1035] = 1
        # 至少提升为顺从5
        if character_data.ability[31] < 5:
            character_data.ability[31] = 5
            now_draw_text += _("在屈服刻印的影响下，{0}的顺从提升至5级\n").format(character_data.name)

    # 苦痛刻印检测苦痛，20000苦痛1，40000苦痛2，80000苦痛3
    pain_count = 0
    pain_count += character_data.status_data[17]
    # 单次增加量
    if 17 in change_data.status_data:
        pain_count += change_data.status_data[17] * 5
    # 需要非深度无意识，且非心控-苦痛快感化
    if handle_premise.handle_normal_6(character_id) and handle_premise.handle_not_hypnosis_pain_as_pleasure(character_id):
        if pain_count >= 20000 and character_data.ability[15] <= 0:
            character_data.ability[15] = 1
            character_data.second_behavior[1036] = 1
            # 至少提升为受虐1
            if character_data.ability[36] < 1:
                character_data.ability[36] = 1
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至1级\n").format(character_data.name)
        if pain_count >= 40000 and character_data.ability[15] <= 1:
            character_data.ability[15] = 2
            character_data.second_behavior[1037] = 1
            # 至少提升为受虐3
            if character_data.ability[36] < 3:
                character_data.ability[36] = 3
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至3级\n").format(character_data.name)
        if pain_count >= 80000 and character_data.ability[15] <= 2:
            character_data.ability[15] = 3
            character_data.second_behavior[1038] = 1
            # 至少提升为受虐5
            if character_data.ability[36] < 5:
                character_data.ability[36] = 5
                now_draw_text += _("在苦痛刻印的影响下，{0}的受虐提升至5级\n").format(character_data.name)

    # 无觉刻印检测无意识下的绝顶，前3级同快乐，后3级仅检测无意识绝顶经验
    if handle_premise.handle_unconscious_flag_ge_1(character_id):
        all_happy_count = 0
        for orgasm in range(8):
            single_happy_count += character_data.h_state.orgasm_count[orgasm][0]
        all_happy_count = character_data.experience[78]
        # print(f"debug happy_count = {happy_count}")
        if character_data.ability[19] <= 0 and (single_happy_count >= 2 or all_happy_count >= 5):
            character_data.ability[19] = 1
            character_data.second_behavior[1061] = 1
        if character_data.ability[19] <= 1 and (single_happy_count >= 8 or all_happy_count >= 20):
            character_data.ability[19] = 2
            character_data.second_behavior[1062] = 1
        if character_data.ability[19] <= 2 and (single_happy_count >= 16 or all_happy_count >= 50):
            character_data.ability[19] = 3
            character_data.second_behavior[1063] = 1
        if character_data.ability[19] <= 3 and all_happy_count >= 100:
            character_data.ability[19] = 4
            character_data.second_behavior[1064] = 1
            # 至少提升为欲望6
            if character_data.ability[33] < 6:
                character_data.ability[33] = 6
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至6级\n").format(character_data.name)
        if character_data.ability[19] <= 4 and all_happy_count >= 200:
            character_data.ability[19] = 5
            character_data.second_behavior[1065] = 1
            # 至少提升为欲望7
            if character_data.ability[33] < 7:
                character_data.ability[33] = 7
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至7级\n").format(character_data.name)
        if character_data.ability[19] <= 5 and all_happy_count >= 500:
            character_data.ability[19] = 6
            character_data.second_behavior[1066] = 1
            # 至少提升为欲望8
            if character_data.ability[33] < 8:
                character_data.ability[33] = 8
                now_draw_text += _("在无觉刻印的影响下，{0}的欲望提升至8级\n").format(character_data.name)

    # 恐怖刻印检测恐怖+苦痛/5，20000恐怖1，40000恐怖2，80000恐怖3
    terror_count = 0
    terror_count += character_data.status_data[18]
    # 单次增加量
    if 18 in change_data.status_data:
        terror_count += change_data.status_data[18] * 5
    if 17 in change_data.status_data:
        terror_count += change_data.status_data[17]
    if terror_count >= 20000 and character_data.ability[17] <= 0:
        character_data.ability[17] = 1
        character_data.second_behavior[1042] = 1
    if terror_count >= 40000 and character_data.ability[17] <= 1:
        character_data.ability[17] = 2
        character_data.second_behavior[1043] = 1
    if terror_count >= 80000 and character_data.ability[17] <= 2:
        character_data.ability[17] = 3
        character_data.second_behavior[1044] = 1

    # 反发刻印检测反感+抑郁+恐怖+苦痛，10000反发1，30000反发2，80000反发3
    hate_count = 0
    hate_count += character_data.status_data[20]
    # 单次增加量
    if 20 in change_data.status_data:
        hate_count += change_data.status_data[20] * 5
    if 18 in change_data.status_data:
        hate_count += change_data.status_data[18]
    if 19 in change_data.status_data:
        hate_count += change_data.status_data[19]
    if 17 in change_data.status_data:
        hate_count += change_data.status_data[17]
    # 需要非深度无意识
    if handle_premise.handle_normal_6(character_id):
        if hate_count >= 10000 and character_data.ability[18] <= 0:
            character_data.ability[18] = 1
            character_data.second_behavior[1045] = 1
        if hate_count >= 50000 and character_data.ability[18] <= 1:
            character_data.ability[18] = 2
            character_data.second_behavior[1046] = 1
        if hate_count >= 100000 and character_data.ability[18] <= 2:
            character_data.ability[18] = 3
            character_data.second_behavior[1047] = 1

    if len(now_draw_text) > 0:
        now_draw_text += "\n"
    now_draw.text = now_draw_text
    now_draw.draw()

def item_effect(character_id: int, pl_to_npc: bool = False):
    """
    处理第二结算中的道具结算
    Keyword arguments:
    character_id -- 角色id
    pl_to_npc -- 玩家对NPC的行为结算
    """

    # print()
    # print(f"进入道具结算")
    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    num = 1100  # 通过num值来判断是二段行为记录的哪个位置

    if character_id != 0:

        # 玩家在H中正在对该NPC进行交互时，仅计算一遍，避免二次结算
        if pl_to_npc:
            pass
        elif pl_character_data.target_character_id == character_id and character_data.sp_flag.is_h:
            return

        for i in range(len(character_data.h_state.body_item)):
            if character_data.h_state.body_item[i][1]:
                # 事前避孕药的结算仅在每日问候的时候出现一起，其他时候不出现
                if i == 11 and character_data.second_behavior[1332] != 0:
                    continue
                character_data.second_behavior[num + i] = 1


def handle_comprehensive_value_effect(character_id: int, effect_all_value_list: list, change_data: game_type.CharacterStatusChange = None) -> int:
    """
    综合型基础数值结算
    Keyword arguments:
    character_id -- 角色id
    effect_all_value_list -- 结算的各项数值
    change_data -- 结算信息记录对象
    Return arguments:
    bool -- 是否结算成功
    """
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
    }
    
    # 创建一个字典来映射操作
    operation_mapping = {
        "G": lambda x, y: x + y,
        "L": lambda x, y: x - y,
        "E": lambda x, y: y
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
        # 角色口上flag
        elif attribute_name == "flag":
            final_character_data.author_flag.chara_int_flag_dict.setdefault(type_son_id, 0)
            final_character_data.author_flag.chara_int_flag_dict[type_son_id] = operation_func(final_character_data.author_flag.chara_int_flag_dict[type_son_id], int(effect_all_value_list[3]))
        # 绝顶
        elif attribute_name == "climax":
            from Script.Settle.default import base_chara_climix_common_settle
            if operation == "E":
                base_chara_climix_common_settle(final_character_id, type_son_id, degree = int(effect_all_value_list[3]))
            elif operation == "G":
                for i in range(int(effect_all_value_list[3]) + 1):
                    base_chara_climix_common_settle(final_character_id, type_son_id,  degree = i)
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

