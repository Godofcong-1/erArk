import datetime
import time
from functools import wraps
from types import FunctionType
from Script.Core import cache_control, constant, game_type, get_text, text_handle
from Script.Design import attr_text, attr_calculation
from Script.UI.Moudle import panel, draw
from Script.Config import game_config, normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
width = normal_config.config_normal.text_width
""" 屏幕宽度 """
_: FunctionType = get_text._
""" 翻译api """


def handle_settle_behavior(character_id: int, now_time: datetime.datetime):
    """
    处理结算角色行为
    Keyword arguments:
    character_id -- 角色id
    now_time -- 结算时间
    """
    now_character_data: game_type.Character = cache.character_data[character_id]
    player_character_data: game_type.Character = cache.character_data[0]
    status_data = game_type.CharacterStatusChange()
    start_time = now_character_data.behavior.start_time
    add_time = int((now_time - start_time).seconds / 60)
    behavior_id = now_character_data.behavior.behavior_id
    if behavior_id in game_config.config_behavior_effect_data:
        for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            constant.settle_behavior_effect_data[effect_id](character_id, add_time, status_data, now_time)
    #进行二段结算
    # check_second_effect(character_id)
    if player_character_data.target_character_id:
        # target_data = game_type.Character = cache.character_data[player_character_data.target_character_id]
        # print("target_data.name :",target_data.name)
        check_second_effect(0)
    #结算上次进行聊天的时间，以重置聊天计数器#
    change_character_talkcount_for_time(character_id, now_time)
    #注释掉了会按不交流的时间自动扣好感的系统#
    # change_character_favorability_for_time(character_id, now_time)
    #注释掉了社交关系#
    # change_character_social(character_id, status_data)
    now_judge = False
    if character_id:
        return
    if status_data is None:
        return
    if status_data.mana_point:
        now_judge = True
    if status_data.hit_point:
        now_judge = True
    # if len(status_data.knowledge):
    #     now_judge = True
    # if len(status_data.language):
    #     now_judge = True
    if len(status_data.status):
        now_judge = True
    # if len(status_data.sex_experience):
    #     now_judge = True
    if len(status_data.experience):
        now_judge = True
    if len(status_data.target_change) and not character_id:
        now_judge = True
    if now_judge:
        now_text_list = []
        now_draw = draw.NormalDraw()
        if now_character_data.cid == 0:
            now_draw.text = "\n" + now_character_data.name + now_character_data.nick_name + ": "
        else:
            now_draw.text = "\n" + now_character_data.name + ": "
        now_draw.width = width
        # now_draw.draw()
        now_text_list.append(now_draw.text)
        if status_data.hit_point and round(status_data.hit_point, 2) != 0:
            now_text_list.append(
                _("\n  体力:") + text_handle.number_to_symbol_string(int(status_data.hit_point))
            )
        if status_data.mana_point and round(status_data.mana_point, 2) != 0:
            now_text_list.append(
                _("\n  气力:") + text_handle.number_to_symbol_string(int(status_data.mana_point))
            )
        if len(status_data.status):
            now_text_list.extend(
                [
                    f"\n  {game_config.config_character_state[i].name}:{attr_text.get_value_text(status_data.status[i])}"
                    for i in status_data.status
                ]
            )
        # if len(status_data.knowledge):
        #     now_text_list.extend(
        #         [
        #             f"\n  {game_config.config_knowledge[i].name}:{attr_text.get_value_text(status_data.knowledge[i])}"
        #             for i in status_data.knowledge
        #         ]
        #     )
        # if len(status_data.language):
        #     now_text_list.extend(
        #         [
        #             f"\n  {game_config.config_language[i].name}:{attr_text.get_value_text(status_data.language[i])}"
        #             for i in status_data.language
        #         ]
        #     )
        # if len(status_data.sex_experience):
        #     now_text_list.extend(
        #         [
        #             game_config.config_organ[i].name
        #             + _("经验:")
        #             + text_handle.number_to_symbol_string(round(status_data.sex_experience[i], 2))
        #             for i in status_data.sex_experience
        #         ]
        #     )
        if len(status_data.experience):
            now_text_list.extend(
                [
                    _("\n  ")
                    + game_config.config_experience[i].name
                    + _("经验:")
                    + text_handle.number_to_symbol_string(status_data.experience[i])
                    for i in status_data.experience
                ]
            )
        if len(status_data.target_change):
            for target_character_id in status_data.target_change:
                if character_id and target_character_id:
                    continue
                target_change: game_type.TargetChange = status_data.target_change[target_character_id]
                target_data: game_type.Character = cache.character_data[target_character_id]
                now_text = f"\n{target_data.name}:"
                judge = 0
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
                    ) + text_handle.number_to_symbol_string(float(target_change.trust))
                    judge = 1
                # if target_change.new_social != target_change.old_social:
                #     now_text += (
                #         " "
                #         + game_config.config_social_type[target_change.old_social].name
                #         + "->"
                #         + game_config.config_social_type[target_change.new_social].name
                #     )
                #     judge = 1
                if len(target_change.status):
                    for status_id in target_change.status:
                        if target_change.status[status_id]:
                            now_text += (
                                "\n  "
                                + game_config.config_character_state[status_id].name
                                + text_handle.number_to_symbol_string(
                                    int(target_change.status[status_id])
                                )
                            )
                            judge = 1
                if len(target_change.experience):
                    for experience_id in target_change.experience:
                        if target_change.experience[experience_id]:
                            now_text += (
                                "\n  "
                                + game_config.config_experience[experience_id].name
                                + _(":")
                                + text_handle.number_to_symbol_string(
                                    int(target_change.experience[experience_id])
                                )
                            )
                            judge = 1
                if target_change.hit_point and round(target_change.hit_point, 2) != 0:
                    now_text += _("\n  体力:") + text_handle.number_to_symbol_string(int(target_change.hit_point))
                    judge = 1
                if target_change.mana_point and round(target_change.mana_point, 2) != 0:
                    now_text += _("\n  气力:") + text_handle.number_to_symbol_string(int(target_change.mana_point))
                    judge = 1
                if judge:
                    now_text_list.append(now_text)
        now_text_time = "\n\n  " + str(add_time) + "分钟过去了\n"
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
    elif consume_time >= 10 and consume_time < 100:
        return (consume_time - 9) * 10 + 9
    elif consume_time >= 100 and consume_time < 1000:
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
    if not target_data.talk_time:
        target_data.talk_time = now_time
    if now_time.day == target_data.talk_time.day and now_time.hour > target_data.talk_time.hour:
        target_data.talk_count -= now_time.hour - target_data.talk_time.hour
        target_data.talk_time = now_time
        # print("检测到时间前进了至少一小时，聊天计数器-1")
    elif now_time.day != target_data.talk_time.day:
        target_data.talk_count = 0
        target_data.talk_time = now_time
        # print("检测到时间前进了至少一天，聊天计数器归零")
    if target_data.talk_count < 0 :
        target_data.talk_count = 0
    # print("target_data.talk_count :",target_data.talk_count)


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

