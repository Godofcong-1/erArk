import random
import datetime
from typing import List
from Script.Core import (
    cache_control,
    value_handle,
    constant,
    game_type,
)
from Script.Design import (
    attr_calculation,
    clothing,
    nature,
)
from Script.Config import game_config


cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """


def init_attr(character_id: int):
    """
    初始化角色属性
    Keyword arguments:
    character_id -- 角色id
    """
    character_data: game_type.Character = cache.character_data[character_id]
    character_data.language[character_data.mother_tongue] = 10000
    character_data.birthday = attr_calculation.get_rand_npc_birthday(character_data.age)
    character_data.end_age = attr_calculation.get_end_age(character_data.sex)
    character_data.height = attr_calculation.get_height(character_data.sex, character_data.age)
    bmi = attr_calculation.get_bmi(character_data.weight_tem)
    character_data.weight = attr_calculation.get_weight(bmi, character_data.height.now_height)
    character_data.bodyfat = attr_calculation.get_body_fat(character_data.sex, character_data.bodyfat_tem)
    character_data.measurements = attr_calculation.get_measurements(
        character_data.sex,
        character_data.height.now_height,
        character_data.weight,
        character_data.bodyfat,
        character_data.bodyfat_tem,
    )
    character_data.sex_experience = attr_calculation.get_sex_experience(
        character_data.sex_experience_tem, character_data.sex
    )
    default_clothing_data = clothing.creator_suit(character_data.clothing_tem, character_data.sex)
    for clothing_id in default_clothing_data:
        clothing_data = default_clothing_data[clothing_id]
        character_data.clothing.setdefault(clothing_id, {})
        character_data.clothing[clothing_id][clothing_data.uid] = clothing_data
        character_data.clothing_data.setdefault(clothing_data.tem_id, set())
        character_data.clothing_data[clothing_data.tem_id].add(clothing_data.uid)
    chest_tem_config = game_config.config_chest[character_data.chest_tem]
    if chest_tem_config.weight_fix:
        fix_weight = value_handle.get_gauss_rand(
            chest_tem_config.weight_fix - 0.5, chest_tem_config.weight_fix + 0.5
        )
        character_data.weight += fix_weight
    character_data.chest = attr_calculation.get_chest(character_data.chest_tem, character_data.birthday)
    character_data.HP_max = attr_calculation.get_max_hit_point(character_data.hit_point_tem)
    character_data.hit_point = character_data.HP_max
    character_data.mana_point_max = attr_calculation.get_max_mana_point(character_data.mana_point_tem)
    character_data.mana_point = character_data.mana_point_max
    new_nature = nature.get_random_nature()
    for nature_id in new_nature:
        if nature_id not in character_data.nature:
            character_data.nature[nature_id] = new_nature[nature_id]
    # init_class(character_data)


# def init_class(character_data: game_type.Character):
#     """
#     初始化角色班级
#     character_data -- 角色对象
#     """
#     if character_data.age <= 18 and character_data.age >= 7:
#         class_grade = str(character_data.age - 6)
#         character_data.classroom = random.choice(constant.place_data["Classroom_" + class_grade])
#         cache.classroom_students_data.setdefault(character_data.classroom, set())
#         cache.classroom_students_data[character_data.classroom].add(character_data.cid)


def init_character_behavior_start_time(character_id: int, now_time: datetime.datetime):
    """
    将角色的行动开始时间同步为指定时间
    Keyword arguments:
    character_id -- 角色id
    now_time -- 指定时间
    """
    character_data = cache.character_data[character_id]
    start_time = datetime.datetime(
        now_time.year,
        now_time.month,
        now_time.day,
        now_time.hour,
        now_time.minute,
    )
    character_data.behavior.start_time = start_time


def character_rest_to_time(character_id: int, need_time: int):
    """
    设置角色状态为休息指定时间
    Keyword arguments:
    character_id -- 角色id
    need_time -- 休息时长(分钟)
    """
    character_data = cache.character_data[character_id]
    character_data.behavior["Duration"] = need_time
    character_data.behavior["BehaviorId"] = constant.Behavior.REST
    character_data.state = constant.CharacterStatus.STATUS_REST


def calculation_favorability(character_id: int, target_character_id: int, favorability: int) -> int:
    """
    按角色性格和关系计算最终增加的好感值
    Keyword arguments:
    character_id -- 角色id
    target_character_id -- 目标角色id
    favorability -- 基础好感值
    Return arguments:
    int -- 最终的好感值
    """
    character_data: game_type.Character = cache.character_data[character_id]
    target_data: game_type.Character = cache.character_data[target_character_id]
    fix = 1.0
    for i in {0, 1, 2, 5, 13, 14, 15, 16}:
        now_fix = 0
        if character_data.nature[i] > 50:
            nature_value = character_data.nature[i] - 50
            now_fix -= nature_value / 50
        else:
            now_fix += character_data.nature[i] / 50
        if target_data.nature[i] > 50:
            nature_value = target_data.nature[i] - 50
            if now_fix < 0:
                now_fix *= -1
                now_fix += nature_value / 50
                now_fix = now_fix / 2
            else:
                now_fix += nature_value / 50
        else:
            nature_value = target_data.nature[i]
            if now_fix < 0:
                now_fix += nature_value / 50
            else:
                now_fix -= nature_value / 50
                now_fix = now_fix / 2
        fix += now_fix
    if character_id in target_data.social_contact_data:
        fix += target_data.social_contact_data[character_id]
    favorability *= fix
    return favorability


def judge_character_in_class_time(character_id: int) -> bool:
    """
    校验角色是否处于上课时间
    Keyword arguments:
    character_id -- 角色id
    Return arguments:
    int -- 权重
    """
    character_data: game_type.Character = cache.character_data[character_id]
    now_time: datetime.datetime = character_data.behavior.start_time
    if now_time is None:
        now_time = cache.game_time
    now_time_value = now_time.hour * 100 + now_time.minute
    if character_data.age <= 18:
        school_id = 0
        if character_data.age in range(13, 16):
            school_id = 1
        elif character_data.age in range(16, 19):
            school_id = 2
        for session_id in game_config.config_school_session_data[school_id]:
            session_config = game_config.config_school_session[session_id]
            if now_time_value >= session_config.start_time and now_time_value <= session_config.end_time:
                return 1
        return 0
    if character_id not in cache.teacher_school_timetable:
        return 0
    now_week = now_time.weekday()
    timetable_list: List[game_type.TeacherTimeTable] = cache.teacher_school_timetable[character_id]
    for timetable in timetable_list:
        if timetable.week_day != now_week:
            continue
        if timetable.time <= now_time_value and timetable.end_time >= now_time_value:
            return 1
    return 0
