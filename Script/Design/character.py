import random
import datetime
from types import FunctionType
from Script.Core import (
    cache_control,
    get_text,
    constant,
    game_type,
)
from Script.Design import (
    map_handle,
    attr_calculation,
    clothing,
    game_time,
    instuct_judege,
)
from Script.Config import normal_config
from Script.UI.Moudle import panel, draw

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """

_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def init_attr(character_id: int):
    """
    初始化角色属性
    Keyword arguments:
    character_id -- 角色id
    """
    # print("进入第二步的init_attr")
    # print("进入第二步的character_id :",character_id)
    character_data: game_type.Character = cache.character_data[character_id]
    # character_data.birthday = attr_calculation.get_rand_npc_birthday(character_data.age)
    # character_data.height = attr_calculation.get_height(character_data.sex, character_data.age)
    # character_data.weight = attr_calculation.get_weight(bmi, character_data.height.now_height)

    # 一系列归零函数
    character_data.ability = attr_calculation.get_ability_zero(character_data.ability)
    character_data.status_data = attr_calculation.get_status_zero(character_data.status_data)
    character_data.talent = attr_calculation.get_talent_zero(character_data.talent)
    character_data.experience = attr_calculation.get_experience_zero(character_data.experience)
    character_data.juel = attr_calculation.get_juel_zero(character_data.juel)
    character_data.second_behavior = attr_calculation.get_second_behavior_zero(character_data.second_behavior)
    character_data.dirty = attr_calculation.get_dirty_reset(character_data.dirty)
    character_data.item = attr_calculation.get_item_zero(character_data.item)
    character_data.h_state = attr_calculation.get_h_state_reset(character_data.h_state)
    character_data.first_record = attr_calculation.get_first_record_zero()
    character_data.action_info = attr_calculation.get_action_info_state_zero()
    character_data.event = attr_calculation.get_event_zero()
    character_data.work = attr_calculation.get_work_zero()
    character_data.entertainment = attr_calculation.get_entertainment_zero()
    character_data.pregnancy = attr_calculation.get_pregnancy_zero()
    character_data.sp_flag = game_type.SPECIAL_FLAG()
    character_data.chara_setting = attr_calculation.get_chara_setting_zero()
    character_data.assistant_services = attr_calculation.get_assistant_services_zero()
    character_data.body_manage = attr_calculation.get_body_manage_zero()
    # character_data.relationship = attr_calculation.get_relationship_zero(character_data.relationship)

    # 主角的初始处理，HP和MP的最大值默认为1000，EP最大值默认为1000，初始化信物，困倦程度归零
    if character_id == 0:
        character_data.talent = attr_calculation.get_Dr_talent_zero(character_data.talent)
        character_data.hit_point_max = 1000
        character_data.mana_point_max = 1000
        character_data.eja_point = 0
        character_data.eja_point_max = 1000
        character_data.sanity_point = 100
        character_data.sanity_point_max = 100
        character_data.semen_point = 100
        character_data.semen_point_max = 100
        character_data.pl_collection.token_list = attr_calculation.get_token_zero(
            character_data.pl_collection.token_list)
        character_data.tired_point = 0
        character_data.pl_ability = attr_calculation.get_pl_ability_zero()
        character_data.pl_collection = attr_calculation.get_collection_zero()
        character_data.cloth = attr_calculation.get_cloth_zero()
        character_data.favorability = {0:0}
        character_data.dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"]) # 此处不可使用翻译
        character_data.pre_dormitory = map_handle.get_map_system_path_str_for_list(["中枢", "博士房间"])
        # 初始收藏地点
        cache.collect_position_list = []
        cache.collect_position_list.append(['中枢', '博士房间'])
        cache.collect_position_list.append(['中枢', '博士办公室'])
        cache.collect_position_list.append(['贸易', '成人用品店'])
        cache.collect_position_list.append(['书', '藏品馆'])

    # 一系列初始化函数
    instuct_judege.init_character_behavior_start_time(character_id,cache.game_time)
    character_data.hit_point = character_data.hit_point_max
    character_data.mana_point = character_data.mana_point_max
    character_data.angry_point = random.randrange(1, 35)
    character_data.hunger_point = 240
    if character_id:
        clothing.get_underwear(character_id)
    # default_clothing_data = clothing.creator_suit(character_data.clothing_tem, character_data.sex)
    # for clothing_id in default_clothing_data:
    #     clothing_data = default_clothing_data[clothing_id]
    #     character_data.clothing.setdefault(clothing_id, {})
    #     character_data.clothing[clothing_id][clothing_data.uid] = clothing_data
    #     character_data.clothing_data.setdefault(clothing_data.tem_id, set())
    #     character_data.clothing_data[clothing_data.tem_id].add(clothing_data.uid)
    # init_class(character_data)


def input_name_func(ask_text: str) -> str:
    """
    输入角色名函数
    Keyword arguments:
    ask_text -- 询问的文本
    Return arguments:
    str -- 角色名
    """
    ask_name_panel = panel.AskForOneMessage()
    ask_name_panel.set(ask_text, 10)
    line_feed.draw()
    line = draw.LineDraw("=", width=window_width)
    line.draw()
    # 几种错误提示
    not_num_error = draw.NormalDraw()
    not_num_error.text = _("角色名不能为纯数字，请重新输入\n")
    not_system_error = draw.NormalDraw()
    not_system_error.text = _("角色名不能为系统保留字，请重新输入\n")
    not_name_error = draw.NormalDraw()
    not_name_error.text = _("已有角色使用该姓名，请重新输入\n")
    # 返回的角色名
    return_name = ""
    # 开始循环
    while 1:
        now_name = ask_name_panel.draw()
        if now_name.isdigit():
            not_num_error.draw()
            continue
        if now_name in get_text.translation_values:
            not_system_error.draw()
            continue
        if now_name in cache.npc_name_data:
            not_name_error.draw()
            continue
        return_name = now_name
        break

    return return_name


# def character_rest_to_time(character_id: int, need_time: int):
#     """
#     设置角色状态为休息指定时间
#     Keyword arguments:
#     character_id -- 角色id
#     need_time -- 休息时长(分钟)
#     """
#     character_data = cache.character_data[character_id]
#     character_data.behavior["Duration"] = need_time
#     character_data.behavior["BehaviorId"] = constant.Behavior.REST
#     character_data.state = constant.CharacterStatus.STATUS_REST


