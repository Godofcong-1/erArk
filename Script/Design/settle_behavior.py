import datetime
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type, get_text, text_handle
from Script.Design import attr_text, attr_calculation, handle_premise
from Script.UI.Moudle import panel, draw
from Script.Config import game_config, normal_config
from Script.UI.Panel import ejaculation_panel

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """


def handle_settle_behavior(character_id: int, now_time: datetime.datetime, instruct_flag = 1):
    """
    处理结算角色行为
    Keyword arguments:
    character_id -- 角色id
    now_time -- 结算时间
    event_flag -- 事件结算变量，0只事件不指令，1只指令不事件
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    player_character_data: game_type.Character = cache.character_data[0]
    change_data = game_type.CharacterStatusChange()
    start_time = now_character_data.behavior.start_time
    add_time = int((now_time - start_time).seconds / 60)

    behavior_id = now_character_data.behavior.behavior_id
    if instruct_flag:
        # 进行一段结算
        if behavior_id in game_config.config_behavior_effect_data:
            for effect_id in game_config.config_behavior_effect_data[behavior_id]:
                constant.settle_behavior_effect_data[effect_id](character_id, add_time, change_data, now_time)
        # 进行二段结算
        check_second_effect(character_id, change_data)
        # 进行无意识结算
        check_unconscious_effect(character_id, add_time, change_data, now_time)
        # 结算上次进行聊天的时间，以重置聊天计数器#
        change_character_talkcount_for_time(character_id, now_time)

    if not instruct_flag:
        event_id = now_character_data.event.event_id
        if event_id != "":
            # 进行事件结算
            # print(f"debug handle_settle_behavior event_id = {event_id}")
            event_data: game_type.Event = game_config.config_event[event_id]
            for effect in event_data.effect:
                constant.settle_behavior_effect_data[int(effect)](
                    character_id, add_time, change_data, now_time
                )

        # 子事件
        son_event_id = now_character_data.event.son_event_id
        if son_event_id != "":
            # 进行事件结算
            # print(f"debug handle_settle_behavior son_event_id = {son_event_id}")
            event_data: game_type.Event = game_config.config_event[son_event_id]
            for effect in event_data.effect:
                constant.settle_behavior_effect_data[int(effect)](
                    character_id, add_time, change_data, now_time
                )

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
                name = f"\n{target_data.name}:"
                now_text = name

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
                    now_text += _("\n  催眠度") + text_handle.number_to_symbol_string(int(target_change.hypnosis_degree))
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
        if not exchange_flag:
            now_text_time = "\n\n " + str(add_time) + "分钟过去了\n"
        else:
            now_text_time = "\n\n 该行动将持续" + str(add_time) + "分钟\n"
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
):
    """
    处理第二结算
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    # print("进入第二结算")

    # 玩家检测自己
    if character_id == 0:
        # 高潮结算
        orgasm_effect(character_id)
        # 道具结算
        item_effect(character_id)
        # 进行结算
        second_behavior_effect(character_id, change_data)


    # NPC自己检测自己
    if character_id != 0:
        # 初见和每日招呼结算
        judge_character_first_meet(character_id)
        # 阴茎位置结算
        insert_position_effect(character_id)
        # 高潮结算
        orgasm_effect(character_id)
        # 道具结算
        item_effect(character_id)
        # 素质结算

        # 进行结算
        second_behavior_effect(character_id, change_data)

        # 刻印结算
        mark_effect(character_id, change_data)
        mark_list = [i for i in range(1030, 1048)]
        # 单独遍历结算刻印
        second_behavior_effect(character_id, change_data, mark_list)


def second_behavior_effect(
        character_id: int,
        change_data: game_type.CharacterStatusChange,
        second_behavior_list: list = None,
        ):
    """
    触发二段行为效果
    Keyword arguments:
    character_id -- 角色id
    change_data -- 状态变更信息记录对象
    """
    character_data: game_type.Character = cache.character_data[character_id]

    # 遍历二段行为id，进行结算
    for behavior_id, behavior_data in character_data.second_behavior.items():
        if behavior_data != 0:
            if second_behavior_list and behavior_id not in second_behavior_list:
                continue
            # 遍历该二段行为的所有结算效果，挨个触发
            for effect_id in game_config.config_second_behavior_effect_data[behavior_id]:
                constant.settle_second_behavior_effect_data[effect_id](character_id, change_data)
            # print(f"debug {character_data.name}触发二段行为效果，behavior_id = {behavior_id}")


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
        if target_character_data.sp_flag.unconscious_h:
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
                elif experience_id in range(51, 55):
                    constant.settle_behavior_effect_data[279](character_id, add_time, change_data, now_time)


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

    # 需要目标不在完全意识不清醒状态下
    if handle_premise.handle_normal_6(character_id):
        # 优先输出初见，次要输出每日招呼
        if character_data.first_record.first_meet and character_data.position == pl_character_data.position:
            character_data.second_behavior[1331] = 1
            character_data.first_record.first_meet = 0
            character_data.first_record.day_first_meet = 0
        elif character_data.first_record.day_first_meet and character_data.position == pl_character_data.position:
            character_data.first_record.day_first_meet = 0
            character_data.second_behavior[1332] = 1


def insert_position_effect(character_id: int):
    """
    处理第二结算中的阴茎位置结算
    Keyword arguments:
    character_id -- 角色id
    """

    character_data: game_type.Character = cache.character_data[character_id]
    pl_character_data: game_type.Character = cache.character_data[0]
    if character_data.h_state.insert_position != -1 and not handle_premise.handle_last_cmd_penis_position(0) and character_data.position == pl_character_data.position:
        position_index = 1201 + character_data.h_state.insert_position
        character_data.second_behavior[position_index] = 1


def orgasm_effect(character_id: int):
    """
    处理第二结算中的高潮结算
    Keyword arguments:
    character_id -- 角色id
    """

    # print()
    character_data: game_type.Character = cache.character_data[character_id]
    # print(f"进入{character_data.name}的高潮结算")

    # 检测射精
    if character_id == 0:
        if character_data.eja_point >= character_data.eja_point_max:
            if character_data.h_state.orgasm_level[3] % 3 == 0:
                character_data.second_behavior[1009] = 1
            elif character_data.h_state.orgasm_level[3] % 3 == 1:
                character_data.second_behavior[1010] = 1
            elif character_data.h_state.orgasm_level[3] % 3 == 2:
                character_data.second_behavior[1010] = 1
            character_data.eja_point = 0
            now_draw = ejaculation_panel.Ejaculation_Panel(width)
            now_draw.draw()
            line = draw.LineDraw("-", width)
            line.draw()
    else:
        # 检测人物的各感度数据是否等于该人物的高潮记录程度数据
        for orgasm in range(8):
            # now_data -- 当前高潮程度
            # pre_data -- 记录里的前高潮程度
            now_data = attr_calculation.get_status_level(character_data.status_data[orgasm])
            pre_data = character_data.h_state.orgasm_level[orgasm]
            # 跳过射精槽
            if orgasm == 3:
                continue
            if now_data > pre_data:
                # 判定触发哪些绝顶
                num = orgasm * 3 + 1000  # 通过num值来判断是二段行为记录的哪个位置
                # now_draw = draw.WaitDraw()
                # now_draw.width = width
                if (now_data - pre_data) >= 3:
                    # now_draw.text = _("\n触发小、普、强绝顶\n")
                    character_data.second_behavior[num] = 1
                    character_data.second_behavior[num + 1] = 1
                    character_data.second_behavior[num + 2] = 1
                elif (now_data - pre_data) == 2:
                    if pre_data % 3 == 0:
                        # now_draw.text = _("\n触发小、普绝顶\n")
                        character_data.second_behavior[num] = 1
                        character_data.second_behavior[num + 1] = 1
                    elif pre_data % 3 == 1:
                        # now_draw.text = _("\n触发普、强绝顶\n")
                        character_data.second_behavior[num + 1] = 1
                        character_data.second_behavior[num + 2] = 1
                    elif pre_data % 3 == 2:
                        # now_draw.text = _("\n触发强绝顶\n")
                        character_data.second_behavior[num + 2] = 1
                else:
                    if pre_data % 3 == 0:
                        # now_draw.text = _("\n触发小绝顶\n")
                        character_data.second_behavior[num] = 1
                    elif pre_data % 3 == 1:
                        # now_draw.text = _("\n触发普绝顶\n")
                        character_data.second_behavior[num + 1] = 1
                    elif pre_data % 3 == 2:
                        # now_draw.text = _("\n触发强绝顶\n")
                        character_data.second_behavior[num + 2] = 1
                # now_draw.draw()

                # 刷新记录
                character_data.h_state.orgasm_level[orgasm] = now_data


def mark_effect(character_id: int, change_data: game_type.CharacterStatusChange):
    """
    处理第二结算中的刻印结算
    Keyword arguments:
    now_data -- 当前高潮程度
    pre_data -- 记录里的前高潮程度
    character_id -- 角色id
    """

    # print()
    # print("进入刻印结算")
    character_data: game_type.Character = cache.character_data[character_id]

    # 快乐刻印检测单指令全部位总高潮次数，2次快乐1,8次快乐2,16次快乐3
    happy_count = 0
    for orgasm in range(8):
        happy_count += character_data.h_state.orgasm_count[orgasm][0]
        # 计数归零
        character_data.h_state.orgasm_count[orgasm][0] = 0
    if happy_count >= 2 and character_data.ability[13] <= 0:
        character_data.ability[13] = 1
        character_data.second_behavior[1030] = 1
    if happy_count >= 8 and character_data.ability[13] <= 1:
        character_data.ability[13] = 2
        character_data.second_behavior[1031] = 1
    if happy_count >= 16 and character_data.ability[13] <= 2:
        character_data.ability[13] = 3
        character_data.second_behavior[1032] = 1

    # 屈服刻印检测屈服+恭顺+羞耻/5，1000以上屈服1,3000以上屈服2,10000以上屈服3
    yield_count = 0
    yield_count += character_data.status_data[10]
    yield_count += character_data.status_data[15]
    yield_count += character_data.status_data[16] / 5
    if yield_count >= 1000 and character_data.ability[14] <= 0:
        character_data.ability[14] = 1
        character_data.second_behavior[1033] = 1
        # 至少提升为顺从1
        if character_data.ability[31] <= 0:
            character_data.ability[31] = 1
    if yield_count >= 3000 and character_data.ability[14] <= 1:
        character_data.ability[14] = 2
        character_data.second_behavior[1034] = 1
        # 至少提升为顺从2
        if character_data.ability[31] <= 1:
            character_data.ability[31] = 2
    if yield_count >= 10000 and character_data.ability[14] <= 2:
        character_data.ability[14] = 3
        character_data.second_behavior[1035] = 1
        # 至少提升为顺从3
        if character_data.ability[31] <= 2:
            character_data.ability[31] = 3

    # 苦痛刻印检测苦痛，2000苦痛1，4000苦痛2，8000苦痛3
    pain_count = 0
    if 17 in change_data.status_data:
        pain_count += change_data.status_data[17]
        if pain_count >= 2000 and character_data.ability[15] <= 0:
            character_data.ability[15] = 1
            character_data.second_behavior[1036] = 1
            # 至少提升为顺从1
            if character_data.ability[31] <= 0:
                character_data.ability[31] = 1
        if pain_count >= 4000 and character_data.ability[15] <= 1:
            character_data.ability[15] = 2
            character_data.second_behavior[1037] = 1
            # 至少提升为顺从2
            if character_data.ability[31] <= 1:
                character_data.ability[31] = 2
        if pain_count >= 8000 and character_data.ability[15] <= 2:
            character_data.ability[15] = 3
            character_data.second_behavior[1038] = 1
            # 至少提升为顺从3
            if character_data.ability[31] <= 2:
                character_data.ability[31] = 3

    # 无觉刻印未实装

    # 恐怖刻印检测恐怖+苦痛/5，2000恐怖1，4000恐怖2，8000恐怖3
    terror_count = 0
    if 18 in change_data.status_data:
        terror_count += character_data.status_data[18]
        terror_count += character_data.status_data[17] / 5
        if terror_count >= 2000 and character_data.ability[17] <= 0:
            character_data.ability[17] = 1
            character_data.second_behavior[1042] = 1
        if terror_count >= 4000 and character_data.ability[17] <= 1:
            character_data.ability[17] = 2
            character_data.second_behavior[1043] = 1
        if terror_count >= 8000 and character_data.ability[17] <= 2:
            character_data.ability[17] = 3
            character_data.second_behavior[1044] = 1

    # 反发刻印检测反感+抑郁/5+恐怖/5+苦痛/10，500反发1，1000反发2，2000反发3
    hate_count = 0
    if 20 in change_data.status_data:
        hate_count += character_data.status_data[20]
        hate_count += character_data.status_data[18] / 5
        hate_count += character_data.status_data[19] / 5
        hate_count += character_data.status_data[17] / 10
        if hate_count >= 1000 and character_data.ability[18] <= 0:
            character_data.ability[18] = 1
            character_data.second_behavior[1045] = 1
        if hate_count >= 2000 and character_data.ability[18] <= 1:
            character_data.ability[18] = 2
            character_data.second_behavior[1046] = 1
        if hate_count >= 4000 and character_data.ability[18] <= 2:
            character_data.ability[18] = 3
            character_data.second_behavior[1047] = 1


def item_effect(character_id: int):
    """
    处理第二结算中的道具结算
    Keyword arguments:
    character_id -- 角色id
    """

    # print()
    # print(f"进入道具结算")
    character_data: game_type.Character = cache.character_data[character_id]
    num = 1100  # 通过num值来判断是二段行为记录的哪个位置

    if character_id != 0:

        for i in range(len(character_data.h_state.body_item)):
            if character_data.h_state.body_item[i][1]:
                character_data.second_behavior[num + i] = 1