def check_second_effect(character_id: int):
    """
    处理第二结算
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_character_id = character_data.target_character_id
    target_character_data : game_type.Character = cache.character_data[target_character_id]
    status_data = game_type.CharacterStatusChange()
    # print()
    # print("进入第二结算")

    #检测自己
    # for orgasm in range(8):
    #     now_orgasm_level = attr_calculation.get_status_level(character_data.status_data[orgasm])
    #     # print("当前orgasm = ",orgasm)
    #     # print("当前character_data.status_data[orgasm] = ",character_data.status_data[orgasm])
    #     # print("当前now_orgasm_level = ",now_orgasm_level)
    #     # print("当前character_data.orgasm_level[orgasm] = ",character_data.orgasm_level[orgasm])
    #     if now_orgasm_level != character_data.orgasm_level[orgasm]:
    #         orgasm_effect(now_orgasm_level, character_data.orgasm_level[orgasm])
    #         character_data.orgasm_level[orgasm] = now_orgasm_level

    #检测交互对象
    orgasm_effect(target_character_id)

    #遍历二段行为id，进行结算
    for second_behavior_id in range(len(target_character_data.second_behavior)):
        if target_character_data.second_behavior[second_behavior_id] != 0:
            print("second_behavior_id :",second_behavior_id)
            print("target_character_data.second_behavior[second_behavior_id] :",target_character_data.second_behavior[second_behavior_id])
            for effect_id in game_config.config_second_behavior_effect_data[second_behavior_id]:
                print("effect_id :",effect_id)
                constant.settle_second_behavior_effect_data[effect_id](character_id, status_data)
        # if behavior_id in game_config.config_behavior_effect_data:
            # for effect_id in game_config.config_behavior_effect_data[behavior_id]:
            #     constant.settle_behavior_effect_data[effect_id](character_id, add_time, status_data, now_time)


def orgasm_effect(character_id: int):
    """
    处理第二结算中的高潮结算
    Keyword arguments:
    now_data -- 当前高潮程度
    pre_data -- 记录里的前高潮程度
    character_id -- 角色id
    """

    # print()
    # print("进入高潮结算")
    character_data: game_type.Character = cache.character_data[character_id]

    #检测人物的各感度数据是否等于该人物的高潮记录程度数据
    for orgasm in range(8):
        now_data = attr_calculation.get_status_level(character_data.status_data[orgasm])
        pre_data = character_data.orgasm_level[orgasm]
        if now_data != pre_data:
            #判定触发哪些绝顶
            num = orgasm*3 #通过num值来判断是二段行为记录的哪个位置
            if (now_data - pre_data) >= 3:
                print("触发小、普、强绝顶")
                character_data.second_behavior[num] = 1
                character_data.second_behavior[num+1] = 1
                character_data.second_behavior[num+2] = 1
            elif (now_data - pre_data) == 2:
                if pre_data % 3 == 0:
                    print("触发小、普绝顶")
                    character_data.second_behavior[num] = 1
                    character_data.second_behavior[num+1] = 1
                elif pre_data % 3 == 1:
                    print("触发普、强绝顶")
                    character_data.second_behavior[num+1] = 1
                    character_data.second_behavior[num+2] = 1
                elif pre_data % 3 == 2:
                    print("触发强绝顶")
                    character_data.second_behavior[num+2] = 1
            else:
                if pre_data % 3 == 0:
                    print("触发小绝顶")
                    character_data.second_behavior[num] = 1
                elif pre_data % 3 == 1:
                    print("触发普绝顶")
                    character_data.second_behavior[num+1] = 1
                elif pre_data % 3 == 2:
                    print("触发强绝顶")
                    character_data.second_behavior[num+2] = 1
            
            #刷新记录
            character_data.orgasm_level[orgasm] = now_data