# def calculation_favorability(character_id: int, target_character_id: int, favorability: int) -> int:
#     """
#     按角色性格和关系计算最终增加的好感值
#     Keyword arguments:
#     character_id -- 角色id
#     target_character_id -- 目标角色id
#     favorability -- 基础好感值
#     Return arguments:
#     int -- 最终的好感值
#     """
#     character_data: game_type.Character = cache.character_data[character_id]
#     target_data: game_type.Character = cache.character_data[target_character_id]
#     fix = 1.0
#     for i in {0, 1, 2, 5, 13, 14, 15, 16}:
#         now_fix = 0
#         if character_data.nature[i] > 50:
#             nature_value = character_data.nature[i] - 50
#             now_fix -= nature_value / 50
#         else:
#             now_fix += character_data.nature[i] / 50
#         if target_data.nature[i] > 50:
#             nature_value = target_data.nature[i] - 50
#             if now_fix < 0:
#                 now_fix *= -1
#                 now_fix += nature_value / 50
#                 now_fix = now_fix / 2
#             else:
#                 now_fix += nature_value / 50
#         else:
#             nature_value = target_data.nature[i]
#             if now_fix < 0:
#                 now_fix += nature_value / 50
#             else:
#                 now_fix -= nature_value / 50
#                 now_fix = now_fix / 2
#         fix += now_fix
#     if character_id in target_data.social_contact_data:
#         fix += target_data.social_contact_data[character_id]
#     favorability *= fix
#     return favorability


def judge_character_time_over_24(character_id: int) -> bool:
    """
    校验角色的时间是否已过24点
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    start_time: datetime.datetime = character_data.behavior.start_time
    end_time = game_time.get_sub_date(minute=character_data.behavior.duration, old_date=start_time)

    if end_time.day != start_time.day:
        return 1
    return 0

def get_character_id_from_adv(adv_id: int) -> int:
    """
    通过剧情id获取角色id
    Keyword arguments:
    adv_id -- 剧情id
    Return arguments:
    int -- 角色id
    """
    for character_id in cache.character_data:
        if cache.character_data[character_id].adv == adv_id:
            return character_id
    return 0